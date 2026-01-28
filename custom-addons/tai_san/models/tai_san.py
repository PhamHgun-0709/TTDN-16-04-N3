# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TaiSan(models.Model):
    _name = 'tai.san.tai.san'
    _description = 'Tài sản'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Tên tài sản', required=True, tracking=True)
    ma_tai_san = fields.Char(string='Mã tài sản', required=True, copy=False, tracking=True)
    loai_tai_san = fields.Selection([
        ('nha_dat', 'Nhà đất'),
        ('may_moc', 'Máy móc thiết bị'),
        ('phuong_tien', 'Phương tiện vận chuyển'),
        ('van_phong', 'Tài sản văn phòng'),
        ('khac', 'Khác')
    ], string='Loại tài sản', required=True, tracking=True)
    ngay_mua = fields.Date(string='Ngày mua', tracking=True)
    nguyen_gia = fields.Float(string='Nguyên giá', tracking=True)
    gia_tri_con_lai = fields.Float(string='Giá trị còn lại', compute='_compute_gia_tri_con_lai', store=True)
    thoi_gian_khau_hao = fields.Integer(string='Thời gian khấu hao (tháng)', tracking=True)
    ty_le_khau_hao = fields.Float(string='Tỷ lệ khấu hao (%)', tracking=True)
    
    # Liên kết với nhân sự
    nhan_vien_id = fields.Many2one('nhan.su.nhan.vien', string='Người sử dụng', ondelete='set null', tracking=True)
    phong_ban_id = fields.Many2one('nhan.su.phong.ban', string='Phòng ban sử dụng', ondelete='set null', tracking=True)
    nguoi_quan_ly_id = fields.Many2one('res.users', string='Người quản lý', tracking=True)
    
    vi_tri = fields.Char(string='Vị trí', tracking=True)
    tinh_trang = fields.Selection([
        ('chua_mua', 'Chưa mua'),
        ('dang_su_dung', 'Đang sử dụng'),
        ('thanh_ly', 'Đã thanh lý')
    ], string='Tình trạng', default='chua_mua', tracking=True)
    trang_thai = fields.Selection([
        ('tot', 'Tốt'),
        ('bao_tri', 'Đang bảo trì'),
        ('hong', 'Hỏng'),
        ('can_thay', 'Cần thay thế')
    ], string='Trạng thái', default='tot', tracking=True)
    
    # Liên kết ngược
    de_xuat_id = fields.Many2one('tai.san.de.xuat', string='Đề xuất', tracking=True)
    mua_tai_san_id = fields.Many2one('tai.san.mua.tai.san', string='Hóa đơn mua', tracking=True)
    cap_phat_ids = fields.One2many('tai.san.cap.phat', 'tai_san_id', string='Lịch sử cấp phát')
    # Liên kết khấu hao (chỉ dùng để truy vấn ngược, không lưu trên tài sản)
    # khau_hao_id = fields.Many2one('tai.chinh.ke.toan.khau.hao.tai.san', string='Khấu hao', tracking=True, readonly=True)
    ghi_chu = fields.Text(string='Ghi chú')
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('ma_tai_san_unique', 'UNIQUE(ma_tai_san)', 'Mã tài sản phải là duy nhất!')
    ]

    @api.depends('nguyen_gia', 'ty_le_khau_hao')
    def _compute_gia_tri_con_lai(self):
        for record in self:
            if record.nguyen_gia and record.ty_le_khau_hao:
                record.gia_tri_con_lai = record.nguyen_gia * (1 - record.ty_le_khau_hao / 100)
            else:
                record.gia_tri_con_lai = record.nguyen_gia
    
    @api.model_create_multi
    def create(self, vals_list):
        records = super(TaiSan, self).create(vals_list)
        
        # Tự động tạo khấu hao cho tài sản CÓ thời gian khấu hao
        for record in records:
            # Chỉ tạo khấu hao cho tài sản có giá trị và thời gian khấu hao
            if record.thoi_gian_khau_hao > 0 and record.nguyen_gia > 0:
                khau_hao = self.env['tai.chinh.ke.toan.khau.hao.tai.san'].create({
                    'tai_san_id': record.id,
                    'nguyen_gia': record.nguyen_gia,
                    'gia_tri_con_lai': record.gia_tri_con_lai,
                    'thoi_gian_khau_hao': record.thoi_gian_khau_hao,
                    'ngay_bat_dau_khau_hao': record.ngay_mua or fields.Date.today(),
                    'phuong_phap_khau_hao': 'duong_thang',
                })
                # Không lưu khau_hao_id vào record để tránh dependency loop
        
        return records
