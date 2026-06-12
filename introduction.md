# Hướng dẫn chi tiết Deploy dự án lên Railway

Tài liệu này hướng dẫn bạn từng bước từ việc chuẩn bị cấu hình mã nguồn (Source Code) dưới máy cục bộ cho đến các bước thực hiện thao tác trên giao diện của **Railway** để triển khai dự án công khai thành công.

---

## 📌 PHẦN 1: Chuẩn bị Cấu hình Mã nguồn (Code Setup)

Trước khi đẩy code lên GitHub và deploy, mã nguồn của bạn bắt buộc phải tuân thủ các quy tắc cấu hình của môi trường Cloud (Railway). Hãy chọn cấu hình phù hợp với ngôn ngữ dự án của bạn dưới đây:

### 1. Nếu dự án của bạn là Node.js (Express, NestJS, Next.js, React...)
* **Cấu hình file `package.json`:** Railway cần biết câu lệnh khởi chạy ứng dụng của bạn. Hãy đảm bảo phần `scripts` có chứa lệnh `start`:
    ```json
    {
      "name": "dự-án-của-bạn",
      "version": "1.0.0",
      "scripts": {
        "start": "node index.js" 
      }
    }
    ```
    *(Thay thế `node index.js` bằng lệnh chạy thực tế của bạn, ví dụ: `next start` hoặc `nest start`)*
* **Cấu hình Cổng (Port):** Thay vì cố định một cổng (như `3000`), bạn phải cho phép ứng dụng nhận cổng động do Railway cấp thông qua biến môi trường `process.env.PORT`.
    ```javascript
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
        console.log(`Server is running on port ${PORT}`);
    });
    ```

### 2. Nếu dự án của bạn là Python (FastAPI, Flask, Django...)
* **Tạo file `requirements.txt`:** Chứa danh sách tất cả các thư viện cần dùng. Bạn có thể tạo tự động bằng lệnh:
    ```bash
    pip freeze > requirements.txt
    ```
* **Cấu hình cổng và host:** Ứng dụng phải lắng nghe trên host `0.0.0.0` và cổng lấy từ biến môi trường. Ví dụ câu lệnh chạy thường dùng với `uvicorn` (cho FastAPI) hoặc `gunicorn`:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port $PORT
    ```

### 3. Đảm bảo bảo mật bằng `.gitignore`
* Tuyệt đối **KHÔNG** đẩy file `.env` chứa mật khẩu, chuỗi kết nối Database hoặc thư mục cài đặt (`node_modules/`, `venv/`) lên GitHub.
* Hãy tạo file `.gitignore` ở thư mục gốc dự án và thêm vào:
    ```text
    .env
    node_modules/
    venv/
    .DS_Store
    ```

---

## 🚀 PHẦN 2: Các bước triển khai trên Railway

Sau khi code đã chuẩn bị xong và được `git push` lên repository GitHub của bạn, hãy làm theo các bước sau:

### Bước 1: Đăng nhập Railway
1. Truy cập vào trang chủ [Railway.app](https://railway.app/).
2. Chọn **Login** (Đăng nhập) và chọn hình thức đăng nhập bằng **GitHub**.
3. *Lưu ý:* Nếu đây là lần đầu tiên sử dụng, hãy cấp quyền cho Railway truy cập vào kho lưu trữ (Repository) của bạn (Có thể chọn quyền truy cập tất cả repo hoặc chỉ chọn đúng repo `2A202600720-Hoangtrungquan-Day12`).

### Bước 2: Tạo Project mới
1. Tại màn hình Dashboard chính, nhấn nút **New Project** (hoặc nút **+ New** ở góc trên cùng bên phải).
2. Chọn tùy chọn **Deploy from GitHub repo**.
3. Tìm kiếm và chọn chính xác tên repository của bạn từ danh sách hiện ra.
4. Nhấn **Deploy Now**. Railway sẽ bắt đầu quá trình tải code và build tự động.

### Bước 3: Cấu hình biến môi trường (Environment Variables)
Nếu ứng dụng của bạn có sử dụng các khóa bí mật hoặc chuỗi kết nối trước đó ở file `.env` cục bộ:
1. Nhấp chuột vào ô dự án vừa tạo trên giao diện Railway.
2. Chọn tab **Variables**.
3. Nhấp vào **Add Variable** (hoặc bấm **Raw Editor** để dán nhanh cấu hình dạng `KEY=VALUE`).
4. Nhập đầy đủ các biến môi trường của bạn vào đây (Ví dụ: `MONGO_URI`, `JWT_SECRET`,...). Sau khi lưu, Railway sẽ tự động thực hiện redeploy lại để áp dụng biến mới.

### Bước 4: Tạo Tên miền truy cập công khai (Generate Domain)
Mặc định dự án được deploy lên sẽ ở chế độ nội bộ. Để lấy link truy cập từ trình duyệt:
1. Nhấp vào ứng dụng của bạn trên giao diện Railway.
2. Chọn tab **Settings** (Cài đặt).
3. Kéo xuống mục **Networking** (Mạng).
4. Nhấp vào nút **Generate Domain**.
5. Bạn sẽ nhận được một đường dẫn có đuôi dạng `xxx.up.railway.app`. Nhấp vào đường dẫn này để kiểm tra thành quả ứng dụng hoạt động công khai.

---

## 🛠️ PHẦN 3: Kiểm tra và Khắc phục lỗi (Troubleshooting)

Nếu trạng thái ứng dụng báo màu đỏ hoặc hiển thị lỗi `Crash`, `Application Error`, hãy xử lý theo quy trình sau:

1. **Xem Logs:** Nhấp vào dịch vụ của bạn, chọn tab **Logs**. Tại đây chia làm 2 phần:
   * **Deploy Logs:** Xem quá trình cài đặt thư viện (nếu lỗi ở đây là do viết sai file cấu hình, thiếu thư viện).
   * **Runtime Logs:** Xem quá trình ứng dụng chạy thực tế (nếu lỗi ở đây là do kết nối cơ sở dữ liệu thất bại, hoặc sai câu lệnh `start`).
2. **Lỗi `Port` phổ biến:** Nếu logs báo lỗi liên quan đến cổng (Port), hãy chắc chắn rằng bạn đã đổi cổng cố định thành cổng động `process.env.PORT` (đối với Node.js) hoặc `$PORT` (đối với Python) như hướng dẫn ở Phần 1.
3. **Cập nhật Code:** Mỗi khi bạn sửa lỗi ở máy cục bộ, bạn chỉ cần dùng lệnh `git commit` và `git push` lên GitHub. Railway sẽ tự động nhận diện thay đổi và cập nhật (Auto-deploy) phiên bản mới nhất cho bạn mà không cần thao tác lại từ đầu.
