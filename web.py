import sqlite3
import time
import random
import logging
from flask import Flask, render_template, request, redirect, url_for

# Set up the logger
logging.basicConfig(filename='rfid_access.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')


messages = []


def log_message(message):
    """
    Logs the message to the messages list with a timestamp.
    """
    timestamped_message = f"{time.strftime('%d-%b-%y %H:%M:%S')} - {message}"
    messages.append(timestamped_message)


def setup_database():
    """
    Set up the SQLite3 database to store authorized RFID keys.
    Creates the database and table if they do not exist.
    """
    conn = sqlite3.connect('rfid_keys.db')
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS authorized_keys (
        rfid_key TEXT UNIQUE,
        description TEXT
    )
    """)

    conn.commit()
    conn.close()


def mock_reader():
    """
    Mock function to simulate reading an RFID key.
    This will return a random key from a set of predefined keys for testing.
    """
    test_keys = ["12345678", "87654321", "11223344", "55667788"]
    return random.choice(test_keys)


def is_key_authorized(rfid_key):
    """
    Check if the given RFID key is authorized (exists in the database).

    :param rfid_key: The RFID key to check.
    :return: True if the key is authorized, False otherwise.
    """
    conn = sqlite3.connect('rfid_keys.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM authorized_keys WHERE rfid_key=?", (rfid_key,))
    result = cursor.fetchone()

    conn.close()

    return bool(result)


def add_key_to_database(rfid_key, description=""):
    conn = None
    try:
        conn = sqlite3.connect('rfid_keys.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO authorized_keys (rfid_key, description) VALUES (?, ?)", (rfid_key, description))
        conn.commit()
        log_message(f"Key {rfid_key} added to the database.")
    except sqlite3.IntegrityError:
        log_message(f"Key {rfid_key} already exists in the database.")
    finally:
        if conn:
            conn.close()


def remove_key_from_database(input_value, by_description=False):
    """
    Remove an RFID key from the authorized key's database.

    :param input_value: The RFID key or description based on which the deletion is performed.
    :param by_description: Boolean indicating whether deletion is based on description.
    """
    conn = sqlite3.connect('rfid_keys.db')
    cursor = conn.cursor()

    if by_description:
        cursor.execute("DELETE FROM authorized_keys WHERE description=?", (input_value,))
    else:
        cursor.execute("DELETE FROM authorized_keys WHERE rfid_key=?", (input_value,))

    if cursor.rowcount:
        log_message(
            f"Entry with {'description' if by_description else 'RFID key'} '{input_value}' removed from the database.")
    else:
        log_message(
            f"Entry with {'description' if by_description else 'RFID key'} '{input_value}' not found in the database.")

    conn.commit()
    conn.close()


def list_all_entries():
    """
    Fetch and log all entries from the database.
    """
    conn = sqlite3.connect('rfid_keys.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM authorized_keys")
    results = cursor.fetchall()

    conn.close()

    if results:
        log_message("Listing all entries from the database:")
        for rfid_key, description in results:
            log_message(f"RFID Key: {rfid_key}, Description: {description}")
    else:
        log_message("No entries found in the database.")


# Flask setup
app = Flask(__name__)
app.secret_key = 'some_secret_key'  # For flashing messages


@app.route('/')
def index():
    return render_template('index.html', messages=messages)


@app.route('/simulate_rfid_scan', methods=['POST'])
def simulate_rfid_scan():
    rfid_key = request.form['rfid_key']
    if not rfid_key:
        rfid_key = mock_reader()  # If no key is entered, use the mock reader.
    if is_key_authorized(rfid_key):
        log_message(f"Read RFID key: {rfid_key}. Access granted!")
    else:
        log_message(f"Read RFID key: {rfid_key}. Access denied!")
    return redirect(url_for('index'))


@app.route('/add_key', methods=['POST'])
def add_key():
    rfid_key = request.form['rfid_key']
    description = request.form['description']
    add_key_to_database(rfid_key, description)
    log_message(f"RFID key: {rfid_key} added with description: {description}")
    return redirect(url_for('index'))


@app.route('/remove_key', methods=['POST'])
def remove_key():
    rfid_key = request.form['rfid_key']
    description = request.form['description']
    if rfid_key:
        remove_key_from_database(rfid_key)
        log_message(f"RFID key: {rfid_key} removed")
    elif description:
        remove_key_from_database(description, by_description=True)
        log_message(f"Description: {description} removed")
    return redirect(url_for('index'))


@app.route('/list_entries', methods=['POST'])
def list_entries():
    list_all_entries()
    return redirect(url_for('index'))


if __name__ == "__main__":
    setup_database()
    app.run(debug=True)
