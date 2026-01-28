# ============================================================================
# Auto train ML model inside Docker container
# ============================================================================

Write-Host ""
Write-Host "========================================================================"
Write-Host " AI FRAUD DETECTION - Auto Training (Docker)"
Write-Host "========================================================================"
Write-Host ""

# Container name from docker-compose.yml
$containerName = "odoo_app_fitdnu"
$dbName = "myodoo"

Write-Host "📝 Configuration:" -ForegroundColor Cyan
Write-Host "   • Container: $containerName"
Write-Host "   • Database: $dbName"
Write-Host ""

# Check if container is running
Write-Host "🔍 Checking container status..." -ForegroundColor Yellow
$running = docker ps --filter "name=$containerName" --format "{{.Names}}"

if ([string]::IsNullOrEmpty($running)) {
    Write-Host "❌ Container '$containerName' not running!" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Start container first:" -ForegroundColor Yellow
    Write-Host "   docker-compose up -d"
    exit 1
}

Write-Host "✓ Container is running" -ForegroundColor Green

Write-Host ""
Write-Host "📦 Copying auto_train.py to container..." -ForegroundColor Yellow
docker cp auto_train.py "${containerName}:/opt/odoo/auto_train.py"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to copy file!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ File copied" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 Running training script inside container..." -ForegroundColor Cyan
Write-Host "========================================================================"
Write-Host ""

docker exec -it $containerName python3 /opt/odoo/auto_train.py

Write-Host ""
Write-Host "========================================================================"
Write-Host ""

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Training completed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 View results:" -ForegroundColor Cyan
    Write-Host "   • Odoo UI: Tài chính > Cảnh báo gian lận"
    Write-Host "   • Model path: custom-addons/tai_chinh_ke_toan/ml_models/"
} else {
    Write-Host "❌ Training failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Try manual method:" -ForegroundColor Yellow
    Write-Host "   1. docker exec -it $containerName bash"
    Write-Host "   2. /opt/odoo/odoo-bin shell -c /etc/odoo/odoo.conf"
    Write-Host "   3. Follow TRAIN_INSTRUCTIONS.md"
}

Write-Host ""
