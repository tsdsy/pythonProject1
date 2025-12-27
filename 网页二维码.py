import qrcode
from PIL import Image
import tkinter as tk
from tkinter import filedialog

# 隐藏主窗口
root = tk.Tk()
root.withdraw()

# 输入网址和文件名
data = input("网址：").strip()
filename = input("文件名：").strip() + ".png"

# 创建二维码对象
qr = qrcode.QRCode(
	box_size=10,  # 边框大小
	border=4,  # 边框宽度
)
qr.add_data(data)
qr.make(fit=True)  # 自动调整大小

# 生成彩色的二维码
img = qr.make_image(fill_color="red", back_color="white").convert("RGB")

# 通过文件对话框选择logo图片
print("请选择logo图片文件...")
logo_path = filedialog.askopenfilename(
	title="选择logo图片",
	filetypes=[
		("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
		("PNG files", "*.png"),
		("JPG files", "*.jpg *.jpeg"),
		("All files", "*.*")
	]
)

if logo_path and logo_path != '':  # 如果选择了文件
	try:
		logo = Image.open(logo_path)

		# RGB模式，避免模式不匹配
		if logo.mode in ('RGBA', 'LA', 'P'):
			# 创建白色背景图层
			background = Image.new('RGB', logo.size, (255, 255, 255))
			if logo.mode == 'P':
				logo = logo.convert('RGBA')
			# 将logo粘贴到白色背景上
			if logo.mode == 'RGBA':
				background.paste(logo, mask=logo.split()[-1])
			else:
				background.paste(logo)
			logo = background

		# 获取二维码的宽高
		qr_width, qr_height = img.size
		logo_size = qr_width // 5
		logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

		# 计算logo的坐标
		pos = (qr_width - logo_size) // 2, (qr_height - logo_size) // 2

		# 粘贴logo到二维码上
		img.paste(logo, pos)
		print("logo图片添加成功！")
	except Exception as e:
		print(f"处理logo图片时出错: {e}")
		print("生成无logo的二维码！")
else:
	print("未选择logo图片，生成无logo的二维码！")

# 保存二维码
img.save(filename)
print(f"二维码保存成功！为{filename}")

# 关闭tkinter窗口
root.destroy()
