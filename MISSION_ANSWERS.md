> **Student Name:** Hoàng Trung Quân
> **Student ID:** 2A202600720
> **Date:** 2026-06-12

## Part 1: Localhost vs Production (10 Points)

### Exercise 1.1: Phân tích Anti-patterns (Những điểm yếu chí mạng)
Trong một ứng dụng AI Agent chạy nội bộ cơ bản, có rất nhiều rủi ro nếu đẩy thẳng lên Production:
1. **Lộ lọt API Keys**: Việc gán trực tiếp (hardcode) các khoá bảo mật như `OPENAI_API_KEY` vào source code là cực kỳ nguy hiểm. Nếu code bị rò rỉ, hacker có thể sử dụng key này gây thiệt hại tài chính.
2. **Cấu hình cứng (Hardcoded Configurations)**: Port `8000` và địa chỉ IP `127.0.0.1` bị fix cứng, làm cho ứng dụng không thể linh hoạt chạy trên các cổng khác khi deploy lên cloud.
3. **Chạy ở Debug Mode**: Chế độ này thường phơi bày các thông báo lỗi chi tiết ra ngoài màn hình (stack trace), gián tiếp cung cấp thông tin cho hacker tấn công hệ thống.
4. **Không có hệ thống giám sát (No Health Checks)**: Ứng dụng không có cơ chế báo cáo tình trạng sống/chết. Nền tảng cloud không thể biết ứng dụng đang treo hay đang chạy để khởi động lại.
5. **Đóng ứng dụng đột ngột (No Graceful Shutdown)**: Khi tắt server, ứng dụng sẽ cắt đứt lập tức mọi request đang xử lý dở dang, gây ra trải nghiệm tồi tệ cho người dùng và có thể mất dữ liệu giao dịch.

### Exercise 1.3: Bảng so sánh Localhost vs Production
| Yếu tố (Feature) | Chế độ Localhost (Develop) | Chế độ Production | Giải thích sự cần thiết |
|------------------|---------------------------|-------------------|-----------------------|
| **Cấu hình (Config)** | Hardcode trong code | Dùng Biến môi trường (Environment Variables) | Giúp bảo mật thông tin nhạy cảm và dễ dàng thay đổi cấu hình mà không cần sửa code. |
| **Giám sát (Health Check)** | Không có | Có các endpoint `/health`, `/ready` | Giúp Cloud Platform (Kubernetes, Docker) tự động quản lý vòng đời ứng dụng (tự restart nếu lỗi). |
| **Ghi log (Logging)** | Lệnh `print()` thô sơ | Log định dạng JSON có cấu trúc | Log JSON dễ dàng được thu thập và phân tích bởi các công cụ như ELK Stack, Datadog. |
| **Tắt ứng dụng (Shutdown)** | Tắt ngay lập tức (Force kill) | Tắt an toàn (Graceful Shutdown) | Đảm bảo hệ thống hoàn thành nốt các requests đang chạy trước khi dừng hẳn. |

---

## Part 2: Docker (10 Points)

### Exercise 2.1: Phân tích cấu trúc Dockerfile
1. **Tại sao sử dụng `python:3.11-slim` làm Base Image?**
   - Phiên bản `slim` là phiên bản đã được tối giản hoá, loại bỏ các công cụ dư thừa của hệ điều hành. Giúp giảm thiểu tối đa kích thước ảnh, tăng tốc độ pull image và giảm bề mặt tấn công.
2. **Thư mục làm việc (`WORKDIR /app`) có ý nghĩa gì?**
   - Chỉ định thư mục mặc định bên trong container. Mọi lệnh `RUN`, `CMD`, `COPY` sau đó sẽ tự động chạy trong thư mục này, giúp file hệ thống gọn gàng.
3. **Tại sao lại COPY file `requirements.txt` riêng lẻ trước khi COPY toàn bộ source code?**
   - Đây là kỹ thuật tận dụng **Docker Cache Layer**. Lớp chứa các thư viện tải từ mạng thường rất nặng. Nếu ta copy source code chung với file này, cứ mỗi lần sửa 1 dòng code, Docker sẽ phải tải lại toàn bộ thư viện. Việc tách riêng giúp Docker dùng lại bộ cache cũ nếu file `requirements.txt` không đổi.
4. **Sự khác biệt giữa CMD và ENTRYPOINT?**
   - `ENTRYPOINT` định nghĩa lệnh thực thi lõi (khó bị ghi đè), trong khi `CMD` truyền tham số mặc định cho `ENTRYPOINT`. Nếu dùng `CMD`, người dùng có thể dễ dàng thay đổi lệnh chạy khi gọi `docker run`.

