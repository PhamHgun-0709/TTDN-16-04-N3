# -*- coding: utf-8 -*-
from odoo import models, fields, api

class VanBanDen(models.Model):
    """Quản lý văn bản đến của cơ quan"""
    
    _name = 'van.ban.den'
    _description = 'Văn bản đến'
    _order = 'ngay_den desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Kích hoạt chatter & activity

    # === THÔNG TIN CƠ BẢN ===
    so_den = fields.Char('Số đến', required=True, copy=False, readonly=True, 
                         default='New', tracking=True)
    so_ky_hieu = fields.Char('Số ký hiệu', required=True, tracking=True)
    ngay_den = fields.Date('Ngày đến', required=True, 
                           default=fields.Date.today, tracking=True)
    ngay_ban_hanh = fields.Date('Ngày ban hành', tracking=True)
    
    # === PHÂN LOẠI & NỘI DUNG ===
    loai_van_ban_id = fields.Many2one('loai.van.ban', 'Loại văn bản', 
                                       required=True, tracking=True)
    trich_yeu = fields.Char('Trích yếu', required=True, tracking=True)
    noi_gui = fields.Char('Nơi gửi', tracking=True)
    noi_dung = fields.Text('Nội dung')
    
    # === NGƯỜI LIÊN QUAN ===
    nguoi_nhan_id = fields.Many2one('res.users', 'Người nhận', 
                                     default=lambda self: self.env.user, tracking=True)
    
    # === TRẠNG THÁI ===
    trang_thai = fields.Selection([
        ('chua_xu_ly', 'Chưa xử lý'),
        ('dang_xu_ly', 'Đang xử lý'),
        ('da_xu_ly', 'Đã xử lý'),
    ], 'Trạng thái', default='chua_xu_ly', tracking=True)
    
    ghi_chu = fields.Text('Ghi chú')
    
    @api.model_create_multi
    def create(self, vals_list):
        """Tự động tạo số đến theo sequence"""
        for vals in vals_list:
            if vals.get('so_den', 'New') == 'New':
                vals['so_den'] = self.env['ir.sequence'].next_by_code('van.ban.den') or 'New'
        return super(VanBanDen, self).create(vals_list)
