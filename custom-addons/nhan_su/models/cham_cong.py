# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class ChamCong(models.Model):
    _name = 'nhan.su.cham.cong'
    _description = 'Chấm công thô'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'ngay_cham_cong desc'

    name = fields.Char(string='Mã chấm công', required=True, copy=False, readonly=True, default='New', tracking=True)
    nhan_vien_id = fields.Many2one('nhan.su.nhan.vien', string='Nhân viên', required=True, ondelete='restrict', tracking=True)
    phong_ban_id = fields.Many2one(related='nhan_vien_id.phong_ban_id', string='Phòng ban', store=True)
    ca_lam_viec_id = fields.Many2one('nhan.su.ca.lam.viec', string='Ca làm việc', tracking=True)
    
    ngay_cham_cong = fields.Date(string='Ngày', required=True, default=fields.Date.today, tracking=True)
    thang = fields.Selection([
        ('1', 'Tháng 1'), ('2', 'Tháng 2'), ('3', 'Tháng 3'),
        ('4', 'Tháng 4'), ('5', 'Tháng 5'), ('6', 'Tháng 6'),
        ('7', 'Tháng 7'), ('8', 'Tháng 8'), ('9', 'Tháng 9'),
        ('10', 'Tháng 10'), ('11', 'Tháng 11'), ('12', 'Tháng 12')
    ], string='Tháng', compute='_compute_thang_nam', store=True)
    nam = fields.Char(string='Năm', compute='_compute_thang_nam', store=True)
    
    # Dữ liệu chấm công thô
    gio_vao = fields.Float(string='Giờ vào', tracking=True)
    gio_ra = fields.Float(string='Giờ ra', tracking=True)
    so_gio_thuc_te = fields.Float(string='Số giờ thực tế', compute='_compute_so_gio_thuc_te', store=True)
    
    # So sánh với ca làm việc
    gio_bat_dau_ca = fields.Float(related='ca_lam_viec_id.gio_bat_dau', string='Giờ bắt đầu ca')
    gio_ket_thuc_ca = fields.Float(related='ca_lam_viec_id.gio_ket_thuc', string='Giờ kết thúc ca')
    so_gio_chuan = fields.Float(related='ca_lam_viec_id.so_gio_chuan', string='Số giờ chuẩn')
    
    # Kết quả phân tích
    di_muon_phut = fields.Integer(string='Đi muộn (phút)', compute='_compute_di_muon_ve_som', store=True)
    ve_som_phut = fields.Integer(string='Về sớm (phút)', compute='_compute_di_muon_ve_som', store=True)
    
    du_cong = fields.Boolean(string='Đủ công', compute='_compute_du_cong', store=True)
    thieu_cong = fields.Float(string='Thiếu công', compute='_compute_thieu_cong', store=True)
    so_cong = fields.Float(string='Số công', compute='_compute_so_cong', store=True)
    
    so_gio_tang_ca = fields.Float(string='Số giờ tăng ca', compute='_compute_tang_ca', store=True)
    
    loai_ngay = fields.Selection([
        ('binh_thuong', 'Ngày thường'),
        ('cuoi_tuan', 'Cuối tuần'),
        ('le', 'Ngày lễ')
    ], string='Loại ngày', default='binh_thuong', tracking=True)
    
    trang_thai = fields.Selection([
        ('du_cong', 'Đủ công'),
        ('tang_ca', 'Tăng ca'),
        ('thieu_cong', 'Thiếu công'),
        ('di_tre', 'Đi trễ'),
        ('ve_som', 'Về sớm'),
        ('vang', 'Vắng'),
        ('nghi_phep', 'Nghỉ phép'),
        ('nghi_khong_phep', 'Nghỉ không phép'),
        ('cong_tac', 'Công tác')
    ], string='Trạng thái', compute='_compute_trang_thai', store=True, tracking=True)
    
    ghi_chu = fields.Text(string='Ghi chú')
    xac_nhan_hr = fields.Boolean(string='HR xác nhận', tracking=True)
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('unique_nhan_vien_ngay', 'UNIQUE(nhan_vien_id, ngay_cham_cong)', 
         'Mỗi nhân viên chỉ được chấm công một lần trong ngày!')
    ]

    @api.onchange('nhan_vien_id')
    def _onchange_nhan_vien_id(self):
        """Tự động điền ca làm việc khi chọn nhân viên"""
        if self.nhan_vien_id and self.nhan_vien_id.ca_lam_viec_id:
            self.ca_lam_viec_id = self.nhan_vien_id.ca_lam_viec_id

    @api.depends('ngay_cham_cong')
    def _compute_thang_nam(self):
        for record in self:
            if record.ngay_cham_cong:
                record.thang = str(record.ngay_cham_cong.month)
                record.nam = str(record.ngay_cham_cong.year)
            else:
                record.thang = False
                record.nam = False

    @api.depends('gio_vao', 'gio_ra', 'ca_lam_viec_id')
    def _compute_so_gio_thuc_te(self):
        """Tính số giờ thực tế dựa trên ca sáng/chiều hoặc ca thông thường"""
        for record in self:
            if not record.gio_vao or not record.gio_ra:
                record.so_gio_thuc_te = 0
                continue
                
            if record.ca_lam_viec_id and record.ca_lam_viec_id.su_dung_ca_sang_chieu:
                # Ca sáng/chiều: tự động trừ nghỉ trưa
                ca = record.ca_lam_viec_id
                gio_thuc_te = record.gio_ra - record.gio_vao
                
                # Nếu làm quá giờ nghỉ trưa, trừ đi thời gian nghỉ (từ gio_ket_thuc_sang đến gio_bat_dau_chieu)
                if record.gio_vao < ca.gio_bat_dau_chieu and record.gio_ra > ca.gio_ket_thuc_sang:
                    thoi_gian_nghi = ca.gio_bat_dau_chieu - ca.gio_ket_thuc_sang
                    gio_thuc_te -= thoi_gian_nghi
                
                record.so_gio_thuc_te = max(0, gio_thuc_te)
            else:
                # Ca thông thường (legacy)
                if record.ca_lam_viec_id and record.ca_lam_viec_id.loai_ca == 'hanh_chinh':
                    record.so_gio_thuc_te = max(0, record.gio_ra - record.gio_vao - 1)
                else:
                    record.so_gio_thuc_te = max(0, record.gio_ra - record.gio_vao)

    @api.depends('gio_vao', 'gio_bat_dau_ca', 'gio_ra', 'gio_ket_thuc_ca', 'ca_lam_viec_id',
                 'ca_lam_viec_id.su_dung_ca_sang_chieu', 'ca_lam_viec_id.gio_bat_dau_sang',
                 'ca_lam_viec_id.gio_ket_thuc_chieu')
    def _compute_di_muon_ve_som(self):
        """Tính đi muộn/về sớm cho ca sáng/chiều và ca thông thường"""
        for record in self:
            if not record.ca_lam_viec_id or not record.gio_vao or not record.gio_ra:
                record.di_muon_phut = 0
                record.ve_som_phut = 0
                continue
            
            ca = record.ca_lam_viec_id
            
            if ca.su_dung_ca_sang_chieu:
                # Ca sáng/chiều: đi muộn tính theo giờ sáng, về sớm tính theo giờ chiều
                gio_cho_phep_vao = ca.gio_bat_dau_sang + (ca.cho_phep_di_muon / 60.0)
                if record.gio_vao > gio_cho_phep_vao:
                    record.di_muon_phut = int((record.gio_vao - ca.gio_bat_dau_sang) * 60)
                else:
                    record.di_muon_phut = 0
                
                gio_cho_phep_ra = ca.gio_ket_thuc_chieu - (ca.cho_phep_ve_som / 60.0)
                if record.gio_ra < gio_cho_phep_ra:
                    record.ve_som_phut = int((ca.gio_ket_thuc_chieu - record.gio_ra) * 60)
                else:
                    record.ve_som_phut = 0
            else:
                # Ca thông thường (legacy)
                gio_cho_phep_vao = ca.gio_bat_dau + (ca.cho_phep_di_muon / 60.0)
                if record.gio_vao > gio_cho_phep_vao:
                    record.di_muon_phut = int((record.gio_vao - ca.gio_bat_dau) * 60)
                else:
                    record.di_muon_phut = 0
                
                gio_cho_phep_ra = ca.gio_ket_thuc - (ca.cho_phep_ve_som / 60.0)
                if record.gio_ra < gio_cho_phep_ra:
                    record.ve_som_phut = int((ca.gio_ket_thuc - record.gio_ra) * 60)
                else:
                    record.ve_som_phut = 0

    @api.depends('so_gio_thuc_te', 'so_gio_chuan')
    def _compute_du_cong(self):
        for record in self:
            if record.so_gio_chuan > 0:
                ty_le = (record.so_gio_thuc_te / record.so_gio_chuan) * 100
                record.du_cong = ty_le >= 100
            else:
                record.du_cong = False

    @api.depends('so_gio_thuc_te', 'so_gio_chuan', 'du_cong')
    def _compute_thieu_cong(self):
        for record in self:
            if not record.du_cong and record.so_gio_chuan > 0:
                ty_le_thieu = (record.so_gio_chuan - record.so_gio_thuc_te) / record.so_gio_chuan
                record.thieu_cong = max(0, min(1, ty_le_thieu))  # Giới hạn 0-1
            else:
                record.thieu_cong = 0

    @api.depends('so_gio_thuc_te', 'so_gio_chuan', 'trang_thai', 'di_muon_phut', 've_som_phut')
    def _compute_so_cong(self):
        """
        Logic tính công cải tiến:
        - Nghỉ phép → 1 công
        - Vắng/nghỉ không phép → 0 công
        - ≥ 87.5% giờ chuẩn (7/8 giờ) → 1 công (dung sai 1 tiếng)
        - 50% – <87.5% → 0.5 công
        - < 50% → 0 công
        """
        for record in self:
            if record.trang_thai == 'nghi_phep':
                record.so_cong = 1.0
            elif record.trang_thai in ['vang', 'nghi_khong_phep']:
                record.so_cong = 0
            elif record.so_gio_chuan > 0:
                ty_le = record.so_gio_thuc_te / record.so_gio_chuan
                
                # Nếu làm từ 87.5% giờ chuẩn trở lên (7/8 giờ) → 1 công
                if ty_le >= 0.875:
                    record.so_cong = 1.0
                elif ty_le >= 0.5:
                    record.so_cong = 0.5
                else:
                    record.so_cong = 0
            else:
                record.so_cong = 0

    @api.depends('gio_vao', 'gio_ra', 'so_gio_thuc_te', 'ca_lam_viec_id', 'ca_lam_viec_id.so_gio_chuan')
    def _compute_tang_ca(self):
        """
        Tính tăng ca = Số giờ thực tế - Số giờ chuẩn (nếu > 0)
        Tăng ca có thể đến từ:
        - Vào sớm hơn giờ bắt đầu ca
        - Ra muộn hơn giờ kết thúc ca
        """
        for record in self:
            if not record.ca_lam_viec_id or not record.gio_vao or not record.gio_ra:
                record.so_gio_tang_ca = 0
                continue
            
            ca = record.ca_lam_viec_id
            so_gio_chuan = ca.so_gio_chuan or 8.0
            
            # Tăng ca = giờ thực tế - giờ chuẩn (nếu dương)
            if record.so_gio_thuc_te > so_gio_chuan:
                record.so_gio_tang_ca = round(record.so_gio_thuc_te - so_gio_chuan, 2)
            else:
                record.so_gio_tang_ca = 0

    def action_check_in(self):
        """Check-in: Ghi nhận giờ vào = giờ hiện tại"""
        from datetime import datetime
        for record in self:
            now = datetime.now()
            # Chuyển giờ hiện tại thành số thập phân (8h30 = 8.5)
            gio_hien_tai = now.hour + now.minute / 60.0
            record.gio_vao = gio_hien_tai
            record.message_post(body=f"✅ Check-in lúc {now.strftime('%H:%M')}")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công',
                'message': f'Đã check-in lúc {datetime.now().strftime("%H:%M")}',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_check_out(self):
        """Check-out: Ghi nhận giờ ra = giờ hiện tại"""
        from datetime import datetime
        for record in self:
            now = datetime.now()
            # Chuyển giờ hiện tại thành số thập phân (17h30 = 17.5)
            gio_hien_tai = now.hour + now.minute / 60.0
            record.gio_ra = gio_hien_tai
            record.message_post(body=f"🚪 Check-out lúc {now.strftime('%H:%M')}")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công',
                'message': f'Đã check-out lúc {datetime.now().strftime("%H:%M")}',
                'type': 'success',
                'sticky': False,
            }
        }

    @api.depends('gio_vao', 'gio_ra', 'di_muon_phut', 've_som_phut', 'du_cong', 'so_gio_thuc_te', 'so_gio_chuan', 'so_gio_tang_ca')
    def _compute_trang_thai(self):
        """
        Logic tính trạng thái:
        - Có tăng ca (> 0) → Tăng ca
        - Đủ giờ thực tế → Đủ công
        - Chưa đủ giờ → xác định nguyên nhân (đi trễ/về sớm/thiếu công)
        """
        for record in self:
            if not record.gio_vao and not record.gio_ra:
                record.trang_thai = 'vang'
            elif record.so_gio_tang_ca > 0:
                # Có tăng ca → Tăng ca
                record.trang_thai = 'tang_ca'
            elif record.du_cong:
                # Đủ giờ thực tế, không tăng ca → Đủ công
                record.trang_thai = 'du_cong'
            else:
                # Chưa đủ giờ → xác định nguyên nhân
                if record.di_muon_phut > 0 and record.ve_som_phut > 0:
                    # Vừa đi muộn vừa về sớm → thiếu công
                    record.trang_thai = 'thieu_cong'
                elif record.di_muon_phut > 0:
                    record.trang_thai = 'di_tre'
                elif record.ve_som_phut > 0:
                    record.trang_thai = 've_som'
                else:
                    record.trang_thai = 'thieu_cong'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('nhan.su.cham.cong') or 'New'
        return super(ChamCong, self).create(vals_list)

    @api.constrains('gio_vao', 'gio_ra')
    def _check_gio_vao_ra(self):
        for record in self:
            # Kiểm tra giới hạn giờ hợp lệ
            if record.gio_vao and (record.gio_vao < 0 or record.gio_vao > 24):
                raise exceptions.ValidationError('Giờ vào phải trong khoảng 0-24!')
            if record.gio_ra and (record.gio_ra < 0 or record.gio_ra > 24):
                raise exceptions.ValidationError('Giờ ra phải trong khoảng 0-24!')
            
            # Kiểm tra logic giờ vào/ra
            if record.gio_vao and record.gio_ra:
                if record.gio_ra <= record.gio_vao:
                    raise exceptions.ValidationError('Giờ ra phải lớn hơn giờ vào!')
                if (record.gio_ra - record.gio_vao) > 16:
                    raise exceptions.ValidationError('Số giờ làm việc trong ngày không được vượt quá 16 giờ!')
    
    @api.model
    def action_cham_cong_tu_dong(self):
        """Chấm công tự động cho tất cả nhân viên đang làm việc"""
        import random
        today = fields.Date.today()
        thang = str(today.month)
        nam = str(today.year)
        
        # Kiểm tra nếu đã có chấm công hôm nay thì không tạo nữa
        existing = self.search([('ngay_cham_cong', '=', today)], limit=1)
        if existing:
            return
        
        # Lấy tất cả nhân viên đang làm việc
        nhan_viens = self.env['nhan.su.nhan.vien'].search([
            ('trang_thai', '=', 'dang_lam'),
            ('ca_lam_viec_id', '!=', False)
        ])
        
        count = 0
        for nhan_vien in nhan_viens:
            # Random giờ vào/ra (mô phỏng thực tế)
            gio_vao = 8.0 + random.uniform(-0.3, 0.5)  # 7:42 - 8:30
            gio_ra = 17.0 + random.uniform(-0.3, 1.0)   # 16:42 - 18:00
            
            # 5% khả năng nghỉ
            if random.random() < 0.05:
                continue
            
            self.create({
                'nhan_vien_id': nhan_vien.id,
                'ca_lam_viec_id': nhan_vien.ca_lam_viec_id.id,
                'ngay_cham_cong': today,
                'gio_vao': gio_vao,
                'gio_ra': gio_ra,
                'loai_ngay': 'binh_thuong',
            })
            count += 1
        
        if count > 0:
            self.env['mail.message'].create({
                'subject': 'Chấm công tự động',
                'body': f'Đã tự động chấm công cho {count} nhân viên ngày {today.strftime("%d/%m/%Y")}',
                'model': 'nhan.su.cham.cong',
            })

