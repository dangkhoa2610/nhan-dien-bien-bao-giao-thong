import os
from collections import Counter

# Đường dẫn đến thư mục dataset mới
DATASET_PATH = "du_lieu/tho/dataset_cropped/dataset"

if not os.path.exists(DATASET_PATH):
    print(f"❌ Không tìm thấy thư mục: {DATASET_PATH}")
else:
    print("📊 THỐNG KÊ DATASET THEO ĐỊNH DẠNG YOLO (OBJECT DETECTION)\n")
    
    splits = [d for d in os.listdir(DATASET_PATH) if os.path.isdir(os.path.join(DATASET_PATH, d))]
    
    total_images_all = 0
    total_boxes_all = 0
    global_class_counts = Counter()

    for split in splits:
        img_dir = os.path.join(DATASET_PATH, split, "images")
        lbl_dir = os.path.join(DATASET_PATH, split, "labels")
        
        if not os.path.exists(img_dir):
            continue
            
        images = [f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        
        box_count = 0
        split_class_counts = Counter()
        
        if os.path.exists(lbl_dir):
            for img_f in images:
                txt_name = os.path.splitext(img_f)[0] + ".txt"
                txt_path = os.path.join(lbl_dir, txt_name)
                
                if os.path.exists(txt_path):
                    with open(txt_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for line in lines:
                            parts = line.strip().split()
                            if parts:
                                class_id = int(parts[0])
                                split_class_counts[class_id] += 1
                                global_class_counts[class_id] += 1
                                box_count += 1

        total_images_all += len(images)
        total_boxes_all += box_count
        
        print(f"📂 Tập [{split.upper()}]:")
        print(f"  - Số lượng ảnh                   : {len(images)}")
        print(f"  - Số lượng nhãn biển báo (boxes) : {box_count}")
        print(f"  - Số loại biển báo xuất hiện    : {len(split_class_counts)}")
        print("-" * 50)

    print(f"✅ TỔNG THỂ DATASET:")
    print(f"- Tổng số ảnh        : {total_images_all}")
    print(f"- Tổng số khung nhãn : {total_boxes_all}")
    print(f"- Danh sách Class ID : {sorted(list(global_class_counts.keys()))}")