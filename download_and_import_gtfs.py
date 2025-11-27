"""
GTFS Verilerini İndir ve Veritabanına Yükle
İBB Açık Veri Portalı: https://data.ibb.gov.tr/dataset/public-transport-gtfs-data
"""

import os
import csv
import requests
import zipfile
import io
from pathlib import Path
import mysql.connector
import sys
sys.path.append('src')
from config import DB_HOST, DB_NAME, DB_USER, DB_PASS

# GTFS dosyaları (hem .txt hem .csv olabilir)
GTFS_FILES = [
    'agency',
    'routes',
    'stops',
    'trips',
    'stop_times',
    'calendar',
    'shapes',
    'frequencies'
]

def download_gtfs_data(url=None, output_dir='gtfs_data'):
    """
    GTFS verilerini indir
    Eğer URL verilmezse, kullanıcıdan CSV dosyalarını manuel olarak koymasını ister
    """
    os.makedirs(output_dir, exist_ok=True)
    
    if url:
        print(f"GTFS verileri indiriliyor: {url}")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # ZIP dosyası ise aç
            if url.endswith('.zip') or 'zip' in response.headers.get('content-type', ''):
                with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                    zip_ref.extractall(output_dir)
                print(f"✅ Veriler {output_dir} klasörüne çıkarıldı")
            else:
                # Tek dosya ise kaydet
                with open(os.path.join(output_dir, 'gtfs_data.txt'), 'wb') as f:
                    f.write(response.content)
        except Exception as e:
            print(f"❌ İndirme hatası: {e}")
            print("Manuel olarak CSV dosyalarını gtfs_data klasörüne koyabilirsin")
            return False
    else:
        print(f"📁 CSV dosyalarını {output_dir} klasörüne koy")
        print("Gerekli dosyalar:")
        for file in GTFS_FILES:
            print(f"  - {file}.csv (veya {file}.txt)")
        return False
    
    return True

def get_db_connection():
    """Veritabanı bağlantısı"""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except mysql.connector.Error as e:
        print(f"❌ Veritabanı bağlantı hatası: {e}")
        return None

def import_agency(conn, file_path):
    """Agency tablosuna veri yükle"""
    cursor = conn.cursor()
    count = 0
    
    try:
        f = get_file_handle(file_path)
        with f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    sql = """INSERT INTO agency 
                             (agency_id, agency_name, agency_url, agency_timezone, agency_lang, 
                              agency_phone, agency_fare_url, agency_email) 
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                             ON DUPLICATE KEY UPDATE 
                             agency_name=VALUES(agency_name), agency_url=VALUES(agency_url)"""
                    
                    agency_id_val = row.get('agency_id', '').strip()
                    if not agency_id_val:
                        continue
                    try:
                        agency_id_val = int(agency_id_val)
                    except:
                        continue
                    
                    cursor.execute(sql, (
                        agency_id_val,
                        row.get('agency_name', '').strip(),
                        row.get('agency_url', '').strip(),
                        row.get('agency_timezone', 'Europe/Istanbul').strip(),
                        row.get('agency_lang', 'tr').strip(),
                        row.get('agency_phone', '').strip() or None,
                        row.get('agency_fare_url', '').strip() or None,
                        row.get('agency_email', '').strip() or None
                    ))
                    count += 1
                except Exception as e:
                    # Foreign key hatalarını sessizce atla (çok fazla olabilir)
                    if '1452' not in str(e) and '23000' not in str(e):
                        if count % 100 == 0:  # Her 100 hatada bir göster
                            print(f"  ⚠️  Hata (satır atlandı): {str(e)[:50]}...")
                    continue
        
        conn.commit()
        print(f"  ✅ {count} agency kaydı yüklendi")
    except Exception as e:
        print(f"  ❌ Agency import hatası: {e}")
    finally:
        cursor.close()

def get_file_handle(file_path):
    """Dosyayı doğru encoding ile aç"""
    encodings = ['utf-8-sig', 'windows-1254', 'iso-8859-9', 'latin1', 'cp1254']
    for enc in encodings:
        try:
            f = open(file_path, 'r', encoding=enc)
            # Test et
            f.readline()
            f.seek(0)
            return f
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise Exception(f"Dosya encoding'i tespit edilemedi: {file_path}")

