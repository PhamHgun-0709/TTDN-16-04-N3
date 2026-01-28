#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script để load demo data vào Odoo"""

import xmlrpc.client

# Kết nối Odoo
url = "http://localhost:8069"
db = "myodoo"
username = "pthung4"
password = "Luck2004!"

# Authenticate
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
print(f"Authenticated as user ID: {uid}")

if uid:
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    # Load demo data cho module nhan_su
    print("\n=== Loading demo data for nhan_su module ===")
    
    # 1. Ca làm việc
    print("\n1. Tạo ca làm việc...")
    ca_ids = models.execute_kw(db, uid, password, 'nhan.su.ca.lam.viec', 'create', [[
        {
            'name': 'Ca hành chính',
            'ma_ca': 'CA001',
            'gio_bat_dau': 8.0,
            'gio_ket_thuc': 17.0,
            'loai_ca': 'hanh_chinh',
            'he_so_tang_ca': 1.5
        },
        {
            'name': 'Ca sáng',
            'ma_ca': 'CA002',
            'gio_bat_dau': 6.0,
            'gio_ket_thuc': 14.0,
            'loai_ca': 'ca_sang',
            'he_so_tang_ca': 1.5
        }
    ]])
    print(f"Created {len(ca_ids)} ca làm việc")
    
    # 2. Phòng ban
    print("\n2. Tạo phòng ban...")
    phong_ban_ids = models.execute_kw(db, uid, password, 'nhan.su.phong.ban', 'create', [[
        {
            'name': 'Phòng Kế toán',
            'ma_phong_ban': 'PB001',
            'mo_ta': 'Phòng kế toán tài chính'
        },
        {
            'name': 'Phòng Nhân sự',
            'ma_phong_ban': 'PB002',
            'mo_ta': 'Phòng quản lý nhân sự'
        },
        {
            'name': 'Phòng Kinh doanh',
            'ma_phong_ban': 'PB003',
            'mo_ta': 'Phòng kinh doanh và marketing'
        },
        {
            'name': 'Phòng Kỹ thuật',
            'ma_phong_ban': 'PB004',
            'mo_ta': 'Phòng kỹ thuật và phát triển'
        }
    ]])
    print(f"Created {len(phong_ban_ids)} phòng ban")
    
    # 3. Chức vụ
    print("\n3. Tạo chức vụ...")
    chuc_vu_ids = models.execute_kw(db, uid, password, 'nhan.su.chuc.vu', 'create', [[
        {
            'name': 'Giám đốc',
            'ma_chuc_vu': 'CV001',
            'mo_ta': 'Giám đốc điều hành'
        },
        {
            'name': 'Phó giám đốc',
            'ma_chuc_vu': 'CV002',
            'mo_ta': 'Phó giám đốc'
        },
        {
            'name': 'Trưởng phòng',
            'ma_chuc_vu': 'CV003',
            'mo_ta': 'Trưởng phòng ban'
        },
        {
            'name': 'Nhân viên',
            'ma_chuc_vu': 'CV004',
            'mo_ta': 'Nhân viên'
        }
    ]])
    print(f"Created {len(chuc_vu_ids)} chức vụ")
    
    # 4. Nhân viên (10 nhân viên mẫu)
    print("\n4. Tạo nhân viên...")
    nhan_vien_data = [
        {
            'name': 'Nguyễn Văn A',
            'ma_nhan_vien': 'NV001',
            'ngay_sinh': '1990-01-15',
            'gioi_tinh': 'nam',
            'so_dien_thoai': '0123456789',
            'email': 'nguyenvana@company.com',
            'dia_chi': 'Hà Nội',
            'phong_ban_id': phong_ban_ids[0],  # Kế toán
            'chuc_vu_id': chuc_vu_ids[0],  # Giám đốc
            'luong_co_ban': 20000000
        },
        {
            'name': 'Trần Thị B',
            'ma_nhan_vien': 'NV002',
            'ngay_sinh': '1992-05-20',
            'gioi_tinh': 'nu',
            'so_dien_thoai': '0987654321',
            'email': 'tranthib@company.com',
            'dia_chi': 'Hà Nội',
            'phong_ban_id': phong_ban_ids[1],  # Nhân sự
            'chuc_vu_id': chuc_vu_ids[1],  # Phó giám đốc
            'luong_co_ban': 15000000
        },
        {
            'name': 'Lê Văn C',
            'ma_nhan_vien': 'NV003',
            'ngay_sinh': '1988-03-10',
            'gioi_tinh': 'nam',
            'so_dien_thoai': '0912345678',
            'email': 'levanc@company.com',
            'dia_chi': 'TP. Hồ Chí Minh',
            'phong_ban_id': phong_ban_ids[2],  # Kinh doanh
            'chuc_vu_id': chuc_vu_ids[2],  # Trưởng phòng
            'luong_co_ban': 12000000
        },
        {
            'name': 'Phạm Thị D',
            'ma_nhan_vien': 'NV004',
            'ngay_sinh': '1995-07-25',
            'gioi_tinh': 'nu',
            'so_dien_thoai': '0898765432',
            'email': 'phamthid@company.com',
            'dia_chi': 'Đà Nẵng',
            'phong_ban_id': phong_ban_ids[3],  # Kỹ thuật
            'chuc_vu_id': chuc_vu_ids[2],  # Trưởng phòng
            'luong_co_ban': 12000000
        },
        {
            'name': 'Hoàng Văn E',
            'ma_nhan_vien': 'NV005',
            'ngay_sinh': '1993-11-30',
            'gioi_tinh': 'nam',
            'so_dien_thoai': '0834567890',
            'email': 'hoangvane@company.com',
            'dia_chi': 'Hải Phòng',
            'phong_ban_id': phong_ban_ids[0],  # Kế toán
            'chuc_vu_id': chuc_vu_ids[3],  # Nhân viên
            'luong_co_ban': 8000000
        },
        {
            'name': 'Ngô Thị F',
            'ma_nhan_vien': 'NV006',
            'ngay_sinh': '1996-02-14',
            'gioi_tinh': 'nu',
            'so_dien_thoai': '0876543210',
            'email': 'ngothif@company.com',
            'dia_chi': 'Cần Thơ',
            'phong_ban_id': phong_ban_ids[1],  # Nhân sự
            'chuc_vu_id': chuc_vu_ids[3],  # Nhân viên
            'luong_co_ban': 7500000
        },
        {
            'name': 'Đỗ Văn G',
            'ma_nhan_vien': 'NV007',
            'ngay_sinh': '1991-08-18',
            'gioi_tinh': 'nam',
            'so_dien_thoai': '0945678901',
            'email': 'dovang@company.com',
            'dia_chi': 'Huế',
            'phong_ban_id': phong_ban_ids[2],  # Kinh doanh
            'chuc_vu_id': chuc_vu_ids[3],  # Nhân viên
            'luong_co_ban': 9000000
        },
        {
            'name': 'Vũ Thị H',
            'ma_nhan_vien': 'NV008',
            'ngay_sinh': '1994-12-05',
            'gioi_tinh': 'nu',
            'so_dien_thoai': '0923456789',
            'email': 'vuthih@company.com',
            'dia_chi': 'Vinh',
            'phong_ban_id': phong_ban_ids[3],  # Kỹ thuật
            'chuc_vu_id': chuc_vu_ids[3],  # Nhân viên
            'luong_co_ban': 10000000
        },
        {
            'name': 'Bùi Văn I',
            'ma_nhan_vien': 'NV009',
            'ngay_sinh': '1997-04-22',
            'gioi_tinh': 'nam',
            'so_dien_thoai': '0867890123',
            'email': 'buivani@company.com',
            'dia_chi': 'Nha Trang',
            'phong_ban_id': phong_ban_ids[0],  # Kế toán
            'chuc_vu_id': chuc_vu_ids[3],  # Nhân viên
            'luong_co_ban': 7000000
        },
        {
            'name': 'Đinh Thị K',
            'ma_nhan_vien': 'NV010',
            'ngay_sinh': '1998-09-16',
            'gioi_tinh': 'nu',
            'so_dien_thoai': '0901234567',
            'email': 'dinhthik@company.com',
            'dia_chi': 'Vũng Tàu',
            'phong_ban_id': phong_ban_ids[2],  # Kinh doanh
            'chuc_vu_id': chuc_vu_ids[3],  # Nhân viên
            'luong_co_ban': 8500000
        }
    ]
    
    nhan_vien_ids = models.execute_kw(db, uid, password, 'nhan.su.nhan.vien', 'create', [nhan_vien_data])
    print(f"Created {len(nhan_vien_ids)} nhân viên")
    
    print("\n=== Demo data loaded successfully! ===")
    print(f"Total records created:")
    print(f"- Ca làm việc: {len(ca_ids)}")
    print(f"- Phòng ban: {len(phong_ban_ids)}")
    print(f"- Chức vụ: {len(chuc_vu_ids)}")
    print(f"- Nhân viên: {len(nhan_vien_ids)}")
else:
    print("Authentication failed!")
