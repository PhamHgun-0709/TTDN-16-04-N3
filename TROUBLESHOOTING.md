# 🔧 Troubleshooting Guide

Hướng dẫn xử lý các lỗi thường gặp khi cài đặt và sử dụng hệ thống ERP.

---

## 🗄️ Lỗi kết nối Database

### Triệu chứng
- Không thể kết nối đến PostgreSQL
- Lỗi: `FATAL: password authentication failed`
- Lỗi: `could not connect to server`

### Giải pháp

**Kiểm tra PostgreSQL đang chạy:**
```bash
# Windows:
Get-Service postgresql*

# Linux:
sudo systemctl status postgresql

# Nếu không chạy, khởi động:
# Windows:
Start-Service postgresql-x64-15  # Thay số version cho đúng

# Linux:
sudo systemctl start postgresql
```

**Kiểm tra kết nối:**
```bash
# Test kết nối database
psql -U odoo -d odoo -h localhost

# Nếu lỗi password, reset password:
# Linux:
sudo -u postgres psql
ALTER USER odoo WITH PASSWORD 'odoo';

# Windows (trong psql):
ALTER USER odoo WITH PASSWORD 'odoo';
```

**Kiểm tra cấu hình pg_hba.conf:**
```bash
# Tìm file pg_hba.conf
# Linux: /etc/postgresql/15/main/pg_hba.conf
# Windows: C:\Program Files\PostgreSQL\15\data\pg_hba.conf

# Đảm bảo có dòng:
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

---

## 🔌 Lỗi Port đã sử dụng

### Triệu chứng
- Lỗi: `Address already in use`
- Không thể khởi động Odoo trên port 8069

### Giải pháp

**Kiểm tra port đang được sử dụng:**
```bash
# Windows:
netstat -ano | findstr :8069
# Xem PID và kill process:
taskkill /PID <PID> /F

# Linux:
sudo lsof -i :8069
# Kill process:
sudo kill -9 <PID>
```

**Đổi port trong odoo.conf:**
```ini
http_port = 8070  # Hoặc port khác chưa sử dụng
```

**Hoặc chạy Odoo với port tùy chỉnh:**
```bash
python odoo-bin -c odoo.conf --http-port=8070
```

---

## 📦 Lỗi import module

### Triệu chứng
- Module không xuất hiện trong Apps
- Lỗi: `Module not found`
- Module bị đánh dấu "To Install" nhưng không cài được

### Giải pháp

**Kiểm tra addons_path:**
```bash
# Xem odoo.conf
cat odoo.conf | grep addons_path

# Đảm bảo đường dẫn đúng:
# Windows:
addons_path = E:\CNTT7\addons,E:\CNTT7\custom-addons

# Linux:
addons_path = /path/to/CNTT7/addons,/path/to/CNTT7/custom-addons
```

**Update Apps List:**
1. Đăng nhập Odoo
2. Bật **Developer Mode** (Settings → Activate Developer Mode)
3. Vào **Apps**
4. Click menu ⋮ → **Update Apps List**
5. Click **Update**

**Kiểm tra __manifest__.py:**
```python
# Đảm bảo file __manifest__.py có định dạng đúng
{
    'name': 'Module Name',
    'version': '1.0',
    'depends': ['base'],
    'data': [...],
    'installable': True,
    'application': True,
}
```

**Restart Odoo server:**
```bash
# Ctrl+C để dừng, sau đó:
python odoo-bin -c odoo.conf
```

---

## 🤖 Model AI không hoạt động

### Triệu chứng
- Không có cảnh báo gian lận
- Lỗi: `No module named 'sklearn'`
- Lỗi khi training model

### Giải pháp

**Kiểm tra ML packages đã cài đặt:**
```bash
# Kiểm tra packages
pip list | grep scikit-learn
pip list | grep pandas
pip list | grep numpy

# Nếu chưa có, cài đặt:
pip install scikit-learn pandas numpy joblib matplotlib seaborn
```

**Kiểm tra file model:**
```bash
# Xem thư mục ml_models
cd custom-addons/tai_chinh_ke_toan/ml_models
ls -la

# Nếu không có model, training lại:
cd ../../..
python train_fraud_model.py
```

**Kiểm tra dữ liệu training:**
```bash
# Đảm bảo có đủ dữ liệu giao dịch (>100 records)
# Truy vấn trong psql:
psql -U odoo -d odoo -c "SELECT COUNT(*) FROM tai_chinh_phieu_thu;"
psql -U odoo -d odoo -c "SELECT COUNT(*) FROM tai_chinh_phieu_chi;"
```

**Kiểm tra logs:**
```bash
# Windows:
Get-Content odoo.log | Select-String "fraud"

