import time
import random  # Simulate sensor data
import psycopg2
from psycopg2 import OperationalError
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import threading

# Flask app setup
app = Flask(__name__)
app.secret_key = 'your_secret_key_eden'  # Replace with a secure key in production

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

# Simulated sensor data class
class FarmSensors:
    def __init__(self):
        self.min_soil_moisture = 30
        self.min_water_level = 100
        self.min_energy_level = 100

    def get_sensor_data(self):
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "soil_moisture": random.randint(0, 100),
            "temperature": random.uniform(15, 35),
            "water_level": random.randint(0, 1000),
            "energy_level": random.uniform(0, 500)
        }

# Livestock management class
class LivestockManager:
    def __init__(self, logger):
        self.logger = logger
        self.min_feed_level = 5
        self.min_water_per_animal = 10

    def get_livestock_data(self):
        return [
            {"id": i, "type": "Chicken", "feed_level": random.uniform(0, 10), "water_consumed": random.uniform(0, 15)}
            for i in range(1, 6)
        ]

    def manage_livestock(self, livestock_data, farm_water_level, timestamp):
        actions = []
        total_water_needed = 0
        for animal in livestock_data:
            if animal["feed_level"] < self.min_feed_level:
                actions.append(f"Refill feed for {animal['type']} ID {animal['id']}: Feed level {animal['feed_level']:.1f}kg below minimum.")
            if animal["water_consumed"] < self.min_water_per_animal:
                water_needed = self.min_water_per_animal - animal["water_consumed"]
                total_water_needed += water_needed
                actions.append(f"Provide {water_needed:.1f}L water to {animal['type']} ID {animal['id']}: Consumed only {animal['water_consumed']:.1f}L.")
            self.logger.save_livestock_data(animal, timestamp)
        if total_water_needed > farm_water_level:
            actions.append(f"Warning: Not enough water for livestock. Need {total_water_needed:.1f}L, available {farm_water_level}L.")
        elif total_water_needed > 0:
            actions.append(f"Allocated {total_water_needed:.1f}L water to livestock.")
        return actions, total_water_needed

# Data logging class using PostgreSQL
class DataLogger:
    def __init__(self, db_name="eden_db", user="eden_user", password="Eden@2025!", host="localhost", port="5432"):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = None
        self.connect()
        self.create_tables()

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                dbname=self.db_name,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            print("Connected to PostgreSQL database.")
        except OperationalError as e:
            print(f"Error connecting to PostgreSQL: {e}")
            raise

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                id SERIAL PRIMARY KEY,
                timestamp TEXT,
                soil_moisture INTEGER,
                temperature REAL,
                water_level INTEGER,
                energy_level REAL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                id SERIAL PRIMARY KEY,
                timestamp TEXT,
                action TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS livestock_data (
                id SERIAL PRIMARY KEY,
                timestamp TEXT,
                animal_id INTEGER,
                animal_type TEXT,
                feed_level REAL,
                water_consumed REAL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        self.conn.commit()
        # Create a default user if not exists
        try:
            cursor.execute("""
                INSERT INTO users (username, password_hash)
                VALUES (%s, %s)
                ON CONFLICT (username) DO NOTHING
            """, ('admin', generate_password_hash('EdenAdmin2025!')))
            self.conn.commit()
        except Exception as e:
            print(f"Error creating default user: {e}")
        cursor.close()

    def save_sensor_data(self, sensor_data):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO sensor_data (timestamp, soil_moisture, temperature, water_level, energy_level)
            VALUES (%s, %s, %s, %s, %s)
        """, (sensor_data["timestamp"], sensor_data["soil_moisture"], sensor_data["temperature"],
              sensor_data["water_level"], sensor_data["energy_level"]))
        self.conn.commit()
        cursor.close()

    def save_action(self, timestamp, action):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO actions (timestamp, action) VALUES (%s, %s)", (timestamp, action))
        self.conn.commit()
        cursor.close()

    def save_livestock_data(self, animal, timestamp):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO livestock_data (timestamp, animal_id, animal_type, feed_level, water_consumed)
            VALUES (%s, %s, %s, %s, %s)
        """, (timestamp, animal["id"], animal["type"], animal["feed_level"], animal["water_consumed"]))
        self.conn.commit()
        cursor.close()

    def get_average_soil_moisture(self, hours=24):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT AVG(soil_moisture)
            FROM sensor_data
            WHERE timestamp >= (NOW() - INTERVAL '%s hours')::TEXT
        """, (hours,))
        result = cursor.fetchone()[0]
        cursor.close()
        return result if result else 0

    def get_average_temperature(self, hours=24):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT AVG(temperature)
            FROM sensor_data
            WHERE timestamp >= (NOW() - INTERVAL '%s hours')::TEXT
        """, (hours,))
        result = cursor.fetchone()[0]
        cursor.close()
        return result if result else 0

    def get_soil_moisture_trend(self, hours=24):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT timestamp, soil_moisture
            FROM sensor_data
            WHERE timestamp >= (NOW() - INTERVAL '%s hours')::TEXT
            ORDER BY timestamp ASC
        """, (hours,))
        results = cursor.fetchall()
        cursor.close()
        return [{"timestamp": r[0], "soil_moisture": r[1]} for r in results]

    def get_latest_sensor_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sensor_data ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        if result:
            return {
                "timestamp": result[1],
                "soil_moisture": result[2],
                "temperature": result[3],
                "water_level": result[4],
                "energy_level": result[5]
            }
        return None

    def get_latest_livestock_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT ON (animal_id) * FROM livestock_data ORDER BY animal_id, id DESC")
        results = cursor.fetchall()
        cursor.close()
        return [
            {"id": r[2], "type": r[3], "feed_level": r[4], "water_consumed": r[5]}
            for r in results
        ]

    def get_latest_actions(self, limit=10):
        cursor = self.conn.cursor()
        cursor.execute("SELECT timestamp, action FROM actions ORDER BY id DESC LIMIT %s", (limit,))
        results = cursor.fetchall()
        cursor.close()
        return [{"timestamp": r[0], "action": r[1]} for r in results]

    def get_user_by_username(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, username, password_hash FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        cursor.close()
        return result

    def create_user(self, username, password):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (username, password_hash)
                VALUES (%s, %s)
                RETURNING id
            """, (username, generate_password_hash(password)))
            user_id = cursor.fetchone()[0]
            self.conn.commit()
            return user_id
        except psycopg2.IntegrityError:
            self.conn.rollback()
            return None
        finally:
            cursor.close()

    def close(self):
        if self.conn:
            self.conn.close()
            print("PostgreSQL connection closed.")

