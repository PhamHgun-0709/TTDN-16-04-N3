# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SoQuy(models.Model):
    _name = 'tai.chinh.ke.toan.so.quy'
    _description = 'Sổ quỹ'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'ngay_ghi_so desc, id desc'

    name = fields.Char(string='Số chứng từ', compute='_compute_name', store=True, readonly=True, index=True)
    ngay_ghi_so = fields.Date(string='Ngày ghi sổ', required=True, default=fields.Date.today, tracking=True, index=True)
    
    loai_phieu = fields.Selection([
        ('thu', 'Thu'),
        ('chi', 'Chi')
    ], string='Loại phiếu', required=True, tracking=True)
    
    phieu_thu_id = fields.Many2one('tai.chinh.ke.toan.phieu.thu', string='Phiếu thu', tracking=True)
    phieu_chi_id = fields.Many2one('tai.chinh.ke.toan.phieu.chi', string='Phiếu chi', tracking=True)
    
    doi_tuong_id = fields.Many2one('res.partner', string='Đối tượng', required=True, tracking=True)
    dien_giai = fields.Char(string='Diễn giải', required=True, tracking=True)
    
    so_tien_thu = fields.Float(string='Số tiền thu', tracking=True)
    so_tien_chi = fields.Float(string='Số tiền chi', tracking=True)
    so_du_truoc = fields.Float(string='Số dư trước', compute='_compute_so_du', store=True)
    so_du_sau = fields.Float(string='Số dư sau', compute='_compute_so_du', store=True)
    ton_quy = fields.Float(string='Tồn quỹ', compute='_compute_ton_quy', store=True)
    
    hinh_thuc = fields.Selection([
        ('tien_mat', 'Tiền mặt'),
        ('chuyen_khoan', 'Chuyển khoản'),
        ('the', 'Thẻ')
    ], string='Hình thức', default='tien_mat', tracking=True)
    
    tai_khoan_id = fields.Many2one('account.account', string='Tài khoản', tracking=True)
    ghi_chu = fields.Text(string='Ghi chú')
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company, index=True)
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('so_tien_check', 'CHECK((so_tien_thu >= 0 AND so_tien_chi >= 0))', 'Số tiền thu/chi phải >= 0!'),
        ('loai_phieu_check', 'CHECK((loai_phieu = \'thu\' AND so_tien_thu > 0 AND so_tien_chi = 0) OR (loai_phieu = \'chi\' AND so_tien_chi > 0 AND so_tien_thu = 0))', 'Phiếu thu phải có số tiền thu, phiếu chi phải có số tiền chi!'),
    ]

    @api.depends('phieu_thu_id', 'phieu_chi_id')
    def _compute_name(self):
        for record in self:
            if record.phieu_thu_id:
                record.name = record.phieu_thu_id.name
            elif record.phieu_chi_id:
                record.name = record.phieu_chi_id.name
            else:
                record.name = 'SQ/' + str(record.id)

    @api.depends('ngay_ghi_so', 'so_tien_thu', 'so_tien_chi')
    def _compute_so_du(self):
        for record in self:
            # Lấy bút toán trước đó
            domain = [('ngay_ghi_so', '<=', record.ngay_ghi_so), ('id', '<', record.id)]
            if record.company_id:
                domain.append(('company_id', '=', record.company_id.id))
            
            so_quy_truoc = self.search(domain, order='ngay_ghi_so desc, id desc', limit=1)
            record.so_du_truoc = so_quy_truoc.so_du_sau if so_quy_truoc else 0
            record.so_du_sau = record.so_du_truoc + record.so_tien_thu - record.so_tien_chi

    @api.depends('ngay_ghi_so', 'so_tien_thu', 'so_tien_chi')
    def _compute_ton_quy(self):
        for record in self:
            # Lấy tất cả các bút toán trước đó
            domain = [('ngay_ghi_so', '<=', record.ngay_ghi_so), ('id', '<=', record.id)]
            if record.company_id:
                domain.append(('company_id', '=', record.company_id.id))
            
            so_quy = self.search(domain, order='ngay_ghi_so, id')
            ton = 0
            for sq in so_quy:
                ton += sq.so_tien_thu - sq.so_tien_chi
            record.ton_quy = ton

    @api.model
    def get_ton_quy_hien_tai(self, company_id=None, hinh_thuc=None):
        """Lấy tồn quỹ hiện tại - Cải thiện hiệu năng"""
        if company_id is None:
            company_id = self.env.company.id
        
        domain = [('company_id', '=', company_id)]
        if hinh_thuc:
            domain.append(('hinh_thuc', '=', hinh_thuc))
        
        # Sử dụng SQL trực tiếp để tính tổng nhanh hơn
        query = """
            SELECT COALESCE(SUM(so_tien_thu - so_tien_chi), 0) as ton_quy
            FROM tai_chinh_ke_toan_so_quy
            WHERE company_id = %s
        """
        params = [company_id]
        
        if hinh_thuc:
            query += " AND hinh_thuc = %s"
            params.append(hinh_thuc)
        
        self.env.cr.execute(query, params)
        result = self.env.cr.fetchone()
        return result[0] if result else 0

    @api.constrains('so_tien_thu', 'so_tien_chi', 'loai_phieu')
    def _check_so_tien(self):
        for record in self:
            if record.loai_phieu == 'thu' and record.so_tien_thu <= 0:
                raise ValidationError(_('Phiếu thu phải có số tiền thu > 0!'))
            if record.loai_phieu == 'chi' and record.so_tien_chi <= 0:
                raise ValidationError(_('Phiếu chi phải có số tiền chi > 0!'))
