# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ThanhToanHangLoat(models.TransientModel):
    _name = 'tai.chinh.ke.toan.thanh.toan.hang.loat'
    _description = 'Thanh toán hàng loạt'

    loai_phieu = fields.Selection([
        ('chi', 'Chi tiền'),
        ('thu', 'Thu tiền'),
        ('duyet', 'Duyệt'),
    ], string='Loại thao tác', required=True, default='duyet')
    
    phieu_ids = fields.Many2many('tai.chinh.ke.toan.phieu.chi', 'thanh_toan_phieu_chi_rel', 'thanh_toan_id', 'phieu_chi_id', string='Phiếu chi')
    phieu_thu_ids = fields.Many2many('tai.chinh.ke.toan.phieu.thu', 'thanh_toan_phieu_thu_rel', 'thanh_toan_id', 'phieu_thu_id', string='Phiếu thu')
    
    tong_so_phieu = fields.Integer(string='Tổng số phiếu', compute='_compute_tong_so_phieu')
    tong_tien = fields.Float(string='Tổng tiền', compute='_compute_tong_tien')
    
    ghi_chu = fields.Text(string='Ghi chú')

    @api.depends('phieu_ids', 'phieu_thu_ids')
    def _compute_tong_so_phieu(self):
        for record in self:
            record.tong_so_phieu = len(record.phieu_ids) + len(record.phieu_thu_ids)

    @api.depends('phieu_ids', 'phieu_thu_ids')
    def _compute_tong_tien(self):
        for record in self:
            tong_chi = sum(record.phieu_ids.mapped('so_tien'))
            tong_thu = sum(record.phieu_thu_ids.mapped('so_tien'))
            record.tong_tien = tong_chi + tong_thu

    @api.model
    def default_get(self, fields_list):
        res = super(ThanhToanHangLoat, self).default_get(fields_list)
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids', [])
        
        if active_model == 'tai.chinh.ke.toan.phieu.chi':
            res['phieu_ids'] = [(6, 0, active_ids)]
            res['loai_phieu'] = 'chi'
        elif active_model == 'tai.chinh.ke.toan.phieu.thu':
            res['phieu_thu_ids'] = [(6, 0, active_ids)]
            res['loai_phieu'] = 'thu'
        
        return res

    def action_thuc_hien(self):
        """Thực hiện thanh toán hàng loạt"""
        self.ensure_one()
        
        thanh_cong = 0
        that_bai = 0
        loi_messages = []
        
        if self.loai_phieu == 'chi':
            for phieu in self.phieu_ids:
                try:
                    if phieu.trang_thai == 'da_duyet':
                        phieu.action_chi_tien()
                        thanh_cong += 1
                    else:
                        that_bai += 1
                        loi_messages.append(f"{phieu.name}: Chưa được duyệt")
                except Exception as e:
                    that_bai += 1
                    loi_messages.append(f"{phieu.name}: {str(e)}")
                    
        elif self.loai_phieu == 'thu':
            for phieu in self.phieu_thu_ids:
                try:
                    if phieu.trang_thai == 'da_duyet':
                        phieu.action_thu_tien()
                        thanh_cong += 1
                    else:
                        that_bai += 1
                        loi_messages.append(f"{phieu.name}: Chưa được duyệt")
                except Exception as e:
                    that_bai += 1
                    loi_messages.append(f"{phieu.name}: {str(e)}")
                    
        elif self.loai_phieu == 'duyet':
            # Duyệt cả phiếu chi và thu
            for phieu in self.phieu_ids:
                if phieu.trang_thai == 'cho_duyet':
                    phieu.action_duyet()
                    thanh_cong += 1
                else:
                    that_bai += 1
                    loi_messages.append(f"{phieu.name}: Không ở trạng thái chờ duyệt")
                    
            for phieu in self.phieu_thu_ids:
                if phieu.trang_thai == 'cho_duyet':
                    phieu.action_duyet()
                    thanh_cong += 1
                else:
                    that_bai += 1
                    loi_messages.append(f"{phieu.name}: Không ở trạng thái chờ duyệt")
        
        # Tạo thông báo kết quả
        message = f"""
        <h4>Kết quả xử lý hàng loạt</h4>
        <p><strong>Thành công:</strong> {thanh_cong} phiếu</p>
        <p><strong>Thất bại:</strong> {that_bai} phiếu</p>
        """
        
        if loi_messages:
            message += "<h5>Chi tiết lỗi:</h5><ul>"
            for msg in loi_messages[:10]:  # Chỉ hiển thị 10 lỗi đầu
                message += f"<li>{msg}</li>"
            if len(loi_messages) > 10:
                message += f"<li>... và {len(loi_messages) - 10} lỗi khác</li>"
            message += "</ul>"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Hoàn thành'),
                'message': message,
                'type': 'success' if that_bai == 0 else 'warning',
                'sticky': True,
            }
        }

    def action_xem_danh_sach(self):
        """Xem danh sách phiếu đã chọn"""
        self.ensure_one()
        
        if self.phieu_ids:
            return {
                'name': _('Phiếu chi đã chọn'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'tai.chinh.ke.toan.phieu.chi',
                'domain': [('id', 'in', self.phieu_ids.ids)],
            }
        elif self.phieu_thu_ids:
            return {
                'name': _('Phiếu thu đã chọn'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'tai.chinh.ke.toan.phieu.thu',
                'domain': [('id', 'in', self.phieu_thu_ids.ids)],
            }
