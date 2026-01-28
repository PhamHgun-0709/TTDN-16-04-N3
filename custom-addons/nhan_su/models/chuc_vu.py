# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ChucVu(models.Model):
    _name = 'nhan.su.chuc.vu'
    _description = 'Chức vụ'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Tên chức vụ', required=True, tracking=True)
    ma_chuc_vu = fields.Char(string='Mã chức vụ', required=True, copy=False, tracking=True)
    cap_bac = fields.Selection([
        ('nhan_vien', 'Nhân viên'),
        ('truong_nhom', 'Trưởng nhóm'),
        ('truong_phong', 'Trưởng phòng'),
        ('pho_phong', 'Phó phòng'),
        ('giam_doc', 'Giám đốc'),
        ('pho_giam_doc', 'Phó giám đốc')
    ], string='Cấp bậc', tracking=True)
    luong_co_ban = fields.Float(string='Lương cơ bản', tracking=True)
    phu_cap = fields.Float(string='Phụ cấp', tracking=True)
    mo_ta = fields.Text(string='Mô tả')
    nhan_vien_ids = fields.One2many('nhan.su.nhan.vien', 'chuc_vu_id', string='Nhân viên')
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('ma_chuc_vu_unique', 'UNIQUE(ma_chuc_vu)', 'Mã chức vụ phải là duy nhất!')
    ]

    @api.constrains('luong_co_ban', 'phu_cap')
    def _check_luong_phu_cap(self):
        """Kiểm tra lương và phụ cấp không âm"""
        for record in self:
            if record.luong_co_ban < 0:
                raise models.ValidationError('Lương cơ bản không được âm!')
            if record.phu_cap < 0:
                raise models.ValidationError('Phụ cấp không được âm!')