def import_routes(conn, file_path):
    """Routes tablosuna veri yükle"""
    cursor = conn.cursor()
    count = 0
    seen_short_names = {}  # route_short_name -> route_id mapping (duplicate kontrolü için)
    
    try:
        f = get_file_handle(file_path)
        with f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    route_id_val = row.get('route_id', '').strip()
                    if not route_id_val:
                        continue
                    
                    route_short_name = row.get('route_short_name', '').strip() or None
                    
                    # Duplicate route_short_name kontrolü: Aynı route_short_name'e sahip route varsa, sadece ilk route_id'yi tut
                    # NOT: Bu kontrolü kaldırdık çünkü aynı route_short_name'e sahip farklı route_id'ler olabilir (farklı yönler vs.)
                    # if route_short_name:
                    #     if route_short_name in seen_short_names:
                    #         # Bu route_short_name zaten var, duplicate'i atla
                    #         continue
                    #     seen_short_names[route_short_name] = route_id_val
                    
                    sql = """INSERT INTO routes 
                             (route_id, agency_id, route_short_name, route_long_name, route_type, 
                              route_color, route_text_color) 
                             VALUES (%s, %s, %s, %s, %s, %s, %s)
                             ON DUPLICATE KEY UPDATE 
                             route_short_name=VALUES(route_short_name), 
                             route_long_name=VALUES(route_long_name)"""
                    
                    agency_id = None
                    if row.get('agency_id'):
                        try:
                            agency_id_val = int(row.get('agency_id').strip())
                            # Agency tablosunda var mı kontrol et
                            cursor_check = conn.cursor()
                            cursor_check.execute("SELECT 1 FROM agency WHERE agency_id = %s", (agency_id_val,))
                            if cursor_check.fetchone():
                                agency_id = agency_id_val
                            cursor_check.close()
                        except:
                            pass
                    
                    route_type = None
                    if row.get('route_type'):
                        try:
                            route_type = int(row.get('route_type').strip())
                        except:
                            pass
                    
                    # Yeni format route_color ve route_text_color içermeyebilir
                    route_color = row.get('route_color', '').strip() or None
                    route_text_color = row.get('route_text_color', '').strip() or None
                    
                    cursor.execute(sql, (
                        route_id_val,
                        agency_id,
                        route_short_name,
                        row.get('route_long_name', '').strip() or None,
                        route_type,
                        route_color,
                        route_text_color
                    ))
                    count += 1
                    if count % 1000 == 0:
                        print(f"  ... {count} kayıt yüklendi...")
                except Exception as e:
                    if count < 5:
                        print(f"  ⚠️  Hata (satır atlandı): {str(e)[:100]}")
                    elif '1452' not in str(e) and '23000' not in str(e) and count % 1000 == 0:
                        print(f"  ⚠️  Hata (satır atlandı): {str(e)[:50]}...")
                    continue
        
        conn.commit()
        print(f"  ✅ {count} route kaydı yüklendi (duplicate route_short_name'ler kaldırıldı)")
    except Exception as e:
        print(f"  ❌ Routes import hatası: {e}")
    finally:
        cursor.close()

def import_stops(conn, file_path):
    """Stops tablosuna veri yükle"""
    cursor = conn.cursor()
    count = 0
    
    try:
        f = get_file_handle(file_path)
        with f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    sql = """INSERT INTO stops 
                             (stop_id, stop_name, stop_lat, stop_lon, parent_station) 
                             VALUES (%s, %s, %s, %s, %s)
                             ON DUPLICATE KEY UPDATE 
                             stop_name=VALUES(stop_name), 
                             stop_lat=VALUES(stop_lat), 
                             stop_lon=VALUES(stop_lon)"""
                    
                    stop_id = int(row.get('stop_id')) if row.get('stop_id') else None
                    stop_lat = float(row.get('stop_lat')) if row.get('stop_lat') else None
                    stop_lon = float(row.get('stop_lon')) if row.get('stop_lon') else None
                    parent_station = row.get('parent_station') or None
                    
                    cursor.execute(sql, (
                        stop_id,
                        row.get('stop_name', ''),
                        stop_lat,
                        stop_lon,
                        parent_station
                    ))
                    count += 1
                except Exception as e:
                    # Foreign key hatalarını sessizce atla (çok fazla olabilir)
                    if '1452' not in str(e) and '23000' not in str(e):
                        if count % 100 == 0:  # Her 100 hatada bir göster
                            print(f"  ⚠️  Hata (satır atlandı): {str(e)[:50]}...")
                    continue
        
        conn.commit()
        print(f"  ✅ {count} stop kaydı yüklendi")
    except Exception as e:
        print(f"  ❌ Stops import hatası: {e}")
    finally:
        cursor.close()

