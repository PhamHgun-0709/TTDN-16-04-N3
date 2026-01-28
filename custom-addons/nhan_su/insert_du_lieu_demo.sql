-- Script chèn dữ liệu demo trực tiếp vào PostgreSQL
-- Tháng 1/2026

-- 1. Tạo ca làm việc nếu chưa có
INSERT INTO nhan_su_ca_lam_viec (name, gio_bat_dau, gio_ket_thuc, so_gio_chuan, he_so_tang_ca, active, create_uid, write_uid, create_date, write_date)
SELECT 'Ca hành chính', 8.0, 17.0, 8.0, 1.5, true, 1, 1, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM nhan_su_ca_lam_viec LIMIT 1);

-- 2. Lấy ID ca làm việc
DO $$
DECLARE
    v_ca_id INT;
    v_nhan_vien RECORD;
    v_ngay DATE;
    v_cham_cong_id INT;
    v_thang TEXT := '1';
    v_nam TEXT := '2026';
    v_count INT := 0;
BEGIN
    -- Lấy ca làm việc
    SELECT id INTO v_ca_id FROM nhan_su_ca_lam_viec LIMIT 1;
    
    RAISE NOTICE 'Ca làm việc ID: %', v_ca_id;
    
    -- Xóa dữ liệu cũ tháng 1/2026
    DELETE FROM nhan_su_cham_cong WHERE thang = v_thang AND nam = v_nam;
    DELETE FROM nhan_su_tong_hop_cong WHERE thang = v_thang AND nam = v_nam;
    
    RAISE NOTICE 'Đã xóa dữ liệu cũ';
    
    -- Cập nhật ca làm việc cho nhân viên
    UPDATE nhan_su_nhan_vien 
    SET ca_lam_viec_id = v_ca_id 
    WHERE ca_lam_viec_id IS NULL AND trang_thai = 'dang_lam';
    
    -- Tạo chấm công cho từng nhân viên (20 ngày làm việc)
    FOR v_nhan_vien IN 
        SELECT id, phong_ban_id FROM nhan_su_nhan_vien 
        WHERE trang_thai = 'dang_lam' 
        LIMIT 10
    LOOP
        FOR i IN 1..20 LOOP
            v_ngay := ('2026-01-' || LPAD(i::TEXT, 2, '0'))::DATE;
            
            -- Insert chấm công
            INSERT INTO nhan_su_cham_cong (
                name, nhan_vien_id, phong_ban_id, ca_lam_viec_id, 
                ngay_cham_cong, thang, nam,
                gio_vao, gio_ra, loai_ngay, active,
                create_uid, write_uid, create_date, write_date
            ) VALUES (
                'New', v_nhan_vien.id, v_nhan_vien.phong_ban_id, v_ca_id,
                v_ngay, v_thang, v_nam,
                8.0, 17.0, 'binh_thuong', true,
                1, 1, NOW(), NOW()
            );
            
            v_count := v_count + 1;
        END LOOP;
    END LOOP;
    
    RAISE NOTICE 'Đã tạo % bản ghi chấm công', v_count;
    
    -- Tạo tổng hợp công cho từng nhân viên
    v_count := 0;
    FOR v_nhan_vien IN 
        SELECT DISTINCT nv.id, nv.phong_ban_id, nv.ca_lam_viec_id
        FROM nhan_su_nhan_vien nv
        INNER JOIN nhan_su_cham_cong cc ON cc.nhan_vien_id = nv.id
        WHERE cc.thang = v_thang AND cc.nam = v_nam
    LOOP
        -- Insert tổng hợp công
        INSERT INTO nhan_su_tong_hop_cong (
            nhan_vien_id, phong_ban_id, ca_lam_viec_id,
            thang, nam, cong_chuan_thang,
            trang_thai, active,
            create_uid, write_uid, create_date, write_date
        ) VALUES (
            v_nhan_vien.id, v_nhan_vien.phong_ban_id, v_nhan_vien.ca_lam_viec_id,
            v_thang, v_nam, 26.0,
            'da_xac_nhan', true,
            1, 1, NOW(), NOW()
        ) RETURNING id INTO v_cham_cong_id;
        
        -- Link chấm công với tổng hợp công
        INSERT INTO nhan_su_tong_hop_cong_nhan_su_cham_cong_rel (nhan_su_tong_hop_cong_id, nhan_su_cham_cong_id)
        SELECT v_cham_cong_id, id 
        FROM nhan_su_cham_cong 
        WHERE nhan_vien_id = v_nhan_vien.id AND thang = v_thang AND nam = v_nam;
        
        v_count := v_count + 1;
    END LOOP;
    
    RAISE NOTICE 'Đã tạo và xác nhận % tổng hợp công', v_count;
    RAISE NOTICE 'HOÀN TẤT!';
END $$;

-- Hiển thị kết quả
SELECT 
    'Chấm công' as loai,
    COUNT(*) as so_luong
FROM nhan_su_cham_cong 
WHERE thang = '1' AND nam = '2026'
UNION ALL
SELECT 
    'Tổng hợp công' as loai,
    COUNT(*) as so_luong
FROM nhan_su_tong_hop_cong 
WHERE thang = '1' AND nam = '2026';
