# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ThayTheTaiSan(models.Model):
    _name = 'tai.san.thay.the'
    _description = 'Thay thế tài sản'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'ngay_de_xuat desc'

    name = fields.Char(string='Số đề xuất thay thế', required=True, copy=False, readonly=True, default='New', tracking=True)
    ngay_de_xuat = fields.Date(string='Ngày đề xuất', default=fields.Date.today, required=True, tracking=True)
    nhan_vien_id = fields.Many2one('nhan.su.nhan.vien', string='Người đề xuất', required=True, ondelete='restrict', tracking=True)
    phong_ban_id = fields.Many2one('nhan.su.phong.ban', string='Phòng ban', ondelete='restrict', tracking=True)
    
    # Tài sản cũ
    tai_san_cu_id = fields.Many2one('tai.san.tai.san', string='Tài sản cũ', required=True, tracking=True)
    ly_do = fields.Selection([
        ('hao_nhieu', 'Hao nhiều'),
        ('het_han', 'Hết hạn sử dụng'),
        ('hong', 'Hỏng hóc')
    ], string='Lý do thay thế', required=True, tracking=True)
    tinh_trang_tai_san_cu = fields.Text(string='Tình trạng tài sản cũ', tracking=True)
    
    # Tài sản mới
    ten_tai_san_moi = fields.Char(string='Tên tài sản mới', required=True, tracking=True)
    loai_tai_san_moi = fields.Selection([
        ('nha_dat', 'Nhà đất'),
        ('may_moc', 'Máy móc thiết bị'),
        ('phuong_tien', 'Phương tiện vận chuyển'),
        ('van_phong', 'Tài sản văn phòng'),
        ('khac', 'Khác')
    ], string='Loại tài sản mới', required=True, tracking=True)
    gia_tri_du_kien = fields.Float(string='Giá trị dự kiến', tracking=True)
    tai_san_moi_id = fields.Many2one('tai.san.tai.san', string='Tài sản mới', tracking=True)
    
    # Xử lý tài sản cũ
    hinh_thuc_xu_ly = fields.Selection([
        ('thanh_ly', 'Thanh lý'),
        ('ban', 'Bán'),
        ('huy', 'Hủy'),
        ('chuyen_nhuong', 'Chuyển nhượng')
    ], string='Hình thức xử lý tài sản cũ', tracking=True)
    gia_tri_xu_ly = fields.Float(string='Giá trị xử lý', tracking=True)
    
    trang_thai = fields.Selection([
        ('de_xuat', 'Đề xuất'),
        ('cho_duyet', 'Chờ duyệt'),
        ('da_duyet', 'Đã duyệt'),
        ('tu_choi', 'Từ chối'),
        ('da_thay', 'Đã thay'),
        ('huy', 'Đã hủy')
    ], string='Trạng thái', default='de_xuat', tracking=True)
    
    ngay_thay_the = fields.Date(string='Ngày thay thế', tracking=True)
    cap_phat_id = fields.Many2one('tai.san.cap.phat', string='Cấp phát', tracking=True)
    ghi_chu = fields.Text(string='Ghi chú')
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('tai.san.thay.the') or 'TT/%(year)s/%(month)s'
        return super(ThayTheTaiSan, self).create(vals)

    def action_gui_duyet(self):
        self.write({'trang_thai': 'cho_duyet'})

    def action_duyet(self):
        self.write({'trang_thai': 'da_duyet'})

    def action_tu_choi(self):
        self.write({'trang_thai': 'tu_choi'})

    def action_hoan_thanh(self):
        self.write({
            'trang_thai': 'da_thay',
            'ngay_thay_the': fields.Date.today()
        })
