# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BaoCaoSoQuy(models.TransientModel):
    _name = 'tai.chinh.ke.toan.bao.cao.so.quy'
    _description = 'Báo cáo sổ quỹ'

    tu_ngay = fields.Date(string='Từ ngày', required=True, default=fields.Date.today)
    den_ngay = fields.Date(string='Đến ngày', required=True, default=fields.Date.today)
    hinh_thuc = fields.Selection([
        ('tien_mat', 'Tiền mặt'),
        ('chuyen_khoan', 'Chuyển khoản'),
        ('the', 'Thẻ'),
        ('tat_ca', 'Tất cả'),
    ], string='Hình thức', default='tat_ca', required=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)

    def action_xem_bao_cao(self):
        """Hiển thị báo cáo sổ quỹ"""
        self.ensure_one()
        
        domain = [
            ('ngay_ghi_so', '>=', self.tu_ngay),
            ('ngay_ghi_so', '<=', self.den_ngay),
            ('company_id', '=', self.company_id.id),
        ]
        
        if self.hinh_thuc != 'tat_ca':
            domain.append(('hinh_thuc', '=', self.hinh_thuc))
        
        return {
            'name': _('Sổ quỹ'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'tai.chinh.ke.toan.so.quy',
            'domain': domain,
            'context': {
                'default_tu_ngay': self.tu_ngay,
                'default_den_ngay': self.den_ngay,
                'search_default_group_by_ngay': 1,
            }
        }

    def action_in_bao_cao(self):
        """In báo cáo sổ quỹ - TODO"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Thông báo'),
                'message': _('Chức năng in báo cáo đang được phát triển!'),
                'type': 'warning',
            }
        }
