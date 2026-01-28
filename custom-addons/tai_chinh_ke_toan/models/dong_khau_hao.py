# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DongKhauHao(models.Model):
    _name = 'tai.chinh.ke.toan.dong.khau.hao'
    _description = 'Dòng khấu hao'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'nam desc, thang desc'

    name = fields.Char(string='Mã dòng khấu hao', compute='_compute_name', store=True, readonly=True)
    khau_hao_id = fields.Many2one('tai.chinh.ke.toan.khau.hao.tai.san', string='Khấu hao tài sản', required=True, ondelete='cascade', tracking=True)
    tai_san_id = fields.Many2one(related='khau_hao_id.tai_san_id', string='Tài sản', store=True)
    
    thang = fields.Selection([
        ('1', 'Tháng 1'), ('2', 'Tháng 2'), ('3', 'Tháng 3'),
        ('4', 'Tháng 4'), ('5', 'Tháng 5'), ('6', 'Tháng 6'),
        ('7', 'Tháng 7'), ('8', 'Tháng 8'), ('9', 'Tháng 9'),
        ('10', 'Tháng 10'), ('11', 'Tháng 11'), ('12', 'Tháng 12')
    ], string='Tháng', required=True, tracking=True)
    nam = fields.Char(string='Năm', required=True, tracking=True)
    ngay_khau_hao = fields.Date(string='Ngày khấu hao', required=True, default=fields.Date.today, tracking=True)
    
    so_tien_khau_hao = fields.Float(string='Số tiền khấu hao', required=True, tracking=True)
    gia_tri_con_lai = fields.Float(string='Giá trị còn lại', tracking=True)
    
    tai_khoan_no = fields.Many2one('account.account', string='TK Nợ', tracking=True)
    tai_khoan_co = fields.Many2one('account.account', string='TK Có', tracking=True)
    
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('da_ghi_nhan', 'Đã ghi nhận'),
        ('huy', 'Đã hủy')
    ], string='Trạng thái', default='nhap', tracking=True)
    
    ghi_chu = fields.Text(string='Ghi chú')
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('unique_khau_hao_thang_nam', 'UNIQUE(khau_hao_id, thang, nam)', 
         'Mỗi tài sản chỉ được khấu hao một lần trong tháng!')
    ]

    @api.depends('khau_hao_id', 'thang', 'nam')
    def _compute_name(self):
        for record in self:
            if record.khau_hao_id and record.thang and record.nam:
                record.name = f"{record.khau_hao_id.name}/T{record.thang}/{record.nam}"
            else:
                record.name = 'New'

    def action_ghi_nhan(self):
        self.write({'trang_thai': 'da_ghi_nhan'})

    def action_huy(self):
        self.write({'trang_thai': 'huy'})
