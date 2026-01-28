# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CaLamViec(models.Model):
    _name = 'nhan.su.ca.lam.viec'
    _description = 'Ca làm việc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Tên ca', required=True, tracking=True)
    ma_ca = fields.Char(string='Mã ca', required=True, copy=False, tracking=True)
    
    # Thời gian ca làm việc (legacy - giữ để tương thích)
    gio_bat_dau = fields.Float(string='Giờ bắt đầu', default=8.0, tracking=True, help='VD: 8.0 = 08:00')
    gio_ket_thuc = fields.Float(string='Giờ kết thúc', default=17.0, tracking=True, help='VD: 17.0 = 17:00')
    
    # Ca sáng/chiều (chuẩn 8h/ngày)
    gio_bat_dau_sang = fields.Float(string='Giờ bắt đầu sáng', default=8.5, tracking=True, help='VD: 8.5 = 08:30')
    gio_ket_thuc_sang = fields.Float(string='Giờ kết thúc sáng', default=12.0, tracking=True, help='VD: 12.0 = 12:00')
    gio_bat_dau_chieu = fields.Float(string='Giờ bắt đầu chiều', default=13.0, tracking=True, help='VD: 13.0 = 13:00')
    gio_ket_thuc_chieu = fields.Float(string='Giờ kết thúc chiều', default=17.5, tracking=True, help='VD: 17.5 = 17:30')
    
    su_dung_ca_sang_chieu = fields.Boolean(string='Sử dụng ca sáng/chiều', default=True, tracking=True,
                                            help='Bật để dùng ca chia sáng/chiều (8:30-12:00, 13:00-17:30)')
    so_gio_chuan = fields.Float(string='Số giờ chuẩn', compute='_compute_so_gio_chuan', store=True)
    
    # Ngày làm việc trong tuần
    ngay_lam_viec_ids = fields.Many2many('nhan.su.ngay.lam.viec', string='Ngày làm việc')
    
    # Dung sai
    cho_phep_di_muon = fields.Integer(string='Cho phép đi muộn (phút)', default=15, tracking=True)
    cho_phep_ve_som = fields.Integer(string='Cho phép về sớm (phút)', default=15, tracking=True)
    
    # Tăng ca
    bat_dau_tinh_tang_ca = fields.Float(string='Bắt đầu tính tăng ca', tracking=True, help='Nếu để trống, sẽ dùng giờ kết thúc ca')
    he_so_tang_ca = fields.Float(string='Hệ số tăng ca', default=1.5, tracking=True)
    
    # Áp dụng
    ap_dung_tu_ngay = fields.Date(string='Áp dụng từ ngày', tracking=True)
    ap_dung_den_ngay = fields.Date(string='Áp dụng đến ngày', tracking=True)
    loai_ca = fields.Selection([
        ('hanh_chinh', 'Hành chính')
    ], string='Loại ca', default='hanh_chinh', tracking=True)
    
    # Nhân viên áp dụng
    nhan_vien_ids = fields.One2many('nhan.su.nhan.vien', 'ca_lam_viec_id', string='Nhân viên', ondelete='set null')
    so_luong_nhan_vien = fields.Integer(string='Số lượng nhân viên', compute='_compute_so_luong_nhan_vien', store=True)
    
    ghi_chu = fields.Text(string='Ghi chú')
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('ma_ca_unique', 'UNIQUE(ma_ca)', 'Mã ca phải là duy nhất!')
    ]

    @api.depends('gio_bat_dau_sang', 'gio_ket_thuc_sang', 'gio_bat_dau_chieu', 'gio_ket_thuc_chieu',
                 'gio_bat_dau', 'gio_ket_thuc', 'loai_ca', 'su_dung_ca_sang_chieu')
    def _compute_so_gio_chuan(self):
        """Tính số giờ chuẩn: ưu tiên ca sáng/chiều (8h/ngày), fallback về ca thông thường"""
        for record in self:
            if record.su_dung_ca_sang_chieu:
                # Ca sáng/chiều: 8:30-12:00 (3.5h) + 13:00-17:30 (4.5h) = 8h
                gio_sang = max(0, record.gio_ket_thuc_sang - record.gio_bat_dau_sang)
                gio_chieu = max(0, record.gio_ket_thuc_chieu - record.gio_bat_dau_chieu)
                record.so_gio_chuan = gio_sang + gio_chieu
            else:
                # Ca thông thường (legacy)
                if record.gio_ket_thuc > record.gio_bat_dau:
                    tong_gio = record.gio_ket_thuc - record.gio_bat_dau
                    # Trừ 1 giờ nghỉ trưa nếu là ca hành chính và ca > 4 giờ
                    if record.loai_ca == 'hanh_chinh' and tong_gio > 4:
                        record.so_gio_chuan = max(0, tong_gio - 1)
                    else:
                        record.so_gio_chuan = tong_gio
                else:
                    record.so_gio_chuan = 0

    @api.depends('nhan_vien_ids')
    def _compute_so_luong_nhan_vien(self):
        for record in self:
            record.so_luong_nhan_vien = len(record.nhan_vien_ids)

    @api.onchange('gio_ket_thuc', 'gio_ket_thuc_chieu', 'su_dung_ca_sang_chieu')
    def _onchange_gio_ket_thuc(self):
        """Tự động điền giờ bắt đầu tính tăng ca nếu chưa có"""
        if not self.bat_dau_tinh_tang_ca:
            if self.su_dung_ca_sang_chieu:
                self.bat_dau_tinh_tang_ca = self.gio_ket_thuc_chieu
            else:
                self.bat_dau_tinh_tang_ca = self.gio_ket_thuc

    @api.constrains('gio_bat_dau', 'gio_ket_thuc', 'bat_dau_tinh_tang_ca',
                    'gio_bat_dau_sang', 'gio_ket_thuc_sang', 'gio_bat_dau_chieu', 'gio_ket_thuc_chieu')
    def _check_gio_bat_dau_ket_thuc(self):
        for record in self:
            # Kiểm tra giới hạn giờ 0-24
            fields_to_check = [
                ('gio_bat_dau', 'Giờ bắt đầu'),
                ('gio_ket_thuc', 'Giờ kết thúc'),
                ('gio_bat_dau_sang', 'Giờ bắt đầu sáng'),
                ('gio_ket_thuc_sang', 'Giờ kết thúc sáng'),
                ('gio_bat_dau_chieu', 'Giờ bắt đầu chiều'),
                ('gio_ket_thuc_chieu', 'Giờ kết thúc chiều'),
                ('bat_dau_tinh_tang_ca', 'Giờ bắt đầu tính tăng ca')
            ]
            
            for field_name, label in fields_to_check:
                value = getattr(record, field_name, None)
                if value and (value < 0 or value > 24):
                    raise models.ValidationError(f'{label} phải trong khoảng 0-24!')
            
            if record.su_dung_ca_sang_chieu:
                # Kiểm tra logic ca sáng/chiều
                if record.gio_ket_thuc_sang <= record.gio_bat_dau_sang:
                    raise models.ValidationError('Giờ kết thúc sáng phải lớn hơn giờ bắt đầu sáng!')
                if record.gio_ket_thuc_chieu <= record.gio_bat_dau_chieu:
                    raise models.ValidationError('Giờ kết thúc chiều phải lớn hơn giờ bắt đầu chiều!')
                if record.gio_bat_dau_chieu <= record.gio_ket_thuc_sang:
                    raise models.ValidationError('Giờ bắt đầu chiều phải sau giờ kết thúc sáng (thời gian nghỉ trưa)!')
            else:
                # Kiểm tra logic ca thông thường
                if record.gio_ket_thuc <= record.gio_bat_dau:
                    raise models.ValidationError('Giờ kết thúc phải lớn hơn giờ bắt đầu!')
                
                # Cảnh báo nếu ca quá ngắn hoặc quá dài
                tong_gio = record.gio_ket_thuc - record.gio_bat_dau
                if tong_gio < 2:
                    raise models.ValidationError('Ca làm việc không nên ngắn hơn 2 giờ!')
                if tong_gio > 12:
                    raise models.ValidationError('Ca làm việc không nên dài quá 12 giờ!')
