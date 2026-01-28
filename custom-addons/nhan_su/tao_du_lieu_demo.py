#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script tạo dữ liệu demo cho module nhân sự
Chạy trong Odoo shell: ./odoo-bin shell -c odoo.conf -d btap
Sau đó: exec(open('custom-addons/nhan_su/tao_du_lieu_demo.py').read())
"""

import random
from datetime import datetime, timedelta

# Lấy environment
env = globals().get('env')
if not env:
    print("ERROR: Script này phải chạy trong Odoo shell!")
    print("Cách chạy:")
    print("  docker exec -it odoo_app_fitdnu odoo shell -c /etc/odoo/odoo.conf -d btap")
    print("  >>> exec(open('/mnt/custom-addons/nhan_su/tao_du_lieu_demo.py').read())")
    exit()

print("\n" + "="*60)
print("TẠO DỮ LIỆU DEMO CHO MODULE NHÂN SỰ")
print("="*60 + "\n")

# Lấy tất cả nhân viên đang làm việc
nhan_viens = env['nhan.su.nhan.vien'].search([('trang_thai', '=', 'dang_lam')])
if not nhan_viens:
    print("CẢNH BÁO: Không tìm thấy nhân viên nào đang làm việc!")
    print("Vui lòng tạo nhân viên trước.")
    exit()

print(f"✓ Tìm thấy {len(nhan_viens)} nhân viên đang làm việc")

# Lấy hoặc tạo ca làm việc
ca_lam_viec = env['nhan.su.ca.lam.viec'].search([], limit=1)
if not ca_lam_viec:
    print("\n→ Tạo ca làm việc mặc định...")
    ca_lam_viec = env['nhan.su.ca.lam.viec'].create({
        'name': 'Ca hành chính',
        'gio_bat_dau': 8.0,  # 8:00
        'gio_ket_thuc': 17.0,  # 17:00
        'so_gio_chuan': 8.0,
        'he_so_tang_ca': 1.5,
    })
    print(f"  ✓ Đã tạo ca làm việc: {ca_lam_viec.name}")
else:
    print(f"✓ Sử dụng ca làm việc: {ca_lam_viec.name}")

# Cập nhật ca làm việc cho nhân viên chưa có
for nv in nhan_viens:
    if not nv.ca_lam_viec_id:
        nv.ca_lam_viec_id = ca_lam_viec.id

# Tháng hiện tại
today = datetime.now()
thang = str(today.month)
nam = str(today.year)

print(f"\n→ Tạo dữ liệu chấm công cho tháng {thang}/{nam}...")

# Xóa dữ liệu cũ (nếu có)
cham_cong_cu = env['nhan.su.cham.cong'].search([
    ('thang', '=', thang),
    ('nam', '=', nam)
])
if cham_cong_cu:
    print(f"  ⚠ Xóa {len(cham_cong_cu)} bản ghi chấm công cũ...")
    cham_cong_cu.unlink()

# Tạo chấm công cho 20 ngày làm việc
so_ngay = 20
cham_cong_created = 0

for nhan_vien in nhan_viens:
    for i in range(so_ngay):
        ngay = datetime(int(nam), int(thang), i+1)
        
        # Random giờ vào/ra (có đôi khi đi muộn/về sớm)
        gio_vao = 8.0 + random.uniform(-0.5, 0.5)  # 7:30 - 8:30
        gio_ra = 17.0 + random.uniform(-0.5, 1.0)  # 16:30 - 18:00
        
        # Đôi khi nghỉ
        if random.random() < 0.05:  # 5% nghỉ
            trang_thai = random.choice(['nghi_phep', 'nghi_khong_phep', 'vang'])
            gio_vao = 0
            gio_ra = 0
        else:
            trang_thai = 'du_cong'
        
        vals = {
            'nhan_vien_id': nhan_vien.id,
            'ca_lam_viec_id': ca_lam_viec.id,
            'ngay_cham_cong': ngay,
            'gio_vao': gio_vao,
            'gio_ra': gio_ra,
            'loai_ngay': 'binh_thuong',
        }
        
        env['nhan.su.cham.cong'].create(vals)
        cham_cong_created += 1

print(f"  ✓ Đã tạo {cham_cong_created} bản ghi chấm công")

# Tạo tổng hợp công
print(f"\n→ Tạo tổng hợp công cho tháng {thang}/{nam}...")

tong_hop_cu = env['nhan.su.tong.hop.cong'].search([
    ('thang', '=', thang),
    ('nam', '=', nam)
])
if tong_hop_cu:
    print(f"  ⚠ Xóa {len(tong_hop_cu)} bản ghi tổng hợp công cũ...")
    tong_hop_cu.unlink()

tong_hop_created = 0
for nhan_vien in nhan_viens:
    # Lấy chấm công của nhân viên này
    cham_congs = env['nhan.su.cham.cong'].search([
        ('nhan_vien_id', '=', nhan_vien.id),
        ('thang', '=', thang),
        ('nam', '=', nam)
    ])
    
    if cham_congs:
        tong_hop = env['nhan.su.tong.hop.cong'].create({
            'nhan_vien_id': nhan_vien.id,
            'thang': thang,
            'nam': nam,
            'cham_cong_ids': [(6, 0, cham_congs.ids)],
            'cong_chuan_thang': 26.0,
        })
        
        # Xác nhận luôn
        tong_hop.action_xac_nhan()
        tong_hop_created += 1

print(f"  ✓ Đã tạo và xác nhận {tong_hop_created} bản tổng hợp công")

# Commit changes
env.cr.commit()

print("\n" + "="*60)
print("✓ HOÀN TẤT!")
print("="*60)
print(f"\nĐã tạo dữ liệu demo cho tháng {thang}/{nam}:")
print(f"  • {len(nhan_viens)} nhân viên")
print(f"  • {cham_cong_created} bản ghi chấm công")
print(f"  • {tong_hop_created} bản tổng hợp công (đã xác nhận)")
print("\nBạn có thể:")
print("  1. Vào 'Chấm công > Bảng chấm công' để xem dữ liệu")
print("  2. Vào 'Chấm công > Tổng hợp công' để xem tổng hợp")
print("  3. Vào 'Bảng lương' và bấm 'Lấy dữ liệu' để tính lương")
print("")
