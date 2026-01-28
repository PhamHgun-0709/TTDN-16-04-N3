# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PhongBan(models.Model):
    _name = 'nhan.su.phong.ban'
    _description = 'Phòng ban'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Tên phòng ban', required=True, tracking=True)
    ma_phong_ban = fields.Char(string='Mã phòng ban', required=True, copy=False, tracking=True)
    truong_phong_id = fields.Many2one('nhan.su.nhan.vien', string='Trưởng phòng', ondelete='set null', tracking=True)
    phong_ban_cha_id = fields.Many2one('nhan.su.phong.ban', string='Phòng ban cấp trên', ondelete='restrict', tracking=True)
    mo_ta = fields.Text(string='Mô tả')
    nhan_vien_ids = fields.One2many('nhan.su.nhan.vien', 'phong_ban_id', string='Nhân viên')
    so_luong_nhan_vien = fields.Integer(string='Số lượng nhân viên', compute='_compute_so_luong_nhan_vien', store=True)
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('ma_phong_ban_unique', 'UNIQUE(ma_phong_ban)', 'Mã phòng ban phải là duy nhất!')
    ]

    @api.depends('nhan_vien_ids')
    def _compute_so_luong_nhan_vien(self):
        for record in self:
            record.so_luong_nhan_vien = len(record.nhan_vien_ids)
