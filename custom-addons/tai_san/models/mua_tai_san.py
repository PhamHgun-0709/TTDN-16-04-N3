# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MuaTaiSan(models.Model):
    _name = 'tai.san.mua.tai.san'
    _description = 'Mua tài sản'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'ngay_mua desc'

    name = fields.Char(string='Số hóa đơn', required=True, copy=False, readonly=True, default='New', tracking=True)
    de_xuat_id = fields.Many2one('tai.san.de.xuat', string='Đề xuất', tracking=True)
    ung_tien_id = fields.Many2one('tai.san.ung.tien', string='Ứng tiền', required=True, tracking=True)
    
    # Thông tin mua hàng
    ngay_mua = fields.Date(string='Ngày mua', default=fields.Date.today, required=True, tracking=True)
    nha_cung_cap = fields.Char(string='Nhà cung cấp', required=True, tracking=True)
    dia_chi_ncc = fields.Text(string='Địa chỉ nhà cung cấp')
    so_dien_thoai_ncc = fields.Char(string='Số điện thoại NCC')
    
    # Thông tin tài sản
    ten_tai_san = fields.Char(string='Tên tài sản', required=True, tracking=True)
    loai_tai_san = fields.Selection([
        ('nha_dat', 'Nhà đất'),
        ('may_moc', 'Máy móc thiết bị'),
        ('phuong_tien', 'Phương tiện vận chuyển'),
        ('van_phong', 'Tài sản văn phòng'),
        ('khac', 'Khác')
    ], string='Loại tài sản', required=True, tracking=True)
    so_luong = fields.Integer(string='Số lượng', default=1, tracking=True)
    
    # Thông tin tài chính
    don_gia = fields.Float(string='Đơn giá', required=True, tracking=True)
    thanh_tien = fields.Float(string='Thành tiền', compute='_compute_thanh_tien', store=True)
    thue_vat = fields.Float(string='Thuế VAT (%)', default=10, tracking=True)
    tien_thue = fields.Float(string='Tiền thuế', compute='_compute_tien_thue', store=True)
    tong_tien = fields.Float(string='Tổng tiền', compute='_compute_tong_tien', store=True)
    
    # Bảo hành
    thoi_gian_bao_hanh = fields.Integer(string='Thời gian bảo hành (tháng)', tracking=True)
    ngay_het_bao_hanh = fields.Date(string='Ngày hết bảo hành', compute='_compute_ngay_het_bao_hanh', store=True)
    
    # Trạng thái
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('da_mua', 'Đã mua'),
        ('da_tao_tai_san', 'Đã tạo tài sản'),
        ('huy', 'Đã hủy')
    ], string='Trạng thái', default='nhap', tracking=True)
    
    # Liên kết tài sản
    tai_san_ids = fields.One2many('tai.san.tai.san', 'mua_tai_san_id', string='Tài sản')
    so_tai_san_da_tao = fields.Integer(string='Số tài sản đã tạo', compute='_compute_so_tai_san')
    
    ghi_chu = fields.Text(string='Ghi chú')
    active = fields.Boolean(string='Active', default=True)

    @api.depends('so_luong', 'don_gia')
    def _compute_thanh_tien(self):
        for record in self:
            record.thanh_tien = record.so_luong * record.don_gia

    @api.depends('thanh_tien', 'thue_vat')
    def _compute_tien_thue(self):
        for record in self:
            record.tien_thue = record.thanh_tien * record.thue_vat / 100

    @api.depends('thanh_tien', 'tien_thue')
    def _compute_tong_tien(self):
        for record in self:
            record.tong_tien = record.thanh_tien + record.tien_thue

    @api.depends('ngay_mua', 'thoi_gian_bao_hanh')
    def _compute_ngay_het_bao_hanh(self):
        from dateutil.relativedelta import relativedelta
        for record in self:
            if record.ngay_mua and record.thoi_gian_bao_hanh:
                record.ngay_het_bao_hanh = record.ngay_mua + relativedelta(months=record.thoi_gian_bao_hanh)
            else:
                record.ngay_het_bao_hanh = False

    @api.depends('tai_san_ids')
    def _compute_so_tai_san(self):
        for record in self:
            record.so_tai_san_da_tao = len(record.tai_san_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('tai.san.mua.tai.san') or 'HD/%(year)s/%(month)s'
        return super(MuaTaiSan, self).create(vals_list)

    @api.onchange('ung_tien_id')
    def _onchange_ung_tien_id(self):
        """Auto-fill thông tin từ ứng tiền"""
        if self.ung_tien_id:
            self.de_xuat_id = self.ung_tien_id.de_xuat_id
            if self.ung_tien_id.de_xuat_id:
                self.ten_tai_san = self.ung_tien_id.de_xuat_id.ten_tai_san
                self.loai_tai_san = self.ung_tien_id.de_xuat_id.loai_tai_san
                self.so_luong = self.ung_tien_id.de_xuat_id.so_luong

    def action_xac_nhan_da_mua(self):
        """Xác nhận đã mua xong - TỰ ĐỘNG TẠO TÀI SẢN"""
        self.write({'trang_thai': 'da_mua'})
        # Tự động tạo tài sản khi xác nhận đã mua
        self.action_tao_tai_san()

    def action_tao_tai_san(self):
        """Tự động tạo tài sản từ hóa đơn mua"""
        self.ensure_one()
        
        tai_san_vals = []
        for i in range(self.so_luong):
            # Tạo mã tài sản tự động
            ma_tai_san = self.env['ir.sequence'].next_by_code('tai.san.tai.san') or 'TS-XXX'
            
            vals = {
                'name': f"{self.ten_tai_san}" if self.so_luong == 1 else f"{self.ten_tai_san} #{i+1}",
                'ma_tai_san': ma_tai_san,
                'loai_tai_san': self.loai_tai_san,
                'ngay_mua': self.ngay_mua,
                'nguyen_gia': self.don_gia,
                'mua_tai_san_id': self.id,
                'de_xuat_id': self.de_xuat_id.id if self.de_xuat_id else False,
                'tinh_trang': 'chua_su_dung',  # Tài sản mới về kho, chưa cấp phát
                'trang_thai': 'tot',
                'ghi_chu': f'Mua từ NCC: {self.nha_cung_cap}, Hóa đơn: {self.name}. Chờ cấp phát.',
            }
            tai_san_vals.append(vals)
        
        # Tạo tài sản
        tai_sans = self.env['tai.san.tai.san'].create(tai_san_vals)
        
        # TỰ ĐỘNG TẠO PHIẾU CHI nếu đã ứng tiền và có đối tượng
        if self.ung_tien_id and self.ung_tien_id.nhan_vien_id:
            # Tìm partner của nhà cung cấp (hoặc tạo mới nếu chưa có)
            partner = self.env['res.partner'].search([('name', '=', self.nha_cung_cap)], limit=1)
            if not partner:
                partner = self.env['res.partner'].create({
                    'name': self.nha_cung_cap,
                    'phone': self.so_dien_thoai_ncc,
                    'street': self.dia_chi_ncc,
                    'supplier_rank': 1,
                })
            
            # Tạo phiếu chi
            phieu_chi = self.env['tai.chinh.ke.toan.phieu.chi'].create({
                'doi_tuong_id': partner.id,
                'ly_do_chi': f'Thanh toán mua {self.ten_tai_san} - Hóa đơn {self.name}',
                'so_tien': self.tong_tien,
                'loai_chi': 'tai_san',
                'hinh_thuc_thanh_toan': 'chuyen_khoan',
                'ngay_lap': self.ngay_mua,
                'ung_tien_id': self.ung_tien_id.id,
                'tai_san_id': tai_sans[0].id if tai_sans else False,
                'ghi_chu': f'Tự động từ hóa đơn mua tài sản {self.name}',
            })
        
        # Update trạng thái
        self.write({'trang_thai': 'da_tao_tai_san'})
        
        # Thông báo
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công!',
                'message': f'Đã tạo {len(tai_sans)} tài sản và phiếu chi thanh toán',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_huy(self):
        self.write({'trang_thai': 'huy'})
