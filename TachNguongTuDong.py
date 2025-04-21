import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog, Button, Label, Frame
from PIL import Image, ImageTk

class AutoThresholdApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tách Ngưỡng Tự Động Dựa Trên Histogram")
        self.root.geometry("1000x700")
        
        # Biến lưu trữ
        self.original_image = None
        self.gray_image = None
        self.threshold_value = 0
        
        # Tạo giao diện
        self.create_ui()
    
    def create_ui(self):
        # Frame chính
        main_frame = Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame cho các nút điều khiển
        control_frame = Frame(main_frame)
        control_frame.pack(pady=10)
        
        # Nút mở ảnh
        Button(control_frame, text="Mở Ảnh", command=self.open_image, width=15).pack(side=tk.LEFT, padx=5)
        
        # Nút tính ngưỡng tự động
        Button(control_frame, text="Tính Ngưỡng Tự Động", command=self.calculate_auto_threshold, width=20).pack(side=tk.LEFT, padx=5)
        
        # Nút lưu ảnh
        Button(control_frame, text="Lưu Ảnh", command=self.save_image, width=15).pack(side=tk.LEFT, padx=5)
        
        # Frame hiển thị ảnh và histogram
        display_frame = Frame(main_frame)
        display_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame hiển thị ảnh
        self.image_frame = Frame(display_frame, bg="gray", width=400, height=400)
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Label hiển thị ảnh gốc
        self.original_label = Label(self.image_frame, text="Ảnh Gốc", bg="gray")
        self.original_label.pack(pady=5)
        self.original_display = Label(self.image_frame, bg="gray")
        self.original_display.pack()
        
        # Label hiển thị ảnh đã xử lý
        self.processed_label = Label(self.image_frame, text="Ảnh Đã Xử Lý", bg="gray")
        self.processed_label.pack(pady=5)
        self.processed_display = Label(self.image_frame, bg="gray")
        self.processed_display.pack()
        
        # Frame hiển thị biểu đồ histogram
        self.histogram_frame = Frame(display_frame, bg="lightgray", width=400, height=400)
        self.histogram_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Label hiển thị thông tin ngưỡng
        self.threshold_info = Label(main_frame, text="Ngưỡng tự động: Chưa tính toán", font=("Arial", 12))
        self.threshold_info.pack(pady=10)
        
        # Label hiển thị hướng dẫn
        instruction = Label(main_frame, 
                           text="Hướng dẫn: Mở ảnh → Tính Ngưỡng Tự Động → Lưu Ảnh\n" +
                                "Thuật toán tự động tìm ngưỡng θ để tổng độ lệch trong từng phần là tối thiểu")
        instruction.pack(pady=5)
    
    def open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if file_path:
            # Đọc ảnh và chuyển đổi sang ảnh xám
            self.original_image = Image.open(file_path)
            self.gray_image = self.original_image.convert('L')
            
            # Hiển thị ảnh gốc
            self.display_image(self.original_image, self.original_display)
            
            # Xóa kết quả cũ nếu có
            self.processed_display.config(image=None)
            self.threshold_info.config(text="Ngưỡng tự động: Chưa tính toán")
            
            # Vẽ histogram
            self.plot_histogram()
    
    def display_image(self, img, display_label, max_size=(300, 300)):
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
        display_label.image = photo
    
    def plot_histogram(self):
        if self.gray_image is None:
            return
        
        # Xóa frame hiển thị histogram cũ
        for widget in self.histogram_frame.winfo_children():
            widget.destroy()
        
        # Tính histogram
        img_array = np.array(self.gray_image)
        hist, bins = np.histogram(img_array.flatten(), bins=256, range=[0, 256])
        
        # Tạo figure và axes cho matplotlib
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5, 7))
        
        # Vẽ histogram
        ax1.set_title("Histogram của ảnh")
        ax1.bar(range(256), hist, width=1)
        ax1.set_xlabel('Mức xám')
        ax1.set_ylabel('Số lượng pixel')
        ax1.set_xlim(0, 255)
        
        # Vẽ biểu đồ mômen quán tính trung bình
        # Tính t(g) - số điểm ảnh có mức xám ≤ g
        t_g = np.cumsum(hist)
        
        # Tính mômen quán tính trung bình m(g)
        m_g = np.zeros(256)
        for g in range(256):
            if t_g[g] > 0:  # Tránh chia cho 0
                m_g[g] = np.sum([i * hist[i] for i in range(g+1)]) / t_g[g]
        
        # Vẽ biểu đồ mômen quán tính
        ax2.set_title("Mômen quán tính trung bình m(g)")
        ax2.plot(range(256), m_g)
        ax2.set_xlabel('g')
        ax2.set_ylabel('m(g)')
        ax2.set_xlim(0, 255)
        
        # Điều chỉnh layout
        plt.tight_layout()
        
        # Hiển thị matplotlib trong tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.histogram_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Lưu histogram và mômen quán tính để tính toán ngưỡng
        self.histogram = hist
        self.moment = m_g
    
    def calculate_auto_threshold(self):
        if self.gray_image is None:
            return
        
        # Tính ngưỡng tự động dựa trên thuật toán Otsu
        img_array = np.array(self.gray_image)
        
        # Tính histogram
        hist, _ = np.histogram(img_array.flatten(), bins=256, range=[0, 256])
        
        # Tổng số pixel
        total_pixels = img_array.size
        
        # Trọng số tích lũy
        w_k = np.cumsum(hist) / total_pixels  # Tỷ lệ pixel có mức xám ≤ k
        
        # Tích lũy cường độ
        m_k = np.cumsum(np.arange(256) * hist) / total_pixels
        
        # Cường độ trung bình toàn cục
        m_G = m_k[-1]
        
        # Phương sai giữa các lớp
        var_between = w_k[:-1] * (1 - w_k[:-1]) * ((m_k[:-1] / w_k[:-1] - m_G) ** 2)
        
        # Tìm ngưỡng tối ưu (phương sai lớn nhất)
        optimal_threshold = np.argmax(var_between)
        self.threshold_value = optimal_threshold
        
        # Hiển thị thông tin ngưỡng
        self.threshold_info.config(text=f"Ngưỡng tự động θ = {optimal_threshold}")
        
        # Áp dụng ngưỡng
        thresholded_img = img_array > optimal_threshold
        thresholded_img = thresholded_img.astype(np.uint8) * 255
        
        # Tạo ảnh kết quả
        result_image = Image.fromarray(thresholded_img)
        
        # Hiển thị ảnh đã xử lý
        self.display_image(result_image, self.processed_display)
        
        # Vẽ lại histogram với ngưỡng
        self.plot_histogram_with_threshold(optimal_threshold)
    
    def plot_histogram_with_threshold(self, threshold):
        if self.gray_image is None:
            return
        
        # Xóa frame hiển thị histogram cũ
        for widget in self.histogram_frame.winfo_children():
            widget.destroy()
        
        # Tính histogram
        img_array = np.array(self.gray_image)
        hist, bins = np.histogram(img_array.flatten(), bins=256, range=[0, 256])
        
        # Tạo figure và axes cho matplotlib
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5, 7))
        
        # Vẽ histogram với màu phân biệt cho 2 phần
        ax1.set_title("Histogram với ngưỡng tự động")
        ax1.bar(range(threshold + 1), hist[:threshold + 1], width=1, color='blue')
        ax1.bar(range(threshold + 1, 256), hist[threshold + 1:], width=1, color='red')
        ax1.axvline(x=threshold, color='green', linestyle='--', linewidth=2)
        ax1.set_xlabel('Mức xám')
        ax1.set_ylabel('Số lượng pixel')
        ax1.set_xlim(0, 255)
        ax1.text(threshold + 5, np.max(hist) * 0.9, f'θ = {threshold}', color='green')
        
        # Tính t(g) - số điểm ảnh có mức xám ≤ g
        t_g = np.cumsum(hist)
        
        # Tính mômen quán tính trung bình m(g)
        m_g = np.zeros(256)
        for g in range(256):
            if t_g[g] > 0:  # Tránh chia cho 0
                m_g[g] = np.sum([i * hist[i] for i in range(g+1)]) / t_g[g]
        
        # Vẽ biểu đồ mômen quán tính với ngưỡng
        ax2.set_title("Mômen quán tính trung bình m(g)")
        ax2.plot(range(256), m_g)
        ax2.axvline(x=threshold, color='green', linestyle='--', linewidth=2)
        ax2.set_xlabel('g')
        ax2.set_ylabel('m(g)')
        ax2.set_xlim(0, 255)
        
        # Điều chỉnh layout
        plt.tight_layout()
        
        # Hiển thị matplotlib trong tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.histogram_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def save_image(self):
        if self.gray_image is None or self.threshold_value == 0:
            return
        
        # Mở hộp thoại lưu file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if file_path:
            # Áp dụng ngưỡng
            img_array = np.array(self.gray_image)
            thresholded_img = img_array > self.threshold_value
            thresholded_img = thresholded_img.astype(np.uint8) * 255
            
            # Tạo ảnh kết quả
            result_image = Image.fromarray(thresholded_img)
            
            # Lưu ảnh
            result_image.save(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoThresholdApp(root)
    root.mainloop()