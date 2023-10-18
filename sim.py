import sqlite3
import time
import random
import logging

# Set up the logger
logging.basicConfig(filename='rfid_access.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')


def log_message(message):
    """
    Logs the message to the console and to a log file.
    """
    print(message)
    logging.info(message)


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
            f"Entry with {'description' if by_description else 'RFID key'} '{input_value}' was not found in the database.")

    conn.commit()
    conn.close()


def main():
    """
    Main loop to allow adding/removing/checking RFID keys.
    """
    try:
        while True:
            log_message(
                "\nOptions:\n1. Simulate RFID scan\n2. Add key to database\n3. Remove key from database\n4. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                log_message("Simulating placing the RFID card on the scanner...")
                rfid_key = mock_reader()
                log_message(f"Read RFID key: {rfid_key}")

                if is_key_authorized(rfid_key):
                    log_message("Access granted!")
                    log_message("Simulating door unlock for 3 seconds...")
                    time.sleep(3)
                    log_message("Simulating door lock again...")
                else:
                    log_message("Access denied!")
                    time.sleep(1)
            elif choice == "2":
                rfid_key = input("Enter the RFID key to add: ")
                description = input("Enter a description for the key (optional): ")
                add_key_to_database(rfid_key, description)
            elif choice == "3":
                removal_choice = input("Remove by (1) RFID key or (2) Description? ")
                if removal_choice == "1":
                    rfid_key = input("Enter the RFID key to remove: ")
                    remove_key_from_database(rfid_key)
                elif removal_choice == "2":
                    description = input("Enter the description of the key to remove: ")
                    remove_key_from_database(description, by_description=True)
                else:
                    log_message("Invalid choice. Please try again.")
            elif choice == "4":
                log_message("Exiting program.")
                break
            else:
                log_message("Invalid choice. Please try again.")

    except KeyboardInterrupt:
        log_message("Exiting program.")


if __name__ == "__main__":
    main()


def main():
    """
    Main loop to constantly "read" RFID keys and check their authorization.
    """
    try:
        while True:
            log_message("Simulating placing the RFID card on the scanner...")
            rfid_key = mock_reader()
            log_message(f"Read RFID key: {rfid_key}")

            if is_key_authorized(rfid_key):
                log_message("Access granted!")
                log_message("Simulating door unlock for 3 seconds...")
                time.sleep(3)
                log_message("Simulating door lock again...")
            else:
                log_message("Access denied!")
                time.sleep(1)
    except KeyboardInterrupt:
        log_message("Exiting program.")


if __name__ == "__main__":
    main()
