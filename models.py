from datetime import datetime
from pydantic import BaseModel

class Employee(BaseModel):
    name: str
    image_url: str

class Attendance(BaseModel):
    employee_name: str
    check_time: datetime