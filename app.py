import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import os
import shutil
from datetime import datetime
import cv2
from PIL import Image, ImageTk
from database import Database
from face_attendance import FaceAttendanceSystem

class AttendanceApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Hệ Thống Chấm Công")
        self.root.geometry("1000x700")
        
        # Thiết lập theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.db = Database()
        self.face_system = FaceAttendanceSystem()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Tạo container chính
        self.main_container = ctk.CTkTabview(self.root)
        self.main_container.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Thêm các tab
        self.main_container.add("Thêm Nhân Viên")
        self.main_container.add("Chấm Công")
        self.main_container.add("Kết Quả")
        
        self.setup_add_employee_tab()
        self.setup_attendance_tab()
        self.setup_results_tab()
    
    def setup_add_employee_tab(self):
        tab = self.main_container.tab("Thêm Nhân Viên")
        
        # Frame thông tin
        info_frame = ctk.CTkFrame(tab)
        info_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Title
        title = ctk.CTkLabel(info_frame, text="Thông Tin Nhân Viên", 
                            font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=20)
        
        # Form container
        form_frame = ctk.CTkFrame(info_frame)
        form_frame.pack(padx=20, pady=10, fill="x")
        
        # Tên nhân viên
        name_label = ctk.CTkLabel(form_frame, text="Tên nhân viên:")
        name_label.pack(pady=5)
        self.name_entry = ctk.CTkEntry(form_frame, placeholder_text="Nhập tên nhân viên",
                                     width=300)
        self.name_entry.pack(pady=5)
        
        # Nút chọn ảnh
        self.image_path = None
        select_btn = ctk.CTkButton(form_frame, text="Chọn ảnh nhân viên",
                                 command=self.choose_image)
        select_btn.pack(pady=15)
        
        # Hiển thị ảnh
        self.image_label = ctk.CTkLabel(form_frame, text="")
        self.image_label.pack(pady=10)
        
        # Nút lưu
        save_btn = ctk.CTkButton(form_frame, text="Lưu thông tin",
                               command=self.save_employee,
                               fg_color="green", hover_color="#006400")
        save_btn.pack(pady=20)
    
    def setup_attendance_tab(self):
        tab = self.main_container.tab("Chấm Công")
        
        # Frame chấm công
        attendance_frame = ctk.CTkFrame(tab)
        attendance_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Title
        title = ctk.CTkLabel(attendance_frame, text="Chấm Công Realtime", 
                            font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=20)
        
        # Nút điều khiển
        self.is_recording = False
        self.record_btn = ctk.CTkButton(attendance_frame, text="Bắt đầu chấm công",
                                      command=self.toggle_attendance,
                                      width=200)
        self.record_btn.pack(pady=10)
        
        # Frame hiển thị camera
        self.video_frame = ctk.CTkFrame(attendance_frame)
        self.video_frame.pack(pady=10)
        self.video_label = ctk.CTkLabel(self.video_frame, text="")
        self.video_label.pack()
    
    def setup_results_tab(self):
        tab = self.main_container.tab("Kết Quả")
        
        # Frame kết quả
        results_frame = ctk.CTkFrame(tab)
        results_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Title
        title = ctk.CTkLabel(results_frame, text="Kết Quả Chấm Công", 
                            font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=20)
        
        # Search frame
        search_frame = ctk.CTkFrame(results_frame)
        search_frame.pack(padx=20, pady=10, fill="x")
        
        # Tìm kiếm
        self.search_name = ctk.CTkEntry(search_frame, placeholder_text="Nhập tên nhân viên",
                                      width=300)
        self.search_name.pack(side="left", padx=10)
        
        search_btn = ctk.CTkButton(search_frame, text="Tìm kiếm",
                                 command=self.search_attendance,
                                 width=100)
        search_btn.pack(side="left", padx=10)
        
        # Tạo frame cho bảng kết quả
        table_frame = ctk.CTkFrame(results_frame)
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Tạo Treeview
        columns = ("name", "time")
        self.result_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Định nghĩa các cột
        self.result_tree.heading("name", text="Tên nhân viên")
        self.result_tree.heading("time", text="Thời gian chấm công")
        
        # Thiết lập độ rộng cột
        self.result_tree.column("name", width=150)
        self.result_tree.column("time", width=150)
        
        # Thêm scrollbar
        scrollbar = ctk.CTkScrollbar(table_frame, command=self.result_tree.yview)
        scrollbar.pack(side="right", fill="y")
        
        self.result_tree.configure(yscrollcommand=scrollbar.set)
        self.result_tree.pack(fill="both", expand=True)
    
    def choose_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            self.image_path = file_path
            # Hiển thị ảnh preview
            image = Image.open(file_path)
            image = image.resize((150, 150))
            photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo
    
    def save_employee(self):
        if not self.name_entry.get() or not self.image_path:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return
            
        try:
            if not os.path.exists("image"):
                os.makedirs("image")
            
            file_ext = os.path.splitext(self.image_path)[1]
            new_image_path = os.path.join("image", f"{self.name_entry.get()}{file_ext}")
            
            shutil.copy2(self.image_path, new_image_path)
            self.db.add_employee(self.name_entry.get(), new_image_path)
            self.face_system.create_new_encodings()
            
            messagebox.showinfo("Thành công", "Đã thêm nhân viên mới")
            
            # Reset form
            self.name_entry.delete(0, "end")
            self.image_path = None
            self.image_label.configure(image=None)
            
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
    
    def toggle_attendance(self):
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.record_btn.configure(text="Dừng chấm công")
            self.start_attendance()
        else:
            self.record_btn.configure(text="Bắt đầu chấm công")
            self.stop_attendance()
    
    def start_attendance(self):
        self.cap = cv2.VideoCapture(0)
        self.update_frame()
    
    def update_frame(self):
        if self.is_recording:
            ret, frame = self.cap.read()
            if ret:
                # Xử lý frame với face_system
                face_locations, face_names = self.face_system.process_frame(frame)
                self.face_system.draw_results(frame, face_locations, face_names)
                
                # Chuyển frame để hiển thị trên UI
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame)
                image = image.resize((640, 480))
                photo = ImageTk.PhotoImage(image=image)
                self.video_label.configure(image=photo)
                self.video_label.image = photo
                
            self.root.after(10, self.update_frame)
    
    def stop_attendance(self):
        if hasattr(self, 'cap'):
            self.cap.release()
    
    def search_attendance(self):
        name = self.search_name.get()
        if not name:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên nhân viên")
            return
            
        # Xóa dữ liệu cũ trong bảng
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
            
        # Lấy dữ liệu từ database
        records = self.db.get_employee_attendance(name)
        
        # Hiển thị kết quả
        for record in records:
            self.result_tree.insert("", "end", values=(
                record["employee_name"],
                record["check_time"].strftime("%Y-%m-%d %H:%M:%S")
            ))
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AttendanceApp()
    app.run()