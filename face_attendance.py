import face_recognition
import cv2
import numpy as np
import os
import pickle
from datetime import datetime
from database import Database
import time  # Thêm để tránh chấm công liên tục

class FaceAttendanceSystem:
    def __init__(self):
        self.db = Database()
        self.video_capture = cv2.VideoCapture(0)
        self.known_face_encodings = []
        self.known_face_names = []
        self.last_attendance_time = {}  # Lưu thời gian chấm công gần nhất của mỗi người
        self.MIN_TIME_BETWEEN_ATTENDANCE = 3600  # Thời gian tối thiểu giữa 2 lần chấm công (giây)
        
        # Kiểm tra webcam
        if not self.video_capture.isOpened():
            raise Exception("Không thể mở webcam")
            
        # Load encodings
        self.load_face_encodings()

    def load_face_encodings(self, file_path="encodings.pkl"):
        """Load hoặc tạo mới face encodings"""
        encodings, names = self.load_encodings(file_path)
        
        if encodings is None:
            self.create_new_encodings()
        else:
            self.known_face_encodings = encodings
            self.known_face_names = names

    def load_encodings(self, file_path="encodings.pkl"):
        """Load encodings từ file"""
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            print(f"Đã load {len(data['encodings'])} encodings từ {file_path}")
            return data["encodings"], data["names"]
        return None, None

    def create_new_encodings(self):
        """Tạo encodings mới từ thư mục ảnh"""
        try:
            image_dir = "image"
            for filename in os.listdir(image_dir):
                if filename.endswith((".jpg", ".jpeg", ".png")):
                    image_path = os.path.join(image_dir, filename)
                    self.process_image(image_path)
            
            # Lưu encodings
            if self.known_face_encodings:
                self.save_encodings()
                
        except Exception as e:
            print(f"Lỗi khi tạo encodings: {str(e)}")
            raise

    def process_image(self, image_path):
        """Xử lý một ảnh và thêm vào encodings"""
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)
        
        if face_encodings:
            self.known_face_encodings.append(face_encodings[0])
            name = os.path.splitext(os.path.basename(image_path))[0]
            self.known_face_names.append(name)
            # Thêm nhân viên vào database
            self.db.add_employee(name, image_path)
            print(f"Đã encode ảnh: {image_path} - Tên: {name}")
        else:
            print(f"Không tìm thấy khuôn mặt trong ảnh: {image_path}")

    def save_encodings(self, file_path="encodings.pkl"):
        """Lưu encodings vào file"""
        data = {
            "encodings": self.known_face_encodings,
            "names": self.known_face_names
        }
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
        print(f"Đã lưu {len(self.known_face_encodings)} encodings")

    def can_record_attendance(self, name):
        """Kiểm tra xem có thể chấm công cho nhân viên không"""
        current_time = time.time()
        if name in self.last_attendance_time:
            time_diff = current_time - self.last_attendance_time[name]
            if time_diff < self.MIN_TIME_BETWEEN_ATTENDANCE:
                return False
        self.last_attendance_time[name] = current_time
        return True

    def process_frame(self, frame):
        """Xử lý một frame từ camera"""
        # Resize frame
        small_frame = cv2.resize(frame, (0, 0), fx=0.2, fy=0.2)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Tìm khuôn mặt
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.5)
            name = "Unknown"

            if True in matches:
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index] and face_distances[best_match_index] < 0.5:
                    name = self.known_face_names[best_match_index]
                    # Ghi nhận chấm công
                    if self.can_record_attendance(name):
                        try:
                            self.db.record_attendance(name)
                            print(f"Đã chấm công cho {name}")
                        except Exception as e:
                            print(f"Lỗi khi chấm công: {str(e)}")

            face_names.append(name)

        return face_locations, face_names

    def draw_results(self, frame, face_locations, face_names):
        """Vẽ kết quả lên frame"""
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale lại vị trí
            top *= 5
            right *= 5
            bottom *= 5
            left *= 5

            # Chọn màu
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)

            # Vẽ khung và tên
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6), 
                       cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

    def run(self):
        """Chạy hệ thống chấm công"""
        process_this_frame = True

        while True:
            ret, frame = self.video_capture.read()
            if not ret:
                print("Lỗi khi đọc frame")
                continue

            if process_this_frame:
                try:
                    face_locations, face_names = self.process_frame(frame)
                    self.draw_results(frame, face_locations, face_names)
                except Exception as e:
                    print(f"Lỗi xử lý frame: {str(e)}")
                    continue

            process_this_frame = not process_this_frame
            cv2.imshow('Face Attendance System', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.video_capture.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        system = FaceAttendanceSystem()
        system.run()
    except Exception as e:
        print(f"Lỗi khởi động hệ thống: {str(e)}")