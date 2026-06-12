# My Production Agent

This is the Final Project for Day 12. It implements a production-ready AI agent using FastAPI, Redis, Nginx, and Docker.

## Features Included
- **Stateless Design**: Uses Redis for tracking conversation histories, rate limiting, and cost guard.
- **Dockerized**: Employs Multi-stage Docker builds.
- **Security**: Includes API key verification via headers (`X-API-Key`).
- **Resilience**: Implements `/health` and `/ready` probes, along with Graceful Shutdown.

## How to Run locally

### Pre-requisites
- Docker & Docker Compose

### Run the stack
```bash
docker compose up --build -d
```
This will start 3 agent instances behind an Nginx load balancer.

### Verify Health
```bash
curl http://localhost/health
```

### Call the Agent
Make sure to include the valid API key:
```bash
curl -X POST "http://localhost/ask?question=Hello" \
     -H "X-API-Key: my-secret-key"
```
