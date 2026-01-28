# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class ChiTietLuong(models.Model):
    """Chi tiết lương CON - Lương của từng nhân viên"""
    _name = 'nhan.su.chi.tiet.luong'
    _description = 'Chi tiết lương nhân viên'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'nhan_vien_id'

    name = fields.Char(string='Mã chi tiết', compute='_compute_name', store=True, readonly=True)
    bang_luong_id = fields.Many2one('nhan.su.bang.luong', string='Bảng lương', required=True, ondelete='cascade')
    
    # Thông tin nhân viên
    nhan_vien_id = fields.Many2one('nhan.su.nhan.vien', string='Nhân viên', required=True, ondelete='restrict', tracking=True)
    phong_ban_id = fields.Many2one(related='nhan_vien_id.phong_ban_id', string='Phòng ban', store=True)
    chuc_vu_id = fields.Many2one('nhan.su.chuc.vu', string='Chức vụ', tracking=True)
    
    # Dữ liệu đầu vào từ tổng hợp công
    tong_hop_cong_id = fields.Many2one('nhan.su.tong.hop.cong', string='Tổng hợp công', tracking=True)
    cong_chuan = fields.Float(string='Công chuẩn', default=26.0)
    tong_cong = fields.Float(related='tong_hop_cong_id.tong_cong', string='Tổng công', store=True)
    cong_quy_doi = fields.Float(related='tong_hop_cong_id.cong_quy_doi_luong', string='Công quy đổi', store=True)
    tong_gio_tang_ca = fields.Float(related='tong_hop_cong_id.tong_gio_tang_ca', string='Giờ tăng ca', store=True)
    
    # ========== CÔNG THỨC TÍNH LƯƠNG ==========
    # Thu nhập = (Lương cơ bản / Công chuẩn) × Công quy đổi + Tiền tăng ca + Phụ cấp
    
    # 1. Lương cơ bản
    luong_co_ban = fields.Float(string='Lương cơ bản', tracking=True)
    don_gia_cong = fields.Float(string='Đơn giá công', compute='_compute_don_gia_cong', store=True)
    
    # 2. Lương theo công
    luong_theo_cong = fields.Float(string='Lương theo công', compute='_compute_luong_theo_cong', store=True)
    
    # 3. Tiền tăng ca
    tien_tang_ca = fields.Float(string='Tiền tăng ca', compute='_compute_tien_tang_ca', store=True)
    
    # 4. Phụ cấp
    phu_cap_chuc_vu = fields.Float(string='Phụ cấp chức vụ', tracking=True)
    phu_cap_an_trua = fields.Float(string='Phụ cấp ăn trưa', default=0, tracking=True)
    phu_cap_xang_xe = fields.Float(string='Phụ cấp xăng xe', default=0, tracking=True)
    phu_cap_dien_thoai = fields.Float(string='Phụ cấp điện thoại', default=0, tracking=True)
    phu_cap_khac = fields.Float(string='Phụ cấp khác', tracking=True)
    tong_phu_cap = fields.Float(string='Tổng phụ cấp', compute='_compute_tong_phu_cap', store=True)
    
    # 5. Thưởng
    thuong = fields.Float(string='Thưởng', tracking=True)
    
    # 6. Thu nhập
    thu_nhap = fields.Float(string='Tổng thu nhập', compute='_compute_thu_nhap', store=True)
    
    # ========== KHẤU TRỪ ==========
    # Thực lĩnh = Thu nhập - Khấu trừ
    
    # Bảo hiểm
    bao_hiem_xa_hoi = fields.Float(string='BHXH (8%)', compute='_compute_bao_hiem', store=True)
    bao_hiem_y_te = fields.Float(string='BHYT (1.5%)', compute='_compute_bao_hiem', store=True)
    bao_hiem_that_nghiep = fields.Float(string='BHTN (1%)', compute='_compute_bao_hiem', store=True)
    tong_bao_hiem = fields.Float(string='Tổng BHXH', compute='_compute_tong_bao_hiem', store=True)
    
    # Thuế
    thue_thu_nhap = fields.Float(string='Thuế TNCN', compute='_compute_thue', store=True)
    
    # Khác
    khau_tru_khac = fields.Float(string='Khấu trừ khác', tracking=True)
    tong_khau_tru = fields.Float(string='Tổng khấu trừ', compute='_compute_tong_khau_tru', store=True)
    
    # 7. Thực lĩnh
    thuc_linh = fields.Float(string='Thực lĩnh', compute='_compute_thuc_linh', store=True)
    
    ghi_chu = fields.Text(string='Ghi chú')
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('unique_bang_luong_nhan_vien', 'UNIQUE(bang_luong_id, nhan_vien_id)', 
         'Nhân viên đã có trong bảng lương này!')
    ]

    @api.depends('bang_luong_id', 'nhan_vien_id')
    def _compute_name(self):
        for record in self:
            if record.bang_luong_id and record.nhan_vien_id:
                record.name = f"{record.bang_luong_id.name}/{record.nhan_vien_id.ma_nhan_vien}"
            else:
                record.name = 'New'

    @api.depends('luong_co_ban', 'cong_chuan')
    def _compute_don_gia_cong(self):
        """Đơn giá công = Lương cơ bản / Công chuẩn"""
        for record in self:
            if record.cong_chuan > 0:
                record.don_gia_cong = record.luong_co_ban / record.cong_chuan
            else:
                record.don_gia_cong = 0

    @api.depends('don_gia_cong', 'cong_quy_doi')
    def _compute_luong_theo_cong(self):
        """Lương theo công = Đơn giá công × Công quy đổi"""
        for record in self:
            record.luong_theo_cong = record.don_gia_cong * record.cong_quy_doi

    @api.depends('tong_gio_tang_ca', 'don_gia_cong', 'tong_hop_cong_id')
    def _compute_tien_tang_ca(self):
        """Tiền tăng ca = (Giờ tăng ca / Giờ chuẩn) × Hệ số × Đơn giá công"""
        for record in self:
            if record.tong_hop_cong_id and record.tong_hop_cong_id.ca_lam_viec_id:
                ca = record.tong_hop_cong_id.ca_lam_viec_id
                if ca.so_gio_chuan > 0:
                    cong_tang_ca = (record.tong_gio_tang_ca / ca.so_gio_chuan) * ca.he_so_tang_ca
                    record.tien_tang_ca = record.don_gia_cong * cong_tang_ca
                else:
                    record.tien_tang_ca = 0
            else:
                record.tien_tang_ca = 0

    @api.depends('phu_cap_chuc_vu', 'phu_cap_an_trua', 'phu_cap_xang_xe', 'phu_cap_dien_thoai', 'phu_cap_khac')
    def _compute_tong_phu_cap(self):
        for record in self:
            record.tong_phu_cap = (record.phu_cap_chuc_vu + record.phu_cap_an_trua + 
                                  record.phu_cap_xang_xe + record.phu_cap_dien_thoai + record.phu_cap_khac)

    @api.depends('luong_theo_cong', 'tien_tang_ca', 'tong_phu_cap', 'thuong')
    def _compute_thu_nhap(self):
        """Thu nhập = Lương theo công + Tiền tăng ca + Phụ cấp + Thưởng"""
        for record in self:
            record.thu_nhap = (record.luong_theo_cong + record.tien_tang_ca + 
                              record.tong_phu_cap + record.thuong)

    @api.depends('luong_co_ban')
    def _compute_bao_hiem(self):
        """Tính bảo hiểm theo lương cơ bản"""
        for record in self:
            record.bao_hiem_xa_hoi = record.luong_co_ban * 0.08
            record.bao_hiem_y_te = record.luong_co_ban * 0.015
            record.bao_hiem_that_nghiep = record.luong_co_ban * 0.01

    @api.depends('bao_hiem_xa_hoi', 'bao_hiem_y_te', 'bao_hiem_that_nghiep')
    def _compute_tong_bao_hiem(self):
        for record in self:
            record.tong_bao_hiem = (record.bao_hiem_xa_hoi + record.bao_hiem_y_te + 
                                   record.bao_hiem_that_nghiep)

    @api.depends('thu_nhap', 'tong_bao_hiem')
    def _compute_thue(self):
        """Tính thuế TNCN theo bậc thuế (đơn giản hóa)"""
        for record in self:
            # Thu nhập tính thuế = Thu nhập - BHXH - Giảm trừ bản thân (11 triệu)
            giam_tru_ban_than = 11000000
            thu_nhap_tinh_thue = record.thu_nhap - record.tong_bao_hiem - giam_tru_ban_than
            
            if thu_nhap_tinh_thue <= 0:
                record.thue_thu_nhap = 0
            elif thu_nhap_tinh_thue <= 5000000:
                record.thue_thu_nhap = thu_nhap_tinh_thue * 0.05
            elif thu_nhap_tinh_thue <= 10000000:
                record.thue_thu_nhap = 5000000 * 0.05 + (thu_nhap_tinh_thue - 5000000) * 0.10
            elif thu_nhap_tinh_thue <= 18000000:
                record.thue_thu_nhap = 5000000 * 0.05 + 5000000 * 0.10 + (thu_nhap_tinh_thue - 10000000) * 0.15
            else:
                record.thue_thu_nhap = 5000000 * 0.05 + 5000000 * 0.10 + 8000000 * 0.15 + (thu_nhap_tinh_thue - 18000000) * 0.20

    @api.depends('tong_bao_hiem', 'thue_thu_nhap', 'khau_tru_khac')
    def _compute_tong_khau_tru(self):
        for record in self:
            record.tong_khau_tru = record.tong_bao_hiem + record.thue_thu_nhap + record.khau_tru_khac

    @api.depends('thu_nhap', 'tong_khau_tru')
    def _compute_thuc_linh(self):
        """Thực lĩnh = Thu nhập - Khấu trừ"""
        for record in self:
            record.thuc_linh = record.thu_nhap - record.tong_khau_tru

    def action_tinh_luong(self):
        """Tính lương tự động từ dữ liệu tổng hợp công"""
        for record in self:
            if not record.tong_hop_cong_id:
                raise exceptions.UserError(f'Chưa có tổng hợp công cho nhân viên {record.nhan_vien_id.name}!')
            
            # Lấy lương cơ bản và phụ cấp từ chức vụ
            if record.chuc_vu_id:
                record.luong_co_ban = record.chuc_vu_id.luong_co_ban
                record.phu_cap_chuc_vu = record.chuc_vu_id.phu_cap
            
            # Các field khác đã tự động tính qua @api.depends
