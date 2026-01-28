# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class TaiChinhDashboard(models.Model):
    _name = 'tai.chinh.ke.toan.dashboard'
    _description = 'Dashboard Tài chính'

    name = fields.Char(string='Tên', default='Dashboard Tài chính', readonly=True)
    
    # Tổng quan thu chi tháng hiện tại
    tong_thu_thang = fields.Float(string='Tổng thu tháng này', compute='_compute_dashboard_data', store=False)
    tong_chi_thang = fields.Float(string='Tổng chi tháng này', compute='_compute_dashboard_data', store=False)
    chenh_lech_thang = fields.Float(string='Chênh lệch tháng', compute='_compute_dashboard_data', store=False)
    ty_le_loi_nhuan = fields.Float(string='Tỷ lệ lợi nhuận', compute='_compute_dashboard_data', store=False)
    
    # Tồn quỹ và phân loại
    ton_quy_hien_tai = fields.Float(string='Tồn quỹ hiện tại', compute='_compute_dashboard_data', store=False)
    ton_quy_tien_mat = fields.Float(string='Tiền mặt', compute='_compute_dashboard_data', store=False)
    ton_quy_ngan_hang = fields.Float(string='Ngân hàng', compute='_compute_dashboard_data', store=False)
    
    # So sánh với tháng trước
    tong_thu_thang_truoc = fields.Float(string='Tổng thu tháng trước', compute='_compute_dashboard_data', store=False)
    tong_chi_thang_truoc = fields.Float(string='Tổng chi tháng trước', compute='_compute_dashboard_data', store=False)
    ty_le_tang_giam_thu = fields.Float(string='% tăng/giảm thu', compute='_compute_dashboard_data', store=False)
    ty_le_tang_giam_chi = fields.Float(string='% tăng/giảm chi', compute='_compute_dashboard_data', store=False)
    
    # Thống kê phiếu thu
    so_phieu_thu_cho_thu = fields.Integer(string='Phiếu thu chờ thu', compute='_compute_dashboard_data', store=False)
    so_phieu_thu_da_thu = fields.Integer(string='Phiếu thu đã thu', compute='_compute_dashboard_data', store=False)
    tong_tien_phieu_thu_cho = fields.Float(string='Tiền phiếu thu chờ', compute='_compute_dashboard_data', store=False)
    
    # Thống kê phiếu chi
    so_phieu_chi_cho_chi = fields.Integer(string='Phiếu chi chờ chi', compute='_compute_dashboard_data', store=False)
    so_phieu_chi_da_chi = fields.Integer(string='Phiếu chi đã chi', compute='_compute_dashboard_data', store=False)
    tong_tien_phieu_chi_cho = fields.Float(string='Tiền phiếu chi chờ', compute='_compute_dashboard_data', store=False)
    
    # Thống kê duyệt
    so_phieu_cho_duyet = fields.Integer(string='Phiếu chờ duyệt', compute='_compute_dashboard_data', store=False)
    so_phieu_da_duyet = fields.Integer(string='Phiếu đã duyệt', compute='_compute_dashboard_data', store=False)

    def _compute_dashboard_data(self):
        """Compute dashboard data - không cache để luôn lấy dữ liệu mới nhất"""
        for record in self:
            company_id = self.env.company.id
            today = fields.Date.today()
            
            # Tháng này
            thang_nay_start = today.replace(day=1)
            thang_nay_end = (thang_nay_start + relativedelta(months=1)) - timedelta(days=1)
            
            # Tháng trước
            thang_truoc_start = (thang_nay_start - relativedelta(months=1))
            thang_truoc_end = thang_nay_start - timedelta(days=1)
            
            # PHẦN 1: TỔNG THU CHI THÁNG NÀY
            # Tổng thu tháng này (đã thu)
            phieu_thu_thang = self.env['tai.chinh.ke.toan.phieu.thu'].search([
                ('ngay_lap', '>=', thang_nay_start),
                ('ngay_lap', '<=', thang_nay_end),
                ('trang_thai', '=', 'da_thu'),
            ])
            record.tong_thu_thang = sum(phieu_thu_thang.mapped('so_tien'))
            
            # Tổng chi tháng này (đã chi)
            phieu_chi_thang = self.env['tai.chinh.ke.toan.phieu.chi'].search([
                ('ngay_lap', '>=', thang_nay_start),
                ('ngay_lap', '<=', thang_nay_end),
                ('trang_thai', '=', 'da_chi'),
            ])
            record.tong_chi_thang = sum(phieu_chi_thang.mapped('so_tien'))
            
            # Chênh lệch = thu - chi
            record.chenh_lech_thang = record.tong_thu_thang - record.tong_chi_thang
            
            # Tỷ lệ lợi nhuận = (chênh lệch / tổng thu) * 100
            if record.tong_thu_thang > 0:
                record.ty_le_loi_nhuan = (record.chenh_lech_thang / record.tong_thu_thang) * 100
            else:
                record.ty_le_loi_nhuan = 0
            
            # PHẦN 2: TỒN QUỸ
            # Tồn quỹ hiện tại (tổng)
            all_so_quy = self.env['tai.chinh.ke.toan.so.quy'].search([])
            record.ton_quy_hien_tai = sum(all_so_quy.mapped('ton_quy'))
            tien_mat_total = 0
            tien_ngan_hang_total = 0
            for sq in all_so_quy:
                if hasattr(sq, 'loai_quy'):
                    if sq.loai_quy == 'tien_mat':
                        tien_mat_total += sq.ton_quy if hasattr(sq, 'ton_quy') else 0
                    else:
                        tien_ngan_hang_total += sq.ton_quy if hasattr(sq, 'ton_quy') else 0
            
            # Nếu không có field loại quỹ, tạm chia theo tỷ lệ
            if tien_mat_total == 0 and tien_ngan_hang_total == 0:
                record.ton_quy_tien_mat = record.ton_quy_hien_tai * 0.4
                record.ton_quy_ngan_hang = record.ton_quy_hien_tai * 0.6
            else:
                record.ton_quy_tien_mat = tien_mat_total
                record.ton_quy_ngan_hang = tien_ngan_hang_total
            
            # PHẦN 3: SO SÁNH VỚI THÁNG TRƯỚC
            # Tháng trước
            phieu_thu_thang_truoc = self.env['tai.chinh.ke.toan.phieu.thu'].search([
                ('ngay_lap', '>=', thang_truoc_start),
                ('ngay_lap', '<=', thang_truoc_end),
                ('trang_thai', '=', 'da_thu'),
            ])
            record.tong_thu_thang_truoc = sum(phieu_thu_thang_truoc.mapped('so_tien'))
            
            phieu_chi_thang_truoc = self.env['tai.chinh.ke.toan.phieu.chi'].search([
                ('ngay_lap', '>=', thang_truoc_start),
                ('ngay_lap', '<=', thang_truoc_end),
                ('trang_thai', '=', 'da_chi'),
            ])
            record.tong_chi_thang_truoc = sum(phieu_chi_thang_truoc.mapped('so_tien'))
            
            # Tỷ lệ tăng/giảm
            if record.tong_thu_thang_truoc > 0:
                record.ty_le_tang_giam_thu = ((record.tong_thu_thang - record.tong_thu_thang_truoc) / record.tong_thu_thang_truoc) * 100
            else:
                # Nếu tháng trước = 0, không tính % (hiển thị 0)
                record.ty_le_tang_giam_thu = 0
                
            if record.tong_chi_thang_truoc > 0:
                record.ty_le_tang_giam_chi = ((record.tong_chi_thang - record.tong_chi_thang_truoc) / record.tong_chi_thang_truoc) * 100
            else:
                # Nếu tháng trước = 0, không tính % (hiển thị 0)
                record.ty_le_tang_giam_chi = 0
            
            # PHẦN 4: THỐNG KÊ PHIẾU THU
            # Phiếu thu chờ thu
            phieu_thu_cho = self.env['tai.chinh.ke.toan.phieu.thu'].search([
                ('trang_thai', 'in', ['cho_duyet', 'da_duyet']),
            ])
            record.so_phieu_thu_cho_thu = len(phieu_thu_cho)
            record.tong_tien_phieu_thu_cho = sum(phieu_thu_cho.mapped('so_tien'))
            
            # Phiếu thu đã thu
            phieu_thu_da_thu = self.env['tai.chinh.ke.toan.phieu.thu'].search([
                ('trang_thai', '=', 'da_thu'),
            ])
            record.so_phieu_thu_da_thu = len(phieu_thu_da_thu)
            
            # PHẦN 5: THỐNG KÊ PHIẾU CHI
            # Phiếu chi chờ chi
            phieu_chi_cho = self.env['tai.chinh.ke.toan.phieu.chi'].search([
                ('trang_thai', 'in', ['cho_duyet', 'da_duyet']),
            ])
            record.so_phieu_chi_cho_chi = len(phieu_chi_cho)
            record.tong_tien_phieu_chi_cho = sum(phieu_chi_cho.mapped('so_tien'))
            
            # Phiếu chi đã chi
            phieu_chi_da_chi = self.env['tai.chinh.ke.toan.phieu.chi'].search([
                ('trang_thai', '=', 'da_chi'),
            ])
            record.so_phieu_chi_da_chi = len(phieu_chi_da_chi)
            
            # PHẦN 6: THỐNG KÊ DUYỆT
            # Số phiếu chờ duyệt (cả thu và chi)
            record.so_phieu_cho_duyet = self.env['tai.chinh.ke.toan.phieu.chi'].search_count([
                ('trang_thai', '=', 'cho_duyet'),
            ]) + self.env['tai.chinh.ke.toan.phieu.thu'].search_count([
                ('trang_thai', '=', 'cho_duyet'),
            ])
            
            # Số phiếu đã duyệt (cả thu và chi)
            record.so_phieu_da_duyet = self.env['tai.chinh.ke.toan.phieu.chi'].search_count([
                ('trang_thai', '=', 'da_duyet'),
            ]) + self.env['tai.chinh.ke.toan.phieu.thu'].search_count([
                ('trang_thai', '=', 'da_duyet'),
            ])

    def action_refresh_dashboard(self):
        """Làm mới dashboard - force recompute tất cả fields"""
        self.invalidate_recordset()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_view_phieu_cho_duyet(self):
        """Xem danh sách phiếu chờ duyệt (cả thu và chi)"""
        # Đếm số phiếu từng loại
        phieu_chi_count = self.env['tai.chinh.ke.toan.phieu.chi'].search_count([
            ('trang_thai', '=', 'cho_duyet')
        ])
        
        phieu_thu_count = self.env['tai.chinh.ke.toan.phieu.thu'].search_count([
            ('trang_thai', '=', 'cho_duyet')
        ])
        
        total = phieu_chi_count + phieu_thu_count
        
        if total == 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Thông báo',
                    'message': 'Không có phiếu nào chờ duyệt',
                    'type': 'info',
                    'sticky': False,
                }
            }
        
        # Mở menu chọn xem phiếu chi hay phiếu thu
        return {
            'name': f'Phiếu chờ duyệt ({total} phiếu: {phieu_chi_count} chi, {phieu_thu_count} thu)',
            'type': 'ir.actions.act_window',
            'res_model': 'tai.chinh.ke.toan.phieu.chi',  # Mặc định hiển thị phiếu chi
            'view_mode': 'list,form',
            'domain': [('trang_thai', '=', 'cho_duyet')],
            'context': {
                'search_default_cho_duyet': 1,
            },
            'help': f'''
                <p class="o_view_nocontent_smiling_face">
                    Có {total} phiếu chờ duyệt
                </p>
                <p>
                    • {phieu_chi_count} phiếu chi chờ duyệt<br/>
                    • {phieu_thu_count} phiếu thu chờ duyệt
                </p>
                <p>Để xem phiếu thu, vào menu: Tài chính > Thu Chi > Phiếu thu</p>
            ''',
        }

    def action_view_phieu_da_duyet(self):
        """Xem danh sách phiếu đã duyệt (cả thu và chi)"""
        phieu_chi_ids = self.env['tai.chinh.ke.toan.phieu.chi'].search([
            ('trang_thai', '=', 'da_duyet')
        ]).ids
        
        phieu_thu_ids = self.env['tai.chinh.ke.toan.phieu.thu'].search([
            ('trang_thai', '=', 'da_duyet')
        ]).ids
        
        if phieu_chi_ids:
            return {
                'name': 'Phiếu chi đã duyệt',
                'type': 'ir.actions.act_window',
                'res_model': 'tai.chinh.ke.toan.phieu.chi',
                'view_mode': 'list,form',
                'domain': [('id', 'in', phieu_chi_ids)],
                'context': {'search_default_da_duyet': 1},
            }
        elif phieu_thu_ids:
            return {
                'name': 'Phiếu thu đã duyệt',
                'type': 'ir.actions.act_window',
                'res_model': 'tai.chinh.ke.toan.phieu.thu',
                'view_mode': 'list,form',
                'domain': [('id', 'in', phieu_thu_ids)],
                'context': {'search_default_da_duyet': 1},
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Thông báo',
                    'message': 'Không có phiếu nào đã duyệt',
                    'type': 'info',
                    'sticky': False,
                }
            }

    def action_view_so_quy(self):
        """Xem sổ quỹ"""
        return {
            'name': 'Sổ quỹ',
            'type': 'ir.actions.act_window',
            'res_model': 'tai.chinh.ke.toan.so.quy',
            'view_mode': 'list,form',
        }
