# -*- coding: utf-8 -*-
# Script load demo data trong Odoo shell

# Ca làm việc
CaLamViec = env['nhan.su.ca.lam.viec']
ca1 = CaLamViec.create({
    'name': 'Ca hành chính',
    'ma_ca': 'CA001',
    'gio_bat_dau': 8.0,
    'gio_ket_thuc': 17.0,
    'loai_ca': 'hanh_chinh',
    'he_so_tang_ca': 1.5
})
ca2 = CaLamViec.create({
    'name': 'Ca sáng',
    'ma_ca': 'CA002',
    'gio_bat_dau': 6.0,
    'gio_ket_thuc': 14.0,
    'loai_ca': 'ca_sang',
    'he_so_tang_ca': 1.5
})
print(f"Created {len(ca1 + ca2)} ca làm việc")

# Phòng ban
PhongBan = env['nhan.su.phong.ban']
pb1 = PhongBan.create({'name': 'Phòng Kế toán', 'ma_phong_ban': 'PB001', 'mo_ta': 'Phòng kế toán tài chính'})
pb2 = PhongBan.create({'name': 'Phòng Nhân sự', 'ma_phong_ban': 'PB002', 'mo_ta': 'Phòng quản lý nhân sự'})
pb3 = PhongBan.create({'name': 'Phòng Kinh doanh', 'ma_phong_ban': 'PB003', 'mo_ta': 'Phòng kinh doanh và marketing'})
pb4 = PhongBan.create({'name': 'Phòng Kỹ thuật', 'ma_phong_ban': 'PB004', 'mo_ta': 'Phòng kỹ thuật và phát triển'})
print(f"Created {len(pb1 + pb2 + pb3 + pb4)} phòng ban")

# Chức vụ
ChucVu = env['nhan.su.chuc.vu']
cv1 = ChucVu.create({'name': 'Giám đốc', 'ma_chuc_vu': 'CV001', 'mo_ta': 'Giám đốc điều hành'})
cv2 = ChucVu.create({'name': 'Phó giám đốc', 'ma_chuc_vu': 'CV002', 'mo_ta': 'Phó giám đốc'})
cv3 = ChucVu.create({'name': 'Trưởng phòng', 'ma_chuc_vu': 'CV003', 'mo_ta': 'Trưởng phòng ban'})
cv4 = ChucVu.create({'name': 'Nhân viên', 'ma_chuc_vu': 'CV004', 'mo_ta': 'Nhân viên'})
print(f"Created {len(cv1 + cv2 + cv3 + cv4)} chức vụ")

# Nhân viên
NhanVien = env['nhan.su.nhan.vien']
nv_data = [
    {'name': 'Nguyễn Văn A', 'ma_nhan_vien': 'NV001', 'ngay_sinh': '1990-01-15', 'gioi_tinh': 'nam', 'so_dien_thoai': '0123456789', 'email': 'nguyenvana@company.com', 'dia_chi': 'Hà Nội', 'phong_ban_id': pb1.id, 'chuc_vu_id': cv1.id},
    {'name': 'Trần Thị B', 'ma_nhan_vien': 'NV002', 'ngay_sinh': '1992-05-20', 'gioi_tinh': 'nu', 'so_dien_thoai': '0987654321', 'email': 'tranthib@company.com', 'dia_chi': 'Hà Nội', 'phong_ban_id': pb2.id, 'chuc_vu_id': cv2.id},
    {'name': 'Lê Văn C', 'ma_nhan_vien': 'NV003', 'ngay_sinh': '1988-03-10', 'gioi_tinh': 'nam', 'so_dien_thoai': '0912345678', 'email': 'levanc@company.com', 'dia_chi': 'TP. Hồ Chí Minh', 'phong_ban_id': pb3.id, 'chuc_vu_id': cv3.id},
    {'name': 'Phạm Thị D', 'ma_nhan_vien': 'NV004', 'ngay_sinh': '1995-07-25', 'gioi_tinh': 'nu', 'so_dien_thoai': '0898765432', 'email': 'phamthid@company.com', 'dia_chi': 'Đà Nẵng', 'phong_ban_id': pb4.id, 'chuc_vu_id': cv3.id},
    {'name': 'Hoàng Văn E', 'ma_nhan_vien': 'NV005', 'ngay_sinh': '1993-11-30', 'gioi_tinh': 'nam', 'so_dien_thoai': '0834567890', 'email': 'hoangvane@company.com', 'dia_chi': 'Hải Phòng', 'phong_ban_id': pb1.id, 'chuc_vu_id': cv4.id},
    {'name': 'Ngô Thị F', 'ma_nhan_vien': 'NV006', 'ngay_sinh': '1996-02-14', 'gioi_tinh': 'nu', 'so_dien_thoai': '0876543210', 'email': 'ngothif@company.com', 'dia_chi': 'Cần Thơ', 'phong_ban_id': pb2.id, 'chuc_vu_id': cv4.id},
    {'name': 'Đỗ Văn G', 'ma_nhan_vien': 'NV007', 'ngay_sinh': '1991-08-18', 'gioi_tinh': 'nam', 'so_dien_thoai': '0945678901', 'email': 'dovang@company.com', 'dia_chi': 'Huế', 'phong_ban_id': pb3.id, 'chuc_vu_id': cv4.id},
    {'name': 'Vũ Thị H', 'ma_nhan_vien': 'NV008', 'ngay_sinh': '1994-12-05', 'gioi_tinh': 'nu', 'so_dien_thoai': '0923456789', 'email': 'vuthih@company.com', 'dia_chi': 'Vinh', 'phong_ban_id': pb4.id, 'chuc_vu_id': cv4.id},
    {'name': 'Bùi Văn I', 'ma_nhan_vien': 'NV009', 'ngay_sinh': '1997-04-22', 'gioi_tinh': 'nam', 'so_dien_thoai': '0867890123', 'email': 'buivani@company.com', 'dia_chi': 'Nha Trang', 'phong_ban_id': pb1.id, 'chuc_vu_id': cv4.id},
    {'name': 'Đinh Thị K', 'ma_nhan_vien': 'NV010', 'ngay_sinh': '1998-09-16', 'gioi_tinh': 'nu', 'so_dien_thoai': '0901234567', 'email': 'dinhthik@company.com', 'dia_chi': 'Vũng Tàu', 'phong_ban_id': pb3.id, 'chuc_vu_id': cv4.id}
]
nhan_vien_records = NhanVien.create(nv_data)
print(f"Created {len(nhan_vien_records)} nhân viên")

env.cr.commit()
print("\n=== Demo data loaded and committed successfully! ===")
