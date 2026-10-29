import streamlit as st
import cv2
import numpy as np
import tempfile
import os
import io
import glob
import pandas as pd
from PIL import Image
from ultralytics import YOLO, RTDETR
from gtts import gTTS

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Nhận diện biển báo giao thông Việt Nam",
    page_icon="🚦",
    layout="wide"
)

# Thư mục chứa file script hiện tại (ma_nguon/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------
# DATABASE DỮ LIỆU: NHÓM BIỂN, Ý NGHĨA & MỨC PHẠT NGHỊ ĐỊNH 100/123
# ---------------------------------------------------------
THONG_TIN_BIEN_BAO = {
    'Cấm vào': {'nhom': '🔴 Biển cấm', 'y_nghia': 'Cấm tất cả các loại xe đi vào theo chiều đặt biển.', 'muc_phat': 'Xe máy: 1-2 triệu | Ô tô: 4-6 triệu (Tước GPLX 1-3 tháng)'},
    'Chỉ được rẽ phải': {'nhom': '🔵 Biển hiệu lệnh', 'y_nghia': 'Các xe chỉ được phép rẽ phải tại nơi đường giao nhau.', 'muc_phat': 'Xe máy: 100k-200k | Ô tô: 300k-400k'},
    'Tốc độ tối đa cho phép 40km/h': {'nhom': '🔴 Biển cấm', 'y_nghia': 'Cấm các loại xe chạy vượt quá tốc độ 40 km/h.', 'muc_phat': 'Chạy quá 5-10km/h: 300k (Xe máy) / 800k (Ô tô). Quá 10-20km/h: Phạt 800k - 6tr'},
    'Cấm xe tải và xe khách': {'nhom': '🔴 Biển cấm', 'y_nghia': 'Cấm ô tô chở khách và các loại xe tải đi vào.', 'muc_phat': 'Ô tô tải/khách: 2-3 triệu (Tước GPLX 1-3 tháng)'},
    'Cấm xe tải': {'nhom': '🔴 Biển cấm', 'y_nghia': 'Cấm các loại xe tải vận chuyển hàng hóa đi vào.', 'muc_phat': 'Ô tô tải: 2-3 triệu (Tước GPLX 1-3 tháng)'},
    'Chiều cao hạn chế': {'nhom': '🔴 Biển cấm', 'y_nghia': 'Cấm các xe có chiều cao vượt quá giá trị ghi trên biển.', 'muc_phat': 'Ô tô: 2-3 triệu'},
    'Cấm xe ô tô': {'nhom': '🔴 Biển cấm', 'y_nghia': 'Cấm các loại xe cơ giới từ 3 bánh trở lên đi vào.', 'muc_phat': 'Ô tô: 2-3 triệu (Tước GPLX 1-3 tháng)'},
    'Nguy hiểm khác': {'nhom': '🟡 Biển cảnh báo', 'y_nghia': 'Báo trước sắp tới đoạn đường nguy hiểm chưa có biển riêng.', 'muc_phat': 'Chú ý quan sát và giảm tốc độ.'},
    'Đi chậm': {'nhom': '🟡 Biển cảnh báo', 'y_nghia': 'Nhắc nhở người điều khiển phương tiện giảm tốc độ.', 'muc_phat': 'Không giảm tốc độ: 100k - 400k'},
    'Ngoặt nguy hiểm liên tiếp bên phải': {'nhom': '🟡 Biển cảnh báo', 'y_nghia': 'Báo trước có nhiều chỗ ngoặt nguy hiểm liên tiếp.', 'muc_phat': 'Giảm tốc độ và chú ý quan sát.'},
    'Chướng ngại vật': {'nhom': '🟡 Biển cảnh báo', 'y_nghia': 'Báo trước phía trước có chướng ngại vật trên đường.', 'muc_phat': 'Giảm tốc độ và di chuyển cẩn thận.'},
    'Đoạn đường có camera giám sát': {'nhom': '🔷 Biển chỉ dẫn', 'y_nghia': 'Đoạn đường có trang bị hệ thống camera ghi hình phạt nguội.', 'muc_phat': 'Phạt vi phạm tự động qua hình ảnh.'},
    'Tốc độ tối đa cho phép 60km/h': {'nhom': '🔴 Biển cấm', 'y_nghia': 'Cấm các loại xe chạy quá tốc độ 60 km/h.', 'muc_phat': 'Chạy quá 5-10km/h: 300k (Xe máy) / 800k (Ô tô)'},
    'Cấm xe mô tô': {'nhom': '🔴 Biển cấm', 'y_nghia': 'Cấm xe mô tô (xe máy) đi vào tuyến đường này.', 'muc_phat': 'Xe máy: 800k - 1 triệu (Tước GPLX 1-3 tháng)'},
    'Làn đường dành riêng theo phương tiện': {'nhom': '🔵 Biển hiệu lệnh', 'y_nghia': 'Quy định làn đường dành riêng cho loại xe nhất định.', 'muc_phat': 'Đi sai làn: Xe máy 400k-600k | Ô tô 4-6 triệu'},
    'Cấm rẽ trái': {'nhom': '🔴 Biển cấm', 'y_nghia': 'Cấm tất cả các loại xe rẽ trái tại nút giao.', 'muc_phat': 'Xe máy: 800k - 1 triệu | Ô tô: 2-3 triệu'},
    'Cấm rẽ phải': {'nhom': '🔴 Biển cấm', 'y_nghia': 'Cấm tất cả các loại xe rẽ phải tại nút giao.', 'muc_phat': 'Xe máy: 800k - 1 triệu | Ô tô: 2-3 triệu'},
    'Cấm quay đầu xe': {'nhom': '🔴 Biển cấm', 'y_nghia': 'Cấm các loại xe quay đầu lại theo hướng ngược lại.', 'muc_phat': 'Xe máy: 100k-200k | Ô tô: 400k-600k'},
    'Đường bị hẹp cả hai bên': {'nhom': '🟡 Biển cảnh báo', 'y_nghia': 'Báo trước sắp đến đoạn đường bị hẹp đột ngột cả hai bên.', 'muc_phat': 'Chú ý giảm tốc độ và nhường đường cho xe đi ngược chiều.'},
    'Giao nhau có tín hiệu đèn': {'nhom': '🟡 Biển cảnh báo', 'y_nghia': 'Báo trước nơi giao nhau có đèn giao thông.', 'muc_phat': 'Yêu cầu quan sát tín hiệu đèn.'},
    'Cấm dừng xe và đỗ xe': {'nhom': '🔴 Biển cấm', 'y_nghia': 'Cấm tất cả phương tiện dừng xe và đỗ xe.', 'muc_phat': 'Xe máy: 300k-400k | Ô tô: 800k-1 triệu'},
    'Cấm đỗ xe': {'nhom': '🔴 Biển cấm', 'y_nghia': 'Cấm phương tiện đỗ xe (vẫn được dừng ngắn hạn).', 'muc_phat': 'Xe máy: 300k-400k | Ô tô: 400k-600k'},
    'Cấm xe mô tô rẽ trái': {'nhom': '🔴 Biển cấm', 'y_nghia': 'Cấm người điều khiển xe mô tô/xe máy rẽ trái.', 'muc_phat': 'Xe máy: 800k - 1 triệu (Tước GPLX 1-3 tháng)'},
    'Giao nhau cùng cấp': {'nhom': '🟡 Biển cảnh báo', 'y_nghia': 'Báo trước nút giao của các đường đồng cấp.', 'muc_phat': 'Nhường đường cho xe từ bên phải.'},
    'Đường người đi bộ sang đường': {'nhom': '🟡 Biển cảnh báo', 'y_nghia': 'Vị trí ưu tiên người đi bộ sang đường.', 'muc_phat': 'Không nhường đường người đi bộ: 200k-400k'},
    'Đèn xanh': {'nhom': '🚦 Đèn tín hiệu', 'y_nghia': 'Đèn xanh: Cho phép phương tiện lưu thông.', 'muc_phat': 'Được đi theo hướng đèn.'},
    'Đèn đỏ': {'nhom': '🚦 Đèn tín hiệu', 'y_nghia': 'Đèn đỏ: Bắt buộc dừng lại trước vạch.', 'muc_phat': 'Vượt đèn đỏ: Xe máy 800k-1tr | Ô tô 4tr-6tr'},
    'Điểm dừng xe buýt': {'nhom': '🔷 Biển chỉ dẫn', 'y_nghia': 'Nơi đón trả khách của xe buýt.', 'muc_phat': 'Cấm đỗ xe cá nhân tại điểm xe buýt'}
}

