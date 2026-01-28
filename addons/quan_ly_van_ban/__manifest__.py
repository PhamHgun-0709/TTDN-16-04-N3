# -*- coding: utf-8 -*-
{
    'name': "Quản lý Văn bản",
    'summary': "Quản lý văn bản đến và văn bản đi",
    'description': """
        Module quản lý văn bản:
        - Loại văn bản
        - Văn bản đến
        - Văn bản đi
    """,
    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Administration',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/demo_data.xml',
        'views/loai_van_ban_views.xml',
        'views/van_ban_den_views.xml',
        'views/van_ban_di_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
