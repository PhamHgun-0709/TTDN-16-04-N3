# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BaoCaoThuChi(models.TransientModel):
    _name = 'tai.chinh.ke.toan.bao.cao.thu.chi'
    _description = 'Báo cáo thu chi'

    tu_ngay = fields.Date(string='Từ ngày', required=True, default=fields.Date.today)
    den_ngay = fields.Date(string='Đến ngày', required=True, default=fields.Date.today)
    loai_bao_cao = fields.Selection([
        ('tong_hop', 'Tổng hợp'),
        ('chi_tiet', 'Chi tiết'),
        ('theo_loai', 'Theo loại'),
    ], string='Loại báo cáo', default='tong_hop', required=True)
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)

    def action_xem_bao_cao(self):
        """Hiển thị báo cáo thu chi"""
        self.ensure_one()
        
        # Lấy dữ liệu phiếu thu
        phieu_thu = self.env['tai.chinh.ke.toan.phieu.thu'].search([
            ('ngay_lap', '>=', self.tu_ngay),
            ('ngay_lap', '<=', self.den_ngay),
            ('trang_thai', '=', 'da_thu'),
            ('company_id', '=', self.company_id.id),
        ])
        
        # Lấy dữ liệu phiếu chi
        phieu_chi = self.env['tai.chinh.ke.toan.phieu.chi'].search([
            ('ngay_lap', '>=', self.tu_ngay),
            ('ngay_lap', '<=', self.den_ngay),
            ('trang_thai', '=', 'da_chi'),
            ('company_id', '=', self.company_id.id),
        ])
        
        tong_thu = sum(phieu_thu.mapped('so_tien'))
        tong_chi = sum(phieu_chi.mapped('so_tien'))
        
        if self.loai_bao_cao == 'tong_hop':
            return self._bao_cao_tong_hop(tong_thu, tong_chi)
        elif self.loai_bao_cao == 'chi_tiet':
            return self._bao_cao_chi_tiet(phieu_thu, phieu_chi)
        else:
            return self._bao_cao_theo_loai(phieu_thu, phieu_chi)
    
    def _bao_cao_tong_hop(self, tong_thu, tong_chi):
        """Báo cáo tổng hợp"""
        message = f"""
        <h3>BÁO CÁO THU CHI TỔNG HỢP</h3>
        <p>Từ ngày: {self.tu_ngay} - Đến ngày: {self.den_ngay}</p>
        <table class="table table-bordered">
            <tr><td><b>Tổng thu:</b></td><td style="text-align: right;">{tong_thu:,.0f} VNĐ</td></tr>
            <tr><td><b>Tổng chi:</b></td><td style="text-align: right;">{tong_chi:,.0f} VNĐ</td></tr>
            <tr style="background-color: #f0f0f0;"><td><b>Chênh lệch:</b></td><td style="text-align: right;"><b>{(tong_thu - tong_chi):,.0f} VNĐ</b></td></tr>
        </table>
        """
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Báo cáo thu chi'),
                'message': message,
                'type': 'info',
                'sticky': True,
            }
        }
    
    def _bao_cao_chi_tiet(self, phieu_thu, phieu_chi):
        """Báo cáo chi tiết - Mở tree view"""
        # Hiển thị cả phiếu thu và chi trong 2 tab
        return {
            'name': _('Báo cáo thu chi chi tiết'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'tai.chinh.ke.toan.phieu.thu',
            'domain': [('id', 'in', phieu_thu.ids)],
            'context': {
                'default_tu_ngay': self.tu_ngay,
                'default_den_ngay': self.den_ngay,
            }
        }
    
    def _bao_cao_theo_loai(self, phieu_thu, phieu_chi):
        """Báo cáo theo loại thu/chi"""
        # Nhóm theo loại
        thu_theo_loai = {}
        for pt in phieu_thu:
            loai = dict(pt._fields['loai_thu'].selection).get(pt.loai_thu, 'Khác')
            thu_theo_loai[loai] = thu_theo_loai.get(loai, 0) + pt.so_tien
        
        chi_theo_loai = {}
        for pc in phieu_chi:
            loai = dict(pc._fields['loai_chi'].selection).get(pc.loai_chi, 'Khác')
            chi_theo_loai[loai] = chi_theo_loai.get(loai, 0) + pc.so_tien
        
        message = f"""
        <h3>BÁO CÁO THU CHI THEO LOẠI</h3>
        <p>Từ ngày: {self.tu_ngay} - Đến ngày: {self.den_ngay}</p>
        
        <h4>THU THEO LOẠI:</h4>
        <table class="table table-bordered">
        """
        for loai, tien in thu_theo_loai.items():
            message += f"<tr><td>{loai}</td><td style='text-align: right;'>{tien:,.0f} VNĐ</td></tr>"
        
        message += """
        </table>
        
        <h4>CHI THEO LOẠI:</h4>
        <table class="table table-bordered">
        """
        for loai, tien in chi_theo_loai.items():
            message += f"<tr><td>{loai}</td><td style='text-align: right;'>{tien:,.0f} VNĐ</td></tr>"
        
        message += "</table>"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Báo cáo theo loại'),
                'message': message,
                'type': 'info',
                'sticky': True,
            }
        }

    def action_xuat_excel(self):
        """Xuất báo cáo ra Excel - TODO: Cần implement"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Thông báo'),
                'message': _('Chức năng xuất Excel đang được phát triển!'),
                'type': 'warning',
            }
        }
