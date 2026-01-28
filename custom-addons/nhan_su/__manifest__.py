# -*- coding: utf-8 -*-
{
    'name': 'Quản lý Nhân sự',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Module quản lý nhân sự',
    'description': """
        Module quản lý nhân sự
        ========================
        - Quản lý thông tin nhân viên
        - Quản lý hợp đồng lao động
        - Quản lý chấm công
        - Quản lý bảng lương
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': ['base', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/ngay_lam_viec_data.xml',
        'data/demo_data.xml',
        'data/cham_cong_demo.xml',
        'data/ir_cron.xml',
        'wizard/tong_hop_cong_wizard_views.xml',
        'views/phong_ban_views.xml',
        'views/chuc_vu_views.xml',
        'views/nhan_vien_views.xml',
        'views/ca_lam_viec_views.xml',
        'views/cham_cong_views.xml',
        'views/tong_hop_cong_views.xml',
        'views/bang_luong_views.xml',
        'views/chi_tiet_luong_views.xml',
        'views/dashboard_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
