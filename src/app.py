from flask import Flask, render_template, request, redirect, url_for
import db  # db.py dosyamızı çağırdık

app = Flask(__name__)

# Anasayfa
@app.route('/')
def index():
    return render_template('index.html')

# --- AGENCY (AJANS) İŞLEMLERİ ---

# 1. READ: Listeleme
@app.route('/agency')
def agency_list():
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # SAF SQL: Tüm ajansları çek
    cursor.execute("SELECT * FROM agency")
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
        sql = "UPDATE agency SET agency_name=%s, agency_url=%s, agency_email=%s WHERE agency_id=%s"
        cursor.execute(sql, (a_name, a_url, a_email, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/agency')
    
    # Sayfa ilk açıldığında mevcut veriyi getirip forma doldurmak için
    cursor.execute("SELECT * FROM agency WHERE agency_id = %s", (id,))
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
        cursor.execute("DELETE FROM agency WHERE agency_id = %s", (id,))
        conn.commit()
    except Exception as e:
        return f"Silinemedi (Bağlı kayıtlar olabilir): {e}"
    finally:
        cursor.close()
        conn.close()
        
    return redirect('/agency')

# --- ROUTES (ROTALAR) İŞLEMLERİ ---

# 1. READ: Rotaları Listeleme
# --- ROUTES (ROTALAR) İŞLEMLERİ ---

# --- ROUTES (ROTALAR) İŞLEMLERİ ---

@app.route('/routes')
def route_list():
    conn = db.get_db_connection()
    if conn is None:
        return "Veri tabanı bağlantı hatası!", 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM routes")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('routes_list.html', route_list=results)
    except Exception as e:
        return f"Bir hata oluştu: {e}"

@app.route('/routes/add', methods=['GET', 'POST'])
def route_add():
    if request.method == 'POST':
        route_id = request.form['route_id']
        agency_id = request.form['agency_id'] or None
        route_short_name = request.form['route_short_name'] or None
        route_long_name = request.form['route_long_name'] or None
        route_type = request.form['route_type'] or None
        route_color = request.form['route_color'] or None
        route_text_color = request.form['route_text_color'] or None
        
        conn = db.get_db_connection()
        cursor = conn.cursor()
        try:
            sql = """INSERT INTO routes (route_id, agency_id, route_short_name, route_long_name, route_type, route_color, route_text_color) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (route_id, agency_id, route_short_name, route_long_name, route_type, route_color, route_text_color))
            conn.commit()
            return redirect('/routes')
        except Exception as e:
            return f"Hata: {e}"
        finally:
            cursor.close()
            conn.close()
    
    # GET: Agency listesini çek
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT agency_id FROM agency")
    agencies = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('route_form.html', route=None, agencies=agencies)

@app.route('/routes/edit/<string:id>', methods=['GET', 'POST'])
def route_edit(id):
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        agency_id = request.form['agency_id'] or None
        route_short_name = request.form['route_short_name'] or None
        route_long_name = request.form['route_long_name'] or None
        route_type = request.form['route_type'] or None
        route_color = request.form['route_color'] or None
        route_text_color = request.form['route_text_color'] or None
        
        sql = """UPDATE routes SET agency_id=%s, route_short_name=%s, route_long_name=%s, 
                 route_type=%s, route_color=%s, route_text_color=%s WHERE route_id=%s"""
        cursor.execute(sql, (agency_id, route_short_name, route_long_name, route_type, route_color, route_text_color, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/routes')
    
    cursor.execute("SELECT * FROM routes WHERE route_id = %s", (id,))
    route_data = cursor.fetchone()
    cursor.execute("SELECT agency_id FROM agency")
    agencies = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('route_form.html', route=route_data, agencies=agencies)

@app.route('/routes/delete/<string:id>')
def route_delete(id):
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM routes WHERE route_id = %s", (id,))
        conn.commit()
    except Exception as e:
        return f"Silinemedi: {e}"
    finally:
        cursor.close()
        conn.close()
    return redirect('/routes')

# --- STOPS (DURAKLAR) İŞLEMLERİ ---

@app.route('/stops')
def stops_list():
    conn = db.get_db_connection()
    if conn is None:
        return "Veri tabanı bağlantı hatası!", 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM stops")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('stops_list.html', stops_list=results)
    except Exception as e:
        return f"Bir hata oluştu: {e}"

@app.route('/stops/add', methods=['GET', 'POST'])
def stops_add():
    if request.method == 'POST':
        stop_id = request.form['stop_id']
        stop_name = request.form['stop_name']
        stop_lat = request.form['stop_lat'] or None
        stop_lon = request.form['stop_lon'] or None
        parent_station = request.form['parent_station'] or None
        
        conn = db.get_db_connection()
        cursor = conn.cursor()
        try:
            sql = """INSERT INTO stops (stop_id, stop_name, stop_lat, stop_lon, parent_station) 
                     VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(sql, (stop_id, stop_name, stop_lat, stop_lon, parent_station))
            conn.commit()
            return redirect('/stops')
        except Exception as e:
            return f"Hata: {e}"
        finally:
            cursor.close()
            conn.close()
    
    # GET: Parent stations listesi
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT stop_id, stop_name FROM stops")
    parent_stations = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('stops_form.html', stop=None, parent_stations=parent_stations)

@app.route('/stops/edit/<int:id>', methods=['GET', 'POST'])
def stops_edit(id):
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        stop_name = request.form['stop_name']
        stop_lat = request.form['stop_lat'] or None
        stop_lon = request.form['stop_lon'] or None
        parent_station = request.form['parent_station'] or None
        
        sql = "UPDATE stops SET stop_name=%s, stop_lat=%s, stop_lon=%s, parent_station=%s WHERE stop_id=%s"
        cursor.execute(sql, (stop_name, stop_lat, stop_lon, parent_station, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/stops')
    
    cursor.execute("SELECT * FROM stops WHERE stop_id = %s", (id,))
    stop_data = cursor.fetchone()
    cursor.execute("SELECT stop_id, stop_name FROM stops")
    parent_stations = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('stops_form.html', stop=stop_data, parent_stations=parent_stations)

@app.route('/stops/delete/<int:id>')
def stops_delete(id):
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM stops WHERE stop_id = %s", (id,))
        conn.commit()
    except Exception as e:
        return f"Silinemedi: {e}"
    finally:
        cursor.close()
        conn.close()
    return redirect('/stops')

# --- TRIPS (SEFERLER) İŞLEMLERİ ---

@app.route('/trips')
def trips_list():
    conn = db.get_db_connection()
    if conn is None:
        return "Veri tabanı bağlantı hatası!", 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM trips")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('trips_list.html', trips_list=results)
    except Exception as e:
        return f"Bir hata oluştu: {e}"

@app.route('/trips/add', methods=['GET', 'POST'])
def trips_add():
    if request.method == 'POST':
        trip_id = request.form['trip_id']
        route_id = request.form['route_id'] or None
        service_id = request.form['service_id'] or None
        trip_headsign = request.form['trip_headsign'] or None
        start_time = request.form['start_time'] or None
        direction_id = request.form['direction_id'] or None
        
        conn = db.get_db_connection()
        cursor = conn.cursor()
        try:
            sql = """INSERT INTO trips (trip_id, route_id, service_id, trip_headsign, start_time, direction_id) 
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (trip_id, route_id, service_id, trip_headsign, start_time, direction_id))
            conn.commit()
            return redirect('/trips')
        except Exception as e:
            return f"Hata: {e}"
        finally:
            cursor.close()
            conn.close()
    
    # GET: Routes ve Calendar listesi
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT route_id FROM routes")
    routes = cursor.fetchall()
    cursor.execute("SELECT service_id FROM calendar")
    services = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('trips_form.html', trip=None, routes=routes, services=services)

@app.route('/trips/edit/<int:id>', methods=['GET', 'POST'])
def trips_edit(id):
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        route_id = request.form['route_id'] or None
        service_id = request.form['service_id'] or None
        trip_headsign = request.form['trip_headsign'] or None
        start_time = request.form['start_time'] or None
        direction_id = request.form['direction_id'] or None
        
        sql = """UPDATE trips SET route_id=%s, service_id=%s, trip_headsign=%s, start_time=%s, direction_id=%s 
                 WHERE trip_id=%s"""
        cursor.execute(sql, (route_id, service_id, trip_headsign, start_time, direction_id, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/trips')
    
    cursor.execute("SELECT * FROM trips WHERE trip_id = %s", (id,))
    trip_data = cursor.fetchone()
    cursor.execute("SELECT route_id FROM routes")
    routes = cursor.fetchall()
    cursor.execute("SELECT service_id FROM calendar")
    services = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('trips_form.html', trip=trip_data, routes=routes, services=services)

@app.route('/trips/delete/<int:id>')
def trips_delete(id):
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM trips WHERE trip_id = %s", (id,))
        conn.commit()
    except Exception as e:
        return f"Silinemedi: {e}"
    finally:
        cursor.close()
        conn.close()
    return redirect('/trips')

# --- STOP_TIMES İŞLEMLERİ ---

@app.route('/stop_times')
def stop_times_list():
    conn = db.get_db_connection()
    if conn is None:
        return "Veri tabanı bağlantı hatası!", 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM stop_times LIMIT 100")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('stop_times_list.html', stop_times_list=results)
    except Exception as e:
        return f"Bir hata oluştu: {e}"

@app.route('/stop_times/add', methods=['GET', 'POST'])
def stop_times_add():
    if request.method == 'POST':
        trip_id = request.form['trip_id']
        stop_id = request.form['stop_id']
        stop_sequence = request.form['stop_sequence']
        arrival_time = request.form['arrival_time']
        departure_time = request.form['departure_time']
        stop_headsign = request.form['stop_headsign'] or None
        
        conn = db.get_db_connection()
        cursor = conn.cursor()
        try:
            sql = """INSERT INTO stop_times (trip_id, stop_id, stop_sequence, arrival_time, departure_time, stop_headsign) 
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (trip_id, stop_id, stop_sequence, arrival_time, departure_time, stop_headsign))
            conn.commit()
            return redirect('/stop_times')
        except Exception as e:
            return f"Hata: {e}"
        finally:
            cursor.close()
            conn.close()
    
    # GET: Trips ve Stops listesi
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT trip_id FROM trips")
    trips = cursor.fetchall()
    cursor.execute("SELECT stop_id, stop_name FROM stops")
    stops = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('stop_times_form.html', stop_time=None, trips=trips, stops=stops)

@app.route('/stop_times/edit/<int:trip_id>/<int:stop_sequence>', methods=['GET', 'POST'])
def stop_times_edit(trip_id, stop_sequence):
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        stop_id = request.form['stop_id']
        arrival_time = request.form['arrival_time']
        departure_time = request.form['departure_time']
        stop_headsign = request.form['stop_headsign'] or None
        
        sql = """UPDATE stop_times SET stop_id=%s, arrival_time=%s, departure_time=%s, stop_headsign=%s 
                 WHERE trip_id=%s AND stop_sequence=%s"""
        cursor.execute(sql, (stop_id, arrival_time, departure_time, stop_headsign, trip_id, stop_sequence))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/stop_times')
    
    cursor.execute("SELECT * FROM stop_times WHERE trip_id = %s AND stop_sequence = %s", (trip_id, stop_sequence))
    stop_time_data = cursor.fetchone()
    cursor.execute("SELECT trip_id FROM trips")
    trips = cursor.fetchall()
    cursor.execute("SELECT stop_id, stop_name FROM stops")
    stops = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('stop_times_form.html', stop_time=stop_time_data, trips=trips, stops=stops)

@app.route('/stop_times/delete/<int:trip_id>/<int:stop_sequence>')
def stop_times_delete(trip_id, stop_sequence):
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM stop_times WHERE trip_id = %s AND stop_sequence = %s", (trip_id, stop_sequence))
        conn.commit()
    except Exception as e:
        return f"Silinemedi: {e}"
    finally:
        cursor.close()
        conn.close()
    return redirect('/stop_times')

# --- CALENDAR İŞLEMLERİ ---

@app.route('/calendar')
def calendar_list():
    conn = db.get_db_connection()
    if conn is None:
        return "Veri tabanı bağlantı hatası!", 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM calendar")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('calendar_list.html', calendar_list=results)
    except Exception as e:
        return f"Bir hata oluştu: {e}"

@app.route('/calendar/add', methods=['GET', 'POST'])
def calendar_add():
    if request.method == 'POST':
        service_id = request.form['service_id']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        sunday = request.form.get('sunday', '0')
        monday = request.form.get('monday', '0')
        tuesday = request.form.get('tuesday', '0')
        wednesday = request.form.get('wednesday', '0')
        thursday = request.form.get('thursday', '0')
        friday = request.form.get('friday', '0')
        saturday = request.form.get('saturday', '0')
        
        conn = db.get_db_connection()
        cursor = conn.cursor()
        try:
            sql = """INSERT INTO calendar (service_id, start_date, end_date, sunday, monday, tuesday, wednesday, thursday, friday, saturday) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (service_id, start_date, end_date, sunday, monday, tuesday, wednesday, thursday, friday, saturday))
            conn.commit()
            return redirect('/calendar')
        except Exception as e:
            return f"Hata: {e}"
        finally:
            cursor.close()
            conn.close()
    
    return render_template('calendar_form.html', calendar=None)

@app.route('/calendar/edit/<string:id>', methods=['GET', 'POST'])
def calendar_edit(id):
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        sunday = request.form.get('sunday', '0')
        monday = request.form.get('monday', '0')
        tuesday = request.form.get('tuesday', '0')
        wednesday = request.form.get('wednesday', '0')
        thursday = request.form.get('thursday', '0')
        friday = request.form.get('friday', '0')
        saturday = request.form.get('saturday', '0')
        
        sql = """UPDATE calendar SET start_date=%s, end_date=%s, sunday=%s, monday=%s, tuesday=%s, 
                 wednesday=%s, thursday=%s, friday=%s, saturday=%s WHERE service_id=%s"""
        cursor.execute(sql, (start_date, end_date, sunday, monday, tuesday, wednesday, thursday, friday, saturday, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/calendar')
    
    cursor.execute("SELECT * FROM calendar WHERE service_id = %s", (id,))
    calendar_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('calendar_form.html', calendar=calendar_data)

@app.route('/calendar/delete/<string:id>')
def calendar_delete(id):
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM calendar WHERE service_id = %s", (id,))
        conn.commit()
    except Exception as e:
        return f"Silinemedi: {e}"
    finally:
        cursor.close()
        conn.close()
    return redirect('/calendar')

# --- SHAPES İŞLEMLERİ ---

@app.route('/shapes')
def shapes_list():
    conn = db.get_db_connection()
    if conn is None:
        return "Veri tabanı bağlantı hatası!", 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM shapes LIMIT 100")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('shapes_list.html', shapes_list=results)
    except Exception as e:
        return f"Bir hata oluştu: {e}"

@app.route('/shapes/add', methods=['GET', 'POST'])
def shapes_add():
    if request.method == 'POST':
        shape_id = request.form['shape_id']
        shape_pt_lat = request.form['shape_pt_lat']
        shape_pt_lon = request.form['shape_pt_lon']
        shape_pt_sequence = request.form['shape_pt_sequence']
        
        conn = db.get_db_connection()
        cursor = conn.cursor()
        try:
            sql = """INSERT INTO shapes (shape_id, shape_pt_lat, shape_pt_lon, shape_pt_sequence) 
                     VALUES (%s, %s, %s, %s)"""
            cursor.execute(sql, (shape_id, shape_pt_lat, shape_pt_lon, shape_pt_sequence))
            conn.commit()
            return redirect('/shapes')
        except Exception as e:
            return f"Hata: {e}"
        finally:
            cursor.close()
            conn.close()
    
    return render_template('shapes_form.html', shape=None)

@app.route('/shapes/edit/<int:shape_id>/<int:shape_pt_sequence>', methods=['GET', 'POST'])
def shapes_edit(shape_id, shape_pt_sequence):
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        shape_pt_lat = request.form['shape_pt_lat']
        shape_pt_lon = request.form['shape_pt_lon']
        
        sql = "UPDATE shapes SET shape_pt_lat=%s, shape_pt_lon=%s WHERE shape_id=%s AND shape_pt_sequence=%s"
        cursor.execute(sql, (shape_pt_lat, shape_pt_lon, shape_id, shape_pt_sequence))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/shapes')
    
    cursor.execute("SELECT * FROM shapes WHERE shape_id = %s AND shape_pt_sequence = %s", (shape_id, shape_pt_sequence))
    shape_data = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('shapes_form.html', shape=shape_data)

@app.route('/shapes/delete/<int:shape_id>/<int:shape_pt_sequence>')
def shapes_delete(shape_id, shape_pt_sequence):
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM shapes WHERE shape_id = %s AND shape_pt_sequence = %s", (shape_id, shape_pt_sequence))
        conn.commit()
    except Exception as e:
        return f"Silinemedi: {e}"
    finally:
        cursor.close()
        conn.close()
    return redirect('/shapes')

# --- FREQUENCIES İŞLEMLERİ ---

@app.route('/frequencies')
def frequencies_list():
    conn = db.get_db_connection()
    if conn is None:
        return "Veri tabanı bağlantı hatası!", 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM frequencies")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('frequencies_list.html', frequencies_list=results)
    except Exception as e:
        return f"Bir hata oluştu: {e}"

@app.route('/frequencies/add', methods=['GET', 'POST'])
def frequencies_add():
    if request.method == 'POST':
        trip_id = request.form['trip_id']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        exact_times = request.form.get('exact_times', '0')
        
        conn = db.get_db_connection()
        cursor = conn.cursor()
        try:
            sql = """INSERT INTO frequencies (trip_id, start_time, end_time, exact_times) 
                     VALUES (%s, %s, %s, %s)"""
            cursor.execute(sql, (trip_id, start_time, end_time, exact_times))
            conn.commit()
            return redirect('/frequencies')
        except Exception as e:
            return f"Hata: {e}"
        finally:
            cursor.close()
            conn.close()
    
    # GET: Trips listesi
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT trip_id FROM trips")
    trips = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('frequencies_form.html', frequency=None, trips=trips)

@app.route('/frequencies/edit/<string:trip_id>/<string:start_time>', methods=['GET', 'POST'])
def frequencies_edit(trip_id, start_time):
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        end_time = request.form['end_time']
        exact_times = request.form.get('exact_times', '0')
        
        sql = "UPDATE frequencies SET end_time=%s, exact_times=%s WHERE trip_id=%s AND start_time=%s"
        cursor.execute(sql, (end_time, exact_times, trip_id, start_time))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/frequencies')
    
    cursor.execute("SELECT * FROM frequencies WHERE trip_id = %s AND start_time = %s", (trip_id, start_time))
    frequency_data = cursor.fetchone()
    cursor.execute("SELECT trip_id FROM trips")
    trips = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('frequencies_form.html', frequency=frequency_data, trips=trips)

@app.route('/frequencies/delete/<string:trip_id>/<string:start_time>')
def frequencies_delete(trip_id, start_time):
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM frequencies WHERE trip_id = %s AND start_time = %s", (trip_id, start_time))
        conn.commit()
    except Exception as e:
        return f"Silinemedi: {e}"
    finally:
        cursor.close()
        conn.close()
    return redirect('/frequencies')

if __name__ == '__main__':
    app.run(debug=True)