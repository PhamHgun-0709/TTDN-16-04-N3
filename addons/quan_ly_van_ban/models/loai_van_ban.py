# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LoaiVanBan(models.Model):
    """Danh mục loại văn bản (CV, QD, TB...)"""
    
    _name = 'loai.van.ban'
    _description = 'Loại văn bản'
    _order = 'ten_loai'

    # === FIELDS ===
    ten_loai = fields.Char('Tên loại văn bản', required=True)
    ma_loai = fields.Char('Mã loại', required=True)  # CV, QD, TB...
    mo_ta = fields.Text('Mô tả')
    active = fields.Boolean('Hoạt động', default=True)
    
    # === CONSTRAINTS ===
    @api.constrains('ma_loai')
    def _check_ma_loai_unique(self):
        """Kiểm tra mã loại không trùng lặp"""
        for record in self:
            if self.search_count([('ma_loai', '=', record.ma_loai), ('id', '!=', record.id)]) > 0:
                raise ValidationError('Mã loại văn bản phải là duy nhất!')
