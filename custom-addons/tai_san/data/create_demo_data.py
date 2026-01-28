# Python script to create demo data for tai_san
# Run in odoo shell

import datetime

# Check existing data
print(f"Nhân viên hiện có: {env['nhan.su.nhan.vien'].search_count([])}")
print(f"Phòng ban hiện có: {env['nhan.su.phong.ban'].search_count([])}")

nv_ids = env['nhan.su.nhan.vien'].search([], limit=10)
pb_ids = env['nhan.su.phong.ban'].search([], limit=5)

print("\nBắt đầu tạo demo data...")

# 1. TÀI SẢN
tai_san_vals = [
    {
        'name': 'Laptop Dell Latitude 5520',
        'ma_tai_san': 'TS-IT-001',
        'loai_tai_san': 'may_moc',
        'ngay_mua': '2024-03-15',
        'nguyen_gia': 25000000,
        'thoi_gian_khau_hao': 36,
        'ty_le_khau_hao': 20,
        'nhan_vien_id': nv_ids[0].id if nv_ids else False,
        'phong_ban_id': pb_ids[0].id if pb_ids else False,
        'vi_tri': 'Văn phòng tầng 2',
        'tinh_trang': 'dang_su_dung',
        'trang_thai': 'tot',
    },
    {
        'name': 'Laptop HP ProBook 450 G8',
        'ma_tai_san': 'TS-IT-002',
        'loai_tai_san': 'may_moc',
        'ngay_mua': '2024-04-20',
        'nguyen_gia': 22000000,
        'thoi_gian_khau_hao': 36,
        'ty_le_khau_hao': 15,
        'nhan_vien_id': nv_ids[2].id if len(nv_ids) > 2 else False,
        'phong_ban_id': pb_ids[1].id if len(pb_ids) > 1 else False,
        'vi_tri': 'Phòng kế toán',
        'tinh_trang': 'dang_su_dung',
        'trang_thai': 'tot',
    },
    {
        'name': 'Xe ô tô Toyota Vios 1.5E MT',
        'ma_tai_san': 'TS-PT-001',
        'loai_tai_san': 'phuong_tien',
        'ngay_mua': '2023-06-10',
        'nguyen_gia': 530000000,
        'thoi_gian_khau_hao': 120,
        'ty_le_khau_hao': 15,
        'nhan_vien_id': nv_ids[4].id if len(nv_ids) > 4 else False,
        'phong_ban_id': pb_ids[3].id if len(pb_ids) > 3 else False,
        'vi_tri': 'Bãi xe công ty',
        'tinh_trang': 'dang_su_dung',
        'trang_thai': 'tot',
    },
    {
        'name': 'Máy photocopy Canon iR2625i',
        'ma_tai_san': 'TS-IT-005',
        'loai_tai_san': 'may_moc',
        'ngay_mua': '2023-11-20',
        'nguyen_gia': 35000000,
        'thoi_gian_khau_hao': 60,
        'ty_le_khau_hao': 30,
        'vi_tri': 'Khu vực chung tầng 1',
        'tinh_trang': 'dang_su_dung',
        'trang_thai': 'bao_tri',
        'ghi_chu': 'Đang bảo trì định kỳ',
    },
    {
        'name': 'Điều hòa Daikin FTKA50VAVMV',
        'ma_tai_san': 'TS-VP-003',
        'loai_tai_san': 'van_phong',
        'ngay_mua': '2023-08-15',
        'nguyen_gia': 18000000,
        'thoi_gian_khau_hao': 84,
        'ty_le_khau_hao': 15,
        'phong_ban_id': pb_ids[0].id if pb_ids else False,
        'vi_tri': 'Phòng kinh doanh tầng 2',
        'tinh_trang': 'dang_su_dung',
        'trang_thai': 'tot',
    },
]

tai_sans = env['tai.san.tai.san'].create(tai_san_vals)
print(f"✅ Đã tạo {len(tai_sans)} tài sản")

