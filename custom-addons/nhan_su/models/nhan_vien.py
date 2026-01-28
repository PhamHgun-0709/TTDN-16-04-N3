# -*- coding: utf-8 -*-

from odoo import models, fields, api


class NhanVien(models.Model):
    _name = 'nhan.su.nhan.vien'
    _description = 'Nhân viên'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Họ và tên', required=True, tracking=True)
    ma_nhan_vien = fields.Char(string='Mã nhân viên', required=True, copy=False, readonly=True, default='New', tracking=True)
    ngay_sinh = fields.Date(string='Ngày sinh', tracking=True)
    gioi_tinh = fields.Selection([
        ('nam', 'Nam'),
        ('nu', 'Nữ'),
        ('khac', 'Khác')
    ], string='Giới tính', tracking=True)
    so_dien_thoai = fields.Char(string='Số điện thoại', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    dia_chi = fields.Text(string='Địa chỉ', tracking=True)
    phong_ban_id = fields.Many2one('nhan.su.phong.ban', string='Phòng ban', required=True, ondelete='restrict', tracking=True)
    chuc_vu_id = fields.Many2one('nhan.su.chuc.vu', string='Chức vụ', required=True, ondelete='restrict', tracking=True)
    ca_lam_viec_id = fields.Many2one('nhan.su.ca.lam.viec', string='Ca làm việc', tracking=True)
    ngay_vao_lam = fields.Date(string='Ngày vào làm', tracking=True)
    luong_co_ban = fields.Float(string='Lương cơ bản', related='chuc_vu_id.luong_co_ban', store=True, readonly=True)
    trang_thai = fields.Selection([
        ('dang_lam', 'Đang làm việc'),
        ('nghi_viec', 'Nghỉ việc'),
        ('tam_nghi', 'Tạm nghỉ')
    ], string='Trạng thái', default='dang_lam', tracking=True)
    ghi_chu = fields.Text(string='Ghi chú')
    active = fields.Boolean(string='Active', default=True)
    
    # Smart Buttons - Liên kết với chấm công và lương
    so_ban_cham_cong = fields.Integer(string='Số bản chấm công', compute='_compute_cham_cong_count')
    so_tong_hop_cong = fields.Integer(string='Số tổng hợp công', compute='_compute_tong_hop_cong_count')
    so_phieu_luong = fields.Integer(string='Số phiếu lương', compute='_compute_phieu_luong_count')

    _sql_constraints = [
        ('ma_nhan_vien_unique', 'UNIQUE(ma_nhan_vien)', 'Mã nhân viên phải là duy nhất!')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('ma_nhan_vien', 'New') == 'New':
                vals['ma_nhan_vien'] = self.env['ir.sequence'].next_by_code('nhan.su.nhan.vien') or 'New'
        return super(NhanVien, self).create(vals_list)
    
    def _compute_cham_cong_count(self):
        """Tối ưu bằng read_group thay vì search_count nhiều lần"""
        if not self.ids:
            for record in self:
                record.so_ban_cham_cong = 0
            return
        
        cham_cong_data = self.env['nhan.su.cham.cong'].read_group(
            [('nhan_vien_id', 'in', self.ids)],
            ['nhan_vien_id'],
            ['nhan_vien_id']
        )
        mapped_data = {item['nhan_vien_id'][0]: item['nhan_vien_id_count'] for item in cham_cong_data}
        for record in self:
            record.so_ban_cham_cong = mapped_data.get(record.id, 0)
    
    def _compute_tong_hop_cong_count(self):
        """Tối ưu bằng read_group thay vì search_count nhiều lần"""
        if not self.ids:
            for record in self:
                record.so_tong_hop_cong = 0
            return
        
        tong_hop_data = self.env['nhan.su.tong.hop.cong'].read_group(
            [('nhan_vien_id', 'in', self.ids)],
            ['nhan_vien_id'],
            ['nhan_vien_id']
        )
        mapped_data = {item['nhan_vien_id'][0]: item['nhan_vien_id_count'] for item in tong_hop_data}
        for record in self:
            record.so_tong_hop_cong = mapped_data.get(record.id, 0)
    
    def _compute_phieu_luong_count(self):
        """Tối ưu bằng read_group thay vì search_count nhiều lần"""
        if not self.ids:
            for record in self:
                record.so_phieu_luong = 0
            return
        
        luong_data = self.env['nhan.su.chi.tiet.luong'].read_group(
            [('nhan_vien_id', 'in', self.ids)],
            ['nhan_vien_id'],
            ['nhan_vien_id']
        )
        mapped_data = {item['nhan_vien_id'][0]: item['nhan_vien_id_count'] for item in luong_data}
        for record in self:
            record.so_phieu_luong = mapped_data.get(record.id, 0)

    @api.constrains('trang_thai', 'ca_lam_viec_id')
    def _check_trang_thai_ca_lam_viec(self):
        """Nhân viên đang làm việc phải có ca làm việc"""
        for record in self:
            if record.trang_thai == 'dang_lam' and not record.ca_lam_viec_id:
                raise models.ValidationError('Nhân viên đang làm việc phải được phân công ca làm việc!')
