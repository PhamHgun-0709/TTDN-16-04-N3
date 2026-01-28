#!/usr/bin/env python3
"""Test tạo giao dịch mới và kiểm tra tự động cảnh báo"""

import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')

import odoo
from datetime import date
from odoo import api

# Parse config
odoo.tools.config.parse_config(['-c', '/etc/odoo/odoo.conf', '-d', 'myodoo'])

# Get registry
with odoo.sql_db.db_connect('myodoo').cursor() as cr:
    env = api.Environment(cr, odoo.SUPERUSER_ID, {})
    
    print("\n" + "="*70)
    print("🧪 TEST: TẠO GIAO DỊCH MỚI VÀ KIỂM TRA CẢNH BÁO TỰ ĐỘNG")
    print("="*70 + "\n")
    
    # Tạo partner test
    partner = env['res.partner'].create({'name': 'TEST - Giao dịch đáng ngờ'})
    print(f"📝 Tạo đối tượng: {partner.name} (ID: {partner.id})")
    
    # Tạo phiếu chi NGHI NGỜ
    phieu = env['tai.chinh.ke.toan.phieu.chi'].create({
        'doi_tuong_id': partner.id,
        'so_tien': 88888888.0,  # 88 triệu - số tròn nghi ngờ
        'ly_do_chi': 'Chi tiêu khẩn cấp ngày nghỉ',
        'ngay_chi': date.today(),
        'nguoi_lap_id': 2,
        'trang_thai': 'da_chi'
    })
    
    print(f"💰 Tạo phiếu chi: PC{phieu.id:04d}")
    print(f"   • Số tiền: {phieu.so_tien:,.0f} VNĐ (SỐ TRÒN)")
    print(f"   • Lý do: {phieu.ly_do_chi}")
    print(f"   • Ngày: {phieu.ngay_chi}")
    
    cr.commit()
    
    # Đếm cảnh báo hiện tại
    CanhBao = env['tai.chinh.ke.toan.canh.bao.gian.lan']
    count_before = CanhBao.search_count([])
    print(f"\n🔍 Chạy AI detection...")
    print(f"   Cảnh báo hiện có: {count_before}")
    
    # Chạy detection - gọi trực tiếp method trên model (không cần create instance)
    CanhBao.phat_hien_gian_lan_tu_dong()
    
    # Kiểm tra kết quả
    count_after = CanhBao.search_count([])
    new_alerts_count = count_after - count_before
    
    print(f"\n📊 KẾT QUẢ:")
    print(f"   • Cảnh báo trước: {count_before}")
    print(f"   • Cảnh báo sau: {count_after}")
    print(f"   • ⭐ CẢNH BÁO MỚI: {new_alerts_count}")
    
    if new_alerts_count > 0:
        print(f"\n{'='*70}")
        print("🚨 CẢNH BÁO TỰ ĐỘNG PHÁT HIỆN:")
        print("="*70 + "\n")
        
        alerts = CanhBao.search(
            [], order='id desc', limit=min(5, new_alerts_count)
        )
        
        muc_do_map = {
            'thap': 'Thấp',
            'trung_binh': 'Trung bình',
            'cao': 'Cao',
            'nghiem_trong': 'Nghiêm trọng'
        }
        
        for i, alert in enumerate(alerts, 1):
            print(f"{i}. [{alert.ma_canh_bao}] {alert.name}")
            print(f"   🎯 Mức độ: {muc_do_map.get(alert.muc_do_nguy_hiem, alert.muc_do_nguy_hiem)}")
            print(f"   📊 Hybrid Score: {alert.hybrid_score:.1f} (Rule 40% + ML 60%)")
            print(f"   🤖 Detection Method: {alert.detection_method.upper()}")
            print(f"   🔬 ML Anomaly Score: {alert.ml_anomaly_score:.3f}")
            print(f"   ✅ ML Confidence: {alert.ml_confidence:.1f}%")
            print(f"   💡 Điểm nghi ngờ: {alert.diem_nghi_ngo}")
            if alert.mo_ta:
                print(f"   📝 {alert.mo_ta[:120]}...")
            print()
        
        print("="*70)
        print("✅ HỆ THỐNG ĐÃ TỰ ĐỘNG PHÁT HIỆN GIAN LẬN!")
        print("="*70)
        print("\n💡 Cách xem trong Odoo UI:")
        print("   👉 Menu: Tài chính > Cảnh báo gian lận")
        print(f"   👉 Tìm mã: {alerts[0].ma_canh_bao}")
        
    else:
        print("\n⚠️  Không có cảnh báo mới")
        print("   (Giao dịch không đủ nghi ngờ hoặc đã có cảnh báo tương tự)\n")
    
    print("\n" + "="*70)
    print("🎓 GIẢI THÍCH:")
    print("="*70)
    print("""
    ✅ TỰ ĐỘNG theo lịch:
       • Mỗi ngày 1 lần - Cron job phát hiện gian lận
       • Mỗi 7 ngày - Tự huấn luyện lại ML model
    
    ⚡ MANUAL khi cần:
       • Chạy: docker exec odoo_app_fitdnu python3 /auto_train.py
       • Hoặc trong Odoo UI: Tài chính > Cảnh báo > Action menu
    
    🤖 AI HYBRID DETECTION:
       • Rule-based: Phát hiện theo quy tắc (40%)
       • ML Isolation Forest: Phát hiện bất thường (60%)
       • Kết hợp: Weighted hybrid score
    """)
