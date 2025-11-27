# TESSERACT GTFS Project Setup Script
# Bu script projeyi kurmak için gerekli tüm adımları otomatik olarak yapar

set -e  # Hata durumunda dur

echo "TESSERACT GTFS Project Setup"


# Renkler
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Python ve pip kontrolü
echo -e "${YELLOW}📦 Python kontrolü...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED} Python3 bulunamadı! Lütfen Python3 yükleyin.${NC}"
    exit 1
fi
echo -e "${GREEN}Python3: $(python3 --version)${NC}"

# 2. MySQL kontrolü
echo -e "${YELLOW}🗄️  MySQL kontrolü...${NC}"
if ! command -v mysql &> /dev/null; then
    echo -e "${RED} MySQL bulunamadı! Lütfen MySQL yükleyin.${NC}"
    exit 1
fi
echo -e "${GREEN}MySQL bulundu${NC}"

# 3. MySQL servisinin çalışıp çalışmadığını kontrol et
echo -e "${YELLOW}🔍 MySQL servisi kontrolü...${NC}"
if ! pgrep -x mysqld > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  MySQL servisi çalışmıyor. Başlatılıyor...${NC}"
    # macOS için
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew services start mysql@8.0 2>/dev/null || brew services start mysql 2>/dev/null || {
                echo -e "${YELLOW}⚠️  Brew ile başlatılamadı. Manuel başlatmayı deneyin:${NC}"
                echo -e "${BLUE}   sudo /opt/homebrew/bin/mysql.server start${NC}"
                echo -e "${YELLOW}   veya${NC}"
                echo -e "${BLUE}   sudo /usr/local/bin/mysql.server start${NC}"
            }
        else
            echo -e "${YELLOW}⚠️  MySQL servisini manuel olarak başlatmanız gerekiyor.${NC}"
        fi
        sleep 3
    else
        # Linux için
        sudo systemctl start mysql 2>/dev/null || {
            echo -e "${RED}❌ MySQL servisini manuel olarak başlatmanız gerekiyor.${NC}"
            echo -e "${BLUE}   sudo systemctl start mysql${NC}"
        }
        sleep 2
    fi
fi

# MySQL bağlantısını test et
if ! mysql -u root -e "SELECT 1" &> /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  MySQL root şifresi gerekli${NC}"
fi
echo -e "${GREEN}✅ MySQL servisi çalışıyor${NC}"

# 4. Python bağımlılıklarını yükle
echo -e "${YELLOW}📥 Python bağımlılıkları yükleniyor...${NC}"
if [ -f "requirements.txt" ]; then
    pip3 install -q -r requirements.txt || pip3 install -r requirements.txt
    echo -e "${GREEN}✅ Bağımlılıklar yüklendi${NC}"
else
    echo -e "${RED}❌ requirements.txt bulunamadı!${NC}"
    exit 1
fi

# 5. MySQL root şifresi sor
echo -e "${YELLOW}🔐 MySQL root şifresi gerekli (veritabanı ve kullanıcı oluşturmak için)${NC}"
read -sp "MySQL root şifresi (boş bırakabilirsiniz): " MYSQL_ROOT_PASSWORD
echo ""

# Şifre boşsa boş string olarak ayarla
if [ -z "$MYSQL_ROOT_PASSWORD" ]; then
    MYSQL_ROOT_PASSWORD=""
    MYSQL_CMD="mysql -u root"
else
    MYSQL_CMD="mysql -u root -p${MYSQL_ROOT_PASSWORD}"
fi

# 6. Config dosyasından bilgileri oku
echo -e "${YELLOW}📋 Konfigürasyon dosyası okunuyor...${NC}"
if [ ! -f "src/config.py" ]; then
    echo -e "${RED}❌ src/config.py bulunamadı!${NC}"
    exit 1
fi

DB_NAME=$(grep "DB_NAME" src/config.py | cut -d'"' -f2)
DB_USER=$(grep "DB_USER" src/config.py | cut -d'"' -f2)
DB_PASS=$(grep "DB_PASS" src/config.py | cut -d'"' -f2)

