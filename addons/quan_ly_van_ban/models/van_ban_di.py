# -*- coding: utf-8 -*-
from odoo import models, fields, api

class VanBanDi(models.Model):
    """Quản lý văn bản đi của cơ quan"""
    
    _name = 'van.ban.di'
    _description = 'Văn bản đi'
    _order = 'ngay_ban_hanh desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Kích hoạt chatter & activity

    # === THÔNG TIN CƠ BẢN ===
    so_van_ban = fields.Char('Số văn bản', required=True, copy=False, readonly=True, 
                              default='New', tracking=True)
    so_ky_hieu = fields.Char('Số ký hiệu', required=True, tracking=True)
    ngay_ban_hanh = fields.Date('Ngày ban hành', required=True, 
                                 default=fields.Date.today, tracking=True)
    
    # === PHÂN LOẠI & NỘI DUNG ===
    loai_van_ban_id = fields.Many2one('loai.van.ban', 'Loại văn bản', 
                                       required=True, tracking=True)
    trich_yeu = fields.Char('Trích yếu', required=True, tracking=True)
    noi_nhan = fields.Char('Nơi nhận', required=True, tracking=True)
    noi_dung = fields.Text('Nội dung')
    
    # === NGƯỜI LIÊN QUAN ===
    nguoi_ky_id = fields.Many2one('res.users', 'Người ký', tracking=True)
    nguoi_soan_id = fields.Many2one('res.users', 'Người soạn', 
                                     default=lambda self: self.env.user, tracking=True)
    
    # === TRẠNG THÁI ===
    trang_thai = fields.Selection([
        ('du_thao', 'Dự thảo'),
        ('cho_duyet', 'Chờ duyệt'),
        ('da_duyet', 'Đã duyệt'),
        ('da_ban_hanh', 'Đã ban hành'),
    ], 'Trạng thái', default='du_thao', tracking=True)
    
    ghi_chu = fields.Text('Ghi chú')
    
    @api.model_create_multi
    def create(self, vals_list):
        """Tự động tạo số văn bản theo sequence"""
        for vals in vals_list:
            if vals.get('so_van_ban', 'New') == 'New':
                vals['so_van_ban'] = self.env['ir.sequence'].next_by_code('van.ban.di') or 'New'
        return super(VanBanDi, self).create(vals_list)