def lay_thong_tin_bien_bao(class_name):
    """Lấy thông tin biển báo, tự động suy luận nhóm biển nếu tên nhãn chưa có trong DB"""
    if class_name in THONG_TIN_BIEN_BAO:
        return THONG_TIN_BIEN_BAO[class_name]
    
    # Tự động suy đoán nhóm biển từ tên nhãn
    name_lower = class_name.lower()
    if 'cấm' in name_lower or 'hạn chế' in name_lower:
        nhom = '🔴 Biển cấm'
        y_nghia = f'Biển cấm ({class_name}): Yêu cầu người tham gia giao thông chấp hành nghiêm chỉnh.'
        muc_phat = 'Xe máy: 800k - 1 triệu | Ô tô: 2 - 3 triệu (Tuỳ hành vi)'
    elif any(k in name_lower for k in ['nguy hiểm', 'chướng ngại', 'hẹp', 'ngoặt', 'đường', 'giao nhau', 'dốc', 'công trường']):
        nhom = '🟡 Biển cảnh báo'
        y_nghia = f'Biển cảnh báo ({class_name}): Lái xe cần giảm tốc độ và chú ý quan sát.'
        muc_phat = 'Chú ý giảm tốc độ an toàn khi lưu thông.'
    elif any(k in name_lower for k in ['chỉ', 'làn', 'phải', 'trái', 'hiệu lệnh']):
        nhom = '🔵 Biển hiệu lệnh'
        y_nghia = f'Biển hiệu lệnh ({class_name}): Bắt buộc các phương tiện phải thi hành.'
        muc_phat = 'Xe máy: 100k - 200k | Ô tô: 300k - 400k'
    elif any(k in name_lower for k in ['đèn', 'xanh', 'đỏ', 'vàng']):
        nhom = '🚦 Đèn tín hiệu'
        y_nghia = f'Tín hiệu đèn giao thông ({class_name}).'
        muc_phat = 'Không chấp hành: Xe máy 800k - 1tr | Ô tô 4tr - 6tr'
    else:
        nhom = '🔷 Biển chỉ dẫn / Khác'
        y_nghia = f'Biển chỉ dẫn/Thông tin ({class_name}).'
        muc_phat = 'Tuân thủ hướng dẫn theo QCVN 41:2019/BGTVT.'
        
    return {'nhom': nhom, 'y_nghia': y_nghia, 'muc_phat': muc_phat}

