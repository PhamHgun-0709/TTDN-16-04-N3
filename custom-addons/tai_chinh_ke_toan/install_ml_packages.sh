#!/bin/bash

# ============================================================================
# Script cài đặt ML packages cho AI Fraud Detection
# ============================================================================

echo ""
echo "========================================================================"
echo " AI FRAUD DETECTION - Installation Script"
echo "========================================================================"
echo ""

echo "[1/4] Upgrading pip..."
python3 -m pip install --upgrade pip

echo ""
echo "[2/4] Installing scikit-learn..."
pip3 install scikit-learn==1.3.2

echo ""
echo "[3/4] Installing joblib..."
pip3 install joblib==1.3.2

echo ""
echo "[4/4] Installing numpy..."
pip3 install numpy==1.24.3

echo ""
echo "========================================================================"
echo " Installation Complete!"
echo "========================================================================"
echo ""
echo "Next steps:"
echo "  1. Restart Odoo"
echo "  2. Update module: -u tai_chinh_ke_toan"
echo "  3. Train ML model (see AI_FRAUD_DETECTION_README.md)"
echo ""
