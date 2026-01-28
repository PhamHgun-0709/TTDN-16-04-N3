# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TaiSanDashboard(models.Model):
    _name = 'tai.san.dashboard'
    _description = 'Dashboard Tài sản'

    name = fields.Char(string='Tên', default='Dashboard')
    
    # Thống kê tài sản theo tình trạng
    tong_tai_san = fields.Integer(string='Tổng tài sản', compute='_compute_stats', store=False)
    tai_san_dang_su_dung = fields.Integer(string='Đang sử dụng', compute='_compute_stats', store=False)
    tai_san_chua_mua = fields.Integer(string='Chưa mua', compute='_compute_stats', store=False)
    tai_san_thanh_ly = fields.Integer(string='Đã thanh lý', compute='_compute_stats', store=False)
    
    # Thống kê theo trạng thái
    tai_san_tot = fields.Integer(string='Tốt', compute='_compute_stats', store=False)
    tai_san_bao_tri = fields.Integer(string='Đang bảo trì', compute='_compute_stats', store=False)
    tai_san_hong = fields.Integer(string='Hỏng', compute='_compute_stats', store=False)
    tai_san_can_thay = fields.Integer(string='Cần thay thế', compute='_compute_stats', store=False)
    
    # Giá trị tài sản
    tong_nguyen_gia = fields.Float(string='Tổng nguyên giá', compute='_compute_stats', store=False)
    tong_gia_tri_con_lai = fields.Float(string='Giá trị còn lại', compute='_compute_stats', store=False)
    tong_gia_tri_khau_hao = fields.Float(string='Giá trị đã khấu hao', compute='_compute_stats', store=False)
    ti_le_khau_hao = fields.Float(string='Tỷ lệ khấu hao (%)', compute='_compute_stats', store=False)
    
    # Quản lý tài sản
    de_xuat_cho_duyet = fields.Integer(string='Đề xuất chờ duyệt', compute='_compute_stats', store=False)
    de_xuat_da_duyet = fields.Integer(string='Đề xuất đã duyệt', compute='_compute_stats', store=False)
    ung_tien_cho_duyet = fields.Integer(string='Ứng tiền chờ duyệt', compute='_compute_stats', store=False)
    ung_tien_da_chi = fields.Integer(string='Ứng tiền đã chi', compute='_compute_stats', store=False)

    def _compute_stats(self):
        for record in self:
            # Thống kê tài sản theo tình trạng
            all_ts = self.env['tai.san.tai.san'].search([('active', '=', True)])
            record.tong_tai_san = len(all_ts)
            record.tai_san_dang_su_dung = len(all_ts.filtered(lambda x: x.tinh_trang == 'dang_su_dung'))
            record.tai_san_chua_mua = len(all_ts.filtered(lambda x: x.tinh_trang == 'chua_mua'))
            record.tai_san_thanh_ly = len(all_ts.filtered(lambda x: x.tinh_trang == 'thanh_ly'))
            
            # Thống kê theo trạng thái
            record.tai_san_tot = len(all_ts.filtered(lambda x: x.trang_thai == 'tot'))
            record.tai_san_bao_tri = len(all_ts.filtered(lambda x: x.trang_thai == 'bao_tri'))
            record.tai_san_hong = len(all_ts.filtered(lambda x: x.trang_thai == 'hong'))
            record.tai_san_can_thay = len(all_ts.filtered(lambda x: x.trang_thai == 'can_thay'))
            
            # Giá trị tài sản
            record.tong_nguyen_gia = sum(all_ts.mapped('nguyen_gia'))
            record.tong_gia_tri_con_lai = sum(all_ts.mapped('gia_tri_con_lai'))
            record.tong_gia_tri_khau_hao = record.tong_nguyen_gia - record.tong_gia_tri_con_lai
            
            if record.tong_nguyen_gia > 0:
                record.ti_le_khau_hao = (record.tong_gia_tri_khau_hao / record.tong_nguyen_gia) * 100
            else:
                record.ti_le_khau_hao = 0
            
            # Quản lý tài sản
            DeXuat = self.env['tai.san.de.xuat']
            record.de_xuat_cho_duyet = DeXuat.search_count([('trang_thai', '=', 'cho_duyet')])
            record.de_xuat_da_duyet = DeXuat.search_count([('trang_thai', '=', 'da_duyet')])
            
            UngTien = self.env['tai.san.ung.tien']
            record.ung_tien_cho_duyet = UngTien.search_count([('trang_thai', '=', 'cho_duyet')])
            record.ung_tien_da_chi = UngTien.search_count([('trang_thai', 'in', ['da_duyet', 'da_chi'])])

    def action_refresh_dashboard(self):
        """Làm mới dashboard - force recompute tất cả fields"""
        self.invalidate_recordset()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_view_de_xuat_cho_duyet(self):
        """Xem danh sách đề xuất chờ duyệt"""
        return {
            'name': 'Đề xuất chờ duyệt',
            'type': 'ir.actions.act_window',
            'res_model': 'tai.san.de.xuat',
            'view_mode': 'list,form',
            'domain': [('trang_thai', '=', 'cho_duyet')],
            'context': {'search_default_cho_duyet': 1},
        }

    def action_view_ung_tien_cho_duyet(self):
        """Xem danh sách ứng tiền chờ duyệt"""
        return {
            'name': 'Ứng tiền chờ duyệt',
            'type': 'ir.actions.act_window',
            'res_model': 'tai.san.ung.tien',
            'view_mode': 'list,form',
            'domain': [('trang_thai', '=', 'cho_duyet')],
            'context': {'search_default_cho_duyet': 1},
        }

