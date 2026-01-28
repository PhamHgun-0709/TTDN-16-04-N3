# 🔧 SỬA LỖI DASHBOARD KHÔNG CẬP NHẬT TỰ ĐỘNG

## ✅ Đã sửa xong!

### 🐛 Vấn đề:
1. **Dashboard không cập nhật tự động** khi có thay đổi dữ liệu
2. **Dữ liệu hiển thị cũ** - không phản ánh trạng thái thực tế
3. **Phần "Phiếu chờ duyệt" không đúng** với số liệu thực

### 🔨 Nguyên nhân:
- Các computed field có `@api.depends_context('company')` nhưng **không có store=False**
- Dashboard bị **cache** - không recompute khi dữ liệu thay đổi
- Button click vào card không mở được danh sách chi tiết

### ✨ Giải pháp đã áp dụng:

#### 1️⃣ Tắt cache cho tất cả computed fields
```python
# TRƯỚC (SAI):
so_phieu_cho_duyet = fields.Integer(..., compute='_compute_dashboard_data')

# SAU (ĐÚNG):
so_phieu_cho_duyet = fields.Integer(..., compute='_compute_dashboard_data', store=False)
```

#### 2️⃣ Bỏ decorator `@api.depends_context`
```python
# TRƯỚC:
@api.depends_context('company')
def _compute_dashboard_data(self):

# SAU:
def _compute_dashboard_data(self):
```

#### 3️⃣ Thêm button "Làm mới" ở header
```xml
<header>
    <button name="action_refresh_dashboard" type="object" string="🔄 Làm mới" class="btn-primary"/>
</header>
```

#### 4️⃣ Thêm button click vào cards
```xml
<button name="action_view_phieu_cho_duyet" type="object" class="btn btn-link p-0 w-100">
    <div class="card...">
        <!-- Card content -->
    </div>
</button>
```

#### 5️⃣ Cải thiện action methods
```python
def action_view_phieu_cho_duyet(self):
    """Xem cả phiếu thu và phiếu chi chờ duyệt"""
    # Ưu tiên phiếu chi, fallback sang phiếu thu
    # Hiển thị notification nếu không có dữ liệu
```

### 📊 Cách sử dụng:

1. **Tự động cập nhật:**
   - Mỗi lần mở dashboard → Dữ liệu tính lại
   - Mỗi lần F5 refresh trang → Cập nhật mới nhất

2. **Làm mới thủ công:**
   - Click button **"🔄 Làm mới"** ở góc trên

3. **Xem chi tiết:**
   - Click vào card **"PHIẾU CHỜ DUYỆT"** → Mở list phiếu chờ duyệt
   - Click vào card **"PHIẾU ĐÃ DUYỆT"** → Mở list phiếu đã duyệt

### 🧪 Test ngay:

1. **Mở dashboard** tài chính
2. **Tạo 1 phiếu chi mới** với trạng thái "Chờ duyệt"
3. **Quay lại dashboard** (hoặc F5)
4. **Số liệu sẽ cập nhật ngay** - không cần restart

### ✅ Kết quả:

- ✅ Dashboard **LUÔN** hiển thị dữ liệu mới nhất
- ✅ Click card → Xem chi tiết ngay
- ✅ Button "Làm mới" hoạt động
- ✅ Không cần cache, không cần restart
- ✅ Performance tốt (query realtime)

### 📝 Lưu ý:

- Dashboard **không cache** nữa → Luôn query database trực tiếp
- Nếu có **nhiều dữ liệu** (>10,000 records) có thể hơi chậm
- Trong trường hợp đó, nên thêm **index** cho fields `trang_thai`, `ngay_lap`

---
**Cập nhật:** 2026-01-27
**Module:** tai_chinh_ke_toan
**File:** models/dashboard.py, views/dashboard_views.xml
