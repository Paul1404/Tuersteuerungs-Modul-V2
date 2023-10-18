import sqlite3
from gpiozero import LED
from mfrc522 import SimpleMFRC522
import time


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


setup_database()

# Initialize the RFID reader and LED (representing the "Lock")
reader = SimpleMFRC522()
door_lock = LED(17)  # Using GPIO17 for the door lock as an example


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


def main():
    """
    Main loop to constantly read RFID keys and check their authorization.
    If the key is authorized, the "door" (LED) unlocks for 3 seconds.
    """
    try:
        while True:
            print("Please place the RFID card on the scanner...")
            rfid_key, _ = reader.read()

            if is_key_authorized(str(rfid_key)):
                print("Access granted!")
                door_lock.off()  # Unlock the "door"
                time.sleep(3)    # Keep the "door" unlocked for 3 seconds
                door_lock.on()   # Lock the "door" again
            else:
                print("Access denied!")
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        door_lock.off()  # Ensure the "door lock" is unlocked upon termination


if __name__ == "__main__":
    main()
