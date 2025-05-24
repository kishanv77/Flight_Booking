from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_NAME = 'flights.db'

# ---------- Initialize DB ----------
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS flights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origin TEXT,
                destination TEXT,
                departure_time TEXT,
                seats_available INTEGER
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                passenger_name TEXT,
                flight_id INTEGER,
                FOREIGN KEY (flight_id) REFERENCES flights(id)
            )
        ''')
        conn.commit()

# ---------- Routes ----------

@app.route('/')
def index():
    return "Flight Booking API"

# Add a flight (admin functionality)
@app.route('/add_flight', methods=['POST'])
def add_flight():
    data = request.json
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO flights (origin, destination, departure_time, seats_available)
            VALUES (?, ?, ?, ?)
        ''', (data['origin'], data['destination'], data['departure_time'], data['seats_available']))
        conn.commit()
    return jsonify({"message": "Flight added successfully"}), 201

# View all flights
@app.route('/flights', methods=['GET'])
def get_flights():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM flights')
        rows = cur.fetchall()
        flights = [{
            'id': row[0],
            'origin': row[1],
            'destination': row[2],
            'departure_time': row[3],
            'seats_available': row[4]
        } for row in rows]
    return jsonify(flights)

# Book a flight
@app.route('/book', methods=['POST'])
def book_flight():
    data = request.json
    flight_id = data['flight_id']
    passenger_name = data['passenger_name']

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        # Check if flight exists and has available seats
        cur.execute('SELECT seats_available FROM flights WHERE id = ?', (flight_id,))
        result = cur.fetchone()
        if not result:
            return jsonify({"error": "Flight not found"}), 404
        if result[0] <= 0:
            return jsonify({"error": "No seats available"}), 400

        # Book the flight
        cur.execute('''
            INSERT INTO bookings (passenger_name, flight_id)
            VALUES (?, ?)
        ''', (passenger_name, flight_id))

        # Decrease available seats
        cur.execute('''
            UPDATE flights SET seats_available = seats_available - 1 WHERE id = ?
        ''', (flight_id,))

        conn.commit()
    return jsonify({"message": "Booking successful"}), 201

# View all bookings
@app.route('/bookings', methods=['GET'])
def get_bookings():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT b.id, b.passenger_name, f.origin, f.destination, f.departure_time
            FROM bookings b
            JOIN flights f ON b.flight_id = f.id
        ''')
        rows = cur.fetchall()
        bookings = [{
            'booking_id': row[0],
            'passenger_name': row[1],
            'origin': row[2],
            'destination': row[3],
            'departure_time': row[4]
        } for row in rows]
    return jsonify(bookings)

# ---------- Main ----------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
