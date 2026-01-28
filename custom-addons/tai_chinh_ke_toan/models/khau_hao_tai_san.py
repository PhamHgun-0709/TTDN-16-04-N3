# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class KhauHaoTaiSan(models.Model):
    _name = 'tai.chinh.ke.toan.khau.hao.tai.san'
    _description = 'Khấu hao tài sản'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'ngay_bat_dau_khau_hao desc'

    name = fields.Char(string='Mã khấu hao', required=True, copy=False, readonly=True, default='New', tracking=True)
    tai_san_id = fields.Many2one('tai.san.tai.san', string='Tài sản', required=True, ondelete='restrict', tracking=True)
    
    # Thông tin khấu hao
    phuong_phap_khau_hao = fields.Selection([
        ('duong_thang', 'Đường thẳng'),
        ('so_du_giam_dan', 'Số dư giảm dần'),
        ('so_luong_san_pham', 'Số lượng sản phẩm')
    ], string='Phương pháp khấu hao', default='duong_thang', required=True, tracking=True)
    
    nguyen_gia = fields.Float(string='Nguyên giá', required=True, tracking=True)
    gia_tri_con_lai = fields.Float(string='Giá trị còn lại', tracking=True)
    gia_tri_thu_hoi = fields.Float(string='Giá trị thu hồi', default=0, tracking=True)
    
    thoi_gian_khau_hao = fields.Integer(string='Thời gian khấu hao (tháng)', required=True, tracking=True)
    thoi_gian_su_dung = fields.Integer(string='Thời gian đã sử dụng (tháng)', compute='_compute_thoi_gian_su_dung', store=True)
    da_khau_hao = fields.Integer(string='Đã khấu hao (tháng)', default=0, tracking=True)
    con_lai = fields.Integer(string='Còn lại (tháng)', compute='_compute_con_lai', store=True)
    
    muc_do_hao = fields.Selection([
        ('it', 'Ít'),
        ('vua', 'Vừa'),
        ('nhieu', 'Nhiều')
    ], string='Mức độ hao', compute='_compute_muc_do_hao', store=True, tracking=True)
    
    ngay_bat_dau_khau_hao = fields.Date(string='Ngày bắt đầu khấu hao', required=True, tracking=True)
    ngay_ket_thuc_khau_hao = fields.Date(string='Ngày kết thúc khấu hao', compute='_compute_ngay_ket_thuc', store=True)
    
    khau_hao_hang_thang = fields.Float(string='Khấu hao hàng tháng', compute='_compute_khau_hao_hang_thang', store=True)
    tong_khau_hao = fields.Float(string='Tổng đã khấu hao', compute='_compute_tong_khau_hao', store=True)
    gia_tri_con_lai_computed = fields.Float(string='Giá trị còn lại (tính)', compute='_compute_tong_khau_hao', store=True)
    
    dong_khau_hao_ids = fields.One2many('tai.chinh.ke.toan.dong.khau.hao', 'khau_hao_id', string='Dòng khấu hao')
    
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('dang_khau_hao', 'Đang khấu hao'),
        ('tam_dung', 'Tạm dừng'),
        ('can_thay', 'Cần thay'),
        ('ket_thuc', 'Kết thúc')
    ], string='Trạng thái', default='nhap', tracking=True)
    
    ghi_chu = fields.Text(string='Ghi chú')
    active = fields.Boolean(string='Active', default=True)

    @api.depends('thoi_gian_khau_hao', 'da_khau_hao')
    def _compute_con_lai(self):
        for record in self:
            record.con_lai = record.thoi_gian_khau_hao - record.da_khau_hao

    @api.depends('ngay_bat_dau_khau_hao')
    def _compute_thoi_gian_su_dung(self):
        for record in self:
            if record.ngay_bat_dau_khau_hao:
                today = fields.Date.today()
                delta = relativedelta(today, record.ngay_bat_dau_khau_hao)
                record.thoi_gian_su_dung = delta.years * 12 + delta.months
            else:
                record.thoi_gian_su_dung = 0

    @api.depends('gia_tri_con_lai_computed', 'nguyen_gia')
    def _compute_muc_do_hao(self):
        for record in self:
            if record.nguyen_gia > 0:
                ty_le = (record.nguyen_gia - record.gia_tri_con_lai_computed) / record.nguyen_gia * 100
                if ty_le < 30:
                    record.muc_do_hao = 'it'
                elif ty_le < 70:
                    record.muc_do_hao = 'vua'
                else:
                    record.muc_do_hao = 'nhieu'
                    # Cảnh báo cần thay thế
                    if ty_le >= 90 and record.trang_thai == 'dang_khau_hao':
                        record.trang_thai = 'can_thay'
            else:
                record.muc_do_hao = False

    @api.depends('thoi_gian_khau_hao', 'da_khau_hao')
    def _compute_con_lai(self):
        for record in self:
            record.con_lai = record.thoi_gian_khau_hao - record.da_khau_hao

    @api.depends('ngay_bat_dau_khau_hao', 'thoi_gian_khau_hao')
    def _compute_ngay_ket_thuc(self):
        for record in self:
            if record.ngay_bat_dau_khau_hao and record.thoi_gian_khau_hao:
                record.ngay_ket_thuc_khau_hao = record.ngay_bat_dau_khau_hao + relativedelta(months=record.thoi_gian_khau_hao)
            else:
                record.ngay_ket_thuc_khau_hao = False

    @api.depends('nguyen_gia', 'gia_tri_thu_hoi', 'thoi_gian_khau_hao', 'phuong_phap_khau_hao')
    def _compute_khau_hao_hang_thang(self):
        for record in self:
            if record.phuong_phap_khau_hao == 'duong_thang' and record.thoi_gian_khau_hao > 0:
                record.khau_hao_hang_thang = (record.nguyen_gia - record.gia_tri_thu_hoi) / record.thoi_gian_khau_hao
            else:
                record.khau_hao_hang_thang = 0

    @api.depends('dong_khau_hao_ids.so_tien_khau_hao')
    def _compute_tong_khau_hao(self):
        for record in self:
            record.tong_khau_hao = sum(record.dong_khau_hao_ids.mapped('so_tien_khau_hao'))
            record.gia_tri_con_lai_computed = record.nguyen_gia - record.tong_khau_hao

    @api.model
    def create(self, vals_list):
        if not isinstance(vals_list, list):
            vals_list = [vals_list]
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('tai.chinh.ke.toan.khau.hao.tai.san') or 'KH/%(year)s/%(month)s'
        return super(KhauHaoTaiSan, self).create(vals_list)

    def action_bat_dau_khau_hao(self):
        self.write({'trang_thai': 'dang_khau_hao'})

    def action_tam_dung(self):
        self.write({'trang_thai': 'tam_dung'})

    def action_ket_thuc(self):
        self.write({'trang_thai': 'ket_thuc'})

    def action_tao_dong_khau_hao_thang(self):
        """Tạo dòng khấu hao cho tháng hiện tại"""
        today = fields.Date.today()
        # Kiểm tra đã có dòng khấu hao tháng này chưa
        existing = self.env['tai.chinh.ke.toan.dong.khau.hao'].search([
            ('khau_hao_id', '=', self.id),
            ('thang', '=', str(today.month)),
            ('nam', '=', str(today.year))
        ])
        if existing:
            return
        
        self.env['tai.chinh.ke.toan.dong.khau.hao'].create({
            'khau_hao_id': self.id,
            'thang': str(today.month),
            'nam': str(today.year),
            'ngay_khau_hao': today,
            'so_tien_khau_hao': self.khau_hao_hang_thang,
        })
        self.da_khau_hao += 1
