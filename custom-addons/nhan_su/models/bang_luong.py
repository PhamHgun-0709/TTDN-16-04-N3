# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class BangLuong(models.Model):
    """Bảng lương CHA - Quản lý quỹ lương toàn công ty theo tháng"""
    _name = 'nhan.su.bang.luong'
    _description = 'Bảng lương'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'nam desc, thang desc'

    name = fields.Char(string='Mã bảng lương', required=True, copy=False, readonly=True, default='New', tracking=True)
    thang = fields.Selection([
        ('1', 'Tháng 1'), ('2', 'Tháng 2'), ('3', 'Tháng 3'),
        ('4', 'Tháng 4'), ('5', 'Tháng 5'), ('6', 'Tháng 6'),
        ('7', 'Tháng 7'), ('8', 'Tháng 8'), ('9', 'Tháng 9'),
        ('10', 'Tháng 10'), ('11', 'Tháng 11'), ('12', 'Tháng 12')
    ], string='Tháng', required=True, tracking=True)
    nam = fields.Char(string='Năm', required=True, tracking=True)
    
    # Chi tiết lương nhân viên (quan hệ CHA-CON)
    chi_tiet_luong_ids = fields.One2many('nhan.su.chi.tiet.luong', 'bang_luong_id', string='Chi tiết lương')
    
    # Thống kê
    so_nhan_vien = fields.Integer(string='Số nhân viên', compute='_compute_thong_ke', store=True)
    tong_quy_luong = fields.Float(string='Tổng quỹ lương', compute='_compute_thong_ke', store=True)
    tong_thu_nhap = fields.Float(string='Tổng thu nhập', compute='_compute_thong_ke', store=True)
    tong_khau_tru = fields.Float(string='Tổng khấu trừ', compute='_compute_thong_ke', store=True)
    tong_thuc_linh = fields.Float(string='Tổng thực lĩnh', compute='_compute_thong_ke', store=True)
    
    # Trạng thái duyệt
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('cho_duyet', 'Chờ duyệt'),
        ('da_duyet', 'Đã duyệt'),
        ('da_chi', 'Đã chi lương'),
        ('huy', 'Đã hủy')
    ], string='Trạng thái', default='nhap', tracking=True)
    
    # Thông tin duyệt
    nguoi_lap_id = fields.Many2one('nhan.su.nhan.vien', string='Người lập', tracking=True)
    ngay_lap = fields.Date(string='Ngày lập', default=fields.Date.today, tracking=True)
    nguoi_duyet_id = fields.Many2one('nhan.su.nhan.vien', string='Người duyệt', tracking=True)
    ngay_duyet = fields.Date(string='Ngày duyệt', tracking=True)
    nguoi_chi_id = fields.Many2one('nhan.su.nhan.vien', string='Người chi', tracking=True)
    ngay_chi = fields.Date(string='Ngày chi', tracking=True)
    
    ghi_chu = fields.Text(string='Ghi chú')
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('unique_thang_nam', 'UNIQUE(thang, nam)', 
         'Đã tồn tại bảng lương cho tháng này!')
    ]

    @api.depends('chi_tiet_luong_ids.thu_nhap', 'chi_tiet_luong_ids.tong_khau_tru', 'chi_tiet_luong_ids.thuc_linh')
    def _compute_thong_ke(self):
        """Tính tổng quỹ lương từ chi tiết"""
        for record in self:
            chi_tiet = record.chi_tiet_luong_ids
            record.so_nhan_vien = len(chi_tiet)
            record.tong_thu_nhap = sum(chi_tiet.mapped('thu_nhap'))
            record.tong_khau_tru = sum(chi_tiet.mapped('tong_khau_tru'))
            record.tong_thuc_linh = sum(chi_tiet.mapped('thuc_linh'))
            record.tong_quy_luong = record.tong_thuc_linh

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('nhan.su.bang.luong') or 'BL/%(year)s/%(month)s'
        return super(BangLuong, self).create(vals)

    def action_lay_tong_hop_cong(self):
        """Lấy dữ liệu tổng hợp công"""
        for record in self:
            if not record.nhan_vien_id or not record.thang or not record.nam:
                continue
            
            tong_hop = self.env['nhan.su.tong.hop.cong'].search([
                ('nhan_vien_id', '=', record.nhan_vien_id.id),
                ('thang', '=', record.thang),
                ('nam', '=', record.nam)
            ], limit=1)
            
            if tong_hop:
                record.tong_hop_cong_id = tong_hop.id
            else:
                raise exceptions.UserError(
                    f'Chưa có tổng hợp công cho nhân viên {record.nhan_vien_id.name} tháng {record.thang}/{record.nam}!'
                )

    def action_lay_du_lieu(self):
        """Lấy dữ liệu và tạo chi tiết lương cho tất cả nhân viên"""
        for record in self:
            if not record.thang or not record.nam:
                raise exceptions.UserError('Vui lòng chọn tháng và năm!')
            
            # Xóa chi tiết cũ (nếu có)
            record.chi_tiet_luong_ids.unlink()
            
            # Lấy tất cả tổng hợp công trong tháng
            tong_hop_congs = self.env['nhan.su.tong.hop.cong'].search([
                ('thang', '=', record.thang),
                ('nam', '=', record.nam),
                ('trang_thai', '=', 'da_xac_nhan')
            ])
            
            if not tong_hop_congs:
                # Kiểm tra xem có tổng hợp công chưa xác nhận không
                tong_hop_chua_xac_nhan = self.env['nhan.su.tong.hop.cong'].search([
                    ('thang', '=', record.thang),
                    ('nam', '=', record.nam)
                ])
                if tong_hop_chua_xac_nhan:
                    raise exceptions.UserError(
                        f'Có {len(tong_hop_chua_xac_nhan)} bản tổng hợp công chưa được xác nhận!\n\n'
                        'Vui lòng vào menu "Chấm công > Tổng hợp công" để xác nhận trước khi tính lương.'
                    )
                else:
                    raise exceptions.UserError(
                        f'Không tìm thấy tổng hợp công nào cho tháng {record.thang}/{record.nam}!\n\n'
                        'Vui lòng:\n'
                        '1. Vào menu "Chấm công > Bảng chấm công" để nhập dữ liệu chấm công\n'
                        '2. Vào menu "Chấm công > Tổng hợp công" để tạo và xác nhận tổng hợp công\n'
                        '3. Sau đó quay lại đây để lấy dữ liệu tính lương'
                    )
            
            # Tạo chi tiết lương cho từng nhân viên
            chi_tiet_vals = []
            for tong_hop in tong_hop_congs:
                nhan_vien = tong_hop.nhan_vien_id
                vals = {
                    'bang_luong_id': record.id,
                    'nhan_vien_id': nhan_vien.id,
                    'chuc_vu_id': nhan_vien.chuc_vu_id.id,
                    'tong_hop_cong_id': tong_hop.id,
                    'luong_co_ban': nhan_vien.chuc_vu_id.luong_co_ban if nhan_vien.chuc_vu_id else 0,
                    'phu_cap_chuc_vu': nhan_vien.chuc_vu_id.phu_cap if nhan_vien.chuc_vu_id else 0,
                }
                chi_tiet_vals.append(vals)
            
            if chi_tiet_vals:
                self.env['nhan.su.chi.tiet.luong'].create(chi_tiet_vals)
                record.message_post(body=f"Đã tạo {len(chi_tiet_vals)} chi tiết lương từ tổng hợp công.")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Thành công',
                    'message': f'Đã tạo chi tiết lương cho {len(chi_tiet_vals)} nhân viên',
                    'type': 'success',
                    'sticky': False,
                }
            }
    
    def action_tinh_luong(self):
        """Tính lại lương cho tất cả chi tiết"""
        for record in self:
            if not record.chi_tiet_luong_ids:
                raise exceptions.UserError('Chưa có chi tiết lương! Vui lòng bấm "Lấy dữ liệu" trước.')
            
            # Trigger recompute bằng cách đọc lại field
            for chi_tiet in record.chi_tiet_luong_ids:
                chi_tiet._compute_thu_nhap()
                chi_tiet._compute_thuc_linh()
            
            record.message_post(body=f"Đã tính lương cho {len(record.chi_tiet_luong_ids)} nhân viên.")

    def action_xac_nhan(self):
        self.write({'trang_thai': 'xac_nhan'})

    def action_thanh_toan(self):
        self.write({
            'trang_thai': 'da_thanh_toan',
            'ngay_thanh_toan': fields.Date.today()
        })
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                thang = vals.get('thang', '')
                nam = vals.get('nam', '')
                vals['name'] = f"BL/T{thang}/{nam}"
        return super(BangLuong, self).create(vals_list)

    def action_lay_du_lieu(self):
        """Lấy dữ liệu tổng hợp công và tạo chi tiết lương"""
        self.ensure_one()
        
        # Xóa chi tiết cũ nếu có
        self.chi_tiet_luong_ids.unlink()
        
        # Tìm tất cả tổng hợp công đã xác nhận trong tháng
        tong_hop_congs = self.env['nhan.su.tong.hop.cong'].search([
            ('thang', '=', self.thang),
            ('nam', '=', self.nam),
            ('trang_thai', '=', 'da_xac_nhan')
        ])
        
        if not tong_hop_congs:
            raise exceptions.UserError(
                f'Không tìm thấy tổng hợp công đã xác nhận cho tháng {self.thang}/{self.nam}!'
            )
        
        # Tạo chi tiết lương cho từng nhân viên
        chi_tiet_vals = []
        for tong_hop in tong_hop_congs:
            nhan_vien = tong_hop.nhan_vien_id
            chi_tiet_vals.append({
                'bang_luong_id': self.id,
                'tong_hop_cong_id': tong_hop.id,
                'nhan_vien_id': nhan_vien.id,
                'chuc_vu_id': nhan_vien.chuc_vu_id.id,
            })
        
        if chi_tiet_vals:
            self.env['nhan.su.chi.tiet.luong'].create(chi_tiet_vals)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f'Đã tạo chi tiết lương cho {len(chi_tiet_vals)} nhân viên',
                    'type': 'success',
                    'sticky': False,
                }
            }

    def action_tinh_luong(self):
        """Tính lương cho tất cả nhân viên"""
        self.ensure_one()
        for chi_tiet in self.chi_tiet_luong_ids:
            chi_tiet.action_tinh_luong()

    def action_trinh_duyet(self):
        """Trình duyệt bảng lương"""
        self.write({'trang_thai': 'cho_duyet'})

    def action_duyet(self):
        """Duyệt bảng lương"""
        self.write({
            'trang_thai': 'da_duyet',
            'nguoi_duyet_id': self.env.user.employee_id.id if self.env.user.employee_id else False,
            'ngay_duyet': fields.Date.today()
        })

    def action_chi_luong(self):
        """Chi lương - Tạo phiếu chi kế toán"""
        self.ensure_one()
        
        if self.trang_thai != 'da_duyet':
            raise exceptions.UserError('Bảng lương chưa được duyệt!')
        
        # Phiếu chi sẽ được tạo từ module kế toán
        
        self.write({
            'trang_thai': 'da_chi',
            'nguoi_chi_id': self.env.user.employee_id.id if self.env.user.employee_id else False,
            'ngay_chi': fields.Date.today()
        })
        
        # Cập nhật trạng thái tổng hợp công
        for chi_tiet in self.chi_tiet_luong_ids:
            if chi_tiet.tong_hop_cong_id:
                chi_tiet.tong_hop_cong_id.trang_thai = 'da_tinh_luong'

    def action_huy(self):
        """Hủy bảng lương"""
        if self.trang_thai == 'da_chi':
            raise exceptions.UserError('Không thể hủy bảng lương đã chi!')
