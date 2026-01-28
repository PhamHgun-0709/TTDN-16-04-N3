#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script load demo data cho module tai_san
Chạy: docker exec odoo_app_fitdnu python3 /mnt/custom-addons/tai_san/data/load_demo_data.py
"""

import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')

import odoo
from odoo import api, SUPERUSER_ID

# Kết nối database
config = odoo.tools.config
config['db_host'] = 'db'
config['db_port'] = '5432'
config['db_user'] = 'pthung4'
config['db_password'] = 'Luck2004!'
config['db_name'] = 'myodoo'

# Init registry
odoo.netsvc.init_logger()
registry = odoo.registry('myodoo')

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    print("=" * 60)
    print("LOADING DEMO DATA FOR TAI_SAN MODULE")
    print("=" * 60)
    
    # Load demo XML file
    demo_file = '/mnt/custom-addons/tai_san/demo/demo_tai_san.xml'
    
    try:
        from odoo.tools import convert
        convert.convert_file(
            cr, 'tai_san', demo_file, 
            {}, 'init', False, 'test', 
            registry._assertion_report
        )
        cr.commit()
        print("\n✅ Demo data loaded successfully!")
        
        # Verify data
        tai_san_count = env['tai.san.tai.san'].search_count([])
        de_xuat_count = env['tai.san.de.xuat'].search_count([])
        cap_phat_count = env['tai.san.cap.phat'].search_count([])
        
        print(f"\n📊 Created records:")
        print(f"   - Tài sản: {tai_san_count}")
        print(f"   - Đề xuất: {de_xuat_count}")
        print(f"   - Cấp phát: {cap_phat_count}")
        
    except Exception as e:
        print(f"\n❌ Error loading demo data: {e}")
        import traceback
        traceback.print_exc()
        cr.rollback()
    
print("\n" + "=" * 60)
