# -*- coding: utf-8 -*-
print("="*70)
print("🔧 TẠO KHẤU HAO CHO TÀI SẢN CÓ SẴN")
print("="*70)

# Tìm tài sản có thời gian khấu hao nhưng chưa có bản ghi khấu hao
tai_san_can_khau_hao = env['tai.san.tai.san'].search([
    ('thoi_gian_khau_hao', '>', 0),
    ('nguyen_gia', '>', 0)
])

print(f"\n📦 Tìm thấy {len(tai_san_can_khau_hao)} tài sản cần khấu hao")

# Lấy danh sách tài sản đã có khấu hao
tai_san_da_khau_hao = env['tai.chinh.ke.toan.khau.hao.tai.san'].search([]).mapped('tai_san_id')
print(f"   Trong đó {len(tai_san_da_khau_hao)} tài sản đã có khấu hao")

# Tạo khấu hao cho tài sản chưa có
count = 0
for tai_san in tai_san_can_khau_hao:
    if tai_san not in tai_san_da_khau_hao:
        khau_hao = env['tai.chinh.ke.toan.khau.hao.tai.san'].create({
            'tai_san_id': tai_san.id,
            'nguyen_gia': tai_san.nguyen_gia,
            'gia_tri_con_lai': tai_san.gia_tri_con_lai,
            'thoi_gian_khau_hao': tai_san.thoi_gian_khau_hao,
            'ngay_bat_dau_khau_hao': tai_san.ngay_mua or '2026-01-01',
            'phuong_phap_khau_hao': 'duong_thang',
        })
        count += 1
        if count <= 5:  # Chỉ in 5 cái đầu
            print(f"   ✓ {tai_san.name}: {tai_san.nguyen_gia:,.0f}đ")

env.cr.commit()

# Kiểm tra lại
tong_khau_hao = env['tai.chinh.ke.toan.khau.hao.tai.san'].search_count([])
print(f"\n✅ Đã tạo {count} bản ghi khấu hao mới")
print(f"📊 Tổng cộng: {tong_khau_hao} bản ghi khấu hao trong hệ thống")
print("="*70)
