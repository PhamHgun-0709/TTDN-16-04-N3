# -*- coding: utf-8 -*-
"""
Script XÓA toàn bộ phiếu thu/chi cũ và TẠO MỚI data cân đối
"""

from datetime import datetime, timedelta
import random

print("="*70)
print("🗑️  XÓA DATA CŨ...")

# Xóa toàn bộ phiếu thu cũ
phieu_thu_ids = env['tai.chinh.ke.toan.phieu.thu'].search([])
print(f"   Tìm thấy {len(phieu_thu_ids)} phiếu thu cũ")
if phieu_thu_ids:
    phieu_thu_ids.unlink()
    print("   ✓ Đã xóa phiếu thu")

# Xóa toàn bộ phiếu chi cũ  
phieu_chi_ids = env['tai.chinh.ke.toan.phieu.chi'].search([])
print(f"   Tìm thấy {len(phieu_chi_ids)} phiếu chi cũ")
if phieu_chi_ids:
    phieu_chi_ids.unlink()
    print("   ✓ Đã xóa phiếu chi")

# Xóa sổ quỹ cũ
so_quy_ids = env['tai.chinh.ke.toan.so.quy'].search([])
print(f"   Tìm thấy {len(so_quy_ids)} bút toán sổ quỹ cũ")
if so_quy_ids:
    so_quy_ids.unlink()
    print("   ✓ Đã xóa sổ quỹ")

env.cr.commit()
print("✅ Đã xóa xong data cũ!\n")

# ==================================================================
# TẠO DATA MỚI CÂN ĐỐI
# ==================================================================

# Lấy partners
partner_ids = env['res.partner'].search([('is_company', '=', False)], limit=10).ids
if not partner_ids:
    partner = env['res.partner'].create({'name': 'Khách hàng mẫu', 'is_company': False})
    partner_ids = [partner.id]

print(f"✓ Có {len(partner_ids)} partners\n")

# ==================================================================
# PHIẾU THU - Tổng 4 TỶ
# ==================================================================
phieu_thu_data = [
    {'so_tien': 1000000000, 'ly_do': 'Thu tien ban hang thang 1/2026', 'loai': 'ban_hang'},
    {'so_tien': 800000000, 'ly_do': 'Thu dich vu tu van du an A', 'loai': 'dich_vu'},
    {'so_tien': 650000000, 'ly_do': 'Thu tien hop dong khach hang B', 'loai': 'ban_hang'},
    {'so_tien': 500000000, 'ly_do': 'Thu phi quan ly va van hanh', 'loai': 'khac'},
    {'so_tien': 400000000, 'ly_do': 'Thu lai dau tu chung khoan', 'loai': 'khac'},
    {'so_tien': 350000000, 'ly_do': 'Thu tien ban hang thang 12/2025', 'loai': 'ban_hang'},
    {'so_tien': 300000000, 'ly_do': 'Thu tien cho thue mat bang', 'loai': 'khac'},
]

print("📝 TẠO PHIẾU THU...")
tong_thu = 0
count_thu = 0

for data in phieu_thu_data:
    try:
        vals = {
            'doi_tuong_id': random.choice(partner_ids),
            'ly_do_thu': data['ly_do'],
            'so_tien': data['so_tien'],
            'loai_thu': data['loai'],
            'hinh_thuc_thanh_toan': random.choice(['tien_mat', 'chuyen_khoan']),
            'ngay_lap': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
        }
        
        phieu = env['tai.chinh.ke.toan.phieu.thu'].create(vals)
        
        # Chuyển trạng thái qua từng bước để đảm bảo workflow
        phieu.write({'trang_thai': 'cho_duyet'})
        phieu.write({'trang_thai': 'da_duyet'})
        phieu.write({'trang_thai': 'da_thu'})
        
        tong_thu += data['so_tien']
        count_thu += 1
        print(f"  ✓ {data['so_tien']:>15,.0f}đ - {data['ly_do']}")
    except Exception as e:
        print(f"  ✗ Lỗi tạo phiếu thu: {e}")

