import os

# Danh sách các thư mục cần tạo
directories = [
    "du_lieu/da_xu_ly/traffic_sign_split/test",
    "du_lieu/da_xu_ly/traffic_sign_split/train",
    "du_lieu/da_xu_ly/traffic_sign_split/val",
    "du_lieu/tho/dataset_cropped",
    "ma_nguon/mo_hinh",
    "ma_nguon/nap_du_lieu",
    "ma_nguon/tien_ich",
    "runs/classify/thu_nghiem_bien_bao/weights",
    "thu_nghiem",
]

# Danh sách các file rỗng cần khởi tạo
files = [
    "ma_nguon/mo_hinh/__init__.py",
    "ma_nguon/mo_hinh/mang_phan_loai.py",
    "ma_nguon/nap_du_lieu/__init__.py",
    "ma_nguon/nap_du_lieu/traffic_sign_dataset.py",
    "ma_nguon/nap_du_lieu/tang_cuong_du_lieu.py",
    "ma_nguon/tien_ich/__init__.py",
    "ma_nguon/tien_ich/chia_du_lieu.py",
    "ma_nguon/tien_ich/chuyen_nhan_yolo.py",
    "ma_nguon/tien_ich/giai_nen.py",
    "ma_nguon/tien_ich/tien_xu_ly_anh.py",
    "ma_nguon/danh_gia_mo_hinh.py",
    "ma_nguon/du_doan_bien_bao.py",
    "ma_nguon/giao_dien_app.py",
    "ma_nguon/he_thong_nhan_dien.py",
    "ma_nguon/huan_luyen_phan_loai.py",
    "thu_nghiem/01_Kham_Pha_Du_Lieu.ipynb",
    ".gitignore",
    "requirements.txt",
]

# Tạo thư mục
for folder in directories:
    os.makedirs(folder, exist_ok=True)

# Tạo file
for file_path in files:
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            pass

print("✅ Đã khởi tạo xong cây thư mục dự án!")