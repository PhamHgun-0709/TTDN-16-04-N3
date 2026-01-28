# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CapPhatTaiSan(models.Model):
    _name = 'tai.san.cap.phat'
    _description = 'Cấp phát tài sản'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'ngay_cap_phat desc'

    name = fields.Char(string='Số cấp phát', required=True, copy=False, readonly=True, default='New', tracking=True)
    de_xuat_id = fields.Many2one('tai.san.de.xuat', string='Đề xuất tài sản', tracking=True)
    ngay_cap_phat = fields.Date(string='Ngày cấp phát', default=fields.Date.today, required=True, tracking=True)
    
    tai_san_id = fields.Many2one('tai.san.tai.san', string='Tài sản', required=True, ondelete='restrict', tracking=True)
    nhan_vien_id = fields.Many2one('nhan.su.nhan.vien', string='Người nhận', required=True, ondelete='restrict', tracking=True)
    phong_ban_id = fields.Many2one('nhan.su.phong.ban', string='Phòng ban nhận', ondelete='restrict', tracking=True)
    
    so_luong = fields.Integer(string='Số lượng', default=1, tracking=True)
    gia_tri = fields.Float(string='Giá trị', tracking=True)
    
    loai_cap_phat = fields.Selection([
        ('mua_moi', 'Mua mới'),
        ('dieu_chuyen', 'Điều chuyển'),
        ('thay_the', 'Thay thế')
    ], string='Loại cấp phát', default='mua_moi', tracking=True)
    
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('cho_nhan', 'Chờ nhận'),
        ('da_nhan', 'Đã nhận'),
        ('huy', 'Đã hủy')
    ], string='Trạng thái', default='nhap', tracking=True)
    
    ngay_nhan = fields.Date(string='Ngày nhận', tracking=True)
    nguoi_giao_id = fields.Many2one('res.users', string='Người giao', tracking=True)
    bien_ban_ban_giao = fields.Text(string='Biên bản bàn giao')
    ghi_chu = fields.Text(string='Ghi chú')
    active = fields.Boolean(string='Active', default=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('tai.san.cap.phat') or 'CP/%(year)s/%(month)s'
        return super(CapPhatTaiSan, self).create(vals_list)

    def action_gui_nhan(self):
        self.write({'trang_thai': 'cho_nhan'})

    def action_xac_nhan_nhan(self):
        self.write({
            'trang_thai': 'da_nhan',
            'ngay_nhan': fields.Date.today()
        })

    def action_huy(self):
        self.write({'trang_thai': 'huy'})
