# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DeXuatTaiSan(models.Model):
    _name = 'tai.san.de.xuat'
    _description = 'Đề xuất tài sản'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'ngay_de_xuat desc'

    name = fields.Char(string='Số đề xuất', required=True, copy=False, readonly=True, default='New', tracking=True)
    ngay_de_xuat = fields.Date(string='Ngày đề xuất', default=fields.Date.today, required=True, tracking=True)
    nhan_vien_id = fields.Many2one('nhan.su.nhan.vien', string='Người đề xuất', required=True, ondelete='restrict', tracking=True)
    phong_ban_id = fields.Many2one('nhan.su.phong.ban', string='Phòng ban', ondelete='restrict', tracking=True)
    
    # Thông tin tài sản đề xuất
    ten_tai_san = fields.Char(string='Tên tài sản', required=True, tracking=True)
    loai_tai_san = fields.Selection([
        ('nha_dat', 'Nhà đất'),
        ('may_moc', 'Máy móc thiết bị'),
        ('phuong_tien', 'Phương tiện vận chuyển'),
        ('van_phong', 'Tài sản văn phòng'),
        ('khac', 'Khác')
    ], string='Loại tài sản', required=True, tracking=True)
    so_luong = fields.Integer(string='Số lượng', default=1, tracking=True)
    don_gia_du_kien = fields.Float(string='Đơn giá dự kiến', tracking=True)
    thanh_tien = fields.Float(string='Thành tiền', compute='_compute_thanh_tien', store=True)
    
    # Lý do và mục đích
    ly_do = fields.Text(string='Lý do đề xuất', required=True, tracking=True)
    muc_dich_su_dung = fields.Text(string='Mục đích sử dụng', tracking=True)
    han_mua = fields.Date(string='Hạn mua dự kiến', tracking=True)
    
    # Trạng thái
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('cho_duyet', 'Chờ duyệt'),
        ('da_duyet', 'Đã duyệt'),
        ('tu_choi', 'Từ chối'),
        ('huy', 'Đã hủy')
    ], string='Trạng thái', default='nhap', tracking=True)
    
    phe_duyet_ids = fields.One2many('tai.san.phe.duyet', 'de_xuat_id', string='Phê duyệt')
    ung_tien_ids = fields.One2many('tai.san.ung.tien', 'de_xuat_id', string='Ứng tiền')
    cap_phat_id = fields.Many2one('tai.san.cap.phat', string='Cấp phát', tracking=True)
    
    ghi_chu = fields.Text(string='Ghi chú')
    active = fields.Boolean(string='Active', default=True)

    @api.depends('so_luong', 'don_gia_du_kien')
    def _compute_thanh_tien(self):
        for record in self:
            record.thanh_tien = record.so_luong * record.don_gia_du_kien

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('tai.san.de.xuat') or 'DX/%(year)s/%(month)s'
        return super(DeXuatTaiSan, self).create(vals_list)

    def action_gui_duyet(self):
        self.write({'trang_thai': 'cho_duyet'})

    def action_duyet(self):
        self.write({'trang_thai': 'da_duyet'})

    def action_tu_choi(self):
        self.write({'trang_thai': 'tu_choi'})

    def action_huy(self):
        self.write({'trang_thai': 'huy'})