### Exercise 2.3: Đánh giá Multi-stage Build (Dung lượng Image)
- **Image tiêu chuẩn (Develop)**: Kích thước thường dao động khoảng ~300 MB đến 400 MB.
- **Image Multi-stage (Production)**: Kích thước giảm xuống chỉ còn ~150 MB.
- **Tại sao?**: Multi-stage build chia quá trình làm 2 bước (Build và Serve). Ở bước Build, ta cần các công cụ nặng như `gcc`, `build-essential`. Nhưng ở bước Serve, ta chỉ copy các file nhị phân (wheels) đã build xong qua một hệ điều hành trống. Từ đó vứt bỏ hoàn toàn được đống rác công cụ build.

---

## Part 3: Cloud Deployment (10 Points)

### Exercise 3.1: Thông tin triển khai Railway/Render
- **Public URL**: *[Cập nhật URL thực tế của bạn tại file DEPLOYMENT.md]*
- Vui lòng tham khảo file `DEPLOYMENT.md` và thư mục `screenshots/` để xem minh chứng triển khai thành công lên nền tảng đám mây.

---

## Part 4: API Security (10 Points)

### Phân tích hệ thống bảo mật & Test Results (Exercise 4.1-4.4)
Hệ thống được thiết lập cơ chế phòng thủ 3 lớp tại Nginx Gateway và Middleware:
1. **API Key Authentication**:
   - Khi tôi gửi request **thiếu** hoặc **sai** Header `X-API-Key`, hệ thống lập tức chặn ở cửa và trả về mã lỗi HTTP `401 Unauthorized`.
   - Chỉ khi truyền đúng API Key (`my-secret-key`), hệ thống mới cho phép đi tiếp, kết quả trả về `200 OK`.
2. **Rate Limiting (Chống Spam)**:
   - Cơ chế này sử dụng cấu trúc `r.pipeline()` của Redis. Hệ thống dùng sliding window để đếm số lượng requests của một IP/Key trong 60 giây qua. 
   - Khi tôi test gửi liên tiếp 15 requests trong khi giới hạn là 10, từ request thứ 11 hệ thống đã chặn lại và báo lỗi `429 Too Many Requests`. Điều này giúp tiết kiệm tiền gọi LLM nếu bị DDOS.
3. **Cost Guard (Kiểm soát chi phí)**:
   - **Cách thực hiện**: Mỗi lần người dùng gọi LLM, hệ thống ước tính chi phí và cộng dồn vào một Redis Key đại diện cho ngân sách tháng (ví dụ: `budget:user_123:2026-06`). 
   - Dùng lệnh `r.incrbyfloat()` để cộng số tiền thập phân. Key được cài đặt `expire` sau 32 ngày để tự động reset ngân sách sang tháng mới.
   - Khi ngân sách vượt mức $10.0, API trả về mã lỗi `402 Payment Required`.

---

## Part 5: Scaling & Reliability (10 Points)

### Phân tích Kiến trúc Scale (Exercise 5.1-5.5)
Để hệ thống có thể mở rộng từ 1 máy chủ lên 100 máy chủ (Scaling), tôi đã triển khai các tiêu chuẩn sau:
1. **Mô hình Stateless (Phi trạng thái)**:
   - Lỗi kinh điển của các app AI là lưu lịch sử chat trong biến danh sách (List) của bộ nhớ Python (RAM). Khi Load Balancer điều hướng request sang một máy chủ B, máy chủ B sẽ không biết người dùng vừa chat gì ở máy chủ A.
   - **Cách khắc phục**: Toàn bộ lịch sử hội thoại được đẩy vào Redis (Dùng `r.lpush` và `r.lrange`). Nhờ vậy, bất kể request rơi vào container nào, các container đều truy xuất chung một nguồn dữ liệu lịch sử.
2. **Health / Readiness Probes**:
   - `/health` báo cáo thời gian uptime, cho biết ứng dụng có đang sống không (Liveness).
   - `/ready` kiểm tra xem hệ thống đã kết nối được với Database/Redis chưa. Nếu Redis chết, `/ready` báo `503 Service Unavailable`, lúc đó Load Balancer sẽ ngừng gửi traffic đến container này.
3. **Graceful Shutdown**:
   - Trong `main.py`, tôi sử dụng `lifespan` context manager. Khi nhận tín hiệu tắt từ Docker, hệ thống sẽ bật cờ `_is_ready = False` để ngừng nhận request mới, đồng thời chạy vòng lặp `while _in_flight_requests > 0` (tối đa 30s) để xử lý cho xong các request đang dang dở rồi mới chịu thoát.
