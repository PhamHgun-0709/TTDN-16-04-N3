# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class PhieuThu(models.Model):
    _name = 'tai.chinh.ke.toan.phieu.thu'
    _description = 'Phiếu thu'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'ngay_lap desc'

    name = fields.Char(string='Số phiếu thu', required=True, copy=False, readonly=True, default='New', tracking=True)
    ngay_lap = fields.Date(string='Ngày lập', default=fields.Date.today, required=True, tracking=True)
    nguoi_lap_id = fields.Many2one('res.users', string='Người lập phiếu', default=lambda self: self.env.user, tracking=True)
    
    # Liên kết với ứng tiền (hoàn ứng) và tài sản (thanh lý)
    ung_tien_id = fields.Many2one('tai.san.ung.tien', string='Ứng tiền (hoàn ứng)', ondelete='set null', tracking=True)
    tai_san_id = fields.Many2one('tai.san.tai.san', string='Tài sản (thanh lý)', ondelete='set null', tracking=True)
    
    doi_tuong_id = fields.Many2one('res.partner', string='Đối tượng nộp', required=True, tracking=True)
    ly_do_thu = fields.Char(string='Lý do thu', required=True, tracking=True)
    so_tien = fields.Float(string='Số tiền', required=True, tracking=True)
    
    hinh_thuc_thanh_toan = fields.Selection([
        ('tien_mat', 'Tiền mặt'),
        ('chuyen_khoan', 'Chuyển khoản'),
        ('the', 'Thẻ')
    ], string='Hình thức thanh toán', default='tien_mat', tracking=True)
    
    tai_khoan_id = fields.Many2one('account.account', string='Tài khoản', tracking=True)
    loai_thu = fields.Selection([
        ('ban_hang', 'Bán hàng'),
        ('dich_vu', 'Dịch vụ'),
        ('hoan_ung', 'Hoàn ứng'),
        ('khac', 'Khác')
    ], string='Loại thu', tracking=True)
    
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('cho_duyet', 'Chờ duyệt'),
        ('da_duyet', 'Đã duyệt'),
        ('da_thu', 'Đã thu'),
        ('huy', 'Đã hủy')
    ], string='Trạng thái', default='nhap', tracking=True)
    
    ngay_thu = fields.Date(string='Ngày thu', tracking=True)
    nguoi_nop = fields.Char(string='Người nộp', tracking=True)
    so_quy_id = fields.Many2one('tai.chinh.ke.toan.so.quy', string='Sổ quỹ', tracking=True)
    
    ghi_chu = fields.Text(string='Ghi chú')
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('so_tien_positive', 'CHECK(so_tien > 0)', 'Số tiền phải lớn hơn 0!'),
        ('name_unique', 'UNIQUE(name, company_id)', 'Số phiếu thu không được trùng!')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('tai.chinh.ke.toan.phieu.thu') or 'New'
        return super(PhieuThu, self).create(vals_list)

    @api.constrains('so_tien')
    def _check_so_tien(self):
        for record in self:
            if record.so_tien <= 0:
                raise ValidationError(_('Số tiền phải lớn hơn 0!'))

    @api.constrains('ngay_lap', 'ngay_thu')
    def _check_ngay_thu(self):
        for record in self:
            if record.ngay_thu and record.ngay_thu < record.ngay_lap:
                raise ValidationError(_('Ngày thu không thể trước ngày lập phiếu!'))

    @api.onchange('ung_tien_id')
    def _onchange_ung_tien_id(self):
        if self.ung_tien_id:
            self.doi_tuong_id = self.ung_tien_id.nhan_vien_id.partner_id if hasattr(self.ung_tien_id, 'nhan_vien_id') else False
            self.so_tien = self.ung_tien_id.so_tien_hoan if hasattr(self.ung_tien_id, 'so_tien_hoan') else 0
            self.ly_do_thu = f'Hoàn ứng tiền - {self.ung_tien_id.name}' if hasattr(self.ung_tien_id, 'name') else 'Hoàn ứng tiền'
            self.loai_thu = 'hoan_ung'

    @api.onchange('tai_san_id')
    def _onchange_tai_san_id(self):
        if self.tai_san_id:
            self.ly_do_thu = f'Thanh lý tài sản - {self.tai_san_id.name}'
            self.so_tien = self.tai_san_id.gia_tri_thanh_ly if hasattr(self.tai_san_id, 'gia_tri_thanh_ly') else 0
            self.loai_thu = 'khac'

    def action_gui_duyet(self):
        self.write({'trang_thai': 'cho_duyet'})

    def action_duyet(self):
        self.write({'trang_thai': 'da_duyet'})

    def action_thu_tien(self):
        for record in self:
            if record.trang_thai != 'da_duyet':
                raise UserError(_('Chỉ có thể thu tiền cho phiếu đã được duyệt!'))
            if record.so_quy_id:
                raise UserError(_('Phiếu thu này đã được thanh toán!'))
            
            # Tạo bút toán sổ quỹ
            so_quy = self.env['tai.chinh.ke.toan.so.quy'].create({
                'ngay_ghi_so': fields.Date.today(),
                'loai_phieu': 'thu',
                'phieu_thu_id': record.id,
                'doi_tuong_id': record.doi_tuong_id.id,
                'dien_giai': record.ly_do_thu,
                'so_tien_thu': record.so_tien,
                'hinh_thuc': record.hinh_thuc_thanh_toan,
            })
            record.write({
                'trang_thai': 'da_thu',
                'ngay_thu': fields.Date.today(),
                'so_quy_id': so_quy.id
            })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Thành công'),
                'message': _('Đã thu tiền thành công!'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_huy(self):
        self.write({'trang_thai': 'huy'})
