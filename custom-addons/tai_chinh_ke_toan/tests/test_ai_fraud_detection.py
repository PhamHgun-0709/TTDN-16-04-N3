#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test AI Fraud Detection
Chạy trong Odoo shell: ./odoo-bin shell -c odoo.conf -d your_database
"""

import logging

_logger = logging.getLogger(__name__)

def test_ml_fraud_detection(env):
    """Test toàn bộ hệ thống AI Fraud Detection"""
    
    print("\n" + "="*70)
    print("🤖 AI FRAUD DETECTION - TEST SUITE")
    print("="*70 + "\n")
    
    model = env['tai.chinh.ke.toan.canh.bao.gian.lan']
    PhieuChi = env['tai.chinh.ke.toan.phieu.chi']
    
    # 1. Kiểm tra số lượng dữ liệu
    print("📊 [1/5] Kiểm tra dữ liệu...")
    total_phieu = PhieuChi.search_count([('trang_thai', '=', 'da_chi')])
    print(f"   ✓ Tổng số phiếu chi: {total_phieu}")
    
    if total_phieu < 50:
        print(f"   ⚠️  CẢNH BÁO: Chỉ có {total_phieu} phiếu chi (cần >= 50 để train ML)")
    else:
        print(f"   ✓ Đủ dữ liệu để train ML model")
    
    # 2. Huấn luyện model
    print("\n🧠 [2/5] Huấn luyện ML Model...")
    try:
        result = model.train_ml_model(min_samples=30)
        if result:
            print("   ✓ Huấn luyện thành công!")
            
            # Lấy thông tin model
            model_data = model._load_ml_model()
            if model_data:
                print(f"   ✓ Model info:")
                print(f"      - Trained samples: {model_data['n_samples']}")
                print(f"      - Features: {', '.join(model_data['feature_names'])}")
                print(f"      - Trained date: {model_data['trained_date']}")
        else:
            print("   ✗ Không thể huấn luyện (không đủ dữ liệu)")
    except Exception as e:
        print(f"   ✗ Lỗi khi huấn luyện: {e}")
    
    # 3. Chạy phát hiện gian lận
    print("\n🔍 [3/5] Phát hiện gian lận (Hybrid)...")
    try:
        model.phat_hien_gian_lan_tu_dong()
        print("   ✓ Phát hiện hoàn tất!")
    except Exception as e:
        print(f"   ✗ Lỗi khi phát hiện: {e}")
    
    # 4. Thống kê kết quả
    print("\n📈 [4/5] Thống kê cảnh báo...")
    
    # Tổng cảnh báo
    total_alerts = model.search_count([])
    print(f"   ✓ Tổng số cảnh báo: {total_alerts}")
    
    # Theo phương pháp
    rule_based = model.search_count([('detection_method', '=', 'rule')])
    ml_based = model.search_count([('detection_method', '=', 'ml')])
    hybrid = model.search_count([('detection_method', '=', 'hybrid')])
    
    print(f"   ✓ Phân loại theo phương pháp:")
    print(f"      - Rule-based: {rule_based}")
    print(f"      - Machine Learning: {ml_based}")
    print(f"      - Hybrid: {hybrid}")
    
    # Theo mức độ
    nghiem_trong = model.search_count([('muc_do_nguy_hiem', '=', 'nghiem_trong')])
    cao = model.search_count([('muc_do_nguy_hiem', '=', 'cao')])
    trung_binh = model.search_count([('muc_do_nguy_hiem', '=', 'trung_binh')])
    thap = model.search_count([('muc_do_nguy_hiem', '=', 'thap')])
    
    print(f"   ✓ Phân loại theo mức độ:")
    print(f"      - Nghiêm trọng: {nghiem_trong}")
    print(f"      - Cao: {cao}")
    print(f"      - Trung bình: {trung_binh}")
    print(f"      - Thấp: {thap}")
    
    # 5. Hiển thị top 5 cảnh báo nguy hiểm nhất
    print("\n⚠️  [5/5] Top 5 cảnh báo nguy hiểm nhất:")
    top_alerts = model.search([], order='hybrid_score desc', limit=5)
    
    if top_alerts:
        for i, alert in enumerate(top_alerts, 1):
            print(f"\n   {i}. {alert.name}")
            print(f"      - Mức độ: {dict(alert._fields['muc_do_nguy_hiem'].selection).get(alert.muc_do_nguy_hiem)}")
            print(f"      - Hybrid Score: {alert.hybrid_score:.2f}")
            print(f"      - Rule Score: {alert.diem_nghi_ngo:.2f}")
            print(f"      - ML Score: {alert.ml_anomaly_score:.2f} (confidence: {(alert.ml_confidence or 0)*100:.1f}%)")
            print(f"      - Phương pháp: {dict(alert._fields['detection_method'].selection).get(alert.detection_method)}")
            print(f"      - Trạng thái: {dict(alert._fields['trang_thai'].selection).get(alert.trang_thai)}")
    else:
        print("   (Chưa có cảnh báo nào)")
    
    print("\n" + "="*70)
    print("✅ TEST HOÀN TẤT!")
    print("="*70 + "\n")
    
    return True


def demo_create_suspicious_transactions(env):
    """Tạo các giao dịch nghi ngờ để test"""
    
    print("\n" + "="*70)
    print("🎭 TẠO DỮ LIỆU DEMO - Giao dịch nghi ngờ")
    print("="*70 + "\n")
    
    PhieuChi = env['tai.chinh.ke.toan.phieu.chi']
    
    from datetime import datetime, timedelta
    import random
    
    # Lấy ngày hiện tại
    today = datetime.now().date()
    
    # Tạo các giao dịch nghi ngờ
    suspicious_cases = [
        {
            'name': 'Demo - Số tiền bất thường cao',
            'so_tien': 500000000,  # 500M
            'ngay_chi': today - timedelta(days=1),
            'nguoi_chi': 'Nguyễn Văn A',
            'ly_do': 'Chi phí đột xuất',
        },
        {
            'name': 'Demo - Số tiền tròn triệu',
            'so_tien': 10000000,  # 10M tròn
            'ngay_chi': today - timedelta(days=2),
            'nguoi_chi': 'Trần Thị B',
            'ly_do': 'Thanh toán dịch vụ',
        },
        {
            'name': 'Demo - Cuối tuần nghi ngờ',
            'so_tien': 75000000,
            'ngay_chi': today - timedelta(days=(today.weekday() - 5) % 7),  # Thứ 7
            'nguoi_chi': 'Lê Văn C',
            'ly_do': 'Tạm ứng',
        },
        {
            'name': 'Demo - Cuối tháng + số tròn',
            'so_tien': 30000000,
            'ngay_chi': today.replace(day=28),
            'nguoi_chi': 'Phạm Thị D',
            'ly_do': 'Chi phí văn phòng',
        },
    ]
    
    created = []
    for case in suspicious_cases:
        try:
            phieu = PhieuChi.create({
                'name': case['name'],
                'so_tien': case['so_tien'],
                'ngay_chi': case['ngay_chi'],
                'nguoi_chi': case['nguoi_chi'],
                'ly_do': case['ly_do'],
                'trang_thai': 'da_chi',
            })
            created.append(phieu)
            print(f"✓ Tạo: {case['name']} - {case['so_tien']:,.0f} VNĐ")
        except Exception as e:
            print(f"✗ Lỗi: {case['name']} - {e}")
    
    print(f"\n✅ Đã tạo {len(created)} giao dịch demo")
    print("="*70 + "\n")
    
    return created


# ============================================================================
# HƯỚNG DẪN SỬ DỤNG
# ============================================================================
"""
1. Vào Odoo shell:
   ./odoo-bin shell -c odoo.conf -d your_database

2. Load script:
   exec(open('custom-addons/tai_chinh_ke_toan/tests/test_ai_fraud_detection.py').read())

3. Chạy test:
   test_ml_fraud_detection(env)

4. Hoặc tạo demo data trước:
   demo_create_suspicious_transactions(env)
   test_ml_fraud_detection(env)
"""

if __name__ == '__main__':
    print(__doc__)