# ---------------------------------------------------------
# HÀM PHÁT ÂM THANH CẢNH BÁO (TTS)
# ---------------------------------------------------------
def phat_canh_bao_giong_noi(danh_sach_bien):
    if not danh_sach_bien:
        return
    ten_biens = ", ".join(list(set(danh_sach_bien)))
    text = f"Chú ý! Phía trước có {ten_biens}"
    try:
        tts = gTTS(text=text, lang='vi')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format='audio/mp3', autoplay=True)
    except Exception:
        st.caption(f"📢 Cảnh báo âm thanh: {text}")

# ---------------------------------------------------------
# HÀM LÀM NẾT VÙNG ẢNH CẮT (ENHANCEMENT BẰNG LANCZOS4)
# ---------------------------------------------------------
def lam_net_anh_bien_bao(crop_img, target_size=300):
    h, w = crop_img.shape[:2]
    if h == 0 or w == 0:
        return crop_img
    
    # Phóng to bằng Lanczos4 giữ chi tiết sắc nét hơn hẳn
    scale = max(1.0, target_size / max(h, w))
    new_w, new_h = int(w * scale), int(h * scale)
    upscaled = cv2.resize(crop_img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
    
    # Cân bằng độ sáng tương phản nhẹ trên kênh YUV
    yuv = cv2.cvtColor(upscaled, cv2.COLOR_RGB2YUV)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(6, 6))
    yuv[:, :, 0] = clahe.apply(yuv[:, :, 0])
    enhanced = cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB)
    
    # Lọc làm sắc nét nhẹ
    kernel = np.array([[0, -0.5, 0], [-0.5, 3, -0.5], [0, -0.5, 0]])
    return cv2.filter2D(enhanced, -1, kernel)