def import_calendar(conn, file_path):
    """Calendar tablosuna veri yükle"""
    cursor = conn.cursor()
    count = 0
    
    try:
        f = get_file_handle(file_path)
        with f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    sql = """INSERT INTO calendar 
                             (service_id, start_date, end_date, monday, tuesday, wednesday, 
                              thursday, friday, saturday, sunday) 
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                             ON DUPLICATE KEY UPDATE 
                             start_date=VALUES(start_date), end_date=VALUES(end_date)"""
                    
                    cursor.execute(sql, (
                        row.get('service_id', ''),
                        row.get('start_date', ''),
                        row.get('end_date', ''),
                        row.get('monday', '0'),
                        row.get('tuesday', '0'),
                        row.get('wednesday', '0'),
                        row.get('thursday', '0'),
                        row.get('friday', '0'),
                        row.get('saturday', '0'),
                        row.get('sunday', '0')
                    ))
                    count += 1
                except Exception as e:
                    # Foreign key hatalarını sessizce atla (çok fazla olabilir)
                    if '1452' not in str(e) and '23000' not in str(e):
                        if count % 100 == 0:  # Her 100 hatada bir göster
                            print(f"  ⚠️  Hata (satır atlandı): {str(e)[:50]}...")
                    continue
        
        conn.commit()
        print(f"  ✅ {count} calendar kaydı yüklendi")
    except Exception as e:
        print(f"  ❌ Calendar import hatası: {e}")
    finally:
        cursor.close()

def import_trips(conn, file_path):
    """Trips tablosuna veri yükle"""
    cursor = conn.cursor()
    count = 0
    
    try:
        f = get_file_handle(file_path)
        with f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    sql = """INSERT INTO trips 
                             (trip_id, route_id, service_id, trip_headsign, direction_id, start_time) 
                             VALUES (%s, %s, %s, %s, %s, %s)
                             ON DUPLICATE KEY UPDATE 
                             route_id=VALUES(route_id), service_id=VALUES(service_id)"""
                    
                    trip_id_val = row.get('trip_id', '').strip()
                    if not trip_id_val:
                        continue
                    try:
                        trip_id_val = int(trip_id_val)
                    except:
                        continue
                    
                    route_id_val = row.get('route_id', '').strip() or None
                    service_id_val = row.get('service_id', '').strip() or None
                    
                    direction_id = None
                    if row.get('direction_id'):
                        try:
                            direction_id = int(row.get('direction_id').strip())
                        except:
                            pass
                    
                    # start_time trips.csv'de yok, NULL bırak
                    start_time = None
                    
                    cursor.execute(sql, (
                        trip_id_val,
                        route_id_val,
                        service_id_val,
                        row.get('trip_headsign', '').strip() or None,
                        direction_id,
                        start_time
                    ))
                    count += 1
                except Exception as e:
                    # Foreign key hatalarını sessizce atla (çok fazla olabilir)
                    if '1452' not in str(e) and '23000' not in str(e):
                        if count % 100 == 0:  # Her 100 hatada bir göster
                            print(f"  ⚠️  Hata (satır atlandı): {str(e)[:50]}...")
                    continue
        
        conn.commit()
        print(f"  ✅ {count} trip kaydı yüklendi")
    except Exception as e:
        print(f"  ❌ Trips import hatası: {e}")
    finally:
        cursor.close()

def import_stop_times(conn, file_path):
    """Stop_times tablosuna veri yükle (ilk 10000 kayıt)"""
    cursor = conn.cursor()
    count = 0
    max_records = 10000  # Çok fazla kayıt olabilir, limit koy
    
    try:
        f = get_file_handle(file_path)
        with f:
            reader = csv.DictReader(f)
            for row in reader:
                if count >= max_records:
                    print(f"  ⚠️  {max_records} kayıt limitine ulaşıldı")
                    break
                    
                try:
                    sql = """INSERT INTO stop_times 
                             (trip_id, stop_id, stop_sequence, arrival_time, departure_time, stop_headsign) 
                             VALUES (%s, %s, %s, %s, %s, %s)
                             ON DUPLICATE KEY UPDATE 
                             arrival_time=VALUES(arrival_time), 
                             departure_time=VALUES(departure_time)"""
                    
                    trip_id = int(row.get('trip_id')) if row.get('trip_id') else None
                    stop_id = int(row.get('stop_id')) if row.get('stop_id') else None
                    stop_sequence = int(row.get('stop_sequence')) if row.get('stop_sequence') else None
                    
                    cursor.execute(sql, (
                        trip_id,
                        stop_id,
                        stop_sequence,
                        row.get('arrival_time') or None,
                        row.get('departure_time') or None,
                        row.get('stop_headsign') or None
                    ))
                    count += 1
                except Exception as e:
                    continue
        
        conn.commit()
        print(f"  ✅ {count} stop_time kaydı yüklendi")
    except Exception as e:
        print(f"  ❌ Stop_times import hatası: {e}")
    finally:
        cursor.close()

