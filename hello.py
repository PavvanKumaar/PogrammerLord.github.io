from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Database configuration
db_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'contacts'
}

# Create a connection to the MySQL database
def create_connection():
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            print("Connection to MySQL database established successfully.")
    except Error as e:
        print(f"Error: {e}")
    return conn

# Create the contacts table if it doesn't exist
def create_table():
    conn = create_connection()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL
                )
            """)
            conn.commit()
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()

# Insert contact details into the database
def insert_contact(name, email, message):
    conn = create_connection()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor()
            sql = "INSERT INTO contacts (name, email, message) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, email, message))
            conn.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()

# Get all contacts from the database
def get_contacts():
    conn = create_connection()
    contacts = []
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts")
            rows = cursor.fetchall()
            for row in rows:
                contact = {
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "message": row[3]
                }
                contacts.append(contact)
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()
    return contacts

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    if request.is_json:
        data = request.get_json()
        name = data['name']
        email = data['email']
        message = data['message']
        contact_id = insert_contact(name, email, message)
        return jsonify({'id': contact_id}), 201
    else:
        return jsonify({"error": "Invalid request format"}), 400

@app.route('/contacts', methods=['GET'])
def list_contacts():
    contacts = get_contacts()
    return jsonify(contacts)

if __name__ == '__main__':
    create_table()
    app.run(debug=True)
