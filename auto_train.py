#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auto train ML model - No interaction needed"""

import sys
import os

# Setup paths
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

print("\n" + "="*70)
print("🤖 AUTO TRAINING ML MODEL...")
print("="*70 + "\n")

try:
    import odoo
    from odoo import api
    from odoo.modules.registry import Registry
    from datetime import datetime, timedelta
    
    # Load config - path in Docker container
    print("📝 Loading config...")
    config_path = '/etc/odoo/odoo.conf'
    odoo.tools.config.parse_config(['-c', config_path])
    
    # Database name
    print("🔍 Using database: myodoo")
    db_name = 'myodoo'
    
    print(f"\n🔌 Connected to database: {db_name}")
    
    # Initialize
    registry = Registry(db_name)
    
    with registry.cursor() as cr:
        env = api.Environment(cr, odoo.SUPERUSER_ID, {})
        
        # Check module
        print("📦 Checking module...")
        try:
            model = env['tai.chinh.ke.toan.canh.bao.gian.lan']
            PhieuChi = env['tai.chinh.ke.toan.phieu.chi']
        except:
            print("❌ Module 'tai_chinh_ke_toan' not installed!")
            print("   Please install the module first.")
            sys.exit(1)
        
        print("✓ Module found\n")
        
        # Check data
        total = PhieuChi.search_count([('trang_thai', '=', 'da_chi')])
        print(f"📊 Current data: {total} phiếu chi")
        
        # Create demo if needed
        if total < 30:
            print(f"⚠️  Only {total} records, creating demo data...")
            
            today = datetime.now().date()
            
            demo_list = [
                {'name': 'Demo - High amount', 'amount': 500000000, 'days': 1},
                {'name': 'Demo - Round 10M', 'amount': 10000000, 'days': 2},
                {'name': 'Demo - Round 20M', 'amount': 20000000, 'days': 3},
                {'name': 'Demo - Weekend', 'amount': 75000000, 'days': 4},
                {'name': 'Demo - End month', 'amount': 30000000, 'days': 5},
                {'name': 'Demo - Normal 1', 'amount': 5500000, 'days': 6},
                {'name': 'Demo - Normal 2', 'amount': 7200000, 'days': 7},
                {'name': 'Demo - Normal 3', 'amount': 3800000, 'days': 8},
                {'name': 'Demo - Normal 4', 'amount': 6100000, 'days': 9},
                {'name': 'Demo - Normal 5', 'amount': 4500000, 'days': 10},
                {'name': 'Demo - High 2', 'amount': 450000000, 'days': 11},
                {'name': 'Demo - Round 15M', 'amount': 15000000, 'days': 12},
                {'name': 'Demo - Normal 6', 'amount': 8900000, 'days': 13},
                {'name': 'Demo - Normal 7', 'amount': 5200000, 'days': 14},
                {'name': 'Demo - Normal 8', 'amount': 6700000, 'days': 15},
                {'name': 'Demo - Round 5M', 'amount': 5000000, 'days': 16},
                {'name': 'Demo - High 3', 'amount': 380000000, 'days': 17},
                {'name': 'Demo - Normal 9', 'amount': 7800000, 'days': 18},
                {'name': 'Demo - Normal 10', 'amount': 6300000, 'days': 19},
                {'name': 'Demo - Round 25M', 'amount': 25000000, 'days': 20},
            ]
            
            # Get or create default partner for demo
            Partner = env['res.partner']
            demo_partner = Partner.search([('name', '=', 'Demo Partner')], limit=1)
            if not demo_partner:
                demo_partner = Partner.create({
                    'name': 'Demo Partner',
                    'company_type': 'person',
                })
            
            created = 0
            for data in demo_list:
                try:
                    PhieuChi.create({
                        'name': data['name'],
                        'so_tien': data['amount'],
                        'ngay_chi': today - timedelta(days=data['days']),
                        'doi_tuong_id': demo_partner.id,
                        'ly_do_chi': 'ML training demo data',
                        'trang_thai': 'da_chi',
                    })
                    created += 1
                except Exception as e:
                    print(f"   ! Error creating {data['name']}: {e}")
            
            cr.commit()
            print(f"✓ Created {created} demo records\n")
            total += created
        
        # TRAIN
        print("🧠 TRAINING ML MODEL...")
        print("   (This may take 30-60 seconds...)\n")
        
        min_samples = 10 if total < 50 else 30
        
        try:
            result = model.train_ml_model(min_samples=min_samples)
            
            if result:
                print("\n" + "="*70)
                print("✅ TRAINING SUCCESSFUL!")
                print("="*70)
                
                # Get model info
                model_data = model._load_ml_model()
                if model_data:
                    print(f"\n📊 Model Info:")
                    print(f"   • Samples trained: {model_data['n_samples']}")
                    print(f"   • Features: {', '.join(model_data['feature_names'])}")
                    print(f"   • Trained at: {model_data['trained_date']}")
                    print(f"   • Model path: {model._get_model_path()}")
                
                # Run detection
                print("\n🔍 Running fraud detection...")
                model.phat_hien_gian_lan_tu_dong()
                
                # Show results
                alerts = model.search([], limit=5, order='hybrid_score desc')
                if alerts:
                    print(f"\n📊 Top 5 Alerts:")
                    for i, alert in enumerate(alerts, 1):
                        method = dict(alert._fields['detection_method'].selection).get(alert.detection_method, 'N/A')
                        level = dict(alert._fields['muc_do_nguy_hiem'].selection).get(alert.muc_do_nguy_hiem, 'N/A')
                        print(f"   {i}. {alert.name}")
                        print(f"      Score: {alert.hybrid_score:.1f} | Method: {method} | Level: {level}")
                
                print("\n🎯 Next Steps:")
                print("   • View alerts in Odoo UI: Tài chính > Cảnh báo gian lận")
                print("   • Model will auto-retrain every 7 days")
                print("   • Detection runs daily automatically")
                
                print("\n" + "="*70)
                print("🎉 ALL DONE!")
                print("="*70 + "\n")
                
            else:
                print("\n❌ Training failed! Check logs.")
                sys.exit(1)
                
        except Exception as e:
            print(f"\n❌ Error during training: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\n💡 This script must run inside Odoo environment:")
    print("   1. Docker: docker exec -it <container> python auto_train.py")
    print("   2. Or use Odoo shell (see TRAIN_INSTRUCTIONS.md)")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
