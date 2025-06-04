import time
import random  # Simulate sensor data (replace with actual IoT sensors)
import psycopg2
from psycopg2 import OperationalError
from datetime import datetime

# Simulated sensor data class (replace with actual IoT sensor integration)
class FarmSensors:
    def __init__(self):
        self.min_soil_moisture = 30  # Threshold for irrigation
        self.min_water_level = 100   # Liters, threshold for water tank
        self.min_energy_level = 100  # Watts, threshold for energy alert

    def get_sensor_data(self):
        """Simulate sensor readings for soil moisture, temperature, water, and energy."""
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "soil_moisture": random.randint(0, 100),      # Percentage
            "temperature": random.uniform(15, 35),        # Celsius
            "water_level": random.randint(0, 1000),       # Liters
            "energy_level": random.uniform(0, 500)        # Watts from solar panels
        }

# Livestock management class
class LivestockManager:
    def __init__(self, logger):
        self.logger = logger
        self.min_feed_level = 5  # Minimum feed level (kg) per animal
        self.min_water_per_animal = 10  # Minimum water (liters) per animal per day

    def get_livestock_data(self):
        """Simulate livestock data (replace with actual data collection)."""
        # Simulate 5 chickens for now
        return [
            {"id": 1, "type": "Chicken", "feed_level": random.uniform(0, 10), "water_consumed": random.uniform(0, 15)},
            {"id": 2, "type": "Chicken", "feed_level": random.uniform(0, 10), "water_consumed": random.uniform(0, 15)},
            {"id": 3, "type": "Chicken", "feed_level": random.uniform(0, 10), "water_consumed": random.uniform(0, 15)},
            {"id": 4, "type": "Chicken", "feed_level": random.uniform(0, 10), "water_consumed": random.uniform(0, 15)},
            {"id": 5, "type": "Chicken", "feed_level": random.uniform(0, 10), "water_consumed": random.uniform(0, 15)}
        ]

    def manage_livestock(self, livestock_data, farm_water_level, timestamp):
        """Make decisions for livestock management."""
        actions = []
        total_water_needed = 0

        for animal in livestock_data:
            # Check feed level
            if animal["feed_level"] < self.min_feed_level:
                actions.append(f"Refill feed for {animal['type']} ID {animal['id']}: Feed level {animal['feed_level']:.1f}kg below minimum.")
                # Placeholder for actual feed refill
            # Check water consumption
            if animal["water_consumed"] < self.min_water_per_animal:
                water_needed = self.min_water_per_animal - animal["water_consumed"]
                total_water_needed += water_needed
                actions.append(f"Provide {water_needed:.1f}L water to {animal['type']} ID {animal['id']}: Consumed only {animal['water_consumed']:.1f}L.")

            # Log livestock data
            self.logger.save_livestock_data(animal, timestamp)

        # Check if there's enough water for livestock
        if total_water_needed > farm_water_level:
            actions.append(f"Warning: Not enough water for livestock. Need {total_water_needed:.1f}L, available {farm_water_level}L.")
        elif total_water_needed > 0:
            # Deduct water from farm's water level (simulated deduction)
            actions.append(f"Allocated {total_water_needed:.1f}L water to livestock.")

        return actions, total_water_needed