# Core AI decision-making class
class EdenAI:
    def __init__(self):
        self.sensors = FarmSensors()
        self.logger = DataLogger()
        self.livestock = LivestockManager(self.logger)
        self.latest_data = None

    def make_decisions(self, sensor_data):
        actions = []
        if sensor_data["soil_moisture"] < self.sensors.min_soil_moisture:
            if sensor_data["water_level"] > self.sensors.min_water_level:
                actions.append("Irrigate: Soil moisture too low.")
            else:
                actions.append("Cannot irrigate: Low water level.")
        if sensor_data["water_level"] < self.sensors.min_water_level:
            actions.append("Refill water tank: Low water level.")
        if sensor_data["energy_level"] < self.sensors.min_energy_level:
            actions.append("Switch to backup power: Low energy level.")
        if sensor_data["temperature"] > 30:
            actions.append("High temperature alert: Check crop health.")
        return actions

    def run(self):
        print("Starting Eden AI for Self-Sustainable Farm...")
        try:
            while True:
                sensor_data = self.sensors.get_sensor_data()
                farm_actions = self.make_decisions(sensor_data)
                livestock_data = self.livestock.get_livestock_data()
                livestock_actions, water_used = self.livestock.manage_livestock(livestock_data, sensor_data["water_level"], sensor_data["timestamp"])
                all_actions = farm_actions + livestock_actions
                self.logger.save_sensor_data(sensor_data)
                for action in all_actions:
                    self.logger.save_action(sensor_data["timestamp"], action)
                self.latest_data = {
                    "sensor_data": sensor_data,
                    "livestock_data": livestock_data,
                    "actions": all_actions,
                    "avg_soil_moisture": self.logger.get_average_soil_moisture(),
                    "avg_temperature": self.logger.get_average_temperature(),
                    "soil_moisture_trend": self.logger.get_soil_moisture_trend()
                }
                print("\nEden Status Report:")
                print(f"Timestamp: {sensor_data['timestamp']}")
                print(f"Soil Moisture: {sensor_data['soil_moisture']}% (24h Avg: {self.latest_data['avg_soil_moisture']:.1f}%)")
                print(f"Temperature: {sensor_data['temperature']:.1f}°C (24h Avg: {self.latest_data['avg_temperature']:.1f}°C)")
                print(f"Water Level: {sensor_data['water_level']}L")
                print(f"Energy Level: {sensor_data['energy_level']:.1f}W")
                print("\nLivestock Status:")
                for animal in livestock_data:
                    print(f"{animal['type']} ID {animal['id']}: Feed Level {animal['feed_level']:.1f}kg, Water Consumed {animal['water_consumed']:.1f}L")
                print("\nActions Taken:")
                if all_actions:
                    for action in all_actions:
                        print(f"- {action}")
                else:
                    print("- No actions taken.")
                time.sleep(300)
        except KeyboardInterrupt:
            print("\nStopping Eden AI...")
            self.logger.close()

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User(user_id, f"user_{user_id}")

# Flask routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = eden.logger.get_user_by_username(username)
        if user_data and check_password_hash(user_data[2], password):
            user = User(user_data[0], user_data[1])
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('register.html')
        user_id = eden.logger.create_user(username, password)
        if user_id:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        flash('Username already exists.', 'error')
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    if eden.latest_data:
        return render_template('dashboard.html', data=eden.latest_data)
    else:
        latest_sensor_data = eden.logger.get_latest_sensor_data()
        latest_livestock_data = eden.logger.get_latest_livestock_data()
        latest_actions = eden.logger.get_latest_actions()
        avg_soil_moisture = eden.logger.get_average_soil_moisture()
        avg_temperature = eden.logger.get_average_temperature()
        soil_moisture_trend = eden.logger.get_soil_moisture_trend()
        data = {
            "sensor_data": latest_sensor_data if latest_sensor_data else {},
            "livestock_data": latest_livestock_data,
            "actions": latest_actions,
            "avg_soil_moisture": avg_soil_moisture,
            "avg_temperature": avg_temperature,
            "soil_moisture_trend": soil_moisture_trend
        }
        return render_template('dashboard.html', data=data)

# Main entry point
if __name__ == "__main__":
    eden = EdenAI()
    ai_thread = threading.Thread(target=eden.run)
    ai_thread.daemon = True
    ai_thread.start()
    app.run(host='0.0.0.0', port=5000)