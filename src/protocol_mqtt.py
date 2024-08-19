"""
protocol_mqtt
============
Module that provides protocol and protocol data updating when receiving messages via MQTT from cloud.

Functions
---------
connect_to_database()
    Used for establishing connection to the sqlite database which stores protocols and protocol data
set_up_database()
    Used for creating protocol and protocol data tables in sqlite database if tables don't exist
add_protocols(protocols)
    Used for adding one or more protocols received from cloud to the sqlite database
remove_protocols(protocol_ids)
    Used for removing one or more protocols based on their ids received from cloud from the sqlite database
main()
    Protocol MQTT app entrypoint.

Constants
---------
transport_protocol: str
    JSON key for MQTT transport protocol
gcb_protocol_topic: str
    MQTT topic for protocols and protocol data
database_file: str
    Location of the database file.
"""
import logging.config
from config_util import Config, CONF_PATH
import mqtt_util
import sqlite3

logging.config.fileConfig('logging.conf')
errorLogger = logging.getLogger('customErrorLogger')
customLogger = logging.getLogger('customConsoleLogger')

TRANSPORT_PROTOCOL = "tcp"
GCB_PROTOCOL_TOPIC = "gateway/protocol"
DATABASE_FILE = './database/modular-protocols.db'


def connect_to_database():
    """
    Function that establishes connection to the sqlite database where the information about protocol and protocol data
    is stored

    Returns
    -------
    : sqlite3.Connection
        Open SQLite database

    """
    return sqlite3.connect(DATABASE_FILE)


def set_up_database():
    """
    Function that creates sqlite database that stores protocol and protocol data if it does not already exist
    Foreign key constraint is also created which enables associated protocol data to be deleted when a certain protocol
    is deleted

    """
    conn = connect_to_database()
    cursor = conn.cursor()

    # Create protocol_entity table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS protocol_entity (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        assigned INTEGER NOT NULL CHECK (assigned IN (0, 1))
    )
    ''')

    # Create protocol_data_entity table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS protocol_data_entity (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aggregation_method TEXT NOT NULL,
        can_id INTEGER NOT NULL,
        divisor INTEGER NOT NULL,
        mode TEXT NOT NULL,
        multiplier INTEGER NOT NULL,
        name TEXT NOT NULL,
        num_bits INTEGER NOT NULL,
        offset_value INTEGER NOT NULL,
        start_bit INTEGER NOT NULL,
        transmit_interval INTEGER NOT NULL,
        unit TEXT,
        protocol INTEGER NOT NULL,
        FOREIGN KEY (protocol) REFERENCES protocol_entity(id) ON DELETE CASCADE
    )
    ''')
    conn.commit()
    conn.close()


def add_protocols(protocols):
    """
    Function that insert data into protocol and protocol data tables after the user submits changes in cloud
    configuration

    Args:
    ----
        protocols: list
            List that stores protocols and their associated data which will be inserted into the database

    """
    conn = connect_to_database()
    cursor = conn.cursor()

    for protocol in protocols:
        protocol_id = protocol["id"]
        protocol_name = protocol["name"]
        protocol_assigned = 1 if protocol["assigned"] else 0

        # Insert protocol
        cursor.execute('''
            INSERT INTO protocol_entity (id, name, assigned)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            assigned=excluded.assigned
        ''', (protocol_id, protocol_name, protocol_assigned))

        # Insert protocol data
        for pdata in protocol["protocolData"]:
            cursor.execute('''
                INSERT INTO protocol_data_entity (
                    id, aggregation_method, can_id, divisor, mode,
                    multiplier, name, num_bits, offset_value,
                    start_bit, transmit_interval, unit, protocol
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pdata["id"], pdata["aggregationMethod"], pdata["canId"], pdata["divisor"], pdata["mode"],
                pdata["multiplier"], pdata["name"], pdata["numBits"], pdata["offsetValue"],
                pdata["startBit"], pdata["transmitInterval"], pdata["unit"], protocol_id
            ))

    conn.commit()
    conn.close()


def remove_protocols(protocol_ids):
    """
    Function that removes data from protocol and protocol data tables after the user submits changes in cloud
    configuration

    Args:
    ----
        protocols_ids: list
            List that stores protocol ids which will be deleted from the database

    """
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys=ON;')

    # Delete protocols (protocol data will be deleted on cascade)
    query_protocol = 'DELETE FROM protocol_entity WHERE id IN ({})'.format(
        ','.join('?' for _ in protocol_ids)
    )
    cursor.execute(query_protocol, protocol_ids)

    conn.commit()
    conn.close()


def main():
    """
    Start Protocol MQTT app entrypoint which sets up database, reads relevant config parameters, connects client to the
    broker, subscribes client to relevant topic and starts client loop

    """
    set_up_database()
    config = Config(CONF_PATH, errorLogger, customLogger)
    config.try_open()
    client = mqtt_util.gcb_init_subscriber(
        "protocol-client-id",
        config.gateway_cloud_broker_iot_username,
        config.gateway_cloud_broker_iot_password)
    client.connect(config.gateway_cloud_broker_address, config.gateway_cloud_broker_port, keepalive=60)
    mqtt_util.gcb_on_topic_subscribe(client, GCB_PROTOCOL_TOPIC)
    client.loop_forever()


if __name__ == "__main__":
    main()
