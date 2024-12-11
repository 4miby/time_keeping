# Hệ Thống Chấm Công Bằng Khuôn Mặt

## Giới thiệu
Hệ thống chấm công bằng khuôn mặt giúp quản lý và ghi nhận thời gian làm việc của nhân viên một cách tự động và chính xác. Hệ thống sử dụng công nghệ nhận diện khuôn mặt để xác định nhân viên và ghi lại thời gian chấm công. Hệ thống sử dụng thư viện face_recognite https://github.com/ageitgey/face_recognition


## Các tính năng
- Thêm nhân viên mới với ảnh và thông tin cá nhân.
- Chấm công tự động qua webcam.
- Hiển thị kết quả chấm công theo tên nhân viên.
- Lưu trữ thông tin nhân viên và lịch sử chấm công trong cơ sở dữ liệu MongoDB.

## Công nghệ sử dụng
- Python
- OpenCV
- Face Recognition
- Tkinter (CustomTkinter)
- MongoDB
- Pydantic

## Cài đặt
1. Clone repository này về máy:
   ```bash
   git clone https://github.com/yourusername/face-attendance-system.git
   cd face-attendance-system
   ```

2. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```

3. Tạo file `.env` trong thư mục gốc và thêm thông tin kết nối MongoDB:
   ```
   MONGODB_URI=your_mongodb_uri
   ```

## Cách sử dụng
1. Chạy ứng dụng:
   ```bash
   python app.py
   ```

2. Giao diện sẽ hiển thị với các tab:
   - **Thêm Nhân Viên**: Nhập tên và chọn ảnh cho nhân viên mới.
   - **Chấm Công**: Bắt đầu chấm công qua webcam.
   - **Kết Quả**: Tìm kiếm và xem lịch sử chấm công của nhân viên.
