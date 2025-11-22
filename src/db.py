# db.py

import mysql.connector
# 1. Adımda oluşturduğunuz config.py dosyasından bilgileri çekin
from config import DB_HOST, DB_NAME, DB_USER, DB_PASS

def get_db_connection():
    """MySQL veri tabanı bağlantısını kurar ve döndürür."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except mysql.connector.Error as e:
        # Bağlantı hatası durumunda detaylı bilgi ver
        print(f" MySQL Bağlantı Hatası: {e}")
        return None

def test_connection():
    """Basit bir sorgu çalıştırarak bağlantıyı test eder."""
    conn = get_db_connection()
    if conn is None:
        return False

    try:
        cur = conn.cursor()
        # Basit bir sorgu ile bağlantının aktif olduğunu kanıtlar
        cur.execute("SELECT 1;")
        result = cur.fetchone()
        cur.close()
        conn.close()
        print(f" BAĞLANTI BAŞARILI! Test Sorgusu Sonucu: {result}")
        return True
    except mysql.connector.Error as e:
        print(f" Sorgu Çalıştırma Hatası: {e}")
        conn.close()
        return False

if __name__ == '__main__':
    # Dosya doğrudan çalıştırıldığında bağlantıyı test et
    test_connection()
def get_all_records(table_name):
    """Belirtilen tablodan ham SQL kullanarak tüm kayıtları çeker."""
    conn = get_db_connection()
    if conn is None:
        return []

    try:
        # dictionary=True, sonuçları sözlük (column_name: value) olarak döndürmeyi sağlar.
        cur = conn.cursor(dictionary=True) 
        
        # Ham SQL sorgusu (ÖRNEK: 'filmler' yerine kendi tablonuzun adını kullanın)
        sql_query = f"SELECT * FROM {table_name};"
        
        cur.execute(sql_query)
        records = cur.fetchall() # Tüm sonuçları al
        
        cur.close()
        conn.close()
        return records

    except mysql.connector.Error as e:
        print(f" Veri Çekme Hatası: {e}")
        if conn:
            conn.close()
        return []
    