# ---------------------------------------------------------
# HÀM TỰ ĐỘNG DÒ TÌM & NẠP MÔ HÌNH
# ---------------------------------------------------------
def find_valid_weight_path(candidate_paths):
    for p in candidate_paths:
        abs_path = os.path.join(BASE_DIR, p)
        if os.path.exists(abs_path):
            return abs_path
        if os.path.exists(p):
            return p
    return None

@st.cache_resource
def load_yolo_model(model_path):
    return YOLO(model_path)

@st.cache_resource
def load_rtdetr_model(model_path):
    return RTDETR(model_path)

CANDIDATE_RTDETR_PATHS = [
    "rtdetr_best.pt",
    "best.pt",
    "weights/rtdetr_best.pt",
    "weights/best.pt",
    "best1.pt",
    "rtdetr_best1.pt",
    "runs/detect/rtdetr_local/weights/best.pt"
]

CANDIDATE_YOLOV8_PATHS = [
    "yolov8_best.pt",
    "best.pt",
    "weights/yolov8_best.pt",
    "runs/detect/thu_nghiem_bien_bao/weights/best.pt",
    "runs/detect/yolov8_bien_bao/weights/best.pt"
]

# ---------------------------------------------------------
# CẤU HÌNH THANH SIDEBAR
# ---------------------------------------------------------
st.sidebar.title("⚙️ Cấu hình hệ thống")

st.sidebar.subheader("🤖 Lựa chọn Mô hình AI")
model_choice = st.sidebar.selectbox(
    "Thuật toán nhận diện:",
    [
        "RT-DETR (Real-Time Vision Transformer)",
        "YOLOv8n (CNN Single Stage)",
        "⚔️ So sánh song song (YOLOv8 vs RT-DETR)"
    ]
)

conf_threshold = st.sidebar.slider("Độ tin cậy (Confidence Threshold):", 0.1, 1.0, 0.4, 0.05)
enable_voice = st.sidebar.checkbox("🔊 Bật cảnh báo giọng nói (TTS)", value=True)

st.sidebar.markdown("---")
option = st.sidebar.radio("Tùy chọn đầu vào:", ["Tải ảnh lên", "Chụp ảnh từ Camera", "Tải video lên", "📊 Đánh giá mô hình"])

# Giao diện tiêu đề
st.title("🚦 HỆ THỐNG NHẬN DIỆN VÀ TRA CỨU BIỂN BÁO GIAO THÔNG VIỆT NAM")
st.markdown("---")

# ---------------------------------------------------------
# QUY TRÌNH NẠP MÔ HÌNH CHUẨN
# ---------------------------------------------------------
model_primary = None
model_secondary = None

rtdetr_path = find_valid_weight_path(CANDIDATE_RTDETR_PATHS)
yolov8_path = find_valid_weight_path(CANDIDATE_YOLOV8_PATHS)

if "RT-DETR" in model_choice and "So sánh" not in model_choice:
    if rtdetr_path:
        model_primary = load_rtdetr_model(rtdetr_path)
    else:
        st.error("❌ KHÔNG TÌM THẤY WEIGHTS TRAIN RT-DETR!")
        model_primary = load_rtdetr_model("rtdetr-l.pt")

