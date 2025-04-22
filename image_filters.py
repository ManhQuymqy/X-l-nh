import tkinter as tk
from tkinter import filedialog, ttk, Scale, Button, Label, Frame, IntVar, StringVar
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

class ImageFilteringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng mô phỏng kỹ thuật lọc ảnh")
        self.root.geometry("1200x800")
        
        # Biến lưu trữ
        self.original_image = None
        self.gray_image = None
        self.filtered_image = None
        
        # Tham số lọc ảnh
        self.filter_type = StringVar(value="median")  # median, mean, knn_mean
        self.window_size = IntVar(value=3)
        self.threshold = IntVar(value=20)
        self.k_value = IntVar(value=4)
        
        # Tạo giao diện
        self.create_ui()
    
    def create_ui(self):
        # Frame chính
        main_frame = Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame điều khiển
        control_frame = Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        # Nút mở ảnh
        Button(control_frame, text="Mở ảnh", command=self.open_image, width=15).pack(side=tk.LEFT, padx=5)
        
        # Chọn loại bộ lọc
        filter_frame = Frame(control_frame)
        filter_frame.pack(side=tk.LEFT, padx=20)
        
        Label(filter_frame, text="Chọn bộ lọc:").pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(filter_frame, text="Lọc trung vị", variable=self.filter_type, value="median").pack(side=tk.LEFT)
        ttk.Radiobutton(filter_frame, text="Lọc trung bình", variable=self.filter_type, value="mean").pack(side=tk.LEFT)
        ttk.Radiobutton(filter_frame, text="Lọc trung bình k giá trị gần nhất", variable=self.filter_type, value="knn_mean").pack(side=tk.LEFT)
        
        # Nút áp dụng bộ lọc
        Button(control_frame, text="Áp dụng bộ lọc", command=self.apply_filter, width=15).pack(side=tk.LEFT, padx=5)
        
        # Nút lưu ảnh
        Button(control_frame, text="Lưu ảnh", command=self.save_image, width=15).pack(side=tk.LEFT, padx=5)
        
        # Frame hiển thị ảnh
        image_frame = Frame(main_frame)
        image_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Frame ảnh gốc
        original_frame = Frame(image_frame)
        original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        Label(original_frame, text="Ảnh gốc").pack()
        self.original_display = Label(original_frame, bg="lightgray")
        self.original_display.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Frame ảnh đã lọc
        filtered_frame = Frame(image_frame)
        filtered_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        Label(filtered_frame, text="Ảnh sau khi lọc").pack()
        self.filtered_display = Label(filtered_frame, bg="lightgray")
        self.filtered_display.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Frame thiết lập tham số
        param_frame = Frame(main_frame)
        param_frame.pack(fill=tk.X, pady=10)
        
        # Kích thước cửa sổ lọc
        window_frame = Frame(param_frame)
        window_frame.pack(fill=tk.X, pady=5)
        
        Label(window_frame, text="Kích thước cửa sổ:").pack(side=tk.LEFT, padx=5)
        
        window_values = [3, 5, 7, 9]
        window_dropdown = ttk.Combobox(window_frame, textvariable=self.window_size, values=window_values, width=5)
        window_dropdown.pack(side=tk.LEFT)
        
        # Ngưỡng theta
        threshold_frame = Frame(param_frame)
        threshold_frame.pack(fill=tk.X, pady=5)
        
        Label(threshold_frame, text="Ngưỡng θ:").pack(side=tk.LEFT, padx=5)
        
        threshold_scale = Scale(
            threshold_frame, 
            from_=0, 
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.threshold,
            length=400
        )
        threshold_scale.pack(side=tk.LEFT)
        
        # Giá trị k (cho lọc k giá trị gần nhất)
        knn_frame = Frame(param_frame)
        knn_frame.pack(fill=tk.X, pady=5)
        
        Label(knn_frame, text="Số giá trị k gần nhất:").pack(side=tk.LEFT, padx=5)
        
        k_scale = Scale(
            knn_frame, 
            from_=1, 
            to=9,
            orient=tk.HORIZONTAL,
            variable=self.k_value,
            length=400
        )
        k_scale.pack(side=tk.LEFT)
        
        # Frame hiển thị kết quả
        self.result_frame = Frame(main_frame)
        self.result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Label hiển thị thời gian xử lý
        self.process_time_label = Label(main_frame, text="Thời gian xử lý: ")
        self.process_time_label.pack(pady=5)
        
        # Frame giải thích
        explanation_frame = Frame(main_frame)
        explanation_frame.pack(fill=tk.X, pady=5)
        
        explanation_text = """
        Kỹ Thuật Lọc Ảnh:
        
        1. Lọc Trung Vị: Thay thế pixel hiện tại bằng giá trị trung vị của các pixel trong cửa sổ lọc.
           * Trung vị là giá trị đứng giữa trong dãy đã sắp xếp
           * Tính chất: Σ|x - xᵢ| → min tại x = Med({xₙ})
        
        2. Lọc Trung Bình: Thay thế pixel hiện tại bằng giá trị trung bình của các pixel trong cửa sổ lọc.
           * Trung bình = (1/n) * Σ xᵢ
           * Tính chất: Σ(x - xᵢ)² → min tại x = AV({xₙ})
        
        3. Lọc Trung Bình K Giá Trị Gần Nhất: Thay thế pixel hiện tại bằng trung bình của k giá trị gần nhất với nó trong cửa sổ lọc.

        Tham số θ: Chỉ áp dụng bộ lọc nếu |I(P) - Lọc(P)| ≤ θ, ngược lại giữ nguyên.
        """
        
        explanation_label = Label(explanation_frame, text=explanation_text, justify=tk.LEFT, wraplength=1180)
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
            
            # Reset ảnh đã lọc
            self.filtered_display.config(image=None)
            self.filtered_image = None
            
            # Xóa kết quả cũ
            for widget in self.result_frame.winfo_children():
                widget.destroy()
            
            # Reset nhãn thời gian xử lý
            self.process_time_label.config(text="Thời gian xử lý: ")
    
    def apply_filter(self):
        if self.gray_image is None:
            return
        
        # Lấy tham số
        filter_type = self.filter_type.get()
        window_size = self.window_size.get()
        threshold = self.threshold.get()
        k_value = self.k_value.get()
        
        # Đảm bảo k_value không lớn hơn số phần tử trong cửa sổ
        max_k = window_size * window_size
        k_value = min(k_value, max_k)
        
        # Chuyển đổi ảnh sang mảng numpy
        img_array = np.array(self.gray_image)
        
        # Ghi lại thời gian bắt đầu
        start_time = time.time()
        
        # Áp dụng bộ lọc tương ứng
        if filter_type == "median":
            filtered_array = self.median_filter(img_array, window_size, threshold)
        elif filter_type == "mean":
            filtered_array = self.mean_filter(img_array, window_size, threshold)
        else:  # knn_mean
            filtered_array = self.knn_mean_filter(img_array, window_size, k_value, threshold)
        
        # Tính thời gian xử lý
        processing_time = time.time() - start_time
        self.process_time_label.config(text=f"Thời gian xử lý: {processing_time:.4f} giây")
        
        # Chuyển đổi lại thành ảnh
        self.filtered_image = Image.fromarray(filtered_array.astype(np.uint8))
        
        # Hiển thị ảnh đã lọc
        self.display_image(self.filtered_image, self.filtered_display)
        
        # Hiển thị kết quả so sánh
        self.show_comparison(img_array, filtered_array)
    
    def median_filter(self, img_array, window_size, threshold):
        """
        Áp dụng bộ lọc trung vị với cửa sổ kích thước window_size và ngưỡng threshold
        """
        # Tạo mảng kết quả
        height, width = img_array.shape
        result = np.copy(img_array)
        
        # Tính padding cần thiết
        pad = window_size // 2
        
        # Padding ảnh
        padded_img = np.pad(img_array, ((pad, pad), (pad, pad)), mode='reflect')
        
        # Áp dụng bộ lọc
        for i in range(height):
            for j in range(width):
                # Lấy cửa sổ hiện tại
                window = padded_img[i:i+window_size, j:j+window_size]
                
                # Tính giá trị trung vị
                med_value = np.median(window)
                
                # Áp dụng ngưỡng
                if abs(int(img_array[i, j]) - int(med_value)) <= threshold:
                    result[i, j] = med_value
        
        return result
    
    def mean_filter(self, img_array, window_size, threshold):
        """
        Áp dụng bộ lọc trung bình với cửa sổ kích thước window_size và ngưỡng threshold
        """
        # Tạo mảng kết quả
        height, width = img_array.shape
        result = np.copy(img_array)
        
        # Tính padding cần thiết
        pad = window_size // 2
        
        # Padding ảnh
        padded_img = np.pad(img_array, ((pad, pad), (pad, pad)), mode='reflect')
        
        # Áp dụng bộ lọc
        for i in range(height):
            for j in range(width):
                # Lấy cửa sổ hiện tại
                window = padded_img[i:i+window_size, j:j+window_size]
                
                # Tính giá trị trung bình
                mean_value = np.mean(window)
                mean_value = round(mean_value)  # Làm tròn đến số nguyên gần nhất
                
                # Áp dụng ngưỡng
                if abs(int(img_array[i, j]) - int(mean_value)) <= threshold:
                    result[i, j] = mean_value
        
        return result
    
    def knn_mean_filter(self, img_array, window_size, k, threshold):
        """
        Áp dụng bộ lọc trung bình k giá trị gần nhất với cửa sổ kích thước window_size,
        k giá trị gần nhất và ngưỡng threshold
        """
        # Tạo mảng kết quả
        height, width = img_array.shape
        result = np.copy(img_array)
        
        # Tính padding cần thiết
        pad = window_size // 2
        
        # Padding ảnh
        padded_img = np.pad(img_array, ((pad, pad), (pad, pad)), mode='reflect')
        
        # Áp dụng bộ lọc
        for i in range(height):
            for j in range(width):
                # Lấy cửa sổ hiện tại
                window = padded_img[i:i+window_size, j:j+window_size].flatten()
                
                # Tính khoảng cách từ giá trị hiện tại đến các giá trị trong cửa sổ
                center_value = img_array[i, j]
                distances = np.abs(window - center_value)
                
                # Lấy k giá trị gần nhất
                k_nearest_indices = np.argsort(distances)[:k]
                k_nearest_values = window[k_nearest_indices]
                
                # Tính trung bình k giá trị gần nhất
                knn_mean = np.mean(k_nearest_values)
                knn_mean = round(knn_mean)  # Làm tròn đến số nguyên gần nhất
                
                # Áp dụng ngưỡng
                if abs(int(center_value) - int(knn_mean)) <= threshold:
                    result[i, j] = knn_mean
        
        return result
    
    def display_image(self, img, display_label, max_size=(500, 400)):
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
    
    def show_comparison(self, original_array, filtered_array):
        # Xóa frame hiển thị kết quả cũ
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        
        # Tính toán chỉ số so sánh
        mse = np.mean((original_array - filtered_array) ** 2)
        if mse == 0:
            psnr = float('inf')
        else:
            max_pixel = 255.0
            psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
        
        # Tính histogram
        hist_orig, _ = np.histogram(original_array, bins=256, range=[0, 256])
        hist_filtered, _ = np.histogram(filtered_array, bins=256, range=[0, 256])
        
        # Hiển thị thông tin so sánh
        info_frame = Frame(self.result_frame)
        info_frame.pack(pady=5)
        
        info_text = (
            f"Thông số so sánh ảnh:\n"
            f"MSE (Mean Squared Error): {mse:.2f}\n"
            f"PSNR (Peak Signal-to-Noise Ratio): {psnr:.2f} dB\n"
            f"Loại bộ lọc: {self.filter_type.get()}, Kích thước cửa sổ: {self.window_size.get()}, Ngưỡng θ: {self.threshold.get()}"
        )
        
        if self.filter_type.get() == "knn_mean":
            info_text += f", Số giá trị k: {self.k_value.get()}"
        
        info_label = Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack()
        
        # Hiển thị histograms
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        # Histogram ảnh gốc
        ax1.set_title("Histogram ảnh gốc")
        ax1.bar(range(256), hist_orig, color='blue', alpha=0.7)
        ax1.set_xlim(0, 255)
        ax1.set_xlabel("Mức xám")
        ax1.set_ylabel("Số lượng pixel")
        
        # Histogram ảnh đã lọc
        ax2.set_title("Histogram ảnh đã lọc")
        ax2.bar(range(256), hist_filtered, color='red', alpha=0.7)
        ax2.set_xlim(0, 255)
        ax2.set_xlabel("Mức xám")
        
        # Điều chỉnh layout
        plt.tight_layout()
        
        # Hiển thị matplotlib trong tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.result_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def save_image(self):
        if self.filtered_image is None:
            return
        
        # Mở hộp thoại lưu file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if file_path:
            self.filtered_image.save(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageFilteringApp(root)
    root.mainloop()