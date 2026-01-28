# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
from calendar import monthrange


class NhanSuDashboard(models.Model):
    _name = 'nhan.su.dashboard'
    _description = 'Dashboard Nhân sự'

    name = fields.Char(string='Tên', default='Dashboard')
    
    # Thống kê nhân viên theo trạng thái
    tong_nhan_vien = fields.Integer(string='Tổng nhân viên', compute='_compute_stats', store=False)
    nhan_vien_dang_lam = fields.Integer(string='Đang làm việc', compute='_compute_stats', store=False)
    nhan_vien_thu_viec = fields.Integer(string='Thử việc', compute='_compute_stats', store=False)
    nhan_vien_nghi_viec = fields.Integer(string='Nghỉ việc', compute='_compute_stats', store=False)
    
    # Thống kê chấm công tháng này
    tong_ngay_cong = fields.Integer(string='Tổng công tháng', compute='_compute_stats', store=False)
    ngay_di_lam = fields.Integer(string='Tổng ngày công đi làm', compute='_compute_stats', store=False)
    ngay_nghi_phep = fields.Integer(string='Ngày nghỉ phép', compute='_compute_stats', store=False)
    ngay_vang = fields.Integer(string='Ngày vắng', compute='_compute_stats', store=False)
    ti_le_di_lam = fields.Float(string='Tỷ lệ đi làm (%)', compute='_compute_stats', store=False)
    
    # Thống kê lương
    tong_luong_thang = fields.Float(string='Tổng lương tháng', compute='_compute_stats', store=False)
    luong_trung_binh = fields.Float(string='Lương TB/người', compute='_compute_stats', store=False)
    tong_phu_cap = fields.Float(string='Tổng phụ cấp', compute='_compute_stats', store=False)
    tong_thuong = fields.Float(string='Tổng thưởng', compute='_compute_stats', store=False)

    def _compute_stats(self):
        for record in self:
            # Thống kê nhân viên theo trạng thái
            all_nv = self.env['nhan.su.nhan.vien'].search([('active', '=', True)])
            record.tong_nhan_vien = len(all_nv)
            record.nhan_vien_dang_lam = len(all_nv.filtered(lambda x: x.trang_thai == 'dang_lam'))
            record.nhan_vien_thu_viec = len(all_nv.filtered(lambda x: x.trang_thai == 'thu_viec'))
            record.nhan_vien_nghi_viec = len(all_nv.filtered(lambda x: x.trang_thai == 'nghi_viec'))
            
            # Lấy thông tin tháng hiện tại
            today = fields.Date.today()
            thang = str(today.month)
            nam = str(today.year)
            
            # Tính số ngày làm việc trong tháng (trừ thứ 7, CN)
            _, last_day_num = monthrange(int(nam), int(thang))
            so_ngay_lam_viec = 0
            
            for day in range(1, last_day_num + 1):
                date = datetime(int(nam), int(thang), day)
                if date.weekday() < 5:  # Thứ 2-6
                    so_ngay_lam_viec += 1
            
            # Thống kê chấm công tháng này
            cham_cong = self.env['nhan.su.cham.cong'].search([
                ('thang', '=', thang),
                ('nam', '=', nam)
            ])
            
            record.tong_ngay_cong = len(cham_cong)
            record.ngay_di_lam = len(cham_cong.filtered(lambda x: x.trang_thai in ['du_cong', 'tang_ca', 'di_tre', 've_som']))
            record.ngay_nghi_phep = len(cham_cong.filtered(lambda x: x.trang_thai == 'nghi_phep'))
            record.ngay_vang = len(cham_cong.filtered(lambda x: x.trang_thai in ['vang', 'nghi']))
            
            # Tính tỷ lệ đi làm
            tong_ngay_can_lam = record.nhan_vien_dang_lam * so_ngay_lam_viec
            if tong_ngay_can_lam > 0:
                record.ti_le_di_lam = (record.ngay_di_lam / tong_ngay_can_lam) * 100
            else:
                record.ti_le_di_lam = 0
            
            # Thống kê lương tháng hiện tại
            bang_luong = self.env['nhan.su.bang.luong'].search([
                ('thang', '=', thang),
                ('nam', '=', nam),
                ('trang_thai', '=', 'da_duyet')
            ], limit=1)
            
            if bang_luong:
                record.tong_luong_thang = bang_luong.tong_thuc_linh
                record.luong_trung_binh = bang_luong.tong_thuc_linh / bang_luong.so_nhan_vien if bang_luong.so_nhan_vien else 0
                record.tong_phu_cap = bang_luong.tong_phu_cap
                record.tong_thuong = bang_luong.tong_thuong
            else:
                # Ước tính từ lương cơ bản
                nv_dang_lam = all_nv.filtered(lambda x: x.trang_thai == 'dang_lam')
                record.tong_luong_thang = sum(nv_dang_lam.mapped('luong_co_ban'))
                record.luong_trung_binh = record.tong_luong_thang / len(nv_dang_lam) if nv_dang_lam else 0
                record.tong_phu_cap = 0
                record.tong_thuong = 0

    def action_refresh_dashboard(self):
        """Làm mới dashboard - force recompute tất cả fields"""
        self.invalidate_recordset()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_view_nhan_vien(self):
        """Xem danh sách nhân viên"""
        return {
            'name': 'Nhân viên',
            'type': 'ir.actions.act_window',
            'res_model': 'nhan.su.nhan.vien',
            'view_mode': 'kanban,list,form',
            'context': {'search_default_dang_lam': 1},
        }

    def action_view_cham_cong(self):
        """Xem chấm công tháng này"""
        today = fields.Date.today()
        return {
            'name': 'Chấm công tháng này',
            'type': 'ir.actions.act_window',
            'res_model': 'nhan.su.cham.cong',
            'view_mode': 'list,form',
            'domain': [('thang', '=', str(today.month)), ('nam', '=', str(today.year))],
        }

