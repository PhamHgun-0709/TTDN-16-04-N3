# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class TongHopCong(models.Model):
    _name = 'nhan.su.tong.hop.cong'
    _description = 'Tổng hợp công'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'nam desc, thang desc'

    name = fields.Char(string='Mã tổng hợp', compute='_compute_name', store=True, readonly=True)
    nhan_vien_id = fields.Many2one('nhan.su.nhan.vien', string='Nhân viên', required=True, ondelete='restrict', tracking=True)
    phong_ban_id = fields.Many2one(related='nhan_vien_id.phong_ban_id', string='Phòng ban', store=True)
    ca_lam_viec_id = fields.Many2one(related='nhan_vien_id.ca_lam_viec_id', string='Ca làm việc', store=True)
    
    thang = fields.Selection([
        ('1', 'Tháng 1'), ('2', 'Tháng 2'), ('3', 'Tháng 3'),
        ('4', 'Tháng 4'), ('5', 'Tháng 5'), ('6', 'Tháng 6'),
        ('7', 'Tháng 7'), ('8', 'Tháng 8'), ('9', 'Tháng 9'),
        ('10', 'Tháng 10'), ('11', 'Tháng 11'), ('12', 'Tháng 12')
    ], string='Tháng', required=True, tracking=True)
    nam = fields.Char(string='Năm', required=True, tracking=True)
    
    # Dữ liệu chấm công
    cham_cong_ids = fields.Many2many('nhan.su.cham.cong', string='Chấm công')
    so_ngay_lam_viec = fields.Integer(string='Số ngày làm việc', compute='_compute_tong_hop', store=True)
    
    # Tổng hợp công
    tong_cong = fields.Float(string='Tổng công', compute='_compute_tong_hop', store=True)
    so_ngay_du_cong = fields.Integer(string='Số ngày đủ công', compute='_compute_tong_hop', store=True)
    so_ngay_thieu_cong = fields.Integer(string='Số ngày thiếu công', compute='_compute_tong_hop', store=True)
    
    # Tăng ca
    tong_gio_tang_ca = fields.Float(string='Tổng giờ tăng ca', compute='_compute_tong_hop', store=True)
    he_so_tang_ca = fields.Float(related='ca_lam_viec_id.he_so_tang_ca', string='Hệ số tăng ca', store=True)
    cong_tang_ca = fields.Float(string='Công tăng ca', compute='_compute_cong_tang_ca', store=True)
    
    # Nghỉ
    so_ngay_vang = fields.Integer(string='Số ngày vắng', compute='_compute_tong_hop', store=True)
    so_ngay_nghi_phep = fields.Integer(string='Số ngày nghỉ phép', compute='_compute_tong_hop', store=True)
    so_ngay_nghi_khong_phep = fields.Integer(string='Số ngày nghỉ không phép', compute='_compute_tong_hop', store=True)
    
    # Đi muộn, về sớm
    so_lan_di_muon = fields.Integer(string='Số lần đi muộn', compute='_compute_tong_hop', store=True)
    so_lan_ve_som = fields.Integer(string='Số lần về sớm', compute='_compute_tong_hop', store=True)
    
    # Công quy đổi (dùng để tính lương)
    cong_chuan_thang = fields.Float(string='Công chuẩn tháng', default=26.0, tracking=True)
    cong_quy_doi_luong = fields.Float(string='Công quy đổi lương', compute='_compute_cong_quy_doi', store=True)
    
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('da_xac_nhan', 'Đã xác nhận'),
        ('da_tinh_luong', 'Đã tính lương')
    ], string='Trạng thái', default='nhap', tracking=True)
    
    ghi_chu = fields.Text(string='Ghi chú')
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('unique_nhan_vien_thang_nam', 'UNIQUE(nhan_vien_id, thang, nam)', 
         'Mỗi nhân viên chỉ có một bản tổng hợp công cho mỗi tháng!')
    ]

    @api.depends('nhan_vien_id', 'thang', 'nam')
    def _compute_name(self):
        for record in self:
            if record.nhan_vien_id and record.thang and record.nam:
                record.name = f"TH/{record.nhan_vien_id.ma_nhan_vien}/T{record.thang}/{record.nam}"
            else:
                record.name = 'New'

    @api.depends('cham_cong_ids.so_cong', 'cham_cong_ids.so_gio_tang_ca', 'cham_cong_ids.trang_thai',
                 'cham_cong_ids.di_muon_phut', 'cham_cong_ids.ve_som_phut', 'cham_cong_ids.du_cong')
    def _compute_tong_hop(self):
        """Tối ưu bằng cách giảm số lần filtered"""
        for record in self:
            cham_cong = record.cham_cong_ids
            
            if not cham_cong:
                record.tong_cong = 0
                record.so_ngay_lam_viec = 0
                record.so_ngay_du_cong = 0
                record.so_ngay_thieu_cong = 0
                record.tong_gio_tang_ca = 0
                record.so_ngay_vang = 0
                record.so_ngay_nghi_phep = 0
                record.so_ngay_nghi_khong_phep = 0
                record.so_lan_di_muon = 0
                record.so_lan_ve_som = 0
                continue
            
            # Tổng công
            record.tong_cong = sum(cham_cong.mapped('so_cong'))
            
            # Số ngày làm việc (có giờ vào và giờ ra)
            record.so_ngay_lam_viec = sum(1 for c in cham_cong if c.gio_vao and c.gio_ra)
            
            # Đủ công / thiếu công
            record.so_ngay_du_cong = sum(1 for c in cham_cong if c.du_cong)
            record.so_ngay_thieu_cong = sum(1 for c in cham_cong 
                                            if not c.du_cong and c.trang_thai not in ['vang', 'nghi_phep', 'nghi_khong_phep'])
            
            # Tăng ca
            record.tong_gio_tang_ca = sum(cham_cong.mapped('so_gio_tang_ca'))
            
            # Nghỉ - dùng Counter cho hiệu quả hơn
            from collections import Counter
            trang_thai_count = Counter(cham_cong.mapped('trang_thai'))
            record.so_ngay_vang = trang_thai_count.get('vang', 0)
            record.so_ngay_nghi_phep = trang_thai_count.get('nghi_phep', 0)
            record.so_ngay_nghi_khong_phep = trang_thai_count.get('nghi_khong_phep', 0)
            
            # Đi muộn, về sớm
            record.so_lan_di_muon = sum(1 for c in cham_cong if c.di_muon_phut > 0)
            record.so_lan_ve_som = sum(1 for c in cham_cong if c.ve_som_phut > 0)

    @api.depends('tong_gio_tang_ca', 'he_so_tang_ca', 'ca_lam_viec_id', 'ca_lam_viec_id.so_gio_chuan')
    def _compute_cong_tang_ca(self):
        """Quy đổi giờ tăng ca thành công"""
        for record in self:
            if record.ca_lam_viec_id and record.ca_lam_viec_id.so_gio_chuan > 0:
                # Quy đổi giờ tăng ca thành công
                record.cong_tang_ca = (record.tong_gio_tang_ca / record.ca_lam_viec_id.so_gio_chuan) * record.he_so_tang_ca
            else:
                record.cong_tang_ca = 0

    @api.depends('tong_cong', 'cong_tang_ca', 'so_ngay_nghi_phep', 'so_ngay_vang')
    def _compute_cong_quy_doi(self):
        """
        Công quy đổi lương = Tổng công + Công tăng ca
        Đây là số liệu duy nhất để tính lương
        Chú ý: Nghỉ phép đã được tính trong tong_cong (= 1.0 công)
        Vắng không phép = 0 công
        """
        for record in self:
            record.cong_quy_doi_luong = record.tong_cong + record.cong_tang_ca

    def action_lay_du_lieu_cham_cong(self):
        """Lấy dữ liệu chấm công từ bảng chấm công và tính lại"""
        for record in self:
            if not record.nhan_vien_id or not record.thang or not record.nam:
                raise exceptions.UserError('Vui lòng chọn đủ thông tin nhân viên, tháng, năm!')
            
            # Tìm các bản chấm công trong tháng
            cham_cong = self.env['nhan.su.cham.cong'].search([
                ('nhan_vien_id', '=', record.nhan_vien_id.id),
                ('thang', '=', record.thang),
                ('nam', '=', record.nam)
            ])
            
            if not cham_cong:
                raise exceptions.UserError(
                    f'Không tìm thấy dữ liệu chấm công cho {record.nhan_vien_id.name} tháng {record.thang}/{record.nam}!'
                )
            
            # Cập nhật link với chấm công
            record.cham_cong_ids = [(6, 0, cham_cong.ids)]
            
            # Force recompute
            record._compute_tong_hop()
            
            record.message_post(body=f"Đã lấy {len(cham_cong)} bản chấm công và cập nhật tổng hợp.")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Thành công',
                    'message': f'Đã tải {len(cham_cong)} bản chấm công',
                    'type': 'success',
                    'sticky': False,
                }
            }
    
    @api.model
    def action_tao_tong_hop_hang_loat(self, thang, nam):
        """Tạo tổng hợp công hàng loạt cho tất cả nhân viên"""
        nhan_viens = self.env['nhan.su.nhan.vien'].search([('trang_thai', '=', 'dang_lam')])
        
        created_count = 0
        for nhan_vien in nhan_viens:
            # Kiểm tra đã tồn tại chưa
            existing = self.search([
                ('nhan_vien_id', '=', nhan_vien.id),
                ('thang', '=', thang),
                ('nam', '=', nam)
            ])
            
            if not existing:
                # Tạo mới
                tong_hop = self.create({
                    'nhan_vien_id': nhan_vien.id,
                    'thang': thang,
                    'nam': nam,
                })
                # Lấy dữ liệu chấm công
                tong_hop.action_lay_du_lieu_cham_cong()
                created_count += 1
        
        return created_count

    def action_xac_nhan(self):
        self.write({'trang_thai': 'da_xac_nhan'})
    
    def action_xac_nhan_hang_loat(self):
        """Xác nhận hàng loạt các bản tổng hợp công được chọn"""
        for record in self:
            if record.trang_thai == 'nhap':
                record.write({'trang_thai': 'da_xac_nhan'})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công',
                'message': f'Đã xác nhận {len(self)} bản tổng hợp công',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_huy_xac_nhan(self):
        self.write({'trang_thai': 'nhap'})
    
    def action_tao_tong_hop_hang_loat(self):
        """Tạo tổng hợp công hàng loạt cho tháng được chọn"""
        # Mở wizard để chọn tháng/năm
        return {
            'name': 'Tạo tổng hợp công theo tháng',
            'type': 'ir.actions.act_window',
            'res_model': 'nhan.su.tong.hop.cong.wizard',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'new',
            'context': self.env.context,
        }
    
    @api.model
    def action_tong_hop_tu_dong(self):
        """Tự động tạo tổng hợp công vào cuối tháng"""
        today = fields.Date.today()
        
        # Kiểm tra nếu là ngày cuối tháng
        import calendar
        last_day = calendar.monthrange(today.year, today.month)[1]
        
        if today.day != last_day:
            return  # Chưa phải cuối tháng
        
        thang = str(today.month)
        nam = str(today.year)
        
        # Kiểm tra đã có tổng hợp công tháng này chưa
        existing = self.search([('thang', '=', thang), ('nam', '=', nam)], limit=1)
        if existing:
            return  # Đã có rồi
        
        # Tạo tổng hợp công cho tất cả nhân viên có chấm công
        nhan_viens = self.env['nhan.su.nhan.vien'].search([
            ('trang_thai', '=', 'dang_lam')
        ])
        
        count = 0
        for nhan_vien in nhan_viens:
            # Kiểm tra có chấm công không
            cham_cong = self.env['nhan.su.cham.cong'].search([
                ('nhan_vien_id', '=', nhan_vien.id),
                ('thang', '=', thang),
                ('nam', '=', nam)
            ], limit=1)
            
            if cham_cong:
                tong_hop = self.create({
                    'nhan_vien_id': nhan_vien.id,
                    'thang': thang,
                    'nam': nam,
                })
                tong_hop.action_lay_du_lieu_cham_cong()
                count += 1
        
        if count > 0:
            # Gửi thông báo
            self.env['mail.message'].create({
                'subject': 'Tổng hợp công tự động',
                'body': f'Đã tự động tạo {count} bản tổng hợp công cho tháng {thang}/{nam}. Vui lòng kiểm tra và xác nhận.',
                'model': 'nhan.su.tong.hop.cong',
            })

    def action_tao_bang_luong_thang(self):
        """Tạo bảng lương cho tháng hiện tại từ tất cả tổng hợp công đã xác nhận"""
        if not self.ids:
            return
        
        # Lấy thông tin tháng/năm từ bản ghi đầu tiên
        first_record = self[0]
        thang = first_record.thang
        nam = first_record.nam
        
        # Kiểm tra xem đã có bảng lương tháng này chưa
        existing_bang_luong = self.env['nhan.su.bang.luong'].search([
            ('thang', '=', thang),
            ('nam', '=', nam)
        ], limit=1)
        
        if existing_bang_luong:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Thông báo',
                    'message': f'Bảng lương tháng {thang}/{nam} đã tồn tại!',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        # Tìm tất cả tổng hợp công đã xác nhận trong tháng
        tong_hop_cong_da_xac_nhan = self.search([
            ('thang', '=', thang),
            ('nam', '=', nam),
            ('trang_thai', '=', 'da_xac_nhan')
        ])
        
        if not tong_hop_cong_da_xac_nhan:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Cảnh báo',
                    'message': f'Không có tổng hợp công đã xác nhận nào cho tháng {thang}/{nam}!',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        # Tạo bảng lương mới
        bang_luong = self.env['nhan.su.bang.luong'].create({
            'thang': thang,
            'nam': nam,
            'ngay_tao': fields.Date.today(),
            'trang_thai': 'nhap',
        })
        
        # Tự động lấy dữ liệu từ tổng hợp công
        bang_luong.action_lay_du_lieu()
        
        # Hiển thị thông báo và chuyển đến bảng lương
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công',
                'message': f'Đã tạo bảng lương tháng {thang}/{nam} cho {len(tong_hop_cong_da_xac_nhan)} nhân viên!',
                'type': 'success',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window',
                    'res_model': 'nhan.su.bang.luong',
                    'res_id': bang_luong.id,
                    'view_mode': 'form',
                    'target': 'current',
                }
            }
        }