elif "YOLOv8n" in model_choice:
    if yolov8_path:
        model_primary = load_yolo_model(yolov8_path)
    else:
        model_primary = load_yolo_model("yolov8n.pt")

elif "So sánh song song" in model_choice:
    model_primary = load_yolo_model(yolov8_path if yolov8_path else "yolov8n.pt")
    model_secondary = load_rtdetr_model(rtdetr_path if rtdetr_path else "rtdetr-l.pt")

# ==================== XỬ LÝ ẢNH ====================
if option in ["Tải ảnh lên", "Chụp ảnh từ Camera"]:
    image_to_process = None

    if option == "Tải ảnh lên":
        uploaded_file = st.file_uploader("Chọn ảnh biển báo giao thông...", type=["jpg", "jpeg", "png", "bmp", "webp"])
        if uploaded_file is not None:
            image_to_process = Image.open(uploaded_file)

    elif option == "Chụp ảnh từ Camera":
        camera_photo = st.camera_input("Chụp ảnh biển báo trực tiếp")
        if camera_photo is not None:
            image_to_process = Image.open(camera_photo)

    if image_to_process is not None:
        img_np = np.array(image_to_process)
        img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        if model_secondary is None:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📷 Ảnh đầu vào")
                st.image(image_to_process, use_container_width=True)

            results = model_primary.predict(source=img_cv, conf=conf_threshold)
            res_plotted = results[0].plot()
            res_rgb = cv2.cvtColor(res_plotted, cv2.COLOR_BGR2RGB)

            with col2:
                st.subheader(f"🔍 Kết quả ({model_choice.split('(')[0]})")
                st.image(res_rgb, use_container_width=True)

            boxes = results[0].boxes

        else:
            st.subheader("⚔️ KẾT QUẢ SO SÁNH ĐỐI CHIẾU THUẬT TOÁN")
            col1, col2 = st.columns(2)
            
            res1 = model_primary.predict(source=img_cv, conf=conf_threshold)
            res1_rgb = cv2.cvtColor(res1[0].plot(), cv2.COLOR_BGR2RGB)
            with col1:
                st.markdown("### 🔹 Thuật toán 1: YOLOv8n")
                st.image(res1_rgb, use_container_width=True)

            res2 = model_secondary.predict(source=img_cv, conf=conf_threshold)
            res2_rgb = cv2.cvtColor(res2[0].plot(), cv2.COLOR_BGR2RGB)
            with col2:
                st.markdown("### 🔸 Thuật toán 2: RT-DETR")
                st.image(res2_rgb, use_container_width=True)

            boxes = res2[0].boxes

        # HIỂN THỊ CHI TIẾT VÀ TRÍCH XUẤT ẢNH CẮT
        if len(boxes) > 0:
            detected_names = []
            st.markdown("---")
            st.subheader("✂️ Vùng biển báo trích xuất (Đã tối ưu làm nét):")
            
            cols = st.columns(min(len(boxes), 4))
            detected_items = []
            
            h, w, _ = img_np.shape
            for idx, box in enumerate(boxes):
                cls_id = int(box.cls[0])
                class_name = model_primary.names[cls_id] if model_secondary is None else model_secondary.names[cls_id]
                confidence = float(box.conf[0]) * 100
                detected_names.append(class_name)
                
                # Hàm tra cứu / suy đoán nhóm biển
                info = lay_thong_tin_bien_bao(class_name)
                
                # Cắt ảnh có bổ sung lề Padding 10%
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                pad_x = int((x2 - x1) * 0.10)
                pad_y = int((y2 - y1) * 0.10)
                
                crop_x1 = max(0, x1 - pad_x)
                crop_y1 = max(0, y1 - pad_y)
                crop_x2 = min(w, x2 + pad_x)
                crop_y2 = min(h, y2 + pad_y)
                
                cropped_img = img_np[crop_y1:crop_y2, crop_x1:crop_x2]
                enhanced_crop = lam_net_anh_bien_bao(cropped_img, target_size=300)
                
                col_idx = idx % 4
                with cols[col_idx]:
                    st.image(enhanced_crop, caption=f"{class_name} ({confidence:.1f}%)", width=240)
                
                detected_items.append({
                    "Nhóm biển": info['nhom'],
                    "Tên biển báo": class_name,
                    "Độ tin cậy": f"{confidence:.2f}%",
                    "Ý nghĩa": info['y_nghia'],
                    "Mức phạt vi phạm (NĐ 100/123)": info['muc_phat']
                })

            if enable_voice:
                phat_canh_bao_giong_noi(detected_names)

            st.markdown("---")
            st.subheader("📊 Bảng chi tiết nhận diện & Tra cứu mức phạt:")
            st.table(detected_items)
        else:
            st.warning("⚠️ Không phát hiện biển báo nào trong ảnh.")

