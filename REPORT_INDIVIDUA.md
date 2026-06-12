# Báo Cáo Cá Nhân - Thực Hành Môn Cloud Infrastructure & Deployment (Day 12)

## 1. Tổng Quan Quá Trình Thực Hành (Chi tiết những công việc đã làm)
Trong buổi học Day 12, tôi đã thực hành quy trình chuyển đổi một ứng dụng AI Agent từ môi trường phát triển cục bộ (localhost) lên môi trường sản xuất (production) chuyên nghiệp. Quá trình này bao gồm việc áp dụng các tiêu chuẩn quan trọng về bảo mật, đóng gói, và khả năng mở rộng hệ thống. Cụ thể, tôi đã hoàn thành các tác vụ sau:

- **Phân tích Localhost vs Production:** Tìm hiểu và khắc phục các rủi ro của việc chạy ứng dụng ở localhost (như lộ API key, hardcode cổng mạng). Thiết lập cấu hình ứng dụng thông qua biến môi trường (Environment Variables) để đảm bảo an toàn.
- **Đóng gói ứng dụng với Docker (Containerization):** 
  - Trực tiếp viết `Dockerfile` cho ứng dụng Python.
  - Sử dụng kỹ thuật Multi-stage build để giảm dung lượng Docker image (từ ~300MB xuống còn một nửa), qua đó tăng tốc độ khởi động và tiết kiệm tài nguyên.
  - Sử dụng `docker-compose.yml` để thiết lập kiến trúc đa dịch vụ (Multi-container).
- **Triển khai lên Cloud (Cloud Deployment):** Thực hành triển khai ứng dụng lên các dịch vụ đám mây (Railway/Render), thiết lập các biến số môi trường trên cloud platform và đảm bảo ứng dụng có thể truy cập qua Public URL.
- **Bảo mật API (API Security):** 
  - Triển khai cơ chế xác thực người dùng bằng API Key và JWT.
  - Thiết lập Rate Limiting (giới hạn số lượng request) và Cost Guard (kiểm soát ngân sách) sử dụng Redis, ngăn chặn tình trạng lạm dụng API dẫn đến vượt quá chi phí sử dụng.
- **Khả năng mở rộng và độ tin cậy (Scaling & Reliability):**
  - Refactor mã nguồn từ Stateful sang Stateless, di chuyển việc lưu trữ dữ liệu tạm thời sang Redis.
  - Cấu hình các endpoint kiểm tra tình trạng hệ thống (`/health` và `/ready`) để phục vụ Load Balancer.
  - Cài đặt Graceful Shutdown, đảm bảo server luôn hoàn tất các request đang xử lý dở dang trước khi tắt.
  - Tích hợp Nginx làm API Gateway/Load Balancer để phân tán traffic đều đặn cho nhiều instance backend.

---

## 2. Sản Phẩm Cá Nhân - Legal AI Hub

Để ứng dụng chuyên sâu kiến thức từ bài Lab, tôi đã tự thiết kế và xây dựng một ứng dụng mang tên **Legal AI Hub**. Đây là một hệ thống tư vấn pháp luật sử dụng cấu trúc đa tác nhân (Multi-Agent) thông qua bộ công cụ LangGraph và Langchain. 

### Giới Thiệu Ứng Dụng (Legal AI Hub)
Legal AI Hub là một trợ lý ảo hỗ trợ người dùng tra cứu, phân tích và giải đáp các vấn đề liên quan đến pháp luật. Thay vì chỉ sử dụng một LLM cơ bản, hệ thống phân chia luồng suy luận thành nhiều Agent chuyên biệt (ví dụ: Agent tra cứu dữ liệu luật, Agent tư vấn,...) phối hợp với nhau để đưa ra câu trả lời chính xác, mang tính pháp lý cao.

**Cấu trúc kỹ thuật của hệ thống:**
1. **Frontend (React & Vite):** Cung cấp giao diện tương tác trực quan cho người dùng. Ứng dụng Frontend được đóng gói và phục vụ (serve) thông qua Nginx rất nhẹ nhàng.
2. **Backend (FastAPI & LangGraph):** Đóng vai trò là "bộ não" xử lý. Backend này đã được tôi tinh chỉnh chuẩn Production: hoạt động dưới dạng Stateless (không lưu trạng thái ở RAM server), tích hợp đầy đủ Health Probes (`/health`, `/ready`), Middleware và Graceful Shutdown.
3. **API Gateway (Nginx):** Đóng vai trò cổng giao tiếp duy nhất ở cổng 80, nhận request và tự động phân luồng:
   - `/` được điều hướng đến Frontend.
   - `/api/*` được điều hướng đến Backend, tự động cân bằng tải (Load Balancing) tới các backend instance nếu hệ thống mở rộng.

### Hướng Dẫn Sử Dụng
Để khởi chạy và trải nghiệm hệ thống Legal AI Hub, bạn làm theo các bước sau:

**Bước 1: Di chuyển vào thư mục mã nguồn**
```bash
cd custom_web_app
```
*(Nếu cần, hãy sao chép file `.env.example` thành `.env` trong thư mục `backend` và điền các khóa API như `OPENAI_API_KEY`)*

**Bước 2: Khởi động hệ thống (Yêu cầu có Docker)**
Chạy lệnh sau để build ảnh và khởi động tất cả các thành phần kiến trúc:
```bash
docker compose up --build -d
```
Hệ thống sẽ tự động cấu hình mạng, dựng Backend, Frontend và API Gateway. Chữ `-d` giúp chạy ngầm (detached mode) để bạn có thể tiếp tục sử dụng terminal.

**Bước 3: Trải nghiệm ứng dụng**
- Mở trình duyệt và truy cập vào địa chỉ: **`http://localhost`** để tương tác với giao diện hỏi đáp pháp lý.
- Ngoài ra, bạn có thể kiểm tra tình trạng của API bằng lệnh:
  ```bash
  curl http://localhost/health
  ```

**Bước 4: Demo khả năng chịu tải (Scaling)**
Hệ thống đã được thiết kế sẵn sàng để mở rộng nếu số lượng người dùng tăng lên. Bạn có thể yêu cầu Docker tạo ra thêm 3 bản sao của Backend bằng lệnh:
```bash
docker compose up --scale backend=3 -d
```
Ngay lập tức, Nginx sẽ nhận diện 3 máy chủ Backend này và luân phiên chia đều traffic đến chúng, đảm bảo hệ thống không bị quá tải.

---

## 3. Lời Kết
Qua quá trình thực hành, tôi đã tự mình nắm vững quy trình từ lúc viết dòng code AI đầu tiên đến khi đưa ứng dụng lên một kiến trúc Production thực tế. Dự án **Legal AI Hub** là minh chứng cụ thể nhất cho thấy khả năng ứng dụng các tiêu chuẩn Đóng gói (Docker), Khả năng mở rộng (Scaling với Nginx & Redis), và độ bảo mật cao vào một sản phẩm phần mềm hiện đại.
