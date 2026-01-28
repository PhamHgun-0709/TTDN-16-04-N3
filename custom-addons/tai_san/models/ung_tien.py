# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class UngTien(models.Model):
    _name = 'tai.san.ung.tien'
    _description = 'Ứng tiền'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'ngay_ung desc'

    name = fields.Char(string='Số phiếu ứng', required=True, copy=False, readonly=True, default='New', tracking=True)
    de_xuat_id = fields.Many2one('tai.san.de.xuat', string='Đề xuất tài sản', required=True, ondelete='restrict', tracking=True)
    ngay_ung = fields.Date(string='Ngày ứng', default=fields.Date.today, required=True, tracking=True)
    nhan_vien_id = fields.Many2one('nhan.su.nhan.vien', string='Người ứng', required=True, ondelete='restrict', tracking=True)
    
    so_tien_ung = fields.Float(string='Số tiền ứng', required=True, tracking=True)
    so_tien_da_chi = fields.Float(string='Số tiền đã chi', tracking=True)
    so_tien_con_lai = fields.Float(string='Số tiền còn lại', compute='_compute_so_tien_con_lai', store=True)
    so_tien_quyet_toan = fields.Float(string='Số tiền quyết toán', tracking=True)
    so_tien_hoan_tra = fields.Float(string='Số tiền hoàn trả', compute='_compute_so_tien_hoan_tra', store=True)
    
    hinh_thuc_ung = fields.Selection([
        ('tien_mat', 'Tiền mặt'),
        ('chuyen_khoan', 'Chuyển khoản')
    ], string='Hình thức ứng', default='tien_mat', tracking=True)
    
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('cho_duyet', 'Chờ duyệt'),
        ('da_duyet', 'Đã duyệt'),
        ('cho_chi', 'Chờ chi'),
        ('da_chi', 'Đã chi'),
        ('da_quyet_toan', 'Đã quyết toán'),
        ('huy', 'Đã hủy')
    ], string='Trạng thái', default='nhap', tracking=True)
    
    # Liên kết với tài sản và phiếu chi
    tai_san_id = fields.Many2one('tai.san.tai.san', string='Tài sản', tracking=True)
    # phieu_chi_ids = fields.One2many('tai.chinh.ke.toan.phieu.chi', 'ung_tien_id', string='Phiếu chi')
    
    ngay_quyet_toan = fields.Date(string='Ngày quyết toán', tracking=True)
    ly_do = fields.Text(string='Lý do ứng', tracking=True)
    ghi_chu = fields.Text(string='Ghi chú')
    active = fields.Boolean(string='Active', default=True)

    @api.depends('so_tien_ung', 'so_tien_da_chi')
    def _compute_so_tien_con_lai(self):
        for record in self:
            record.so_tien_con_lai = record.so_tien_ung - record.so_tien_da_chi

    @api.depends('so_tien_ung', 'so_tien_quyet_toan')
    def _compute_so_tien_hoan_tra(self):
        for record in self:
            record.so_tien_hoan_tra = record.so_tien_ung - record.so_tien_quyet_toan

    @api.model
    def create(self, vals_list):
        if not isinstance(vals_list, list):
            vals_list = [vals_list]
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('tai.san.ung.tien') or 'UT/%(year)s/%(month)s'
        return super(UngTien, self).create(vals_list)

    def action_gui_duyet(self):
        self.write({'trang_thai': 'cho_duyet'})

    def action_duyet(self):
        self.write({'trang_thai': 'da_duyet'})

    def action_chi_tien(self):
        self.write({'trang_thai': 'cho_chi'})

    def action_quyet_toan(self):
        if self.so_tien_quyet_toan <= 0:
            raise exceptions.ValidationError('Vui lòng nhập số tiền quyết toán!')
        self.write({
            'trang_thai': 'da_quyet_toan',
            'ngay_quyet_toan': fields.Date.today()
        })

    def action_tao_tai_san(self):
        """Tạo tài sản tự động từ đề xuất sau khi duyệt ứng tiền"""
        self.ensure_one()
        
        if self.trang_thai not in ['da_duyet', 'da_chi']:
            raise exceptions.ValidationError('Chỉ có thể tạo tài sản khi đã duyệt hoặc đã chi tiền!')
        
        if self.tai_san_id:
            raise exceptions.ValidationError('Đã tồn tại tài sản cho phiếu ứng này!')
        
        # Lấy thông tin từ đề xuất
        de_xuat = self.de_xuat_id
        
        # Tạo mã tài sản tự động dựa theo loại
        loai_prefix = {
            'may_moc': 'TS-IT',
            'phuong_tien': 'TS-PT',
            'van_phong': 'TS-VP',
            'nha_dat': 'TS-ND',
            'khac': 'TS-KH'
        }
        prefix = loai_prefix.get(de_xuat.loai_tai_san, 'TS-KH')
        
        # Đếm số tài sản cùng loại để tạo mã
        count = self.env['tai.san.tai.san'].search_count([('ma_tai_san', 'like', prefix)])
        ma_tai_san = f"{prefix}-{str(count + 1).zfill(3)}"
        
        # Tạo tài sản mới
        tai_san_vals = {
            'name': de_xuat.ten_tai_san,
            'ma_tai_san': ma_tai_san,
            'loai_tai_san': de_xuat.loai_tai_san,
            'ngay_mua': fields.Date.today(),
            'nguyen_gia': self.so_tien_quyet_toan or de_xuat.thanh_tien,
            'nhan_vien_id': self.nhan_vien_id.id,
            'phong_ban_id': de_xuat.phong_ban_id.id,
            'tinh_trang': 'dang_su_dung',
            'trang_thai': 'tot',
            'de_xuat_id': de_xuat.id,
            'ghi_chu': f'Tạo từ phiếu ứng {self.name} - Đề xuất {de_xuat.name}'
        }
        
        tai_san = self.env['tai.san.tai.san'].create(tai_san_vals)
        
        # Cập nhật liên kết
        self.write({'tai_san_id': tai_san.id})
        
        # Hiển thị thông báo
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công!',
                'message': f'Đã tạo tài sản {tai_san.name} (Mã: {tai_san.ma_tai_san})',
                'type': 'success',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window',
                    'res_model': 'tai.san.tai.san',
                    'res_id': tai_san.id,
                    'view_mode': 'form',
                    'target': 'current',
                }
            }
        }
