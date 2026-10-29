import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

def tim_thu_muc_ket_qua():
    """Tự động tìm thư mục chứa results.csv trong runs/"""
    danh_sach_csv = glob.glob("runs/**/results.csv", recursive=True)
    if not danh_sach_csv:
        return None
    # Lấy thư mục chứa file results.csv đầu tiên tìm thấy
    return os.path.dirname(danh_sach_csv[0])

def danh_gia_mo_hinh():
    run_dir = tim_thu_muc_ket_qua()
    
    if not run_dir:
        print("❌ Không tìm thấy file 'results.csv' trong thư mục 'runs/'.")
        print("👉 Vui lòng giải nén hoặc chép các file kết quả train vào thư mục 'runs/'.")
        return

    print(f"📂 Đang phân tích kết quả từ thư mục: {run_dir}\n")
    
    csv_path = os.path.join(run_dir, "results.csv")
    df = pd.read_csv(csv_path)
    
    # Xóa khoảng trắng thừa ở tên cột do YOLO tạo ra
    df.columns = df.columns.str.strip()
    
    # Lấy ra các cột chỉ số chính
    epoch_col = df['epoch'] if 'epoch' in df.columns else df.index
    
    # Xác định các cột mAP, Precision, Recall
    map50_col = [c for c in df.columns if 'metrics/mAP50(B)' in c or 'mAP50' in c][0]
    map50_95_col = [c for c in df.columns if 'metrics/mAP50-95(B)' in c or 'mAP50-95' in c][0]
    precision_col = [c for c in df.columns if 'metrics/precision(B)' in c or 'precision' in c][0]
    recall_col = [c for c in df.columns if 'metrics/recall(B)' in c or 'recall' in c][0]
    
    # Epoch đạt kết quả tốt nhất (mAP50 cao nhất)
    best_idx = df[map50_col].idxmax()
    best_row = df.loc[best_idx]
    last_row = df.iloc[-1]
    
    print("==================================================")
    print("📊 THỐNG KÊ CHỈ SỐ HUẤN LUYỆN (EVALUATION METRICS)")
    print("==================================================")
    print(f"Tổng số Epoch đã train: {len(df)}")
    print(f"\n🌟 EPOCH TỐT NHẤT (Epoch {int(best_row['epoch'] if 'epoch' in df.columns else best_idx + 1)}):")
    print(f"  - mAP50      : {best_row[map50_col]:.4f} ({best_row[map50_col]*100:.2f}%)")
    print(f"  - mAP50-95   : {best_row[map50_95_col]:.4f} ({best_row[map50_95_col]*100:.2f}%)")
    print(f"  - Precision  : {best_row[precision_col]:.4f} ({best_row[precision_col]*100:.2f}%)")
    print(f"  - Recall     : {best_row[recall_col]:.4f} ({best_row[recall_col]*100:.2f}%)")
    
    print(f"\n🏁 EPOCH CUỐI CÙNG (Epoch {int(last_row['epoch'] if 'epoch' in df.columns else len(df))}):")
    print(f"  - mAP50      : {last_row[map50_col]:.4f}")
    print(f"  - mAP50-95   : {last_row[map50_95_col]:.4f}")
    print("==================================================\n")

    # -----------------------------------------------------
    # VẼ BIỂU ĐỒ DIỄN BIẾN ĐỘ CHÍNH XÁC VÀ HÀM MẤT MÁT (LOSS)
    # -----------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Biểu đồ 1: Độ chính xác (mAP50, Precision, Recall)
    axes[0].plot(epoch_col, df[map50_col], label='mAP50', color='blue', linewidth=2)
    axes[0].plot(epoch_col, df[map50_95_col], label='mAP50-95', color='cyan', linestyle='--')
    axes[0].plot(epoch_col, df[precision_col], label='Precision', color='green', alpha=0.7)
    axes[0].plot(epoch_col, df[recall_col], label='Recall', color='orange', alpha=0.7)
    axes[0].set_title('Đánh giá độ chính xác theo Epoch')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Giá trị (0.0 - 1.0)')
    axes[0].grid(True, linestyle=':', alpha=0.6)
    axes[0].legend()
    
    # Biểu đồ 2: Hàm mất mát (Loss)
    loss_cols = [c for c in df.columns if 'loss' in c.lower()]
    for col in loss_cols:
        axes[1].plot(epoch_col, df[col], label=col)
    axes[1].set_title('Diễn biến Hàm mất mát (Loss Curves)')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Loss Value')
    axes[1].grid(True, linestyle=':', alpha=0.6)
    axes[1].legend()

    plt.tight_layout()
    output_chart_path = os.path.join(run_dir, "bieu_do_danh_gia_tong_hop.png")
    plt.savefig(output_chart_path, dpi=300)
    print(f"✅ Đã biểu diễn và lưu biểu đồ tổng hợp tại: {output_chart_path}")
    plt.show()

if __name__ == "__main__":
    danh_gia_mo_hinh()