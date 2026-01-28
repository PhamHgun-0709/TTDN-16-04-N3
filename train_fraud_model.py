#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để train ML model cho fraud detection
Chạy: python train_fraud_model.py [database_name]
"""

import sys
import os

# Add Odoo to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import odoo
from odoo import api

def train_model(db_name=None):
    """Train ML fraud detection model"""
    
    print("\n" + "="*70)
    print("🤖 AI FRAUD DETECTION - TRAINING SCRIPT")
    print("="*70 + "\n")
    
    # Cấu hình
    config_file = 'odoo.conf'
    
    print("📝 Đang load config...")
    odoo.tools.config.parse_config(['-c', config_file])
    
    # Auto-detect database nếu không có argument
    if not db_name and len(sys.argv) > 1:
        db_name = sys.argv[1]
    
    if not db_name:
        print("\n📋 Đang tìm databases...")
        import psycopg2
        try:
            conn = psycopg2.connect(
                host=odoo.tools.config['db_host'],
                port=odoo.tools.config['db_port'],
                user=odoo.tools.config['db_user'],
                password=odoo.tools.config['db_password'],
                dbname='postgres'
            )
            cur = conn.cursor()
            cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false AND datname NOT IN ('postgres', 'template0', 'template1');")
            databases = [row[0] for row in cur.fetchall()]
            cur.close()
            conn.close()
            
            if len(databases) == 1:
                db_name = databases[0]
                print(f"✓ Tự động chọn database: {db_name}")
            elif len(databases) > 1:
                print("Tìm thấy nhiều databases:")
                for i, db in enumerate(databases, 1):
                    print(f"   {i}. {db}")
                print(f"\nSử dụng: python train_fraud_model.py <database_name>")
                return False
            else:
                print("❌ Không tìm thấy database nào!")
                return False
                
        except Exception as e:
            print(f"❌ Lỗi kết nối PostgreSQL: {e}")
            print("💡 Nếu dùng Docker, database có thể đang trong container.")
            print("   Thử: docker exec -it <container> python train_fraud_model.py")
            return False
    
    print(f"\n🔌 Đang kết nối database: {db_name}")
    
    try:
        # Initialize Odoo registry
        registry = odoo.registry(db_name)
        
        with registry.cursor() as cr:
            env = api.Environment(cr, odoo.SUPERUSER_ID, {})
            
            # Kiểm tra module có cài chưa
            module = env['ir.module.module'].search([
                ('name', '=', 'tai_chinh_ke_toan'),
                ('state', '=', 'installed')
            ])
            
            if not module:
                print("❌ Module 'tai_chinh_ke_toan' chưa được cài đặt!")
                print("   Vui lòng cài module trước khi train.")
                return False
            
            print("✓ Module đã được cài đặt\n")
            
            # Kiểm tra số lượng dữ liệu
            PhieuChi = env['tai.chinh.ke.toan.phieu.chi']
            total = PhieuChi.search_count([('trang_thai', '=', 'da_chi')])
            
            print(f"📊 Số lượng phiếu chi: {total}")
            
            if total < 30:
                print(f"⚠️  Chỉ có {total} phiếu chi (khuyến nghị >= 50)")
                print("🎭 Tự động tạo dữ liệu demo...")
                
                from datetime import datetime, timedelta
                import random
                
                today = datetime.now().date()
                
                demo_data = [
                    {'name': 'Demo - Số tiền cao bất thường', 'so_tien': 500000000, 'days_ago': 1},
                    {'name': 'Demo - Số tiền tròn', 'so_tien': 10000000, 'days_ago': 2},
                    {'name': 'Demo - Cuối tuần', 'so_tien': 75000000, 'days_ago': 3},
                    {'name': 'Demo - Cuối tháng', 'so_tien': 30000000, 'days_ago': 4},
                    {'name': 'Demo - Bình thường 1', 'so_tien': 5500000, 'days_ago': 5},
                    {'name': 'Demo - Bình thường 2', 'so_tien': 7200000, 'days_ago': 6},
                    {'name': 'Demo - Bình thường 3', 'so_tien': 3800000, 'days_ago': 7},
                ]
                
                for data in demo_data:
                    try:
                        PhieuChi.create({
                            'name': data['name'],
                            'so_tien': data['so_tien'],
                            'ngay_chi': today - timedelta(days=data['days_ago']),
                            'nguoi_chi': 'Demo User',
                            'ly_do': 'Dữ liệu demo cho ML training',
                            'trang_thai': 'da_chi',
                        })
                        print(f"   ✓ Tạo: {data['name']}")
                    except:
                        pass
                
                cr.commit()
                print(f"✓ Đã tạo {len(demo_data)} phiếu chi demo\n")
            
            # Train model
            print("🧠 Đang train ML model...")
            print("   (Có thể mất 30-60 giây...)\n")
            
            Model = env['tai.chinh.ke.toan.canh.bao.gian.lan']
            min_samples = 30 if total < 50 else 50
            
            result = Model.train_ml_model(min_samples=min_samples)
            
            if result:
                print("\n" + "="*70)
                print("✅ TRAIN THÀNH CÔNG!")
                print("="*70)
                
                # Load model info
                model_data = Model._load_ml_model()
                if model_data:
                    print(f"\n📊 Thông tin model:")
                    print(f"   • Samples: {model_data['n_samples']}")
                    print(f"   • Features: {', '.join(model_data['feature_names'])}")
                    print(f"   • Trained: {model_data['trained_date']}")
                    print(f"   • Model path: {Model._get_model_path()}")
                
                print("\n🎯 Bước tiếp theo:")
                print("   1. Chạy detection: Model.phat_hien_gian_lan_tu_dong()")
                print("   2. Xem kết quả trong Odoo UI: Tài chính > Cảnh báo gian lận")
                
                return True
            else:
                print("\n❌ Train thất bại! Kiểm tra log.")
                return False
                
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    try:
        train_model()
    except KeyboardInterrupt:
        print("\n\n⚠️  Đã hủy bởi người dùng")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
