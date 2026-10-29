import os
import torch
from ultralytics import YOLO

def main():
    # 1. Đường dẫn file data.yaml
    YAML_PATH = "du_lieu/tho/dataset_cropped/dataset/data.yaml"
    
    if not os.path.exists(YAML_PATH):
        print(f"❌ Không tìm thấy file cấu hình: {YAML_PATH}")
        return

    # 2. Tự động chọn thiết bị huấn luyện (GPU nếu có, ngược lại dùng CPU)
    device = 0 if torch.cuda.is_available() else "cpu"
    print(f"🚀 Sử dụng thiết bị huấn luyện: {device}")

    # 3. Khởi tạo mô hình YOLOv8n (Pretrained Nano model - nhẹ và nhanh)
    model = YOLO("yolov8n.pt")

    # 4. Tiến hành huấn luyện mô hình
    print("⏳ Đang bắt đầu huấn luyện...")
    model.train(
        data=YAML_PATH,
        epochs=50,                  # Số vòng lặp huấn luyện (có thể chỉnh thành 100 nếu có GPU mạnh)
        imgsz=640,                  # Kích thước ảnh chuẩn của YOLO
        batch=16,                   # Số ảnh xử lý trong 1 lượt (giảm xuống 8 hoặc 4 nếu bị tràn RAM/VRAM)
        workers=4,                  # Số luồng đọc dữ liệu
        project="runs/detect",      # Lưu kết quả đúng thư mục 'runs/detect' trong cây thư mục gốc
        name="thu_nghiem_bien_bao", # Tên folder chứa kết quả đợt train này
        exist_ok=True,              # Cho phép ghi đè nếu chạy lại
        device=device
    )

    print("\n✅ HOÀN THÀNH HUẤN LUYỆN!")
    print("📌 Trọng số mô hình tốt nhất lưu tại: runs/detect/thu_nghiem_bien_bao/weights/best.pt")

if __name__ == "__main__":
    main()