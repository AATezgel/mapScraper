#!/bin/bash

echo "🚀 Django Map Scraper - Deployment Hazırlığı"
echo "=============================================="
echo ""

# Renk kodları
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Git kontrolü
echo -e "${BLUE}📌 Step 1: Git repository kontrolü${NC}"
if [ ! -d .git ]; then
    echo -e "${YELLOW}Git repository bulunamadı. İlk commit için hazırlanıyor...${NC}"
    git init
    git add .
    git commit -m "Initial commit: Django Map Scraper with SERP API integration"
    echo -e "${GREEN}✅ Git repository oluşturuldu${NC}"
else
    echo -e "${GREEN}✅ Git repository mevcut${NC}"
fi
echo ""

# 2. Değişiklikleri commit et
echo -e "${BLUE}📌 Step 2: Değişiklikleri commit etme${NC}"
git add .
if git diff-index --quiet HEAD --; then
    echo -e "${GREEN}✅ Commit edilecek değişiklik yok${NC}"
else
    git commit -m "Production deployment hazırlıkları: render.yaml, build.sh, güvenlik ayarları"
    echo -e "${GREEN}✅ Değişiklikler commit edildi${NC}"
fi
echo ""

# 3. Gerekli dosyaları kontrol et
echo -e "${BLUE}📌 Step 3: Deployment dosyalarını kontrol etme${NC}"
files=("build.sh" "render.yaml" "Procfile" "requirements.txt" ".gitignore")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file mevcut${NC}"
    else
        echo -e "${YELLOW}⚠️  $file bulunamadı${NC}"
    fi
done
echo ""

# 4. Requirements kontrolü
echo -e "${BLUE}📌 Step 4: Requirements.txt kontrolü${NC}"
required_packages=("gunicorn" "whitenoise" "psycopg2-binary" "dj-database-url")
for package in "${required_packages[@]}"; do
    if grep -q "$package" requirements.txt; then
        echo -e "${GREEN}✅ $package requirements.txt'de mevcut${NC}"
    else
        echo -e "${YELLOW}⚠️  $package requirements.txt'de bulunamadı${NC}"
    fi
done
echo ""

# 5. Özet bilgiler
echo -e "${BLUE}📌 Deployment Bilgileri${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}Artık deploy etmeye hazırsınız!${NC}"
echo ""
echo "Sonraki adımlar:"
echo ""
echo "1️⃣  GitHub'a Push:"
echo "   git push origin main"
echo ""
echo "2️⃣  Render.com'a Git:"
echo "   https://render.com"
echo "   • GitHub ile giriş yap"
echo "   • New + → Web Service"
echo "   • Repository'nizi seçin"
echo "   • Root Directory: scraperApp/mapScraper"
echo ""
echo "3️⃣  Environment Variables Ekle:"
echo "   • SECRET_KEY (otomatik generate edilecek)"
echo "   • DEBUG = False"
echo "   • ALLOWED_HOSTS = .onrender.com"
echo "   • SERP_API_KEY = 19b8cfa3a27fb5b568411275ca980abbba9cdc077b6a1ee93bf5c18ca556b397"
echo ""
echo "4️⃣  PostgreSQL Database Ekle:"
echo "   • Dashboard → New + → PostgreSQL"
echo "   • Database'i Web Service'e bağla"
echo ""
echo "5️⃣  Deploy!"
echo "   • Create Web Service butonuna tıkla"
echo "   • 5-10 dakika bekle"
echo ""
echo -e "${GREEN}Deploy linkiniz: https://your-app-name.onrender.com 🎉${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}💡 İpucu: Detaylı rehber için DEPLOYMENT_GUIDE.md dosyasını okuyun${NC}"
echo ""