if [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASS" ]; then
    echo -e "${RED}❌ Config dosyasında DB_NAME, DB_USER veya DB_PASS bulunamadı!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Konfigürasyon okundu:${NC}"
echo -e "${BLUE}   Database: ${DB_NAME}${NC}"
echo -e "${BLUE}   User: ${DB_USER}${NC}"

# 7. Veritabanı ve kullanıcı oluştur
echo -e "${YELLOW}🗄️  Veritabanı ve kullanıcı oluşturuluyor...${NC}"

# SQL script oluştur
cat > /tmp/setup_db.sql << EOF
CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF

# SQL script'i çalıştır
if [ -z "$MYSQL_ROOT_PASSWORD" ]; then
    mysql -u root < /tmp/setup_db.sql 2>/dev/null || {
        echo -e "${RED}❌ Veritabanı oluşturulamadı. Root şifresi gerekli olabilir.${NC}"
        rm /tmp/setup_db.sql
        exit 1
    }
else
    mysql -u root -p"${MYSQL_ROOT_PASSWORD}" < /tmp/setup_db.sql 2>/dev/null || {
        echo -e "${RED}❌ Veritabanı oluşturulamadı. Şifre yanlış olabilir.${NC}"
        rm /tmp/setup_db.sql
        exit 1
    }
fi
rm /tmp/setup_db.sql
echo -e "${GREEN}✅ Veritabanı ve kullanıcı oluşturuldu${NC}"

# 8. Mevcut tabloları sil (varsa)
echo -e "${YELLOW}🗑️  Mevcut tablolar kontrol ediliyor ve temizleniyor...${NC}"
cat > /tmp/drop_tables.sql << EOF
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS frequencies;
DROP TABLE IF EXISTS stop_times;
DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS shapes;
DROP TABLE IF EXISTS calendar;
DROP TABLE IF EXISTS routes;
DROP TABLE IF EXISTS stops;
DROP TABLE IF EXISTS agency;
SET FOREIGN_KEY_CHECKS = 1;
EOF

$MYSQL_CMD ${DB_NAME} < /tmp/drop_tables.sql 2>/dev/null || true
rm /tmp/drop_tables.sql 2>/dev/null || true
echo -e "${GREEN}✅ Eski tablolar temizlendi${NC}"

# 9. Schema'yı yükle
echo -e "${YELLOW}📋 Veritabanı şeması yükleniyor...${NC}"
if [ -f "DOCS/schema.sql" ]; then
    # Yorum satırlarını temizle (-- ile başlayan veya boşluk sonrası -- olan satırları kaldır)
    sed 's/--.*$//' DOCS/schema.sql | sed '/^[[:space:]]*$/d' > /tmp/schema_clean.sql
    
    $MYSQL_CMD ${DB_NAME} < /tmp/schema_clean.sql || {
        echo -e "${RED}❌ Şema yüklenemedi!${NC}"
        rm /tmp/schema_clean.sql 2>/dev/null || true
        exit 1
    }
    rm /tmp/schema_clean.sql 2>/dev/null || true
    echo -e "${GREEN}✅ Şema yüklendi${NC}"
else
    echo -e "${YELLOW}⚠️  DOCS/schema.sql bulunamadı, atlanıyor...${NC}"
fi

# 10. GTFS verilerini import et
echo -e "${YELLOW}📥 GTFS verileri import ediliyor...${NC}"
if [ -d "gtfs_data" ] && [ "$(ls -A gtfs_data/*.csv 2>/dev/null)" ]; then
    python3 download_and_import_gtfs.py
    echo -e "${GREEN}✅ Veriler import edildi${NC}"
else
    echo -e "${YELLOW}⚠️  gtfs_data klasörü veya CSV dosyaları bulunamadı.${NC}"
    echo -e "${YELLOW}   Verileri manuel olarak import edebilirsiniz:${NC}"
    echo -e "${BLUE}   python3 download_and_import_gtfs.py${NC}"
fi

# 10. Özet
echo ""
echo "=========================================="
echo -e "${GREEN}✅ Kurulum tamamlandı!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}🚀 Uygulamayı başlatmak için:${NC}"
echo "   cd src"
echo "   python3 app.py"
echo ""
echo -e "${BLUE}🌐 Tarayıcıda açın: http://localhost:5000${NC}"
echo ""
echo -e "${BLUE}📊 Veritabanı bilgileri:${NC}"
echo "   Database: ${DB_NAME}"
echo "   User: ${DB_USER}"
echo "   Password: ${DB_PASS}"
echo ""

