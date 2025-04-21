import tkinter as tk
from tkinter import filedialog, Scale, Button, Label, Frame, IntVar
from PIL import Image, ImageTk
import numpy as np

class ThresholdApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng tách ngưỡng ảnh")
        self.root.geometry("800x600")
        
        # Biến lưu trữ
        self.original_image = None
        self.image_array = None
        self.threshold_value = IntVar(value=128)
        self.min_value = IntVar(value=0)
        self.max_value = IntVar(value=255)
        
        # Tạo giao diện
        self.create_ui()
    
    def create_ui(self):
        # Khung nút điều khiển
        controls = Frame(self.root)
        controls.pack(pady=10)
        
        # Nút mở ảnh
        Button(controls, text="Mở ảnh", command=self.open_image, width=10).pack(side=tk.LEFT, padx=5)
        
        # Nút lưu ảnh
        Button(controls, text="Lưu ảnh", command=self.save_image, width=10).pack(side=tk.LEFT, padx=5)
        
        # Khung hiển thị ảnh
        self.image_frame = Frame(self.root, bg="gray", width=600, height=300)
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Label hiển thị ảnh
        self.image_label = Label(self.image_frame, bg="gray")
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Khung điều chỉnh tham số
        settings_frame = Frame(self.root)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Điều chỉnh ngưỡng θ
        threshold_frame = Frame(settings_frame)
        threshold_frame.pack(fill=tk.X, pady=5)
        
        Label(threshold_frame, text="Ngưỡng (θ):").pack(side=tk.LEFT, padx=5)
        self.threshold_scale = Scale(
            threshold_frame, 
            from_=0, 
            to=255,
            orient=tk.HORIZONTAL,
            length=500,
            variable=self.threshold_value,
            command=self.update_threshold
        )
        self.threshold_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Điều chỉnh giá trị Min
        min_frame = Frame(settings_frame)
        min_frame.pack(fill=tk.X, pady=5)
        
        Label(min_frame, text="Giá trị Min:").pack(side=tk.LEFT, padx=5)
        self.min_scale = Scale(
            min_frame,
            from_=0,
            to=255,
            orient=tk.HORIZONTAL,
            length=500,
            variable=self.min_value,
            command=self.update_threshold
        )
        self.min_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Điều chỉnh giá trị Max
        max_frame = Frame(settings_frame)
        max_frame.pack(fill=tk.X, pady=5)
        
        Label(max_frame, text="Giá trị Max:").pack(side=tk.LEFT, padx=5)
        self.max_scale = Scale(
            max_frame,
            from_=0,
            to=255,
            orient=tk.HORIZONTAL,
            length=500,
            variable=self.max_value,
            command=self.update_threshold
        )
        self.max_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if file_path:
            # Đọc ảnh và lưu vào biến
            self.original_image = Image.open(file_path)
            
            # Chuyển đổi sang ảnh xám nếu là ảnh màu
            if self.original_image.mode != 'L':
                self.original_image = self.original_image.convert('L')
                
            self.image_array = np.array(self.original_image)
            
            # Hiển thị ảnh
            self.display_image(self.original_image)
            
            # Áp dụng tách ngưỡng với giá trị hiện tại
            self.update_threshold(None)
    
    def apply_threshold(self, img_array, threshold, min_val, max_val):
        """
        Áp dụng kỹ thuật tách ngưỡng:
        g(x,y) = max_val nếu f(x,y) > threshold
                 min_val nếu f(x,y) <= threshold
        """
        # Tạo bản sao để không thay đổi ảnh gốc
        result = img_array.copy()
        
        # Lấy kích thước ảnh
        m, n = img_array.shape[0], img_array.shape[1]
        
        # Duyệt qua từng pixel và áp dụng tách ngưỡng
        for i in range(m):
            for j in range(n):
                if img_array[i, j] > threshold:
                    result[i, j] = max_val
                else:
                    result[i, j] = min_val
        
        return result
    
    def update_threshold(self, _):
        if self.image_array is None:
            return
        
        # Lấy giá trị tham số hiện tại
        threshold = self.threshold_value.get()
        min_val = self.min_value.get()
        max_val = self.max_value.get()
        
        # Áp dụng tách ngưỡng
        thresholded_array = self.apply_threshold(self.image_array, threshold, min_val, max_val)
        
        # Chuyển đổi từ array sang Image
        thresholded_image = Image.fromarray(thresholded_array.astype('uint8'))
        
        # Hiển thị ảnh đã xử lý
        self.display_image(thresholded_image)
    
    def display_image(self, img):
        # Tính toán tỷ lệ điều chỉnh kích thước ảnh
        width, height = img.size
        max_width = 600
        max_height = 300
        
        # Giữ nguyên tỷ lệ ảnh
        scale = min(max_width / width, max_height / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # Thay đổi kích thước ảnh
        resized_img = img.resize((new_width, new_height))
        
        # Hiển thị ảnh
        photo = ImageTk.PhotoImage(resized_img)
        self.image_label.config(image=photo)
        self.image_label.image = photo  # Giữ tham chiếu
    
    def save_image(self):
        if self.image_array is None:
            return
        
        # Lấy giá trị tham số hiện tại
        threshold = self.threshold_value.get()
        min_val = self.min_value.get()
        max_val = self.max_value.get()
        
        # Áp dụng tách ngưỡng
        thresholded_array = self.apply_threshold(self.image_array, threshold, min_val, max_val)
        thresholded_image = Image.fromarray(thresholded_array.astype('uint8'))
        
        # Mở hộp thoại lưu file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if file_path:
            thresholded_image.save(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = ThresholdApp(root)
    root.mainloop()