# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import datetime


class TongHopCongWizard(models.TransientModel):
    _name = 'nhan.su.tong.hop.cong.wizard'
    _description = 'Wizard tạo tổng hợp công hàng loạt'

    thang = fields.Selection([
        ('1', 'Tháng 1'), ('2', 'Tháng 2'), ('3', 'Tháng 3'),
        ('4', 'Tháng 4'), ('5', 'Tháng 5'), ('6', 'Tháng 6'),
        ('7', 'Tháng 7'), ('8', 'Tháng 8'), ('9', 'Tháng 9'),
        ('10', 'Tháng 10'), ('11', 'Tháng 11'), ('12', 'Tháng 12'),
    ], string='Tháng', required=True, default=lambda self: str(datetime.now().month))
    
    nam = fields.Char(string='Năm', required=True, default=lambda self: str(datetime.now().year))

    def action_tao_tong_hop(self):
        """Tạo tổng hợp công cho tất cả nhân viên có chấm công trong tháng"""
        self.ensure_one()
        
        # Kiểm tra đã có tổng hợp công trong tháng này chưa
        existing = self.env['nhan.su.tong.hop.cong'].search([
            ('thang', '=', self.thang),
            ('nam', '=', self.nam)
        ])
        
        if existing:
            raise exceptions.UserError(
                f'Đã tồn tại {len(existing)} bản tổng hợp công cho tháng {self.thang}/{self.nam}!\n\n'
                'Vui lòng xóa các bản tổng hợp cũ hoặc chọn tháng khác.'
            )
        
        # Lấy danh sách nhân viên có chấm công trong tháng
        cham_congs = self.env['nhan.su.cham.cong'].search([
            ('thang', '=', self.thang),
            ('nam', '=', self.nam)
        ])
        
        if not cham_congs:
            raise exceptions.UserError(
                f'Không tìm thấy dữ liệu chấm công nào cho tháng {self.thang}/{self.nam}!\n\n'
                'Vui lòng nhập chấm công trước.'
            )
        
        # Lấy danh sách nhân viên unique
        nhan_vien_ids = cham_congs.mapped('nhan_vien_id').ids
        
        # Tạo tổng hợp công cho từng nhân viên
        created_count = 0
        for nhan_vien_id in nhan_vien_ids:
            tong_hop = self.env['nhan.su.tong.hop.cong'].create({
                'nhan_vien_id': nhan_vien_id,
                'thang': self.thang,
                'nam': self.nam,
            })
            # Tự động lấy dữ liệu chấm công
            tong_hop.action_lay_du_lieu_cham_cong()
            created_count += 1
        
        # Chuyển đến list view tổng hợp công vừa tạo
        return {
            'type': 'ir.actions.act_window',
            'name': f'Tổng hợp công tháng {self.thang}/{self.nam} ({created_count} bản ghi)',
            'res_model': 'nhan.su.tong.hop.cong',
            'view_mode': 'list,form',
            'views': [(False, 'list'), (False, 'form')],
            'domain': [('thang', '=', self.thang), ('nam', '=', self.nam)],
            'target': 'current',
        }
