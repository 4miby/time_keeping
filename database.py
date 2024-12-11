import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client['face_attendance']
        
    def add_employee(self, name: str, image_path: str):
        """Thêm hoặc cập nhật nhân viên"""
        employee = {
            'name': name,
            'image_path': image_path,
            'updated_at': datetime.now()
        }
        
        # Upsert - tạo mới nếu chưa có, cập nhật nếu đã có
        self.db.employees.update_one(
            {'name': name},
            {'$set': employee},
            upsert=True
        )
    
    def record_attendance(self, employee_name: str):
        """Ghi nhận chấm công"""
        attendance = {
            'employee_name': employee_name,
            'check_time': datetime.now()
        }
        return self.db.attendance.insert_one(attendance)
    
    def get_employee_attendance(self, employee_name: str):
        """Lấy lịch sử chấm công của nhân viên"""
        return self.db.attendance.find({'employee_name': employee_name})