# Linux:
tail -f odoo.log | grep fraud
cat odoo.log | grep -i error
```

**Test model thủ công:**
```bash
python test_fraud_alert.py
```

---

## 🐍 Lỗi Python Dependencies

### Triệu chứng
- Lỗi: `ModuleNotFoundError`
- Lỗi khi import các thư viện Python

### Giải pháp

**Cài đặt lại requirements:**
```bash
# Activate virtual environment trước
# Windows:
venv\Scripts\activate

# Linux:
source venv/bin/activate

# Cài đặt lại:
pip install --upgrade pip
pip install -r requirements.txt
```

**Kiểm tra Python version:**
```bash
python --version
# Phải là Python 3.10 trở lên
```

**Cài đặt package cụ thể bị thiếu:**
```bash
pip install <package-name>
```

---

## 🐳 Lỗi Docker

### Triệu chứng
- Container không khởi động
- Lỗi: `Error response from daemon`
- Database không kết nối

### Giải pháp

**Xem logs chi tiết:**
```bash
docker-compose logs -f odoo
docker-compose logs -f db
```

**Restart containers:**
```bash
docker-compose down
docker-compose up -d
```

**Xóa và tạo lại (mất dữ liệu):**
```bash
docker-compose down -v
docker-compose up -d
```

**Kiểm tra disk space:**
```bash
# Docker cần nhiều dung lượng
docker system df
docker system prune  # Dọn dẹp
```

---

## 💾 Lỗi Database Migration

### Triệu chứng
- Lỗi khi upgrade module
- Lỗi: `column does not exist`
- Database schema không đúng

### Giải pháp

**Backup database trước:**
```bash
pg_dump -U odoo -d odoo > backup.sql
```

**Update module:**
```bash
# Từ command line:
python odoo-bin -c odoo.conf -d odoo -u <module_name>

# Hoặc từ UI:
# Apps → Module → Upgrade
```

**Nếu lỗi nghiêm trọng, restore backup:**
```bash
dropdb -U odoo odoo
createdb -U odoo odoo
psql -U odoo -d odoo < backup.sql
```

---

## 🔐 Lỗi Permission/Access Rights

### Triệu chứng
- Lỗi: `Access Denied`
- Không thấy menu/chức năng
- Không thể tạo/sửa/xóa records

### Giải pháp

**Kiểm tra user groups:**
1. Settings → Users & Companies → Users
2. Chọn user cần kiểm tra
3. Tab **Access Rights** → Đảm bảo có đúng groups

**Update security rules:**
```bash
# Update module sau khi sửa ir.model.access.csv
python odoo-bin -c odoo.conf -d odoo -u <module_name>
```

**Chạy với superuser (development only):**
```python
# Trong code, thêm sudo():
self.sudo().create({...})
```

---

## 📊 Lỗi Performance/Slow

### Triệu chứng
- Hệ thống chạy chậm
- Timeout khi load trang
- Database queries lâu

### Giải pháp

**Tăng resources trong odoo.conf:**
```ini
workers = 4
max_cron_threads = 2
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_time_cpu = 600
limit_time_real = 1200
```

**Tối ưu database:**
```bash
# Vacuum và analyze
psql -U odoo -d odoo -c "VACUUM ANALYZE;"

# Reindex
psql -U odoo -d odoo -c "REINDEX DATABASE odoo;"
```

**Kiểm tra logs chậm:**
```bash
# Bật log timing trong odoo.conf:
log_level = debug_sql

# Xem queries chậm:
grep "query time" odoo.log
```

---

## 🆘 Lỗi khác / Cần hỗ trợ

Nếu gặp lỗi không có trong danh sách trên:

1. **Kiểm tra logs**: `odoo.log` thường có thông tin chi tiết
2. **Google error message**: Copy error và search
3. **Odoo Community**: https://www.odoo.com/forum/help-1
4. **GitHub Issues**: Tạo issue trong repository

**Liên hệ hỗ trợ:**
- Email: pthung0709@gmail.com
- Facebook: AIoTLab - DaiNam University

---

## 📝 Tips Debug

**Bật Developer Mode:**
- Settings → Activate Developer Mode
- Có thêm menu Technical, logs chi tiết

**Xem logs realtime:**
```bash
# Windows:
Get-Content odoo.log -Wait -Tail 50

# Linux:
tail -f odoo.log
```

**Test từng module riêng:**
```bash
# Chỉ load một module:
python odoo-bin -c odoo.conf -d odoo -i base,nhan_su --stop-after-init
```

**Python debugger:**
```python
# Thêm vào code:
import pdb; pdb.set_trace()
```

---

© 2025 AIoTLab, Faculty of Information Technology, DaiNam University. All rights reserved.