# Data logging class using PostgreSQL
class DataLogger:
    def __init__(self, db_name="eden_db", user="eden_user", password="your_secure_password", host="localhost", port="5432"):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Connect to PostgreSQL database."""
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
        """Create tables for sensor data, actions, and livestock data."""
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
        self.conn.commit()
        cursor.close()

    def save_sensor_data(self, sensor_data):
        """Save sensor data to PostgreSQL database."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO sensor_data (timestamp, soil_moisture, temperature, water_level, energy_level)
            VALUES (%s, %s, %s, %s, %s)
        """, (sensor_data["timestamp"], sensor_data["soil_moisture"], sensor_data["temperature"],
              sensor_data["water_level"], sensor_data["energy_level"]))
        self.conn.commit()
        cursor.close()

    def save_action(self, timestamp, action):
        """Save AI actions to PostgreSQL database."""
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO actions (timestamp, action) VALUES (%s, %s)", (timestamp, action))
        self.conn.commit()
        cursor.close()

    def save_livestock_data(self, animal, timestamp):
        """Save livestock data to PostgreSQL database."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO livestock_data (timestamp, animal_id, animal_type, feed_level, water_consumed)
            VALUES (%s, %s, %s, %s, %s)
        """, (timestamp, animal["id"], animal["type"], animal["feed_level"], animal["water_consumed"]))
        self.conn.commit()
        cursor.close()

    def get_average_soil_moisture(self, hours=24):
        """Get average soil moisture over the last specified hours."""
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
        """Get average temperature over the last specified hours."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT AVG(temperature)
            FROM sensor_data
            WHERE timestamp >= (NOW() - INTERVAL '%s hours')::TEXT
        """, (hours,))
        result = cursor.fetchone()[0]
        cursor.close()
        return result if result else 0

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            print("PostgreSQL connection closed.")

# Core AI decision-making class
class EdenAI:
    def __init__(self):
        self.sensors = FarmSensors()
        self.logger = DataLogger()
        self.livestock = LivestockManager(self.logger)

    def make_decisions(self, sensor_data):
        """Make AI decisions based on sensor data."""
        actions = []

        # Decision 1: Irrigation
        if sensor_data["soil_moisture"] < self.sensors.min_soil_moisture:
            if sensor_data["water_level"] > self.sensors.min_water_level:
                actions.append("Irrigate: Soil moisture too low.")
                # Placeholder for actual irrigation control
            else:
                actions.append("Cannot irrigate: Low water level.")

        # Decision 2: Water management
        if sensor_data["water_level"] < self.sensors.min_water_level:
            actions.append("Refill water tank: Low water level.")
            # Placeholder for water recycling system activation

        # Decision 3: Energy management
        if sensor_data["energy_level"] < self.sensors.min_energy_level:
            actions.append("Switch to backup power: Low energy level.")
            # Placeholder for energy system control

        # Decision 4: Temperature alert (for crop health)
        if sensor_data["temperature"] > 30:
            actions.append("High temperature alert: Check crop health.")

        return actions

    def run(self):
        """Main loop for Eden AI."""
        print("Starting Eden AI for Self-Sustainable Farm...")
        try:
            while True:
                # Collect sensor data
                sensor_data = self.sensors.get_sensor_data()
                
                # Make farm decisions
                farm_actions = self.make_decisions(sensor_data)
                
                # Manage livestock
                livestock_data = self.livestock.get_livestock_data()
                livestock_actions, water_used = self.livestock.manage_livestock(livestock_data, sensor_data["water_level"], sensor_data["timestamp"])
                
                # Combine actions
                all_actions = farm_actions + livestock_actions
                
                # Log sensor data and actions
                self.logger.save_sensor_data(sensor_data)
                for action in all_actions:
                    self.logger.save_action(sensor_data["timestamp"], action)
                
                # Get historical analysis
                avg_soil_moisture = self.logger.get_average_soil_moisture(hours=24)
                avg_temperature = self.logger.get_average_temperature(hours=24)
                
                # Display current status
                print("\nEden Status Report:")
                print(f"Timestamp: {sensor_data['timestamp']}")
                print("Farm Status:")
                print(f"Soil Moisture: {sensor_data['soil_moisture']}% (24h Avg: {avg_soil_moisture:.1f}%)")
                print(f"Temperature: {sensor_data['temperature']:.1f}°C (24h Avg: {avg_temperature:.1f}°C)")
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
                
                time.sleep(300)  # Check every 5 minutes
        except KeyboardInterrupt:
            print("\nStopping Eden AI...")
            self.logger.close()

# Main entry point
if __name__ == "__main__":
    eden = EdenAI()
    eden.run()