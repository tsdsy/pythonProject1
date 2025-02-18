import tkinter as tk
from tkinter import filedialog, colorchooser, ttk
from PIL import Image, ImageTk, ImageOps
import cv2
import numpy as np

class PhotoEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("证件照处理工具")
        
        # 尺寸标准（300dpi）
        self.sizes = {
            "一寸": (295, 413),    # 2.5cm×3.5cm
            "二寸": (413, 579)     # 3.5cm×4.9cm
        }
        
        # 创建界面
        self.create_widgets()
        self.current_image = None
        self.original_image = None
        self.bg_color = (255, 255, 255)  # 默认白色背景
        
    def create_widgets(self):
        # 文件选择区域
        file_frame = tk.Frame(self.master)
        file_frame.pack(pady=10)
        
        self.btn_open = tk.Button(file_frame, text="选择图片", command=self.open_image)
        self.btn_open.pack(side=tk.LEFT, padx=5)
        
        # 尺寸选择
        size_frame = tk.Frame(self.master)
        size_frame.pack(pady=5)
        
        tk.Label(size_frame, text="证件照尺寸:").pack(side=tk.LEFT)
        self.size_var = tk.StringVar()
        self.size_combobox = ttk.Combobox(size_frame, textvariable=self.size_var, values=list(self.sizes.keys()))
        self.size_combobox.pack(side=tk.LEFT, padx=5)
        self.size_combobox.current(0)
        
        # 背景颜色选择
        color_frame = tk.Frame(self.master)
        color_frame.pack(pady=5)
        
        self.btn_color = tk.Button(color_frame, text="选择背景颜色", command=self.choose_color)
        self.btn_color.pack(side=tk.LEFT, padx=5)
        
        # 图像显示区域
        self.canvas = tk.Canvas(self.master, width=600, height=400)
        self.canvas.pack(pady=10)
        
        # 处理按钮
        self.btn_process = tk.Button(self.master, text="保存证件照", command=self.process_image)
        self.btn_process.pack(pady=10)
    
    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("图片文件", "*.jpg *.jpeg *.png")])
        if file_path:
            self.original_image = Image.open(file_path)
            self.original_image = self.original_image.convert("RGBA")
            self.current_image = self.original_image.copy()
            self.show_image()
    
    def show_image(self):
        if self.current_image:
            # 调整显示尺寸
            display_img = self.current_image.copy()
            w, h = display_img.size
            ratio = min(600/w, 400/h)
            display_img = display_img.resize((int(w*ratio), int(h*ratio)), Image.LANCZOS)
            
            self.tk_image = ImageTk.PhotoImage(display_img)
            self.canvas.create_image(300, 200, image=self.tk_image, anchor=tk.CENTER)

    def choose_color(self):
        color = colorchooser.askcolor(title="选择背景颜色")
        if color[1]:
            self.bg_color = tuple(int(color[0][i]) for i in range(3))
            self.apply_background()

    def apply_background(self):
        try:
            if self.current_image:
                img_cv = cv2.cvtColor(np.array(self.current_image), cv2.COLOR_RGB2BGR)
                mask = np.zeros(img_cv.shape[:2], np.uint8)
                
                # 自动计算前景区域（改进点1）
                h, w = img_cv.shape[:2]
                rect = (int(w*0.1), int(h*0.1), int(w*0.9), int(h*0.9))  # 假设人物位于中央80%区域
                
                # 增加迭代次数（改进点2）
                cv2.grabCut(img_cv, mask, rect, None, None, 10, cv2.GC_INIT_WITH_RECT)
                
                # 优化掩码处理（改进点3）
                mask2 = np.where((mask == cv2.GC_BGD) | (mask == cv2.GC_PR_BGD), 0, 1).astype('uint8')
                
                # 添加形态学操作（改进点4）
                kernel = np.ones((3,3), np.uint8)
                mask2 = cv2.erode(mask2, kernel, iterations=1)
                mask2 = cv2.dilate(mask2, kernel, iterations=1)
                
                # 边缘平滑处理（改进点5）
                mask2 = cv2.GaussianBlur(mask2, (5,5), 0)
                
                # 保留人物部分
                img_cv = img_cv * mask2[:, :, np.newaxis]
                
                # 将OpenCV图像转换回PIL格式
                img_pil = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
                
                # 将掩码转换为PIL格式
                mask_pil = Image.fromarray(mask2 * 255).convert("L")
                
                # 创建新的背景图像
                new_bg = Image.new("RGB", self.current_image.size, self.bg_color)
                
                # 使用掩码进行背景替换
                self.current_image = Image.composite(img_pil, new_bg, mask_pil)
                self.show_image()

        except Exception as e:
            tk.messagebox.showerror("处理错误", f"背景替换失败：{str(e)}")
        finally:
            self.progress.stop()
            self.progress.pack_forget()

    def process_image(self):
        if self.current_image and self.size_var.get():
            # 获取目标尺寸
            target_size = self.sizes[self.size_var.get()]
            
            # 裁剪为证件照比例
            cropped = self.crop_to_aspect(self.current_image, target_size)
            
            # 调整到精确尺寸
            resized = cropped.resize(target_size, Image.LANCZOS)
            
            # 保存文件
            save_path = filedialog.asksaveasfilename(
                defaultextension=".jpg",
                filetypes=[("JPEG 图片", "*.jpg"), ("PNG 图片", "*.png")],
                initialdir="C:\\Users\\YourUsername\\Pictures"
            )
            if save_path:
                resized.save(save_path, 
                            quality=100,
                            dpi=(300, 300),  # 符合证件照标准
                            subsampling=0)
                tk.messagebox.showinfo("保存成功", f"证件照已保存至：{save_path}")

    def crop_to_aspect(self, img, target_size):
        """智能裁剪到目标宽高比"""
        target_ratio = target_size[0] / target_size[1]
        img_ratio = img.width / img.height
        
        if img_ratio > target_ratio:
            # 裁剪宽度
            new_width = int(img.height * target_ratio)
            left = (img.width - new_width) // 2
            return img.crop((left, 0, left + new_width, img.height))
        else:
            # 裁剪高度
            new_height = int(img.width / target_ratio)
            top = (img.height - new_height) // 2
            return img.crop((0, top, img.width, top + new_height))

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoEditor(root)
    root.mainloop()
