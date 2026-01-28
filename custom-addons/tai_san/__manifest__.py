# -*- coding: utf-8 -*-
{
    'name': 'Quản lý Tài sản',
    'version': '1.0',
    'category': 'Asset Management',
    'summary': 'Module quản lý tài sản',
    'description': """
        Module quản lý tài sản
        ========================
        - Quản lý tài sản cố định
        - Quản lý khấu hao tài sản
        - Quản lý bảo trì tài sản
        - Báo cáo tài sản
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': ['base', 'account', 'nhan_su'],
    'data': [
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'views/tai_san_views.xml',
        'views/de_xuat_tai_san_views.xml',
        'views/phe_duyet_views.xml',
        'views/ung_tien_views.xml',
        'views/mua_tai_san_views.xml',
        'views/cap_phat_tai_san_views.xml',
        'views/thay_the_tai_san_views.xml',
        'views/dashboard_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [
        'demo/demo_tai_san.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
