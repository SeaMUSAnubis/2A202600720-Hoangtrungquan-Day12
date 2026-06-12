"""
Cost Guard — Bảo Vệ Budget LLM

Mục tiêu: Tránh bill bất ngờ từ LLM API.
- Đếm tokens đã dùng mỗi ngày
- Cảnh báo khi gần hết budget
- Block khi vượt budget

Đã được refactor để sử dụng Redis theo yêu cầu của bài thực hành.
"""
import os
import time
import json
import logging
from fastapi import HTTPException

try:
    import redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    _redis = redis.from_url(REDIS_URL, decode_responses=True)
    _redis.ping()
    USE_REDIS = True
except Exception:
    USE_REDIS = False
    _memory_store = {}

logger = logging.getLogger(__name__)

PRICE_PER_1K_INPUT_TOKENS = 0.00015
PRICE_PER_1K_OUTPUT_TOKENS = 0.0006

class CostGuard:
    def __init__(
        self,
        daily_budget_usd: float = 1.0,
        global_daily_budget_usd: float = 10.0,
        warn_at_pct: float = 0.8,
    ):
        self.daily_budget_usd = daily_budget_usd
        self.global_daily_budget_usd = global_daily_budget_usd
        self.warn_at_pct = warn_at_pct

    def _get_global_cost(self) -> float:
        today = time.strftime("%Y-%m-%d")
        key = f"global_budget:{today}"
        if USE_REDIS:
            return float(_redis.get(key) or 0)
        return float(_memory_store.get(key, 0))

    def _add_global_cost(self, cost: float):
        today = time.strftime("%Y-%m-%d")
        key = f"global_budget:{today}"
        if USE_REDIS:
            _redis.incrbyfloat(key, cost)
            _redis.expire(key, 86400)
        else:
            _memory_store[key] = self._get_global_cost() + cost

    def _get_user_cost(self, user_id: str) -> float:
        today = time.strftime("%Y-%m-%d")
        key = f"budget:{user_id}:{today}"
        if USE_REDIS:
            return float(_redis.get(key) or 0)
        return float(_memory_store.get(key, 0))

    def _add_user_cost(self, user_id: str, cost: float):
        today = time.strftime("%Y-%m-%d")
        key = f"budget:{user_id}:{today}"
        if USE_REDIS:
            _redis.incrbyfloat(key, cost)
            _redis.expire(key, 86400)
        else:
            _memory_store[key] = self._get_user_cost(user_id) + cost

    def check_budget(self, user_id: str) -> None:
        global_cost = self._get_global_cost()
        if global_cost >= self.global_daily_budget_usd:
            logger.critical(f"GLOBAL BUDGET EXCEEDED: ${global_cost:.4f}")
            raise HTTPException(
                status_code=503,
                detail="Service temporarily unavailable due to budget limits. Try again tomorrow.",
            )

        user_cost = self._get_user_cost(user_id)
        if user_cost >= self.daily_budget_usd:
            raise HTTPException(
                status_code=402,
                detail={
                    "error": "Daily budget exceeded",
                    "used_usd": user_cost,
                    "budget_usd": self.daily_budget_usd,
                    "resets_at": "midnight UTC",
                },
            )

        if user_cost >= self.daily_budget_usd * self.warn_at_pct:
            logger.warning(
                f"User {user_id} at {user_cost/self.daily_budget_usd*100:.0f}% budget"
            )

    def record_usage(
        self, user_id: str, input_tokens: int, output_tokens: int
    ) -> None:
        cost = (input_tokens / 1000 * PRICE_PER_1K_INPUT_TOKENS +
                output_tokens / 1000 * PRICE_PER_1K_OUTPUT_TOKENS)
        self._add_global_cost(cost)
        self._add_user_cost(user_id, cost)
        logger.info(
            f"Usage recorded: user={user_id} cost=${cost:.6f}"
        )

    def get_usage(self, user_id: str) -> dict:
        user_cost = self._get_user_cost(user_id)
        return {
            "user_id": user_id,
            "cost_usd": user_cost,
            "budget_usd": self.daily_budget_usd,
            "budget_remaining_usd": max(0, self.daily_budget_usd - user_cost),
            "budget_used_pct": round(user_cost / self.daily_budget_usd * 100, 1) if self.daily_budget_usd else 0,
        }

cost_guard = CostGuard(daily_budget_usd=1.0, global_daily_budget_usd=10.0)
