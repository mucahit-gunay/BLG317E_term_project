from flask import Flask, render_template, request, redirect, url_for
import db  # db.py dosyamızı çağırdık

app = Flask(__name__)

# Anasayfa
@app.route('/')
def index():
    return render_template('layout.html') # Şimdilik boş şablon dönsün

# --- AGENCY (AJANS) İŞLEMLERİ ---

# 1. READ: Listeleme
@app.route('/agency')
def agency_list():
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # SAF SQL: Tüm ajansları çek
    cursor.execute("SELECT * FROM Agency")
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('agency_list.html', agency_list=results)

# 2. CREATE: Ekleme
@app.route('/agency/add', methods=['GET', 'POST'])
def agency_add():
    if request.method == 'POST':
        # Formdan verileri al (Tablo yapısına uygun)
        a_id = request.form['agency_id']
        a_name = request.form['agency_name']
        a_url = request.form['agency_url']
        a_timezone = request.form['agency_timezone']
        a_lang = request.form['agency_lang']
        a_phone = request.form['agency_phone'] or None # Boşsa NULL olsun
        a_fare_url = request.form['agency_fare_url'] or None
        a_email = request.form['agency_email'] or None
        
        conn = db.get_db_connection()
        cursor = conn.cursor()
        
        # GÜNCEL SQL
        sql = """INSERT INTO agency 
                 (agency_id, agency_name, agency_url, agency_timezone, agency_lang, agency_phone, agency_fare_url, agency_email) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        try:
            cursor.execute(sql, (a_id, a_name, a_url, a_timezone, a_lang, a_phone, a_fare_url, a_email))
            conn.commit()
        except Exception as e:
            return f"Hata oluştu: {e}"
        finally:
            cursor.close()
            conn.close()
            
        return redirect('/agency')
    
    return render_template('agency_form.html', agency=None)

# 3. UPDATE: Güncelleme
@app.route('/agency/edit/<string:id>', methods=['GET', 'POST'])
def agency_edit(id):
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        # Güncellenmiş verileri al
        a_name = request.form['agency_name']
        a_url = request.form['agency_url']
        a_email = request.form['agency_email']
        
        # SAF SQL: Güncelle
        sql = "UPDATE Agency SET agency_name=%s, agency_url=%s, agency_email=%s WHERE agency_id=%s"
        cursor.execute(sql, (a_name, a_url, a_email, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/agency')
    
    # Sayfa ilk açıldığında mevcut veriyi getirip forma doldurmak için
    cursor.execute("SELECT * FROM Agency WHERE agency_id = %s", (id,))
    agency_data = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return render_template('agency_form.html', agency=agency_data)

# 4. DELETE: Silme
@app.route('/agency/delete/<string:id>')
def agency_delete(id):
    conn = db.get_db_connection()
    cursor = conn.cursor()
    
    # SAF SQL: Sil
    # NOT: Eğer bu ajansa bağlı Rotalar varsa hata verebilir (Foreign Key kuralı)
    try:
        cursor.execute("DELETE FROM Agency WHERE agency_id = %s", (id,))
        conn.commit()
    except Exception as e:
        return f"Silinemedi (Bağlı kayıtlar olabilir): {e}"
    finally:
        cursor.close()
        conn.close()
        
    return redirect('/agency')

if __name__ == '__main__':
    app.run(debug=True)
# --- HENÜZ YAPILMAMIŞ SAYFALAR İÇİN GEÇİCİ ROTALAR ---
# Bunları eklemezseniz menüdeki linklere tıklayınca hata alırsınız.

# app.py

# --- ROUTES (ROTALAR) İŞLEMLERİ ---

# 1. READ: Rotaları Listeleme
# --- ROUTES (ROTALAR) İŞLEMLERİ ---

@app.route('/routes')
def route_list():
    # 1. Veri tabanına bağlan
    conn = db.get_db_connection()
    
    # Bağlantı kontrolü
    if conn is None:
        return "Veri tabanı bağlantı hatası!", 500

    try:
        cursor = conn.cursor(dictionary=True)
        
        # 2. Routes tablosundan verileri çek
        # NOT: Tablo adınızın veritabanında 'routes' (küçük harf) olduğundan emin olun.
        # Eğer büyük harf kullandıysanız 'Routes' yazın.
        cursor.execute("SELECT * FROM routes") 
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # 3. Verileri şablona gönder
        return render_template('routes_list.html', route_list=results)
        
    except Exception as e:
        return f"Bir hata oluştu: {e}"
@app.route('/stops')
def stops_placeholder():
    return "Stops sayfası yapım aşamasında."

@app.route('/trips')
def trips_placeholder():
    return "Trips sayfası yapım aşamasında."

@app.route('/stop_times')
def stoptimes_placeholder():
    return "Stop Times sayfası yapım aşamasında."

@app.route('/calendar')
def calendar_placeholder():
    return "Calendar sayfası yapım aşamasında."

@app.route('/shapes')
def shapes_placeholder():
    return "Shapes sayfası yapım aşamasında."

@app.route('/frequencies')
def frequencies_placeholder():
    return "Frequencies sayfası yapım aşamasında."