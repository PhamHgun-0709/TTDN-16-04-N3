# -*- coding: utf-8 -*-
{
    'name': 'Quản lý Tài chính - Kế toán',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Module quản lý tài chính và kế toán',
    'description': """
        Module quản lý tài chính và kế toán
        ====================================
        - Quản lý thu chi
        - Quản lý công nợ
        - Báo cáo tài chính
        - Quản lý ngân sách
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': ['base', 'account', 'mail', 'nhan_su', 'tai_san'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/ir_cron_data.xml',
        'views/phieu_chi_views.xml',
        'views/phieu_thu_views.xml',
        'views/so_quy_views.xml',
        'views/khau_hao_tai_san_views.xml',
        'views/dong_khau_hao_views.xml',
        'views/bao_cao_views.xml',
        'views/thanh_toan_hang_loat_views.xml',
        'views/canh_bao_gian_lan_views.xml',
        'views/dashboard_views.xml',
        'views/menu_views.xml',
        # 'security/canh_bao_gian_lan.csv',
    ],
    'demo': [
        'data/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
