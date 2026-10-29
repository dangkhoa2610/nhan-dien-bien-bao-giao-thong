import os
import glob
from ultralytics import YOLO

MODEL_PATH = "runs/detect/thu_nghiem_bien_bao/weights/best.pt"
TEST_IMAGES_DIR = "du_lieu/tho/dataset_cropped/dataset/test/images"

def detect_traffic_signs(img_path, conf_threshold=0.5):
    # Kiểm tra file mô hình
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Không tìm thấy file weights tại: {MODEL_PATH}")
        print("👉 Bạn hãy đảm bảo đã copy file best.pt từ Google Drive về đúng thư mục trên!")
        return

    # Kiểm tra đường dẫn ảnh
    if not os.path.exists(img_path):
        print(f"❌ Đường dẫn ảnh không tồn tại: {img_path}")
        return

    print(f"🔍 Đang tiến hành nhận diện ảnh: {img_path}")
    model = YOLO(MODEL_PATH)
    
    # Chạy dự đoán
    results = model.predict(
        source=img_path, 
        conf=conf_threshold, 
        save=True, 
        project="runs/detect", 
        name="du_doan",
        exist_ok=True
    )

    print("\n✅ Hoàn thành nhận diện!")
    print(f"📌 Ảnh kết quả được lưu tại thư mục: runs/detect/du_doan/")

if __name__ == "__main__":
    # Tự động lấy file ảnh đầu tiên trong tập test/images
    search_pattern = os.path.join(TEST_IMAGES_DIR, "*.[jJ][pP][gG]")
    image_files = glob.glob(search_pattern) + glob.glob(os.path.join(TEST_IMAGES_DIR, "*.[pP][nN][gG]"))
    
    if image_files:
        sample_img = image_files[0] # Lấy ảnh đầu tiên tìm được
        detect_traffic_signs(sample_img, conf_threshold=0.5)
    else:
        print(f"⚠️ Không tìm thấy file ảnh nào trong thư mục: {TEST_IMAGES_DIR}")