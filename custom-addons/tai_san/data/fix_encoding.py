#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script sửa encoding UTF-8 cho dữ liệu cũ trong module tai_san
Chạy: docker exec odoo_app_fitdnu python3 /mnt/custom-addons/tai_san/data/fix_encoding.py
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
from odoo.modules.registry import Registry
registry = Registry('myodoo')

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    print("=" * 60)
    print("FIX ENCODING UTF-8 FOR TAI_SAN DATA")
    print("=" * 60)
    
    # Sửa vị trí tài sản
    tai_sans = env['tai.san.tai.san'].search([])
    fixed_count = 0
    
    for ts in tai_sans:
        try:
            if ts.vi_tri and ('?' in ts.vi_tri or '�' in ts.vi_tri):
                print(f"❌ Lỗi encoding: {ts.ma_tai_san} - {ts.vi_tri}")
                # Thử khôi phục text gốc
                new_vi_tri = ts.vi_tri
                replacements = {
                    'V??n ph??ng': 'Văn phòng',
                    't???ng': 'tầng',
                    't??ng': 'tầng',
                    'Ph??ng k???': 'Phòng kế',
                    'to??n': 'toán',
                    'B??i xe': 'Bãi xe',
                    'c??ng ty': 'công ty',
                    'Khu v???c': 'Khu vực',
                    'chung t???ng': 'chung tầng',
                    'Ph??ng': 'Phòng',
                    'kinh doanh': 'kinh doanh'
                }
                
                for old, new in replacements.items():
                    if old in new_vi_tri:
                        new_vi_tri = new_vi_tri.replace(old, new)
                
                if new_vi_tri != ts.vi_tri:
                    ts.vi_tri = new_vi_tri
                    print(f"✅ Đã sửa: {ts.ma_tai_san} - {new_vi_tri}")
                    fixed_count += 1
        except Exception as e:
            print(f"⚠️ Không sửa được {ts.ma_tai_san}: {e}")
    
    if fixed_count > 0:
        cr.commit()
        print(f"\n✅ Đã sửa {fixed_count} bản ghi!")
    else:
        print("\n✅ Không có lỗi encoding nào cần sửa!")
    
print("=" * 60)