# 2. ĐỀ XUẤT
de_xuat_vals = [
    {
        'name': 'DX/2025/001',
        'ngay_de_xuat': '2025-12-01',
        'nhan_vien_id': nv_ids[7].id if len(nv_ids) > 7 else nv_ids[0].id,
        'phong_ban_id': pb_ids[1].id if len(pb_ids) > 1 else pb_ids[0].id,
        'ten_tai_san': 'Laptop Dell Inspiron 15',
        'loai_tai_san': 'may_moc',
        'so_luong': 1,
        'don_gia_du_kien': 20000000,
        'ly_do': 'Laptop hiện tại đã hỏng, cần thay thế',
        'muc_dich_su_dung': 'Làm việc với phần mềm kế toán, Excel',
        'han_mua': '2026-01-15',
        'trang_thai': 'da_duyet',
    },
    {
        'name': 'DX/2025/002',
        'ngay_de_xuat': '2025-12-05',
        'nhan_vien_id': nv_ids[5].id if len(nv_ids) > 5 else nv_ids[0].id,
        'phong_ban_id': pb_ids[2].id if len(pb_ids) > 2 else pb_ids[0].id,
        'ten_tai_san': 'Máy in màu Epson L8050',
        'loai_tai_san': 'may_moc',
        'so_luong': 1,
        'don_gia_du_kien': 12000000,
        'ly_do': 'Phòng hành chính cần máy in màu',
        'muc_dich_su_dung': 'In tài liệu văn phòng, hợp đồng',
        'han_mua': '2026-01-20',
        'trang_thai': 'cho_duyet',
    },
    {
        'name': 'DX/2025/003',
        'ngay_de_xuat': '2025-12-10',
        'nhan_vien_id': nv_ids[8].id if len(nv_ids) > 8 else nv_ids[0].id,
        'phong_ban_id': pb_ids[3].id if len(pb_ids) > 3 else pb_ids[0].id,
        'ten_tai_san': 'MacBook Pro 14 inch M3',
        'loai_tai_san': 'may_moc',
        'so_luong': 1,
        'don_gia_du_kien': 45000000,
        'ly_do': 'Cần MacBook để làm việc với thiết kế đồ họa',
        'muc_dich_su_dung': 'Thiết kế poster, edit video',
        'han_mua': '2026-02-01',
        'trang_thai': 'cho_duyet',
    },
]

de_xuats = env['tai.san.de.xuat'].create(de_xuat_vals)
print(f"✅ Đã tạo {len(de_xuats)} đề xuất")

# 3. CẤP PHÁT
cap_phat_vals = [
    {
        'name': 'CP/2024/001',
        'ngay_cap_phat': '2024-03-20',
        'tai_san_id': tai_sans[0].id,
        'nhan_vien_id': nv_ids[0].id if nv_ids else False,
        'phong_ban_id': pb_ids[0].id if pb_ids else False,
        'so_luong': 1,
        'gia_tri': 25000000,
        'loai_cap_phat': 'mua_moi',
        'trang_thai': 'da_nhan',
        'ngay_nhan': '2024-03-20',
        'bien_ban_ban_giao': 'Đã bàn giao laptop Dell Latitude 5520',
    },
    {
        'name': 'CP/2024/002',
        'ngay_cap_phat': '2024-04-25',
        'tai_san_id': tai_sans[1].id,
        'nhan_vien_id': nv_ids[2].id if len(nv_ids) > 2 else nv_ids[0].id,
        'phong_ban_id': pb_ids[1].id if len(pb_ids) > 1 else pb_ids[0].id,
        'so_luong': 1,
        'gia_tri': 22000000,
        'loai_cap_phat': 'mua_moi',
        'trang_thai': 'da_nhan',
        'ngay_nhan': '2024-04-25',
    },
    {
        'name': 'CP/2023/015',
        'ngay_cap_phat': '2023-06-15',
        'tai_san_id': tai_sans[2].id,
        'nhan_vien_id': nv_ids[4].id if len(nv_ids) > 4 else nv_ids[0].id,
        'phong_ban_id': pb_ids[3].id if len(pb_ids) > 3 else pb_ids[0].id,
        'so_luong': 1,
        'gia_tri': 530000000,
        'loai_cap_phat': 'mua_moi',
        'trang_thai': 'da_nhan',
        'ngay_nhan': '2023-06-15',
        'bien_ban_ban_giao': 'Bàn giao xe ô tô Toyota Vios',
    },
]

cap_phats = env['tai.san.cap.phat'].create(cap_phat_vals)
print(f"✅ Đã tạo {len(cap_phats)} cấp phát")

env.cr.commit()

print("\n" + "="*60)
print("HOÀN TẤT TẠO DEMO DATA!")
print(f"- Tài sản: {len(tai_sans)}")
print(f"- Đề xuất: {len(de_xuats)}")
print(f"- Cấp phát: {len(cap_phats)}")
print("="*60)