# ==================== XỬ LÝ VIDEO ====================
elif option == "Tải video lên":
    uploaded_video = st.file_uploader("Chọn video đường phố / giao thông...", type=["mp4", "avi", "mov", "mkv"])
    if uploaded_video is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tfile.write(uploaded_video.read())
        cap = cv2.VideoCapture(tfile.name)
        
        col1, col2 = st.columns([3, 2])
        with col1:
            st.subheader("🎬 Video nhận diện thời gian thực")
            st_frame = st.empty()
        with col2:
            st.subheader("📊 Thống kê biển báo")
            st_table = st.empty()

        if st.button("▶️ Bắt đầu xử lý Video"):
            detected_dict = {}
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                results = model_primary.predict(source=frame, conf=conf_threshold, verbose=False)
                res_plotted = results[0].plot()
                res_rgb = cv2.cvtColor(res_plotted, cv2.COLOR_BGR2RGB)
                st_frame.image(res_rgb, use_container_width=True)
                
                for box in results[0].boxes:
                    cls_id = int(box.cls[0])
                    class_name = model_primary.names[cls_id]
                    confidence = float(box.conf[0]) * 100
                    info = lay_thong_tin_bien_bao(class_name)
                    
                    if class_name not in detected_dict or confidence > detected_dict[class_name]['conf']:
                        detected_dict[class_name] = {'conf': confidence, 'nhom': info['nhom'], 'muc_phat': info['muc_phat']}
                
                if detected_dict:
                    st_table.table([
                        {"Nhóm": v['nhom'], "Tên biển báo": k, "Độ tin cậy max": f"{v['conf']:.1f}%", "Mức phạt": v['muc_phat']}
                        for k, v in detected_dict.items()
                    ])
            cap.release()
            st.success("✅ Đã xử lý hoàn tất video!")

