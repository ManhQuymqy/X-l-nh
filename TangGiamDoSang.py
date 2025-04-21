import tkinter as tk
from tkinter import filedialog, Scale, Button, Label
from PIL import Image, ImageTk
import numpy as np

class BrightnessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tăng/Giảm Độ Sáng Ảnh")
        self.root.geometry("700x500")
        
        # Biến lưu trữ
        self.original_image = None
        self.image_array = None
        
        # Tạo giao diện
        self.create_ui()
    
    def create_ui(self):
        # Khung nút điều khiển
        controls = tk.Frame(self.root)
        controls.pack(pady=10)
        
        # Nút mở ảnh
        Button(controls, text="Mở ảnh", command=self.open_image, width=10).pack(side=tk.LEFT, padx=5)
        
        # Nút lưu ảnh
        Button(controls, text="Lưu ảnh", command=self.save_image, width=10).pack(side=tk.LEFT, padx=5)
        
        # Khung hiển thị ảnh
        self.image_frame = tk.Frame(self.root, bg="gray", width=600, height=300)
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Label hiển thị ảnh
        self.image_label = Label(self.image_frame, bg="gray")
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Label hiển thị thông tin độ sáng
        self.brightness_label = Label(self.root, text="Điều chỉnh độ sáng (c = 0)")
        self.brightness_label.pack(pady=5)
        
        # Thanh trượt điều chỉnh độ sáng
        self.brightness_scale = Scale(
            self.root, 
            from_=-100, 
            to=100,
            orient=tk.HORIZONTAL,
            length=500, 
            command=self.update_brightness
        )
        self.brightness_scale.set(0)
        self.brightness_scale.pack(pady=5)
    
    def open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if file_path:
            # Đọc ảnh và lưu vào biến
            self.original_image = Image.open(file_path)
            self.image_array = np.array(self.original_image)
            
            # Hiển thị ảnh
            self.display_image(self.original_image)
            
            # Reset thanh trượt
            self.brightness_scale.set(0)
    
    def adjust_brightness(self, img_array, c):
        """
        Thuật toán tăng/giảm độ sáng chính xác theo yêu cầu:
        - Duyệt qua từng pixel
        - Cộng giá trị c vào mỗi pixel
        """
        # Tạo bản sao để không thay đổi ảnh gốc
        result = img_array.copy()
        
        # Lấy kích thước ảnh
        m, n = img_array.shape[0], img_array.shape[1]
        
        # Duyệt qua từng pixel - triển khai đúng theo thuật toán đã yêu cầu
        for i in range(m):
            for j in range(n):
                # Xử lý ảnh màu RGB
                if len(img_array.shape) == 3:
                    for k in range(img_array.shape[2]):
                        # Công thức: I[i,j] = I[i,j] + c
                        new_value = int(result[i, j, k]) + c
                        # Giới hạn giá trị trong khoảng [0,255]
                        result[i, j, k] = max(0, min(255, new_value))
                # Xử lý ảnh xám
                else:
                    # Công thức: I[i,j] = I[i,j] + c
                    new_value = int(result[i, j]) + c
                    # Giới hạn giá trị trong khoảng [0,255]
                    result[i, j] = max(0, min(255, new_value))
        
        return result
    
    def update_brightness(self, val):
        if self.image_array is None:
            return
        
        # Lấy giá trị độ sáng
        c = int(val)
        self.brightness_label.config(text=f"Điều chỉnh độ sáng (c = {c})")
        
        # Điều chỉnh độ sáng ảnh
        adjusted_array = self.adjust_brightness(self.image_array, c)
        
        # Chuyển đổi từ array sang Image
        adjusted_image = Image.fromarray(adjusted_array.astype('uint8'))
        
        # Hiển thị ảnh
        self.display_image(adjusted_image)
    
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
        
        # Lấy giá trị độ sáng hiện tại
        c = int(self.brightness_scale.get())
        
        # Điều chỉnh độ sáng
        adjusted_array = self.adjust_brightness(self.image_array, c)
        adjusted_image = Image.fromarray(adjusted_array.astype('uint8'))
        
        # Mở hộp thoại lưu file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if file_path:
            adjusted_image.save(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = BrightnessApp(root)
    root.mainloop()