# ==================================================================
# PHIẾU CHI - Tổng 3 TỶ (để lợi nhuận dương +1 tỷ)
# ==================================================================
phieu_chi_data = [
    {'so_tien': 600000000, 'ly_do': 'Chi luong nhan vien thang 1/2026', 'loai': 'chi_luong'},
    {'so_tien': 500000000, 'ly_do': 'Mua hang hoa nhap kho', 'loai': 'mua_hang'},
    {'so_tien': 400000000, 'ly_do': 'Thanh toan nha cung cap ABC', 'loai': 'mua_hang'},
    {'so_tien': 350000000, 'ly_do': 'Mua thiet bi may moc', 'loai': 'tai_san'},
    {'so_tien': 300000000, 'ly_do': 'Chi phi van phong va tien ich', 'loai': 'van_phong'},
    {'so_tien': 250000000, 'ly_do': 'Chi phi marketing va quang cao', 'loai': 'khac'},
    {'so_tien': 200000000, 'ly_do': 'Thanh toan dich vu bao tri', 'loai': 'dich_vu'},
    {'so_tien': 150000000, 'ly_do': 'Chi phi dao tao va phat trien', 'loai': 'khac'},
    {'so_tien': 120000000, 'ly_do': 'Chi phi van chuyen va logistics', 'loai': 'khac'},
    {'so_tien': 130000000, 'ly_do': 'Chi phi bao hiem va thue', 'loai': 'khac'},
]

print("\n📝 TẠO PHIẾU CHI...")
tong_chi = 0
count_chi = 0

for data in phieu_chi_data:
    try:
        vals = {
            'doi_tuong_id': random.choice(partner_ids),
            'ly_do_chi': data['ly_do'],
            'so_tien': data['so_tien'],
            'loai_chi': data['loai'],
            'hinh_thuc_thanh_toan': 'chuyen_khoan',  # Dùng chuyển khoản để không kiểm tra tồn quỹ
            'ngay_lap': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
        }
        
        phieu = env['tai.chinh.ke.toan.phieu.chi'].create(vals)
        
        # Chuyển trạng thái qua từng bước và TẠO BÚT TOÁN SỔ QUỸ
        phieu.write({'trang_thai': 'cho_duyet'})
        phieu.write({'trang_thai': 'da_duyet'})
        phieu.action_chi_tien()  # Gọi action để tự động tạo sổ quỹ
        
        tong_chi += data['so_tien']
        count_chi += 1
        print(f"  ✓ {data['so_tien']:>15,.0f}đ - {data['ly_do']}")
    except Exception as e:
        print(f"  ✗ Lỗi tạo phiếu chi: {e}")

# Commit tất cả
env.cr.commit()

# ==================================================================
# TỔNG KẾT
# ==================================================================
chenh_lech = tong_thu - tong_chi
ty_le = (chenh_lech / tong_thu * 100) if tong_thu > 0 else 0

print("\n" + "="*70)
print("📊 TỔNG KẾT DATA MỚI:")
print("="*70)
print(f"   ✓ Đã tạo {count_thu} phiếu THU")
print(f"   💰 Tổng THU:       {tong_thu:>20,.0f}đ")
print("")
print(f"   ✓ Đã tạo {count_chi} phiếu CHI")
print(f"   💸 Tổng CHI:       {tong_chi:>20,.0f}đ")
print("   " + "-"*66)
print(f"   📈 Chênh lệch:     {chenh_lech:>20,.0f}đ ({ty_le:>6.1f}%)")
print("="*70)

if chenh_lech > 0:
    print("✅ Tình hình tài chính: DƯƠNG (+1 tỷ) - Tốt!")
    print("   Dashboard sẽ hiển thị màu xanh!")
else:
    print("⚠️  Tình hình tài chính: ÂM - Cần cải thiện!")

print("\n💡 TIẾP THEO:")
print("   1. F5 HARD REFRESH browser (Ctrl+Shift+R)")
print("   2. Dashboard sẽ hiển thị:")
print(f"      - Tổng thu: {tong_thu:,.0f}đ")
print(f"      - Tổng chi: {tong_chi:,.0f}đ")
print(f"      - Chênh lệch: +{chenh_lech:,.0f}đ")
print("="*70)
