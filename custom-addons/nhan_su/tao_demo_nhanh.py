# Script đơn giản để chạy trong Odoo shell
# Chạy: docker exec -it odoo_app_fitdnu odoo shell -c /etc/odoo/odoo.conf -d btap
# Sau đó paste nội dung này

import random
from datetime import datetime

print("Bắt đầu tạo dữ liệu demo...")

# Lấy nhân viên
nhan_viens = env['nhan.su.nhan.vien'].search([('trang_thai', '=', 'dang_lam')], limit=5)
print(f"Tìm thấy {len(nhan_viens)} nhân viên")

# Lấy/tạo ca làm việc
ca = env['nhan.su.ca.lam.viec'].search([], limit=1)
if not ca:
    ca = env['nhan.su.ca.lam.viec'].create({
        'name': 'Ca hành chính',
        'gio_bat_dau': 8.0,
        'gio_ket_thuc': 17.0,
        'so_gio_chuan': 8.0,
        'he_so_tang_ca': 1.5,
    })
    print(f"Đã tạo ca làm việc: {ca.name}")

# Tháng hiện tại
today = datetime.now()
thang = str(today.month)
nam = str(today.year)

# Xóa dữ liệu cũ
env['nhan.su.cham.cong'].search([('thang','=',thang),('nam','=',nam)]).unlink()
env['nhan.su.tong.hop.cong'].search([('thang','=',thang),('nam','=',nam)]).unlink()

# Tạo chấm công
count = 0
for nv in nhan_viens:
    if not nv.ca_lam_viec_id:
        nv.ca_lam_viec_id = ca.id
    for day in range(1, 21):
        env['nhan.su.cham.cong'].create({
            'nhan_vien_id': nv.id,
            'ca_lam_viec_id': ca.id,
            'ngay_cham_cong': datetime(int(nam), int(thang), day),
            'gio_vao': 8.0,
            'gio_ra': 17.0,
            'loai_ngay': 'binh_thuong',
        })
        count += 1
print(f"Đã tạo {count} bản ghi chấm công")

# Tạo tổng hợp công
count2 = 0
for nv in nhan_viens:
    ccs = env['nhan.su.cham.cong'].search([('nhan_vien_id','=',nv.id),('thang','=',thang),('nam','=',nam)])
    if ccs:
        th = env['nhan.su.tong.hop.cong'].create({
            'nhan_vien_id': nv.id,
            'thang': thang,
            'nam': nam,
            'cham_cong_ids': [(6, 0, ccs.ids)],
            'cong_chuan_thang': 26.0,
        })
        th.action_xac_nhan()
        count2 += 1
print(f"Đã tạo và xác nhận {count2} tổng hợp công")

env.cr.commit()
print("HOÀN TẤT! Bạn có thể quay lại Bảng lương và bấm 'Lấy dữ liệu'")
