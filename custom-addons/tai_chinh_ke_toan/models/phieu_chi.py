# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class PhieuChi(models.Model):
    _name = 'tai.chinh.ke.toan.phieu.chi'
    _description = 'Phiếu chi'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'ngay_lap desc'

    name = fields.Char(string='Số phiếu chi', required=True, copy=False, readonly=True, default='New', tracking=True)
    ngay_lap = fields.Date(string='Ngày lập', default=fields.Date.today, required=True, tracking=True)
    nguoi_lap_id = fields.Many2one('res.users', string='Người lập phiếu', default=lambda self: self.env.user, tracking=True)
    
    # Liên kết với ứng tiền, tài sản và bảng lương
    ung_tien_id = fields.Many2one('tai.san.ung.tien', string='Ứng tiền', ondelete='set null', tracking=True)
    tai_san_id = fields.Many2one('tai.san.tai.san', string='Tài sản', ondelete='set null', tracking=True)
    bang_luong_id = fields.Many2one('nhan.su.bang.luong', string='Bảng lương', ondelete='set null', tracking=True)
    nhan_vien_id = fields.Many2one('nhan.su.nhan.vien', string='Nhân viên', ondelete='set null', tracking=True)
    
    doi_tuong_id = fields.Many2one('res.partner', string='Đối tượng nhận', required=True, tracking=True)
    ly_do_chi = fields.Char(string='Lý do chi', required=True, tracking=True)
    so_tien = fields.Float(string='Số tiền', required=True, tracking=True)
    
    hinh_thuc_thanh_toan = fields.Selection([
        ('tien_mat', 'Tiền mặt'),
        ('chuyen_khoan', 'Chuyển khoản'),
        ('the', 'Thẻ')
    ], string='Hình thức thanh toán', default='tien_mat', tracking=True)
    
    tai_khoan_id = fields.Many2one('account.account', string='Tài khoản', tracking=True)
    loai_chi = fields.Selection([
        ('mua_hang', 'Mua hàng'),
        ('chi_luong', 'Chi lương'),
        ('van_phong', 'Văn phòng'),
        ('dich_vu', 'Dịch vụ'),
        ('tai_san', 'Tài sản'),
        ('khac', 'Khác')
    ], string='Loại chi', tracking=True)
    
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('cho_duyet', 'Chờ duyệt'),
        ('da_duyet', 'Đã duyệt'),
        ('da_chi', 'Đã chi'),
        ('huy', 'Đã hủy')
    ], string='Trạng thái', default='nhap', tracking=True)
    
    ngay_chi = fields.Date(string='Ngày chi', tracking=True)
    nguoi_nhan = fields.Char(string='Người nhận', tracking=True)
    so_quy_id = fields.Many2one('tai.chinh.ke.toan.so.quy', string='Sổ quỹ', tracking=True)
    
    ghi_chu = fields.Text(string='Ghi chú')
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    active = fields.Boolean(string='Active', default=True)
    
    # Fraud Detection Fields
    canh_bao_gian_lan_ids = fields.One2many('tai.chinh.ke.toan.canh.bao.gian.lan', 'phieu_chi_id', string='Cảnh báo gian lận')
    co_canh_bao = fields.Boolean(string='Có cảnh báo', compute='_compute_fraud_info', store=False)
    muc_do_rui_ro = fields.Selection([
        ('thap', 'Thấp'),
        ('trung_binh', 'Trung bình'),
        ('cao', 'Cao'),
        ('nghiem_trong', 'Nghiêm trọng')
    ], string='Mức độ rủi ro', compute='_compute_fraud_info', store=False)
    so_canh_bao = fields.Integer(string='Số cảnh báo', compute='_compute_fraud_info', store=False)
    
    @api.depends('canh_bao_gian_lan_ids', 'canh_bao_gian_lan_ids.trang_thai', 'canh_bao_gian_lan_ids.muc_do_nguy_hiem')
    def _compute_fraud_info(self):
        """Tính toán thông tin cảnh báo gian lận"""
        for record in self:
            # Chỉ tính cảnh báo chưa xử lý hoặc đang kiểm tra
            active_warnings = record.canh_bao_gian_lan_ids.filtered(
                lambda w: w.trang_thai in ('chua_xu_ly', 'dang_kiem_tra')
            )
            
            record.so_canh_bao = len(active_warnings)
            record.co_canh_bao = bool(active_warnings)
            
            # Xác định mức độ rủi ro cao nhất
            if active_warnings:
                muc_do_list = active_warnings.mapped('muc_do_nguy_hiem')
                if 'nghiem_trong' in muc_do_list:
                    record.muc_do_rui_ro = 'nghiem_trong'
                elif 'cao' in muc_do_list:
                    record.muc_do_rui_ro = 'cao'
                elif 'trung_binh' in muc_do_list:
                    record.muc_do_rui_ro = 'trung_binh'
                else:
                    record.muc_do_rui_ro = 'thap'
            else:
                record.muc_do_rui_ro = False

    _sql_constraints = [
        ('so_tien_positive', 'CHECK(so_tien > 0)', 'Số tiền phải lớn hơn 0!'),
        ('name_unique', 'UNIQUE(name, company_id)', 'Số phiếu chi không được trùng!')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('tai.chinh.ke.toan.phieu.chi') or 'New'
        records = super(PhieuChi, self).create(vals_list)
        
        # Tự động chạy fraud detection cho phiếu chi mới
        for record in records:
            if record.trang_thai in ('da_duyet', 'da_chi'):
                self.env['tai.chinh.ke.toan.canh.bao.gian.lan']._auto_detect_fraud_for_phieu_chi(record)
        
        return records

    @api.constrains('so_tien')
    def _check_so_tien(self):
        for record in self:
            if record.so_tien <= 0:
                raise ValidationError(_('Số tiền phải lớn hơn 0!'))

    @api.constrains('ngay_lap', 'ngay_chi')
    def _check_ngay_chi(self):
        for record in self:
            if record.ngay_chi and record.ngay_chi < record.ngay_lap:
                raise ValidationError(_('Ngày chi không thể trước ngày lập phiếu!'))

    @api.onchange('ung_tien_id')
    def _onchange_ung_tien_id(self):
        if self.ung_tien_id:
            self.doi_tuong_id = self.ung_tien_id.nhan_vien_id.partner_id if hasattr(self.ung_tien_id, 'nhan_vien_id') else False
            self.so_tien = self.ung_tien_id.so_tien if hasattr(self.ung_tien_id, 'so_tien') else 0
            self.ly_do_chi = f'Ứng tiền - {self.ung_tien_id.name}' if hasattr(self.ung_tien_id, 'name') else 'Ứng tiền'
            self.loai_chi = 'khac'

    @api.onchange('tai_san_id')
    def _onchange_tai_san_id(self):
        if self.tai_san_id:
            self.ly_do_chi = f'Mua tài sản - {self.tai_san_id.name}'
            self.so_tien = self.tai_san_id.gia_tri if hasattr(self.tai_san_id, 'gia_tri') else 0
            self.loai_chi = 'tai_san'

    @api.onchange('bang_luong_id')
    def _onchange_bang_luong_id(self):
        if self.bang_luong_id:
            self.ly_do_chi = f'Chi lương tháng {self.bang_luong_id.name}' if hasattr(self.bang_luong_id, 'name') else 'Chi lương'
            self.so_tien = self.bang_luong_id.tong_luong if hasattr(self.bang_luong_id, 'tong_luong') else 0
            self.loai_chi = 'chi_luong'
    def action_gui_duyet(self):
        self.write({'trang_thai': 'cho_duyet'})

    def action_duyet(self):
        self.write({'trang_thai': 'da_duyet'})

    def action_chi_tien(self):
        for record in self:
            if record.trang_thai != 'da_duyet':
                raise UserError(_('Chỉ có thể chi tiền cho phiếu đã được duyệt!'))
            
            # Tự động chạy fraud detection khi chuyển sang trạng thái đã chi
            self.env['tai.chinh.ke.toan.canh.bao.gian.lan']._auto_detect_fraud_for_phieu_chi(record)
            if record.so_quy_id:
                raise UserError(_('Phiếu chi này đã được thanh toán!'))
            
            # Kiểm tra tồn quỹ
            ton_quy = self.env['tai.chinh.ke.toan.so.quy'].get_ton_quy_hien_tai()
            if record.hinh_thuc_thanh_toan == 'tien_mat' and ton_quy < record.so_tien:
                raise UserError(_('Quỹ tiền mặt không đủ! Tồn quỹ: %s, Cần chi: %s') % (ton_quy, record.so_tien))
            
            # Tạo bút toán sổ quỹ
            so_quy = self.env['tai.chinh.ke.toan.so.quy'].create({
                'ngay_ghi_so': fields.Date.today(),
                'loai_phieu': 'chi',
                'phieu_chi_id': record.id,
                'doi_tuong_id': record.doi_tuong_id.id,
                'dien_giai': record.ly_do_chi,
                'so_tien_chi': record.so_tien,
                'hinh_thuc': record.hinh_thuc_thanh_toan,
            })
            record.write({
                'trang_thai': 'da_chi',
                'ngay_chi': fields.Date.today(),
                'so_quy_id': so_quy.id
            })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Thành công'),
                'message': _('Đã chi tiền thành công!'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_huy(self):
        self.write({'trang_thai': 'huy'})
