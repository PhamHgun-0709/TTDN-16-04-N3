#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script cập nhật tổng hợp công từ dữ liệu chấm công
Chạy: docker exec odoo_app_fitdnu python3 /mnt/custom-addons/nhan_su/data/update_tong_hop_cong.py
"""

import xmlrpc.client

# Kết nối đến Odoo
url = 'http://localhost:8069'
db = 'myodoo'
username = 'pthung0709@gmail.com'
password = 'Luck2004!'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

if uid:
    print(f"Đã kết nối thành công với user ID: {uid}")
    
    # Tìm tất cả tổng hợp công
    tong_hop_ids = models.execute_kw(db, uid, password,
        'nhan.su.tong.hop.cong', 'search', [[]])
    
    print(f"Tìm thấy {len(tong_hop_ids)} bản tổng hợp công")
    
    updated = 0
    failed = 0
    
    for tong_hop_id in tong_hop_ids:
        try:
            # Gọi method lấy dữ liệu chấm công
            result = models.execute_kw(db, uid, password,
                'nhan.su.tong.hop.cong', 'action_lay_du_lieu_cham_cong',
                [[tong_hop_id]])
            
            # Đọc lại để xem kết quả
            tong_hop = models.execute_kw(db, uid, password,
                'nhan.su.tong.hop.cong', 'read',
                [[tong_hop_id]], {'fields': ['name', 'nhan_vien_id', 'tong_cong', 'so_ngay_lam_viec']})
            
            if tong_hop:
                th = tong_hop[0]
                nv_name = th['nhan_vien_id'][1] if th['nhan_vien_id'] else 'N/A'
                print(f"✓ {th['name']} - {nv_name}: {th['tong_cong']} công, {th['so_ngay_lam_viec']} ngày")
                updated += 1
        except Exception as e:
            print(f"✗ Lỗi ID {tong_hop_id}: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Hoàn tất! Cập nhật: {updated}, Lỗi: {failed}")
else:
    print("Không thể kết nối đến Odoo. Kiểm tra username/password.")
