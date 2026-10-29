import os
from ultralytics import RTDETR

if __name__ == '__main__':
    # Lấy đường dẫn thư mục hiện tại
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    path_last = os.path.join(BASE_DIR, 'weights', 'last.pt')
    data_yaml = os.path.join(BASE_DIR, 'dataset', 'data.yaml')

    if not os.path.exists(path_last):
        print(f"❌ Không tìm thấy file weights tại: {path_last}")
        exit()

    if not os.path.exists(data_yaml):
        print(f"❌ Không tìm thấy file data.yaml tại: {data_yaml}")
        exit()

    print(f"📦 Đang nạp trọng số epoch 43 từ: {path_last}")
    model = RTDETR(path_last)

    # Chạy tiếp tục 7 epoch
    model.train(
        data=data_yaml,
        epochs=7,
        imgsz=640,
        batch=8,
        device='cpu',
        workers=0,  # Đặt 0 để tránh lỗi nạp dữ liệu đệm trên Windows
        project=os.path.join(BASE_DIR, 'runs', 'detect'),
        name='rtdetr_local',
        exist_ok=True
    )