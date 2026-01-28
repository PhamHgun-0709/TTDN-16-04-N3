#!/bin/bash
# Load demo data via odoo shell

docker exec -i odoo_app_fitdnu python3 /usr/bin/odoo shell -c /etc/odoo/odoo.conf -d myodoo --no-http << 'EOFPYTHON'

from odoo.tools import convert

print("="*60)
print("LOADING DEMO DATA FOR TAI_SAN MODULE")
print("="*60)

# Load demo XML
demo_file = '/mnt/custom-addons/tai_san/demo/demo_tai_san.xml'

try:
    convert.convert_file(
        env.cr, 'tai_san', demo_file,
        {}, 'init', False, 'test',
        env.registry._assertion_report
    )
    env.cr.commit()
    
    # Verify
    tai_san_count = env['tai.san.tai.san'].search_count([])
    de_xuat_count = env['tai.san.de.xuat'].search_count([])
    cap_phat_count = env['tai.san.cap.phat'].search_count([])
    
    print(f"\n✅ Demo data loaded successfully!")
    print(f"\n📊 Created records:")
    print(f"   - Tài sản: {tai_san_count}")
    print(f"   - Đề xuất: {de_xuat_count}")
    print(f"   - Cấp phát: {cap_phat_count}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    env.cr.rollback()

print("\n" + "="*60)

EOFPYTHON
