# -*- coding: utf-8 -*-

from odoo import models, fields


class NgayLamViec(models.Model):
    _name = 'nhan.su.ngay.lam.viec'
    _description = 'Ngày làm việc trong tuần'
    _order = 'thu_tu'

    name = fields.Char(string='Tên ngày', required=True)
    ma_ngay = fields.Char(string='Mã ngày', required=True)
    thu_tu = fields.Integer(string='Thứ tự', required=True, help='1=Thứ 2, 2=Thứ 3, ..., 7=Chủ nhật')
    la_ngay_lam_viec = fields.Boolean(string='Là ngày làm việc', default=True,
                                       help='Thứ 2-6 là ngày làm việc, Thứ 7-CN là nghỉ')
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('ma_ngay_unique', 'UNIQUE(ma_ngay)', 'Mã ngày phải là duy nhất!')
    ]