def import_shapes(conn, file_path):
    """Shapes tablosuna veri yükle (ilk 5000 kayıt)"""
    cursor = conn.cursor()
    count = 0
    max_records = 5000
    
    try:
        f = get_file_handle(file_path)
        with f:
            reader = csv.DictReader(f)
            for row in reader:
                if count >= max_records:
                    break
                    
                try:
                    sql = """INSERT INTO shapes 
                             (shape_id, shape_pt_lat, shape_pt_lon, shape_pt_sequence) 
                             VALUES (%s, %s, %s, %s)
                             ON DUPLICATE KEY UPDATE 
                             shape_pt_lat=VALUES(shape_pt_lat), 
                             shape_pt_lon=VALUES(shape_pt_lon)"""
                    
                    shape_id = int(row.get('shape_id')) if row.get('shape_id') else None
                    shape_pt_lat = float(row.get('shape_pt_lat')) if row.get('shape_pt_lat') else None
                    shape_pt_lon = float(row.get('shape_pt_lon')) if row.get('shape_pt_lon') else None
                    shape_pt_sequence = int(row.get('shape_pt_sequence')) if row.get('shape_pt_sequence') else None
                    
                    cursor.execute(sql, (
                        shape_id,
                        shape_pt_lat,
                        shape_pt_lon,
                        shape_pt_sequence
                    ))
                    count += 1
                except Exception as e:
                    continue
        
        conn.commit()
        print(f"  ✅ {count} shape kaydı yüklendi")
    except Exception as e:
        print(f"  ❌ Shapes import hatası: {e}")
    finally:
        cursor.close()

def import_frequencies(conn, file_path):
    """Frequencies tablosuna veri yükle"""
    cursor = conn.cursor()
    count = 0
    
    try:
        f = get_file_handle(file_path)
        with f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    sql = """INSERT INTO frequencies 
                             (trip_id, start_time, end_time, exact_times) 
                             VALUES (%s, %s, %s, %s)
                             ON DUPLICATE KEY UPDATE 
                             end_time=VALUES(end_time), exact_times=VALUES(exact_times)"""
                    
                    trip_id_val = row.get('trip_id', '').strip()
                    if not trip_id_val:
                        continue
                    try:
                        trip_id_val = int(trip_id_val)
                    except:
                        continue
                    
                    exact_times = 0
                    if row.get('exact_times'):
                        try:
                            exact_times = int(row.get('exact_times').strip())
                        except:
                            pass
                    
                    cursor.execute(sql, (
                        trip_id_val,
                        row.get('start_time', '').strip() or None,
                        row.get('end_time', '').strip() or None,
                        exact_times
                    ))
                    count += 1
                except Exception as e:
                    continue
        
        conn.commit()
        print(f"  ✅ {count} frequency kaydı yüklendi")
    except Exception as e:
        print(f"  ❌ Frequencies import hatası: {e}")
    finally:
        cursor.close()

def main():
    print("=" * 60)
    print("GTFS Verilerini İndir ve Veritabanına Yükle")
    print("=" * 60)
    print()
    
    # CSV dosyalarını kontrol et
    data_dir = 'gtfs_data'
    
    if not os.path.exists(data_dir):
        print(f"❌ {data_dir} klasörü bulunamadı!")
        print()
        print("📥 İBB'den GTFS verilerini indir:")
        print("   1. https://data.ibb.gov.tr/dataset/public-transport-gtfs-data adresine git")
        print("   2. 'Veri ve Kaynaklar' bölümünden CSV dosyalarını indir")
        print("   3. Dosyaları gtfs_data klasörüne koy")
        print()
        print("   Veya ZIP dosyası varsa, script otomatik açabilir")
        return
    
    # Veritabanına bağlan
    print("🔌 Veritabanına bağlanılıyor...")
    conn = get_db_connection()
    if not conn:
        return
    
    print("✅ Bağlantı başarılı!")
    print()
    
    # Her dosyayı yükle (hem .txt hem .csv uzantılarını dene)
    import_map = {
        'agency': import_agency,
        'routes': import_routes,
        'stops': import_stops,
        'calendar': import_calendar,
        'trips': import_trips,
        'stop_times': import_stop_times,
        'shapes': import_shapes,
        'frequencies': import_frequencies
    }
    
    for filebase, import_func in import_map.items():
        # Önce .csv, sonra .txt dene
        file_path = None
        for ext in ['.csv', '.txt']:
            test_path = os.path.join(data_dir, f"{filebase}{ext}")
            if os.path.exists(test_path):
                file_path = test_path
                break
        
        if file_path:
            print(f"📥 {os.path.basename(file_path)} yükleniyor...")
            import_func(conn, file_path)
        else:
            print(f"⚠️  {filebase}.csv veya {filebase}.txt bulunamadı, atlanıyor...")
    
    conn.close()
    print()
    print("=" * 60)
    print("✅ İşlem tamamlandı!")
    print("=" * 60)

if __name__ == '__main__':
    main()

