import tkinter as tk
from tkinter import filedialog, Scale, Button, Label, Frame, IntVar
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class HistogramEqualizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kỹ thuật Cân bằng Histogram (Histogram Equalization)")
        self.root.geometry("1200x800")
        
        # Biến lưu trữ
        self.original_image = None
        self.gray_image = None
        self.equalized_image = None
        self.new_level = IntVar(value=256)  # Mặc định: 256 mức xám
        
        # Tạo giao diện
        self.create_ui()
    
    def create_ui(self):
        # Panel chính
        main_frame = Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel điều khiển
        control_frame = Frame(main_frame)
        control_frame.pack(pady=10)
        
        # Nút mở ảnh
        Button(control_frame, text="Mở ảnh", command=self.open_image, width=15).pack(side=tk.LEFT, padx=5)
        
        # Nút cân bằng histogram
        Button(control_frame, text="Cân bằng Histogram", command=self.equalize_histogram, width=20).pack(side=tk.LEFT, padx=5)
        
        # Nút lưu ảnh
        Button(control_frame, text="Lưu ảnh đã xử lý", command=self.save_image, width=15).pack(side=tk.LEFT, padx=5)
        
        # Panel hiển thị ảnh
        image_frame = Frame(main_frame)
        image_frame.pack(fill=tk.BOTH, expand=True)
        
        # Hiển thị ảnh gốc
        original_panel = Frame(image_frame)
        original_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        Label(original_panel, text="Ảnh gốc").pack()
        self.original_display = Label(original_panel, bg="lightgray")
        self.original_display.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Hiển thị ảnh đã cân bằng histogram
        equalized_panel = Frame(image_frame)
        equalized_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        Label(equalized_panel, text="Ảnh đã cân bằng histogram").pack()
        self.equalized_display = Label(equalized_panel, bg="lightgray")
        self.equalized_display.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Panel điều chỉnh tham số
        params_frame = Frame(main_frame)
        params_frame.pack(fill=tk.X, pady=10)
        
        Label(params_frame, text="Số mức xám đầu ra (new_level):").pack(side=tk.LEFT, padx=5)
        
        # Thanh trượt điều chỉnh số mức xám
        levels_scale = Scale(
            params_frame, 
            from_=2, 
            to=256,
            orient=tk.HORIZONTAL,
            length=400,
            variable=self.new_level
        )
        levels_scale.pack(side=tk.LEFT, padx=5)
        
        # Panel hiển thị histogram
        self.histogram_frame = Frame(main_frame, height=300)
        self.histogram_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Panel giải thích
        explanation_frame = Frame(main_frame)
        explanation_frame.pack(fill=tk.X, pady=10)
        
        explanation_text = """
        Kỹ thuật Cân bằng Histogram (Histogram Equalization):
        
        Nguyên lý: Phân phối lại các mức xám sao cho histogram của ảnh đầu ra gần với phân phối đồng đều.
        
        Các bước thực hiện:
        1. Tính histogram h(g) của ảnh gốc
        2. Tính histogram tích lũy: t(g) = Σ(i=0 đến g) h(i)
        3. Xác định trung bình điểm ảnh cho mỗi mức xám: TB = (m*n)/new_level
        4. Ánh xạ mỗi mức xám g sang mức xám mới: f(g) = max{0, round(t(g)/TB - 1)}
        
        Kết quả: Ảnh đầu ra có độ tương phản được cải thiện và histogram được phân phối đều hơn.
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
            
            # Vẽ histogram của ảnh gốc
            self.plot_original_histogram()
    
    def equalize_histogram(self):
        if self.gray_image is None:
            return
        
        # Lấy số mức xám đầu ra
        new_level = self.new_level.get()
        
        # Chuyển đổi ảnh sang mảng numpy
        img_array = np.array(self.gray_image)
        
        # Kích thước ảnh
        m, n = img_array.shape
        
        # Tính histogram của ảnh gốc
        hist, _ = np.histogram(img_array.flatten(), bins=256, range=[0, 256])
        
        # Tính histogram tích lũy (cumulative histogram)
        cumulative_hist = np.cumsum(hist)
        
        # Số điểm ảnh trung bình cho mỗi mức xám trong ảnh cân bằng
        TB = (m * n) / new_level
        
        # Tính hàm ánh xạ: f(g) = max{0, round(t(g)/TB - 1)}
        mapping = np.zeros(256, dtype=np.uint8)
        for g in range(256):
            t_g = cumulative_hist[g]
            f_g = max(0, round(t_g / TB - 1))
            # Đảm bảo f(g) không vượt quá new_level-1
            mapping[g] = min(f_g, new_level - 1)
        
        # Áp dụng hàm ánh xạ vào ảnh
        equalized_array = mapping[img_array]
        
        # Chuyển đổi lại thành ảnh
        self.equalized_image = Image.fromarray(equalized_array.astype(np.uint8))
        
        # Hiển thị ảnh đã cân bằng
        self.display_image(self.equalized_image, self.equalized_display)
        
        # Vẽ histogram của ảnh gốc và ảnh đã cân bằng
        self.plot_histograms(img_array, equalized_array)
    
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
    
    def plot_original_histogram(self):
        if self.gray_image is None:
            return
        
        # Xóa frame hiển thị histogram cũ
        for widget in self.histogram_frame.winfo_children():
            widget.destroy()
        
        # Chuyển đổi ảnh sang mảng numpy
        img_array = np.array(self.gray_image)
        
        # Tạo figure và axes cho matplotlib
        fig, ax = plt.subplots(figsize=(10, 4))
        
        # Vẽ histogram ảnh gốc
        ax.set_title("Histogram ảnh gốc")
        ax.hist(img_array.flatten(), bins=256, range=[0, 256], color='blue', alpha=0.7)
        ax.set_xlim(0, 255)
        ax.set_xlabel("Mức xám")
        ax.set_ylabel("Số lượng pixel")
        
        # Điều chỉnh layout
        plt.tight_layout()
        
        # Hiển thị matplotlib trong tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.histogram_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def plot_histograms(self, original_array, equalized_array):
        # Xóa frame hiển thị histogram cũ
        for widget in self.histogram_frame.winfo_children():
            widget.destroy()
        
        # Tạo figure và axes cho matplotlib
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        # Vẽ histogram ảnh gốc
        ax1.set_title("Histogram ảnh gốc")
        ax1.hist(original_array.flatten(), bins=256, range=[0, 256], color='blue', alpha=0.7)
        ax1.set_xlim(0, 255)
        ax1.set_xlabel("Mức xám")
        ax1.set_ylabel("Số lượng pixel")
        
        # Vẽ histogram ảnh đã cân bằng
        ax2.set_title(f"Histogram ảnh đã cân bằng (new_level={self.new_level.get()})")
        ax2.hist(equalized_array.flatten(), bins=256, range=[0, 256], color='red', alpha=0.7)
        ax2.set_xlim(0, 255)
        ax2.set_xlabel("Mức xám")
        
        # Điều chỉnh layout
        plt.tight_layout()
        
        # Hiển thị matplotlib trong tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.histogram_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Hiển thị thêm thông tin về chất lượng cân bằng
        self.display_equalization_metrics(original_array, equalized_array)
    
    def display_equalization_metrics(self, original_array, equalized_array):
        # Tính toán các chỉ số đánh giá chất lượng cân bằng histogram
        
        # Tính histogram
        hist_orig, _ = np.histogram(original_array.flatten(), bins=256, range=[0, 256])
        hist_eq, _ = np.histogram(equalized_array.flatten(), bins=256, range=[0, 256])
        
        # Chuẩn hóa histogram (chuyển thành phân phối xác suất)
        total_pixels = np.prod(original_array.shape)
        pdf_orig = hist_orig / total_pixels
        pdf_eq = hist_eq / total_pixels
        
        # Tính độ lệch chuẩn (standard deviation) của histogram
        # Độ lệch chuẩn cao hơn thường chỉ ra độ tương phản tốt hơn
        std_orig = np.std(original_array)
        std_eq = np.std(equalized_array)
        
        # Tính entropy của histogram (thước đo thông tin)
        # Entropy cao hơn thường chỉ ra phân phối đồng đều hơn
        entropy_orig = -np.sum(pdf_orig[pdf_orig > 0] * np.log2(pdf_orig[pdf_orig > 0]))
        entropy_eq = -np.sum(pdf_eq[pdf_eq > 0] * np.log2(pdf_eq[pdf_eq > 0]))
        
        # Tạo frame để hiển thị thông tin
        metrics_frame = Frame(self.histogram_frame)
        metrics_frame.pack(pady=10)
        
        metrics_text = (
            f"Thông số đánh giá chất lượng cân bằng histogram:\n\n"
            f"Độ lệch chuẩn (đo độ tương phản):\n"
            f"   - Ảnh gốc: {std_orig:.2f}\n"
            f"   - Ảnh đã cân bằng: {std_eq:.2f}\n\n"
            f"Entropy (đo tính đồng đều của phân phối):\n"
            f"   - Ảnh gốc: {entropy_orig:.2f} bits\n"
            f"   - Ảnh đã cân bằng: {entropy_eq:.2f} bits\n"
            f"Entropy cao hơn chỉ ra phân phối đồng đều hơn."
        )
        
        metrics_label = Label(metrics_frame, text=metrics_text, justify=tk.LEFT)
        metrics_label.pack()
    
    def save_image(self):
        if self.equalized_image is None:
            return
        
        # Mở hộp thoại lưu file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if file_path:
            self.equalized_image.save(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = HistogramEqualizationApp(root)
    root.mainloop()