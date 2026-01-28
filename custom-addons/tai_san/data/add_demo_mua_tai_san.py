#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script thêm dữ liệu demo cho Mua tài sản trực tiếp vào PostgreSQL
Chạy: docker exec odoo_app_fitdnu python3 /mnt/custom-addons/tai_san/data/add_demo_mua_tai_san.py
"""

import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')

import odoo
from odoo import api, SUPERUSER_ID
from datetime import datetime, timedelta

# Kết nối database
config = odoo.tools.config
config['db_host'] = 'db'
config['db_port'] = '5432'
config['db_user'] = 'pthung4'
config['db_password'] = 'Luck2004!'
config['db_name'] = 'myodoo'

# Init registry
odoo.netsvc.init_logger()
from odoo.modules.registry import Registry
registry = Registry('myodoo')

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    print("=" * 60)
    print("THÊM DỮ LIỆU DEMO MUA TÀI SẢN")
    print("=" * 60)
    
    try:
        # Lấy nhân viên
        nhan_viens = env['nhan.su.nhan.vien'].search([], limit=3)
        if not nhan_viens:
            print("❌ Không có nhân viên trong hệ thống!")
            sys.exit(1)
        
        # Tạo hoặc lấy đề xuất và ứng tiền
        print("\n📝 Chuẩn bị dữ liệu đề xuất và ứng tiền...")
        ung_tiens = []
        
        for nv in nhan_viens:
            # Tạo đề xuất
            de_xuat = env['tai.san.de.xuat'].create({
                'nhan_vien_id': nv.id,
                'ngay_de_xuat': datetime.now().date() - timedelta(days=10),
                'ten_tai_san': 'Tài sản văn phòng',
                'loai_tai_san': 'van_phong',
                'ly_do': f'Đề xuất mua tài sản cho {nv.name}',
                'trang_thai': 'da_duyet'
            })
            print(f"✅ Tạo đề xuất: {de_xuat.name} - {nv.name}")
            
            # Tạo ứng tiền
            ung_tien = env['tai.san.ung.tien'].create({
                'de_xuat_id': de_xuat.id,
                'nhan_vien_id': nv.id,
                'ngay_ung': datetime.now().date() - timedelta(days=7),
                'so_tien_ung': 20000000,
                'ly_do': f'Ứng tiền mua tài sản cho {nv.name}',
                'trang_thai': 'da_duyet'
            })
            print(f"✅ Tạo ứng tiền: {ung_tien.name} - {ung_tien.so_tien_ung:,.0f}đ")
            ung_tiens.append(ung_tien)
        
        print(f"\n✅ Đã chuẩn bị {len(ung_tiens)} ứng tiền")
        
        # Dữ liệu demo
        demo_data = [
            {
                'ung_tien_id': ung_tiens[0].id,
                'ngay_mua': datetime.now().date() - timedelta(days=5),
                'nha_cung_cap': 'Công ty TNHH Công nghệ FPT',
                'dia_chi_ncc': '10 Phạm Văn Bạch, Cầu Giấy, Hà Nội',
                'so_dien_thoai_ncc': '024-7300-8866',
                'ten_tai_san': 'Laptop Dell Latitude 5520',
                'loai_tai_san': 'van_phong',
                'so_luong': 2,
                'don_gia': 18000000,
                'thue_vat': 10,
                'thoi_gian_bao_hanh': 24,
                'trang_thai': 'da_mua',
                'ghi_chu': 'Mua laptop cho nhân viên IT mới'
            },
            {
                'ung_tien_id': ung_tiens[1].id if len(ung_tiens) > 1 else ung_tiens[0].id,
                'ngay_mua': datetime.now().date() - timedelta(days=3),
                'nha_cung_cap': 'Công ty CP Thiết bị văn phòng Hòa Phát',
                'dia_chi_ncc': '15 Nguyễn Trãi, Thanh Xuân, Hà Nội',
                'so_dien_thoai_ncc': '024-3556-6789',
                'ten_tai_san': 'Bàn làm việc văn phòng',
                'loai_tai_san': 'van_phong',
                'so_luong': 5,
                'don_gia': 2500000,
                'thue_vat': 10,
                'thoi_gian_bao_hanh': 12,
                'trang_thai': 'da_tao_tai_san',
                'ghi_chu': 'Bàn làm việc cho phòng kinh doanh'
            },
            {
                'ung_tien_id': ung_tiens[2].id if len(ung_tiens) > 2 else ung_tiens[0].id,
                'ngay_mua': datetime.now().date() - timedelta(days=1),
                'nha_cung_cap': 'Showroom ô tô Hyundai Thành Công',
                'dia_chi_ncc': 'Giải Phóng, Hoàng Mai, Hà Nội',
                'so_dien_thoai_ncc': '1900-6600',
                'ten_tai_san': 'Xe ô tô Hyundai Accent',
                'loai_tai_san': 'phuong_tien',
                'so_luong': 1,
                'don_gia': 450000000,
                'thue_vat': 10,
                'thoi_gian_bao_hanh': 36,
                'trang_thai': 'nhap',
                'ghi_chu': 'Xe công ty cho giám đốc'
            }
        ]
        
        created_count = 0
        for data in demo_data:
            # Tạo bản ghi mua tài sản
            mua_ts = env['tai.san.mua.tai.san'].create(data)
            print(f"✅ Tạo: {mua_ts.name} - {mua_ts.ten_tai_san} ({mua_ts.trang_thai})")
            
            # Nếu đã tạo tài sản thì tạo luôn tài sản
            if data['trang_thai'] == 'da_tao_tai_san':
                for i in range(data['so_luong']):
                    # Generate mã tài sản
                    ma_tai_san = env['ir.sequence'].next_by_code('tai.san.tai.san') or f"TS-{i+1}"
                    
                    tai_san = env['tai.san.tai.san'].create({
                        'name': data['ten_tai_san'],
                        'ma_tai_san': ma_tai_san,
                        'loai_tai_san': data['loai_tai_san'],
                        'ngay_mua': data['ngay_mua'],
                        'nguyen_gia': data['don_gia'],
                        'mua_tai_san_id': mua_ts.id,
                        'de_xuat_id': mua_ts.de_xuat_id.id if mua_ts.de_xuat_id else False,
                        'tinh_trang': 'chua_mua',
                        'trang_thai': 'tot',
                        'ghi_chu': f'Mua từ NCC: {data["nha_cung_cap"]}, Hóa đơn: {mua_ts.name}. Chờ cấp phát.'
                    })
                    print(f"   → Tạo tài sản: {tai_san.ma_tai_san}")
            
            created_count += 1
        
        cr.commit()
        print(f"\n✅ Đã tạo {created_count} hóa đơn mua tài sản!")
        
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        cr.rollback()
    
print("=" * 60)
