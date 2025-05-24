from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for flashing messages

BACKEND_URL = 'http://localhost:5000'  # Backend API base URL

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/flights')
def flights():
    response = requests.get(f'{BACKEND_URL}/flights')
    flights = response.json()
    return render_template('flights.html', flights=flights)

@app.route('/book/<int:flight_id>', methods=['GET', 'POST'])
def book(flight_id):
    if request.method == 'POST':
        passenger_name = request.form['passenger_name']
        data = {
            'flight_id': flight_id,
            'passenger_name': passenger_name
        }
        response = requests.post(f'{BACKEND_URL}/book', json=data)
        if response.status_code == 201:
            flash('Booking successful!', 'success')
            return redirect(url_for('bookings'))
        else:
            flash(response.json().get('error', 'Booking failed'), 'danger')
    return render_template('book.html', flight_id=flight_id)

@app.route('/bookings')
def bookings():
    response = requests.get(f'{BACKEND_URL}/bookings')
    bookings = response.json()
    return render_template('bookings.html', bookings=bookings)

if __name__ == '__main__':
    app.run(port=5001, debug=True)  # Run frontend on a different port
