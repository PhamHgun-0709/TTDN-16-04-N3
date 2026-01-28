-- Insert demo data for tai_san module
-- 10 assets with different statuses

INSERT INTO tai_san_tai_san (name, ma_tai_san, loai_tai_san, ngay_mua, nguyen_gia, thoi_gian_khau_hao, ty_le_khau_hao, vi_tri, tinh_trang, trang_thai, ghi_chu, create_uid, create_date, write_uid, write_date, active) VALUES
('Laptop Dell Latitude 5520', 'TS-IT-001', 'may_moc', '2024-03-15', 25000000, 36, 20, 'Văn phòng tầng 2', 'dang_su_dung', 'tot', 'Laptop phục vụ công việc', 2, NOW(), 2, NOW(), true),
('Laptop HP ProBook 450 G8', 'TS-IT-002', 'may_moc', '2024-04-20', 22000000, 36, 15, 'Phòng kế toán', 'dang_su_dung', 'tot', 'Máy tính kế toán', 2, NOW(), 2, NOW(), true),
('Xe Toyota Camry 2023', 'TS-VAN-001', 'phuong_tien', '2023-06-10', 1200000000, 120, 25, 'Bãi đỗ xe công ty', 'dang_su_dung', 'tot', 'Xe công ty', 2, NOW(), 2, NOW(), true),
('Bàn làm việc Executive', 'TS-NOI-001', 'van_phong', '2024-01-05', 8000000, 60, 10, 'Phòng giám đốc', 'dang_su_dung', 'tot', 'Bàn giám đốc', 2, NOW(), 2, NOW(), true),
('Máy in HP LaserJet Pro', 'TS-IT-010', 'may_moc', '2022-08-15', 12000000, 48, 60, 'Khu vực in ấn', 'dang_su_dung', 'bao_tri', 'Đang bảo trì', 2, NOW(), 2, NOW(), true),
('Điều hòa Daikin 18000BTU', 'TS-TB-005', 'may_moc', '2021-05-20', 15000000, 84, 40, 'Phòng họp tầng 3', 'dang_su_dung', 'tot', 'Điều hòa phòng họp', 2, NOW(), 2, NOW(), true),
('Máy photocopy Canon', 'TS-IT-015', 'may_moc', '2023-09-10', 35000000, 60, 30, 'Khu hành chính', 'dang_su_dung', 'tot', 'Máy photo văn phòng', 2, NOW(), 2, NOW(), true),
('Bộ bàn ghế văn phòng', 'TS-NOI-010', 'van_phong', '2024-02-20', 12000000, 60, 15, 'Văn phòng nhân viên', 'dang_su_dung', 'tot', 'Bộ bàn ghế cho 10 người', 2, NOW(), 2, NOW(), true),
('Máy tính để bàn cũ', 'TS-IT-099', 'may_moc', '2019-03-10', 10000000, 48, 95, 'Kho thiết bị', 'thanh_ly', 'hong', 'Đã thanh lý', 2, NOW(), 2, NOW(), true),
('Tủ hồ sơ sắt', 'TS-NOI-020', 'van_phong', '2023-11-15', 5000000, 84, 20, 'Phòng lưu trữ', 'dang_su_dung', 'tot', 'Tủ lưu trữ hồ sơ', 2, NOW(), 2, NOW(), true);

-- Insert demo data for tai_chinh_ke_toan module
-- 10 phieu chi and phieu thu

INSERT INTO tai_chinh_ke_toan_phieu_chi (name, ngay_lap, loai_chi, so_tien, hinh_thuc_thanh_toan, ly_do_chi, trang_thai, nguoi_lap_id, create_uid, create_date, write_uid, write_date) VALUES
('PC001', '2026-01-20', 'mua_hang', 15000000, 'tien_mat', 'Mua văn phòng phẩm tháng 1', 'da_chi', 2, 2, NOW(), 2, NOW()),
('PC002', '2026-01-21', 'luong', 50000000, 'chuyen_khoan', 'Tạm ứng lương tháng 1/2026', 'da_duyet', 2, 2, NOW(), 2, NOW()),
('PC003', '2026-01-22', 'dien_nuoc', 8000000, 'chuyen_khoan', 'Tiền điện nước tháng 12/2025', 'da_chi', 2, 2, NOW(), 2, NOW()),
('PC004', '2026-01-23', 'khac', 5000000, 'tien_mat', 'Chi phí bảo trì máy móc', 'cho_duyet', 2, 2, NOW(), 2, NOW()),
('PC005', '2026-01-24', 'mua_hang', 25000000, 'chuyen_khoan', 'Mua thiết bị văn phòng', 'nhap', 2, 2, NOW(), 2, NOW());

INSERT INTO tai_chinh_ke_toan_phieu_thu (name, ngay_lap, loai_thu, so_tien, hinh_thuc_thanh_toan, ly_do_thu, trang_thai, nguoi_lap_id, create_uid, create_date, write_uid, write_date) VALUES
('PT001', '2026-01-18', 'ban_hang', 80000000, 'chuyen_khoan', 'Thu tiền hợp đồng dịch vụ Q4/2025', 'da_thu', 2, 2, NOW(), 2, NOW()),
('PT002', '2026-01-19', 'ban_hang', 45000000, 'tien_mat', 'Thu tiền khách hàng ABC', 'da_duyet', 2, 2, NOW(), 2, NOW()),
('PT003', '2026-01-21', 'khac', 10000000, 'chuyen_khoan', 'Thu phí dịch vụ tư vấn', 'da_thu', 2, 2, NOW(), 2, NOW()),
('PT004', '2026-01-23', 'ban_hang', 65000000, 'chuyen_khoan', 'Thu tiền hợp đồng mới', 'cho_duyet', 2, 2, NOW(), 2, NOW()),
('PT005', '2026-01-25', 'khac', 15000000, 'tien_mat', 'Thu hồi ứng trước', 'nhap', 2, 2, NOW(), 2, NOW());
