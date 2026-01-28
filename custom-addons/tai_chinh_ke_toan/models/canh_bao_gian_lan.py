# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
import statistics
import logging
import os
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

_logger = logging.getLogger(__name__)

class CanhBaoGianLan(models.Model):
    _name = 'tai.chinh.ke.toan.canh.bao.gian.lan'
    _description = 'Cảnh báo gian lận tài chính'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'ngay_phat_hien desc, muc_do_nguy_hiem desc'
    
    name = fields.Char(string='Tiêu đề', required=True)
    ma_canh_bao = fields.Char(string='Mã cảnh báo', readonly=True, default='New')
    
    loai_gian_lan = fields.Selection([
        ('so_tien_bat_thuong', 'Số tiền bất thường'),
        ('tan_suat_cao', 'Tần suất giao dịch cao'),
        ('thoi_gian_nghi_ngo', 'Thời gian nghi ngờ'),
        ('so_tien_tron', 'Số tiền tròn bất thường'),
        ('nguoi_chi_nghi_ngo', 'Người chi nghi ngờ'),
        ('doi_tuong_nghi_ngo', 'Đối tượng nhận tiền nghi ngờ'),
        ('khac', 'Khác')
    ], string='Loại gian lận', required=True)
    
    muc_do_nguy_hiem = fields.Selection([
        ('thap', 'Thấp'),
        ('trung_binh', 'Trung bình'),
        ('cao', 'Cao'),
        ('nghiem_trong', 'Nghiêm trọng')
    ], string='Mức độ nguy hiểm', default='trung_binh', required=True)
    
    mo_ta = fields.Text(string='Mô tả chi tiết', required=True)
    giai_phap = fields.Text(string='Giải pháp khuyến nghị')
    
    phieu_chi_id = fields.Many2one('tai.chinh.ke.toan.phieu.chi', string='Phiếu chi liên quan')
    phieu_thu_id = fields.Many2one('tai.chinh.ke.toan.phieu.thu', string='Phiếu thu liên quan')
    
    ngay_phat_hien = fields.Datetime(string='Ngày phát hiện', default=fields.Datetime.now, required=True)
    nguoi_phat_hien = fields.Many2one('res.users', string='Người phát hiện', default=lambda self: self.env.user)
    
    trang_thai = fields.Selection([
        ('chua_xu_ly', 'Chưa xử lý'),
        ('dang_kiem_tra', 'Đang kiểm tra'),
        ('xac_nhan', 'Xác nhận gian lận'),
        ('khong_gian_lan', 'Không phải gian lận'),
        ('da_xu_ly', 'Đã xử lý')
    ], string='Trạng thái', default='chua_xu_ly', required=True)
    
    nguoi_xu_ly = fields.Many2one('res.users', string='Người xử lý')
    ngay_xu_ly = fields.Datetime(string='Ngày xử lý')
    ghi_chu_xu_ly = fields.Text(string='Ghi chú xử lý')
    
    # Thông tin phân tích
    chi_tiet_phan_tich = fields.Text(string='Chi tiết phân tích')
    diem_nghi_ngo = fields.Float(string='Điểm nghi ngờ', digits=(5, 2), help='Điểm từ 0-100')
    
    # ML Scoring
    ml_anomaly_score = fields.Float(string='ML Anomaly Score', digits=(5, 2), help='Điểm bất thường từ ML model (-1 = outlier, 1 = normal)')
    ml_confidence = fields.Float(string='ML Confidence', digits=(5, 2), help='Độ tin cậy của ML prediction')
    hybrid_score = fields.Float(string='Hybrid Score', digits=(5, 2), help='Điểm tổng hợp (Rule + ML)', compute='_compute_hybrid_score', store=True)
    detection_method = fields.Selection([
        ('rule', 'Rule-based'),
        ('ml', 'Machine Learning'),
        ('hybrid', 'Hybrid (Rule + ML)')
    ], string='Phương pháp phát hiện', default='hybrid')
    
    @api.depends('diem_nghi_ngo', 'ml_anomaly_score', 'ml_confidence')
    def _compute_hybrid_score(self):
        """Tính điểm tổng hợp từ rule-based và ML"""
        for record in self:
            if record.detection_method == 'rule':
                record.hybrid_score = record.diem_nghi_ngo
            elif record.detection_method == 'ml':
                # Chuyển ML score (-1 to 1) sang 0-100
                record.hybrid_score = (1 - record.ml_anomaly_score) * 50 * (record.ml_confidence or 1.0)
            else:  # hybrid
                # Weighted average: 40% rule + 60% ML
                rule_score = record.diem_nghi_ngo or 0
                ml_score = (1 - record.ml_anomaly_score) * 50 * (record.ml_confidence or 0.5) if record.ml_anomaly_score else 0
                record.hybrid_score = (rule_score * 0.4) + (ml_score * 0.6)
    
    @api.model
    def create(self, vals_list):
        # Odoo 19 passes list, handle both list and dict for compatibility
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
        
        for vals in vals_list:
            if vals.get('ma_canh_bao', 'New') == 'New':
                vals['ma_canh_bao'] = self.env['ir.sequence'].next_by_code('tai.chinh.ke.toan.canh.bao.gian.lan') or 'New'
        
        return super(CanhBaoGianLan, self).create(vals_list)
    
    def action_bat_dau_kiem_tra(self):
        """Bắt đầu kiểm tra cảnh báo"""
        self.write({
            'trang_thai': 'dang_kiem_tra',
            'nguoi_xu_ly': self.env.user.id,
            'ngay_xu_ly': fields.Datetime.now()
        })
        
    def action_xac_nhan_gian_lan(self):
        """Xác nhận là gian lận thật"""
        self.write({
            'trang_thai': 'xac_nhan'
        })
        
    def action_khong_phai_gian_lan(self):
        """Xác nhận không phải gian lận"""
        self.write({
            'trang_thai': 'khong_gian_lan'
        })
        
    def action_da_xu_ly(self):
        """Đánh dấu đã xử lý xong"""
        self.write({
            'trang_thai': 'da_xu_ly'
        })
    
    @api.model
    def _get_model_path(self):
        """Lấy đường dẫn lưu ML model"""
        addon_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_dir = os.path.join(addon_path, 'ml_models')
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        return os.path.join(model_dir, 'fraud_detection_model.pkl')
    
    @api.model
    def _extract_features_from_phieu_chi(self, phieu_chi_list):
        """Trích xuất features từ danh sách phiếu chi cho ML"""
        features = []
        for phieu in phieu_chi_list:
            # Feature engineering
            feature_vector = [
                phieu.so_tien,  # Số tiền
                1 if phieu.so_tien % 1000000 == 0 else 0,  # Số tròn triệu
                phieu.ngay_chi.weekday() if phieu.ngay_chi else 0,  # Ngày trong tuần
                phieu.ngay_chi.day if phieu.ngay_chi else 1,  # Ngày trong tháng
                1 if phieu.ngay_chi and phieu.ngay_chi.day >= 28 else 0,  # Cuối tháng
                1 if phieu.ngay_chi and phieu.ngay_chi.weekday() in [5, 6] else 0,  # Cuối tuần
            ]
            features.append(feature_vector)
        return np.array(features)
    
    @api.model
    def _auto_detect_fraud_for_phieu_chi(self, phieu_chi):
        """Tự động phát hiện gian lận cho phiếu chi (rule-based)"""
        if not phieu_chi or phieu_chi.trang_thai not in ('da_duyet', 'da_chi'):
            return
        
        warnings = []
        
        # Rule 1: Số tiền tròn bất thường (999,999,000 hoặc 888,888,888)
        if phieu_chi.so_tien % 1000000 == 0 and phieu_chi.so_tien >= 100000000:
            tron_percentage = str(phieu_chi.so_tien).count('0') / len(str(int(phieu_chi.so_tien))) * 100
            if tron_percentage >= 40:
                warnings.append({
                    'name': f'Số tiền tròn nghi ngờ: {phieu_chi.so_tien:,.0f}đ',
                    'loai_gian_lan': 'so_tien_tron',
                    'muc_do_nguy_hiem': 'trung_binh',
                    'mo_ta': f'Phiếu chi {phieu_chi.name} có số tiền quá tròn ({phieu_chi.so_tien:,.0f}đ)',
                    'diem_nghi_ngo': 35.0,
                    'detection_method': 'rule'
                })
        
        # Rule 2: Số tiền quá lớn (>500 triệu)
        if phieu_chi.so_tien > 500000000:
            warnings.append({
                'name': f'Số tiền lớn bất thường: {phieu_chi.so_tien:,.0f}đ',
                'loai_gian_lan': 'so_tien_bat_thuong',
                'muc_do_nguy_hiem': 'cao',
                'mo_ta': f'Phiếu chi {phieu_chi.name} có số tiền quá lớn ({phieu_chi.so_tien:,.0f}đ)',
                'diem_nghi_ngo': 60.0,
                'detection_method': 'rule'
            })
        
        # Rule 3: Chi vào cuối tuần
        if phieu_chi.ngay_chi and phieu_chi.ngay_chi.weekday() in [5, 6]:
            warnings.append({
                'name': f'Chi tiền vào cuối tuần',
                'loai_gian_lan': 'thoi_gian_nghi_ngo',
                'muc_do_nguy_hiem': 'thap',
                'mo_ta': f'Phiếu chi {phieu_chi.name} được chi vào cuối tuần ({phieu_chi.ngay_chi})',
                'diem_nghi_ngo': 20.0,
                'detection_method': 'rule'
            })
        
        # Tạo cảnh báo
        for warning_data in warnings:
            warning_data['phieu_chi_id'] = phieu_chi.id
            self.create(warning_data)
        
        return len(warnings)
    
    @api.model
    def train_ml_model(self, min_samples=100):
        """Huấn luyện ML model từ dữ liệu lịch sử"""
        _logger.info("Bắt đầu huấn luyện ML model phát hiện gian lận...")
        
        PhieuChi = self.env['tai.chinh.ke.toan.phieu.chi']
        
        # Lấy dữ liệu 6 tháng gần nhất
        ngay_bat_dau = fields.Date.today() - timedelta(days=180)
        phieu_chi = PhieuChi.search([
            ('ngay_chi', '>=', ngay_bat_dau),
            ('trang_thai', '=', 'da_chi')
        ])
        
        if len(phieu_chi) < min_samples:
            _logger.warning(f"Không đủ dữ liệu để train model. Cần ít nhất {min_samples} mẫu, chỉ có {len(phieu_chi)}.")
            return False
        
        # Trích xuất features
        X = self._extract_features_from_phieu_chi(phieu_chi)
        
        # Chuẩn hóa dữ liệu
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Huấn luyện Isolation Forest
        model = IsolationForest(
            contamination=0.1,  # 10% dữ liệu là outlier
            random_state=42,
            n_estimators=100,
            max_samples='auto',
            n_jobs=-1
        )
        model.fit(X_scaled)
        
        # Lưu model và scaler
        model_path = self._get_model_path()
        joblib.dump({
            'model': model,
            'scaler': scaler,
            'trained_date': fields.Datetime.now(),
            'n_samples': len(phieu_chi),
            'feature_names': ['so_tien', 'so_tron', 'weekday', 'day_of_month', 'cuoi_thang', 'cuoi_tuan']
        }, model_path)
        
        _logger.info(f"Huấn luyện thành công! Model đã lưu tại: {model_path}")
        _logger.info(f"Số mẫu: {len(phieu_chi)}")
        
        # Tạo config record để lưu metadata
        self.env['ir.config_parameter'].sudo().set_param('fraud_detection.last_training', fields.Datetime.now())
        self.env['ir.config_parameter'].sudo().set_param('fraud_detection.n_samples', len(phieu_chi))
        
        return True
    
    @api.model
    def _load_ml_model(self):
        """Load ML model đã train"""
        model_path = self._get_model_path()
        if not os.path.exists(model_path):
            _logger.warning("ML model chưa được train. Vui lòng chạy train_ml_model() trước.")
            return None
        
        try:
            model_data = joblib.load(model_path)
            return model_data
        except Exception as e:
            _logger.error(f"Lỗi khi load model: {e}")
            return None
    
    @api.model
    def _phat_hien_bang_ml(self, ngay_bat_dau):
        """Phát hiện gian lận bằng Machine Learning (Isolation Forest)"""
        _logger.info("Bắt đầu phát hiện gian lận bằng ML...")
        
        # Load model
        model_data = self._load_ml_model()
        if not model_data:
            _logger.warning("Không thể load ML model. Bỏ qua ML detection.")
            return
        
        model = model_data['model']
        scaler = model_data['scaler']
        
        PhieuChi = self.env['tai.chinh.ke.toan.phieu.chi']
        
        # Lấy phiếu chi cần kiểm tra
        phieu_chi = PhieuChi.search([
            ('ngay_chi', '>=', ngay_bat_dau),
            ('trang_thai', '=', 'da_chi')
        ])
        
        if not phieu_chi:
            return
        
        # Trích xuất features
        X = self._extract_features_from_phieu_chi(phieu_chi)
        X_scaled = scaler.transform(X)
        
        # Dự đoán
        predictions = model.predict(X_scaled)  # -1 = outlier, 1 = normal
        anomaly_scores = model.score_samples(X_scaled)  # Điểm bất thường (càng âm càng bất thường)
        
        # Tạo cảnh báo cho các outlier
        for i, phieu in enumerate(phieu_chi):
            if predictions[i] == -1:  # Phát hiện anomaly
                # Kiểm tra đã có cảnh báo chưa
                canh_bao_ton_tai = self.search([
                    ('phieu_chi_id', '=', phieu.id),
                    ('detection_method', 'in', ['ml', 'hybrid']),
                    ('trang_thai', 'in', ['chua_xu_ly', 'dang_kiem_tra'])
                ])
                
                if not canh_bao_ton_tai:
                    # Normalize anomaly score to confidence (0-1)
                    confidence = min(1.0, abs(anomaly_scores[i]) / 0.5)
                    ml_score = (1 - predictions[i]) * 50 * confidence  # 0-100
                    
                    muc_do = 'trung_binh'
                    if ml_score > 80:
                        muc_do = 'nghiem_trong'
                    elif ml_score > 60:
                        muc_do = 'cao'
                    elif ml_score > 40:
                        muc_do = 'trung_binh'
                    else:
                        muc_do = 'thap'
                    
                    self.create({
                        'name': f'ML phát hiện bất thường: {phieu.name}',
                        'loai_gian_lan': 'khac',
                        'muc_do_nguy_hiem': muc_do,
                        'mo_ta': f'Machine Learning model (Isolation Forest) phát hiện phiếu chi "{phieu.name}" có hành vi bất thường với độ tin cậy {confidence*100:.1f}%. '
                                 f'Số tiền: {phieu.so_tien:,.0f} VNĐ. Model được train từ {model_data["n_samples"]} mẫu lịch sử.',
                        'giai_phap': 'Đây là cảnh báo từ AI/ML. Xem xét kỹ giao dịch này và so sánh với các giao dịch tương tự trong lịch sử. '
                                     'Kiểm tra xem có yếu tố nào khác thường (thời gian, số tiền, người chi, v.v.)',
                        'phieu_chi_id': phieu.id,
                        'chi_tiet_phan_tich': f'ML Model: Isolation Forest\n'
                                             f'Anomaly Score: {anomaly_scores[i]:.4f}\n'
                                             f'Prediction: {"OUTLIER" if predictions[i] == -1 else "NORMAL"}\n'
                                             f'Confidence: {confidence*100:.1f}%\n'
                                             f'Trained samples: {model_data["n_samples"]}\n'
                                             f'Last training: {model_data["trained_date"]}',
                        'diem_nghi_ngo': 0,  # Rule-based score = 0
                        'ml_anomaly_score': float(predictions[i]),
                        'ml_confidence': confidence,
                        'detection_method': 'ml'
                    })
        
        _logger.info(f"ML detection hoàn tất. Phát hiện {sum(1 for p in predictions if p == -1)} anomalies trong {len(phieu_chi)} giao dịch.")
    
    @api.model
    def phat_hien_gian_lan_tu_dong(self):
        """Phương thức chạy tự động để phát hiện gian lận (Hybrid: Rule-based + ML)"""
        _logger.info("="*50)
        _logger.info("BẮT ĐẦU PHÁT HIỆN GIAN LẬN TỰ ĐỘNG (HYBRID AI)")
        _logger.info("="*50)
        
        # Lấy dữ liệu 30 ngày gần nhất
        ngay_bat_dau = fields.Date.today() - timedelta(days=30)
        
        # === RULE-BASED DETECTION ===
        _logger.info("[1/2] Phát hiện theo luật (Rule-based)...")
        self._phat_hien_so_tien_bat_thuong(ngay_bat_dau)
        self._phat_hien_tan_suat_cao(ngay_bat_dau)
        self._phat_hien_thoi_gian_nghi_ngo(ngay_bat_dau)
        self._phat_hien_so_tien_tron(ngay_bat_dau)
        self._phat_hien_nguoi_chi_nghi_ngo(ngay_bat_dau)
        
        # === MACHINE LEARNING DETECTION ===
        _logger.info("[2/2] Phát hiện bằng AI/ML (Isolation Forest)...")
        self._phat_hien_bang_ml(ngay_bat_dau)
        
        _logger.info("="*50)
        _logger.info("HOÀN TẤT PHÁT HIỆN GIAN LẬN")
        _logger.info("="*50)
        
        return True
    
    def _phat_hien_so_tien_bat_thuong(self, ngay_bat_dau):
        """Phát hiện số tiền bất thường (quá lớn hoặc quá nhỏ so với trung bình)"""
        PhieuChi = self.env['tai.chinh.ke.toan.phieu.chi']
        
        # Lấy tất cả phiếu chi trong khoảng thời gian
        phieu_chi = PhieuChi.search([
            ('ngay_chi', '>=', ngay_bat_dau),
            ('trang_thai', '=', 'da_chi')
        ])
        
        if not phieu_chi:
            return
        
        # Tính số tiền trung bình và độ lệch chuẩn
        so_tien_list = [p.so_tien for p in phieu_chi]
        trung_binh = statistics.mean(so_tien_list)
        
        if len(so_tien_list) > 1:
            do_lech_chuan = statistics.stdev(so_tien_list)
        else:
            return
        
        # Phát hiện các phiếu chi có số tiền bất thường (> 2 độ lệch chuẩn)
        for phieu in phieu_chi:
            if abs(phieu.so_tien - trung_binh) > 2 * do_lech_chuan:
                # Kiểm tra xem đã có cảnh báo chưa
                canh_bao_ton_tai = self.search([
                    ('phieu_chi_id', '=', phieu.id),
                    ('loai_gian_lan', '=', 'so_tien_bat_thuong'),
                    ('trang_thai', 'in', ['chua_xu_ly', 'dang_kiem_tra'])
                ])
                
                if not canh_bao_ton_tai:
                    diem_nghi_ngo = min(100, abs((phieu.so_tien - trung_binh) / do_lech_chuan) * 20)
                    
                    muc_do = 'thap'
                    if diem_nghi_ngo > 70:
                        muc_do = 'nghiem_trong'
                    elif diem_nghi_ngo > 50:
                        muc_do = 'cao'
                    elif diem_nghi_ngo > 30:
                        muc_do = 'trung_binh'
                    
                    self.create({
                        'name': f'Số tiền bất thường: {phieu.name}',
                        'loai_gian_lan': 'so_tien_bat_thuong',
                        'muc_do_nguy_hiem': muc_do,
                        'mo_ta': f'Phiếu chi "{phieu.name}" có số tiền {phieu.so_tien:,.0f} VNĐ cao bất thường so với trung bình {trung_binh:,.0f} VNĐ. Chênh lệch {abs(phieu.so_tien - trung_binh):,.0f} VNĐ ({abs((phieu.so_tien - trung_binh) / trung_binh * 100):.1f}%).',
                        'giai_phap': 'Xác minh lại hóa đơn, chứng từ liên quan. Kiểm tra sự phê duyệt của cấp quản lý. Đối chiếu với ngân sách và kế hoạch chi tiêu.',
                        'phieu_chi_id': phieu.id,
                        'chi_tiet_phan_tich': f'Số tiền trung bình: {trung_binh:,.0f} VNĐ\nĐộ lệch chuẩn: {do_lech_chuan:,.0f} VNĐ\nSố tiền phiếu: {phieu.so_tien:,.0f} VNĐ\nSố độ lệch: {abs((phieu.so_tien - trung_binh) / do_lech_chuan):.2f}',
                        'diem_nghi_ngo': diem_nghi_ngo
                    })
    
    def _phat_hien_tan_suat_cao(self, ngay_bat_dau):
        """Phát hiện người chi có tần suất giao dịch cao bất thường"""
        PhieuChi = self.env['tai.chinh.ke.toan.phieu.chi']
        
        # Đếm số lượng phiếu chi theo người chi (doi_tuong_id)
        query = """
            SELECT doi_tuong_id, COUNT(*) as so_luong
            FROM tai_chinh_ke_toan_phieu_chi
            WHERE ngay_chi >= %s AND trang_thai = 'da_chi'
            GROUP BY doi_tuong_id
            HAVING COUNT(*) > 5
            ORDER BY so_luong DESC
        """
        
        self.env.cr.execute(query, (ngay_bat_dau,))
        results = self.env.cr.fetchall()
        
        for doi_tuong_id, so_luong in results:
            # Lấy thông tin đối tượng
            phieu_chi = PhieuChi.search([('doi_tuong_id', '=', doi_tuong_id)], limit=1)
            
            # Lấy tên đối tượng
            ten_doi_tuong = phieu_chi.doi_tuong_id.name if phieu_chi and phieu_chi.doi_tuong_id else f'ID {doi_tuong_id}'
            
            # Kiểm tra xem đã có cảnh báo chưa
            canh_bao_ton_tai = self.search([
                ('loai_gian_lan', '=', 'tan_suat_cao'),
                ('chi_tiet_phan_tich', 'ilike', ten_doi_tuong),
                ('trang_thai', 'in', ['chua_xu_ly', 'dang_kiem_tra']),
                ('ngay_phat_hien', '>=', fields.Datetime.now() - timedelta(days=7))
            ])
            
            if not canh_bao_ton_tai and so_luong > 5:
                diem_nghi_ngo = min(100, so_luong * 10)
                
                muc_do = 'thap'
                if so_luong > 15:
                    muc_do = 'nghiem_trong'
                elif so_luong > 10:
                    muc_do = 'cao'
                elif so_luong > 7:
                    muc_do = 'trung_binh'
                
                self.create({
                    'name': f'Tần suất giao dịch cao: {ten_doi_tuong}',
                    'loai_gian_lan': 'tan_suat_cao',
                    'muc_do_nguy_hiem': muc_do,
                    'mo_ta': f'Người chi "{ten_doi_tuong}" có {so_luong} giao dịch trong 30 ngày gần nhất, cao bất thường. Cần kiểm tra xem có hiện tượng tách nhỏ hóa đơn để vượt quyền phê duyệt không.',
                    'giai_phap': 'Rà soát lại toàn bộ các giao dịch của người này. Kiểm tra xem có giao dịch nào trùng lặp hoặc không hợp lệ. Xác minh với bộ phận liên quan.',
                    'chi_tiet_phan_tich': f'Người chi: {ten_doi_tuong}\nSố giao dịch: {so_luong}\nThời gian: 30 ngày\nTrung bình: {so_luong/30:.1f} giao dịch/ngày',
                    'diem_nghi_ngo': diem_nghi_ngo
                })
    
    def _phat_hien_thoi_gian_nghi_ngo(self, ngay_bat_dau):
        """Phát hiện giao dịch vào thời gian nghi ngờ (cuối ngày, cuối tuần, cuối tháng)"""
        PhieuChi = self.env['tai.chinh.ke.toan.phieu.chi']
        
        # Tìm các phiếu chi vào thời gian nghi ngờ
        phieu_chi = PhieuChi.search([
            ('ngay_chi', '>=', ngay_bat_dau),
            ('trang_thai', '=', 'da_chi')
        ])
        
        for phieu in phieu_chi:
            ngay = phieu.ngay_chi
            if not ngay:
                continue
            
            # Chuyển sang datetime nếu là date
            if isinstance(ngay, str):
                ngay = fields.Date.from_string(ngay)
            
            nghi_ngo = False
            ly_do = []
            
            # Kiểm tra cuối tháng (3 ngày cuối)
            if ngay.day >= 28:
                nghi_ngo = True
                ly_do.append('giao dịch vào cuối tháng')
            
            # Kiểm tra cuối tuần
            if ngay.weekday() in [5, 6]:  # Thứ 7, CN
                nghi_ngo = True
                ly_do.append('giao dịch vào cuối tuần')
            
            # Kiểm tra số tiền lớn
            if phieu.so_tien > 50000000:  # > 50M
                nghi_ngo = True
                ly_do.append('số tiền lớn')
            
            if nghi_ngo:
                # Kiểm tra xem đã có cảnh báo chưa
                canh_bao_ton_tai = self.search([
                    ('phieu_chi_id', '=', phieu.id),
                    ('loai_gian_lan', '=', 'thoi_gian_nghi_ngo'),
                    ('trang_thai', 'in', ['chua_xu_ly', 'dang_kiem_tra'])
                ])
                
                if not canh_bao_ton_tai:
                    diem_nghi_ngo = 30 + (len(ly_do) * 20)
                    
                    muc_do = 'trung_binh'
                    if len(ly_do) >= 3:
                        muc_do = 'cao'
                    elif len(ly_do) >= 2:
                        muc_do = 'trung_binh'
                    
                    self.create({
                        'name': f'Thời gian nghi ngờ: {phieu.name}',
                        'loai_gian_lan': 'thoi_gian_nghi_ngo',
                        'muc_do_nguy_hiem': muc_do,
                        'mo_ta': f'Phiếu chi "{phieu.name}" có dấu hiệu nghi ngờ: {", ".join(ly_do)}. Đây có thể là dấu hiệu cố ý thực hiện giao dịch vào thời điểm ít kiểm soát.',
                        'giai_phap': 'Kiểm tra tính hợp lệ của giao dịch. Xác minh với người yêu cầu chi. Rà soát quy trình phê duyệt.',
                        'phieu_chi_id': phieu.id,
                        'chi_tiet_phan_tich': f'Ngày giao dịch: {ngay}\nLý do nghi ngờ: {", ".join(ly_do)}\nSố tiền: {phieu.so_tien:,.0f} VNĐ',
                        'diem_nghi_ngo': diem_nghi_ngo
                    })
    
    def _phat_hien_so_tien_tron(self, ngay_bat_dau):
        """Phát hiện số tiền tròn bất thường (5M, 10M, 20M...)"""
        PhieuChi = self.env['tai.chinh.ke.toan.phieu.chi']
        
        phieu_chi = PhieuChi.search([
            ('ngay_chi', '>=', ngay_bat_dau),
            ('trang_thai', '=', 'da_chi')
        ])
        
        for phieu in phieu_chi:
            # Kiểm tra số tiền tròn (chia hết cho 1M và >= 5M)
            if phieu.so_tien >= 5000000 and phieu.so_tien % 1000000 == 0:
                # Kiểm tra xem đã có cảnh báo chưa
                canh_bao_ton_tai = self.search([
                    ('phieu_chi_id', '=', phieu.id),
                    ('loai_gian_lan', '=', 'so_tien_tron'),
                    ('trang_thai', 'in', ['chua_xu_ly', 'dang_kiem_tra'])
                ])
                
                if not canh_bao_ton_tai:
                    diem_nghi_ngo = 20 + (phieu.so_tien / 10000000) * 10
                    
                    self.create({
                        'name': f'Số tiền tròn: {phieu.name}',
                        'loai_gian_lan': 'so_tien_tron',
                        'muc_do_nguy_hiem': 'thap',
                        'mo_ta': f'Phiếu chi "{phieu.name}" có số tiền {phieu.so_tien:,.0f} VNĐ là số tròn triệu. Đây có thể là dấu hiệu ước lượng hoặc không có chứng từ thực tế.',
                        'giai_phap': 'Kiểm tra hóa đơn, chứng từ gốc. Xác minh tính chính xác của số tiền.',
                        'phieu_chi_id': phieu.id,
                        'chi_tiet_phan_tich': f'Số tiền: {phieu.so_tien:,.0f} VNĐ\nSố tiền tròn: {int(phieu.so_tien/1000000)} triệu',
                        'diem_nghi_ngo': min(100, diem_nghi_ngo)
                    })
    
    def _phat_hien_nguoi_chi_nghi_ngo(self, ngay_bat_dau):
        """Phát hiện người chi có tổng số tiền chi cao bất thường"""
        PhieuChi = self.env['tai.chinh.ke.toan.phieu.chi']
        
        query = """
            SELECT doi_tuong_id, SUM(so_tien) as tong_tien, COUNT(*) as so_luong
            FROM tai_chinh_ke_toan_phieu_chi
            WHERE ngay_chi >= %s AND trang_thai = 'da_chi'
            GROUP BY doi_tuong_id
            ORDER BY tong_tien DESC
        """
        
        self.env.cr.execute(query, (ngay_bat_dau,))
        results = self.env.cr.fetchall()
        
        if not results:
            return
        
        # Tính tổng tiền trung bình
        tong_tien_list = [r[1] for r in results]
        trung_binh = statistics.mean(tong_tien_list) if tong_tien_list else 0
        
        for doi_tuong_id, tong_tien, so_luong in results:
            # Lấy thông tin đối tượng
            phieu_chi = PhieuChi.search([('doi_tuong_id', '=', doi_tuong_id)], limit=1)
            ten_doi_tuong = phieu_chi.doi_tuong_id.name if phieu_chi and phieu_chi.doi_tuong_id else f'ID {doi_tuong_id}'
            
            # Nếu tổng tiền > 150% trung bình
            if tong_tien > trung_binh * 1.5 and tong_tien > 20000000:
                # Kiểm tra xem đã có cảnh báo chưa
                canh_bao_ton_tai = self.search([
                    ('loai_gian_lan', '=', 'nguoi_chi_nghi_ngo'),
                    ('chi_tiet_phan_tich', 'ilike', ten_doi_tuong),
                    ('trang_thai', 'in', ['chua_xu_ly', 'dang_kiem_tra']),
                    ('ngay_phat_hien', '>=', fields.Datetime.now() - timedelta(days=7))
                ])
                
                if not canh_bao_ton_tai:
                    ty_le = (tong_tien / trung_binh - 1) * 100
                    diem_nghi_ngo = min(100, 30 + ty_le)
                    
                    muc_do = 'trung_binh'
                    if ty_le > 200:
                        muc_do = 'nghiem_trong'
                    elif ty_le > 100:
                        muc_do = 'cao'
                    
                    self.create({
                        'name': f'Người chi nghi ngờ: {ten_doi_tuong}',
                        'loai_gian_lan': 'nguoi_chi_nghi_ngo',
                        'muc_do_nguy_hiem': muc_do,
                        'mo_ta': f'Người chi "{ten_doi_tuong}" có tổng số tiền chi {tong_tien:,.0f} VNĐ cao hơn {ty_le:.1f}% so với trung bình ({so_luong} giao dịch). Cần xem xét kỹ toàn bộ các giao dịch.',
                        'giai_phap': 'Rà soát tất cả giao dịch của người này. Đối chiếu với quyền hạn và ngân sách được giao. Kiểm tra quy trình phê duyệt.',
                        'chi_tiet_phan_tich': f'Người chi: {ten_doi_tuong}\nTổng tiền: {tong_tien:,.0f} VNĐ\nSố giao dịch: {so_luong}\nTrung bình: {trung_binh:,.0f} VNĐ\nChênh lệch: +{ty_le:.1f}%',
                        'diem_nghi_ngo': diem_nghi_ngo
                    })