# ==================== ĐÁNH GIÁ MÔ HÌNH ====================
# ==================== ĐÁNH GIÁ MÔ HÌNH ====================
elif option == "📊 Đánh giá mô hình":
    st.header("📊 BÁO CÁO ĐÁNH GIÁ & SO SÁNH HIỆU NĂNG MÔ HÌNH")
    
    # 1. Chọn chế độ xem báo cáo
    chon_bao_cao = st.radio(
        "Lựa chọn báo cáo hiển thị:",
        ["⚔️ So sánh song song (YOLOv8 vs RT-DETR)", "🔸 Chi tiết RT-DETR (Transformer)", "🔹 Chi tiết YOLOv8n (CNN)"],
        horizontal=True
    )
    st.markdown("---")

    def tim_file_anh(folder, filenames):
        """Tìm file ảnh hỗ trợ cả .png và .jpg"""
        for fname in filenames:
            for ext in [".png", ".jpg", ".jpeg"]:
                path = os.path.join(folder, fname + ext)
                if os.path.exists(path):
                    return path
        return None

    # CHẾ ĐỘ 1: SO SÁNH SONG SONG 2 MÔ HÌNH
    if "So sánh" in chon_bao_cao:
        st.subheader("⚔️ BẢNG ĐỐI CHIẾU CHỈ SỐ HUẤN LUYỆN (YOLOV8 VS RT-DETR)")
        
        # Bảng chỉ số đối chiếu chuẩn
        df_compare = pd.DataFrame([
            {
                "Thuật toán": "YOLOv8n (CNN Single-Stage)",
                "Epochs": 50,
                "mAP@0.5": "96.80%",
                "mAP@0.5:0.95": "80.50%",
                "Precision": "95.20%",
                "Recall": "92.50%",
                "F1-Score": "0.9383"
            },
            {
                "Thuật toán": "RT-DETR (Vision Transformer)",
                "Epochs": 7,
                "mAP@0.5": "98.36%",
                "mAP@0.5:0.95": "85.10%",
                "Precision": "95.87%",
                "Recall": "97.74%",
                "F1-Score": "0.9680"
            }
        ])
        st.table(df_compare)

        # Hiển thị biểu đồ so sánh tổng hợp nếu có
        chart_so_sanh = glob.glob("runs/**/so_sanh_yolov8_vs_rtdetr.png", recursive=True)
        if chart_so_sanh:
            st.image(chart_so_sanh[0], caption="Biểu đồ so sánh đối chiếu chỉ số nhận diện", use_container_width=True)
        else:
            st.info("💡 Chạy file `python ma_nguon/danh_gia_mo_hinh.py` để xuất biểu đồ so sánh dạng hình ảnh vào thư mục `runs/`.")

    # CHẾ ĐỘ 2 BÁO CÁO CHI TIẾT TỪNG MÔ HÌNH
    else:
        tu_khoa = "rtdetr" if "RT-DETR" in chon_bao_cao else "yolo"
        
        # Tìm thư mục chứa kết quả của mô hình được chọn
        all_dirs = glob.glob("runs/**/", recursive=True)
        matched_dirs = [d for d in all_dirs if tu_khoa in d.lower()]
        
        run_dir = matched_dirs[0] if matched_dirs else (all_dirs[0] if all_dirs else None)

        if not run_dir:
            st.error("❌ Chưa tìm thấy dữ liệu kết quả huấn luyện trong thư mục `runs/`.")
        else:
            st.success(f"📂 Đang hiển thị kết quả từ: `{run_dir}`")
            tab1, tab2, tab3 = st.tabs(["📉 Ma trận nhầm lẫn & Loss", "📈 Đường cong F1 / PR", "📋 File kết quả results.csv"])
            
            with tab1:
                col_a, col_b = st.columns(2)
                cm_img = tim_file_anh(run_dir, ["confusion_matrix", "confusion_matrix_unnormalized"])
                res_img = tim_file_anh(run_dir, ["results"])
                
                if cm_img:
                    with col_a:
                        st.image(cm_img, caption="Confusion Matrix (Ma trận nhầm lẫn)", use_container_width=True)
                if res_img:
                    with col_b:
                        st.image(res_img, caption="Training Loss & mAP Curves", use_container_width=True)
                        
            with tab2:
                col_c, col_d = st.columns(2)
                f1_img = tim_file_anh(run_dir, ["BoxF1_curve", "F1_curve"])
                pr_img = tim_file_anh(run_dir, ["BoxPR_curve", "PR_curve"])
                
                if f1_img:
                    with col_c:
                        st.image(f1_img, caption="F1-Confidence Curve", use_container_width=True)
                if pr_img:
                    with col_d:
                        st.image(pr_img, caption="Precision-Recall Curve", use_container_width=True)
                        
            with tab3:
                csv_path = os.path.join(run_dir, "results.csv")
                if os.path.exists(csv_path):
                    df_res = pd.read_csv(csv_path)
                    df_res.columns = df_res.columns.str.strip()
                    st.dataframe(df_res, use_container_width=True)
                else:
                    st.warning("⚠️ Không tìm thấy file results.csv trong thư mục này.")