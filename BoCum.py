import tkinter as tk
from tkinter import filedialog, Scale, Button, Label, Frame, IntVar
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ClusteringQuantizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kỹ Thuật Bó Cụm (Clustering/Quantization)")
        self.root.geometry("1000x750")
        
        # Biến lưu trữ
        self.original_image = None
        self.gray_image = None
        self.bunch_size = IntVar(value=32)  # Mặc định bunch_size = 32
        
        # Tạo giao diện
        self.create_ui()
    
    def create_ui(self):
        # Khung chính
        main_frame = Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Khung điều khiển
        control_frame = Frame(main_frame)
        control_frame.pack(pady=10)
        
        # Nút mở ảnh
        Button(control_frame, text="Mở Ảnh", command=self.open_image, width=15).pack(side=tk.LEFT, padx=5)
        
        # Nút lưu ảnh
        Button(control_frame, text="Lưu Ảnh", command=self.save_image, width=15).pack(side=tk.LEFT, padx=5)
        
        # Khung hiển thị ảnh
        image_display_frame = Frame(main_frame)
        image_display_frame.pack(fill=tk.X, expand=True)
        
        # Frame ảnh gốc
        original_frame = Frame(image_display_frame, padx=5, pady=5)
        original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        Label(original_frame, text="Ảnh Gốc").pack()
        self.original_display = Label(original_frame, bg="lightgray")
        self.original_display.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Frame ảnh đã xử lý
        processed_frame = Frame(image_display_frame, padx=5, pady=5)
        processed_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        Label(processed_frame, text="Ảnh Sau Khi Bó Cụm").pack()
        self.processed_display = Label(processed_frame, bg="lightgray")
        self.processed_display.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Khung điều chỉnh bunch_size
        param_frame = Frame(main_frame)
        param_frame.pack(fill=tk.X, pady=10)
        
        Label(param_frame, text="Kích thước nhóm (bunch_size):").pack(side=tk.LEFT, padx=5)
        
        # Thanh trượt để điều chỉnh bunch_size
        bunch_scale = Scale(
            param_frame, 
            from_=2, 
            to=128,
            orient=tk.HORIZONTAL,
            length=500,
            variable=self.bunch_size,
            command=self.update_bunch_size
        )
        bunch_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Hiển thị số nhóm tương ứng
        self.group_count_label = Label(param_frame, text="Số nhóm: 256/32 = 8")
        self.group_count_label.pack(side=tk.LEFT, padx=10)
        
        # Khung hiển thị histogram
        self.histogram_frame = Frame(main_frame, height=300)
        self.histogram_frame.pack(fill=tk.X, expand=True, pady=10)
        
        # Giải thích kỹ thuật
        explanation_frame = Frame(main_frame)
        explanation_frame.pack(fill=tk.X, pady=10)
        
        explanation_text = """
        Kỹ thuật Bó Cụm (Clustering/Quantization):
        - Giảm bớt số mức xám của ảnh bằng cách nhóm các mức xám gần nhau thành một nhóm
        - Công thức: I[i,j] = (I[i,j] div bunch_size) * bunch_size
        - Khi chỉ có 2 nhóm, kỹ thuật này tương đương với tách ngưỡng
        - Tăng bunch_size sẽ giảm số nhóm và tạo ra hiệu ứng poster-like
        """
        
        explanation_label = Label(explanation_frame, text=explanation_text, justify=tk.LEFT, wraplength=980)
        explanation_label.pack(padx=5, pady=5)
    
    def open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if file_path:
            # Đọc ảnh và chuyển đổi sang ảnh xám
            self.original_image = Image.open(file_path)
            
            # Kiểm tra xem ảnh có phải là ảnh xám không
            if self.original_image.mode != 'L':
                self.gray_image = self.original_image.convert('L')
            else:
                self.gray_image = self.original_image
            
            # Hiển thị ảnh gốc
            self.display_image(self.gray_image, self.original_display)
            
            # Cập nhật ảnh xử lý với kích thước bunch hiện tại
            self.update_bunch_size(self.bunch_size.get())
            
            # Cập nhật thông tin số nhóm
            self.update_group_count(self.bunch_size.get())
    
    def update_bunch_size(self, value):
        if self.gray_image is None:
            return
        
        bunch_size = int(value)
        
        # Cập nhật label hiển thị số nhóm
        self.update_group_count(bunch_size)
        
        # Áp dụng thuật toán bó cụm
        processed_image = self.apply_clustering(bunch_size)
        
        # Hiển thị ảnh kết quả
        self.display_image(processed_image, self.processed_display)
        
        # Vẽ histogram
        self.plot_histograms(self.gray_image, processed_image, bunch_size)
    
    def update_group_count(self, bunch_size):
        group_count = 256 // int(bunch_size)
        self.group_count_label.config(text=f"Số nhóm: 256/{bunch_size} = {group_count}")
    
    def apply_clustering(self, bunch_size):
        """
        Áp dụng kỹ thuật bó cụm với kích thước nhóm (bunch_size) đã cho
        Công thức: I[i,j] = (I[i,j] div bunch_size) * bunch_size
        """
        # Chuyển đổi ảnh sang mảng numpy
        img_array = np.array(self.gray_image)
        
        # Áp dụng công thức bó cụm
        # I[i,j] = (I[i,j] div bunch_size) * bunch_size
        processed_array = (img_array // bunch_size) * bunch_size
        
        # Chuyển đổi lại thành ảnh
        processed_image = Image.fromarray(processed_array.astype(np.uint8))
        
        return processed_image
    
    def display_image(self, img, display_label, max_size=(400, 300)):
        # Tính toán tỷ lệ để giữ nguyên tỷ lệ ảnh
        width, height = img.size
        scale = min(max_size[0] / width, max_size[1] / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # Thay đổi kích thước ảnh
        resized_img = img.resize((new_width, new_height))
        
        # Hiển thị ảnh
        photo = ImageTk.PhotoImage(resized_img)
        display_label.config(image=photo)
        display_label.image = photo  # Giữ tham chiếu
    
    def plot_histograms(self, original_img, processed_img, bunch_size):
        # Xóa frame hiển thị histogram cũ
        for widget in self.histogram_frame.winfo_children():
            widget.destroy()
        
        # Chuyển đổi thành mảng numpy
        original_array = np.array(original_img)
        processed_array = np.array(processed_img)
        
        # Tạo figure và axes cho matplotlib
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        # Vẽ histogram ảnh gốc
        ax1.set_title("Histogram ảnh gốc")
        ax1.hist(original_array.flatten(), bins=256, range=[0, 256], color='blue', alpha=0.7)
        ax1.set_xlim(0, 255)
        ax1.set_xlabel("Mức xám")
        ax1.set_ylabel("Số lượng pixel")
        
        # Vẽ histogram ảnh đã xử lý
        ax2.set_title(f"Histogram sau khi bó cụm (bunch_size={bunch_size})")
        ax2.hist(processed_array.flatten(), bins=256, range=[0, 256], color='red', alpha=0.7)
        ax2.set_xlim(0, 255)
        ax2.set_xlabel("Mức xám")
        
        # Thêm các đường dọc thể hiện ranh giới các nhóm
        for i in range(0, 256, bunch_size):
            ax2.axvline(x=i, color='green', linestyle='--', alpha=0.5)
        
        # Điều chỉnh layout
        plt.tight_layout()
        
        # Hiển thị matplotlib trong tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.histogram_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def save_image(self):
        if self.gray_image is None:
            return
        
        # Mở hộp thoại lưu file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if file_path:
            # Áp dụng thuật toán bó cụm với kích thước hiện tại
            bunch_size = self.bunch_size.get()
            processed_image = self.apply_clustering(bunch_size)
            
            # Lưu ảnh
            processed_image.save(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = ClusteringQuantizationApp(root)
    root.mainloop()