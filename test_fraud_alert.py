#!/usr/bin/env python3
"""Test fraud detection với giao dịch nghi ngờ mới"""

import sys
import os
from datetime import date, timedelta

# Add Odoo to path
sys.path.insert(0, '/usr/lib/python3/dist-packages')
os.environ['ODOO_RC'] = '/etc/odoo/odoo.conf'

import odoo
from odoo import api

def main():
    db_name = 'myodoo'
    
    print("\n" + "="*70)
    print("🧪 TEST: TẠO GIAO DỊCH NGHI NGỜ VÀ PHÁT HIỆN")
    print("="*70 + "\n")
    
    # Initialize Odoo
    odoo.tools.config.parse_config(['-c', '/etc/odoo/odoo.conf', '-d', db_name])
    
    with odoo.api.Environment.manage():
        registry = odoo.registry(db_name)
        
        with registry.cursor() as cr:
            uid = odoo.SUPERUSER_ID
            ctx = odoo.api.Environment(cr, uid, {})['res.users'].context_get()
            env = odoo.api.Environment(cr, uid, ctx)
            
            # 1. Tạo partner test
            print("📝 Tạo đối tượng test...")
            Partner = env['res.partner']
            partner = Partner.create({
                'name': 'TEST - Người chi nghi ngờ'
            })
            print(f"   ✓ Partner ID: {partner.id} - {partner.name}")
            
            # 2. Tạo phiếu chi NGHI NGỜ
            print("\n💰 Tạo phiếu chi nghi ngờ...")
            PhieuChi = env['tai.chinh.ke.toan.phieu.chi']
            
            phieu = PhieuChi.create({
                'doi_tuong_id': partner.id,
                'so_tien': 88888888.0,  # Số tròn 88 triệu - rất nghi ngờ
                'ly_do_chi': 'Thanh toán khẩn cấp cuối tuần - SOS',
                'ngay_chi': date.today(),
                'nguoi_lap_id': 2,
                'trang_thai': 'da_chi'
            })
            
            cr.commit()
            
            print(f"   ✓ Phiếu chi: PC{phieu.id:04d}")
            print(f"   • Số tiền: {phieu.so_tien:,.0f} VNĐ")
            print(f"   • Lý do: {phieu.ly_do_chi}")
            print(f"   • Ngày: {phieu.ngay_chi}")
            
            # 3. Chạy detection ngay
            print("\n🔍 Chạy AI detection...")
            CanhBao = env['tai.chinh.ke.toan.canh.bao.gian.lan']
            canh_bao_model = CanhBao.create({})  # Tạo instance để gọi method
            
            # Count alerts before
            alerts_before = CanhBao.search_count([])
            
            # Run detection
            canh_bao_model.phat_hien_gian_lan_tu_dong()
            
            # Count alerts after
            alerts_after = CanhBao.search_count([])
            new_alerts = alerts_after - alerts_before
            
            print(f"\n📊 Kết quả:")
            print(f"   • Cảnh báo trước: {alerts_before}")
            print(f"   • Cảnh báo sau: {alerts_after}")
            print(f"   • Cảnh báo MỚI: {new_alerts}")
            
            if new_alerts > 0:
                print("\n🚨 CẢNH BÁO MỚI NHẤT:")
                latest_alerts = CanhBao.search([], order='id desc', limit=5)
                for i, alert in enumerate(latest_alerts, 1):
                    print(f"\n   {i}. {alert.name}")
                    print(f"      • Mức độ: {dict(alert._fields['muc_do_nguy_hiem'].selection).get(alert.muc_do_nguy_hiem)}")
                    print(f"      • Điểm nghi ngờ: {alert.diem_nghi_ngo}")
                    print(f"      • Hybrid score: {alert.hybrid_score:.1f}")
                    print(f"      • Method: {alert.detection_method}")
                    if alert.mo_ta:
                        print(f"      • Mô tả: {alert.mo_ta[:100]}...")
            
            print("\n" + "="*70)
            print("✅ HOÀN TẤT!")
            print("="*70)

if __name__ == '__main__':
    main()
