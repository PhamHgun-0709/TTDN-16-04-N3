# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PheDuyet(models.Model):
    _name = 'tai.san.phe.duyet'
    _description = 'Phê duyệt'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'ngay_phe_duyet desc'

    name = fields.Char(string='Số phê duyệt', required=True, copy=False, default='New', tracking=True)
    de_xuat_id = fields.Many2one('tai.san.de.xuat', string='Đề xuất tài sản', required=True, ondelete='cascade', tracking=True)
    cap_duyet = fields.Selection([
        ('cap_1', 'Cấp 1 - Trưởng phòng'),
        ('cap_2', 'Cấp 2 - Giám đốc'),
        ('cap_3', 'Cấp 3 - Tổng giám đốc')
    ], string='Cấp duyệt', required=True, tracking=True)
    nhan_vien_id = fields.Many2one('nhan.su.nhan.vien', string='Người phê duyệt', ondelete='set null', tracking=True, 
                                     domain="[('chuc_vu_id.name', 'ilike', chuc_vu_filter)]")
    chuc_vu_filter = fields.Char(string='Chức vụ filter', compute='_compute_chuc_vu_filter', store=False)
    ngay_phe_duyet = fields.Datetime(string='Ngày phê duyệt', tracking=True)
    
    ket_qua = fields.Selection([
        ('cho_duyet', 'Chờ duyệt'),
        ('dong_y', 'Đồng ý'),
        ('tu_choi', 'Từ chối'),
        ('yeu_cau_bo_sung', 'Yêu cầu bổ sung')
    ], string='Kết quả', default='cho_duyet', tracking=True)
    
    so_tien_duyet = fields.Float(string='Số tiền được duyệt', tracking=True)
    y_kien = fields.Text(string='Ý kiến', tracking=True)
    ghi_chu = fields.Text(string='Ghi chú')
    active = fields.Boolean(string='Active', default=True)

    @api.depends('cap_duyet')
    def _compute_chuc_vu_filter(self):
        """Tính toán filter chức vụ dựa trên cấp duyệt"""
        for record in self:
            if record.cap_duyet == 'cap_1':
                record.chuc_vu_filter = 'Trưởng phòng'
            elif record.cap_duyet == 'cap_2':
                record.chuc_vu_filter = 'Giám đốc'
            elif record.cap_duyet == 'cap_3':
                record.chuc_vu_filter = 'Tổng giám đốc'
            else:
                record.chuc_vu_filter = ''

    @api.onchange('cap_duyet')
    def _onchange_cap_duyet(self):
        """Xóa người phê duyệt khi thay đổi cấp duyệt"""
        self.nhan_vien_id = False
        # Trả về domain để lọc nhân viên theo chức vụ
        if self.cap_duyet == 'cap_1':
            chuc_vu_name = 'Trưởng phòng'
        elif self.cap_duyet == 'cap_2':
            chuc_vu_name = 'Giám đốc'
        elif self.cap_duyet == 'cap_3':
            chuc_vu_name = 'Tổng giám đốc'
        else:
            return {'domain': {'nhan_vien_id': []}}
        
        return {
            'domain': {
                'nhan_vien_id': [('chuc_vu_id.name', 'ilike', chuc_vu_name)]
            }
        }

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('tai.san.phe.duyet') or 'PD/%(year)s/%(month)s'
        return super(PheDuyet, self).create(vals)

    def action_dong_y(self):
        self.write({
            'ket_qua': 'dong_y',
            'nhan_vien_id': self.env.user.id,
            'ngay_phe_duyet': fields.Datetime.now()
        })

    def action_tu_choi(self):
        self.write({
            'ket_qua': 'tu_choi',
            'nhan_vien_id': self.env.user.id,
            'ngay_phe_duyet': fields.Datetime.now()
        })
