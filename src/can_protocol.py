"""
protocol_mqtt
============
Module that provides protocol and protocol data updating when receiving messages via MQTT from cloud.

Functions
---------
connect_to_database()
    Used for establishing connection to the sqlite database which stores protocols and protocol data
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
gcb_protocol_startup_topic: str
    MQTT topic for protocols and protocol data on app.py startup
processed_ids: dict
    Contains protocol data id which are processed as a key, values are thread and whether the thread is active or not
"""
import time
import threading
import logging.config
from src.config_util import Config, CONF_PATH
import src.mqtt_util as mqtt_util
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from src.protocol_classes import ProtocolEntity, ProtocolDataEntity, set_up_database, create_database_engine
logging.config.fileConfig('logging.conf')
errorLogger = logging.getLogger('customErrorLogger')
customLogger = logging.getLogger('customConsoleLogger')

TRANSPORT_PROTOCOL = "tcp"
GCB_PROTOCOL_TOPIC = "gateway/protocol"
GCB_PROTOCOL_STARTUP_TOPIC = "gateway/protocol-startup"
processed_ids = {}


def connect_to_database():
    """
    Function that establishes a session to the SQLite database.

    Returns
    -------
    : sqlalchemy.orm.session.Session
        SQLAlchemy session connected to the database.
    """
    engine = create_database_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def add_protocols(protocols):
    """
    Function that inserts data into protocol and protocol data tables after the user submits changes in
    cloud configuration.

    Args:
    ----
        protocols: list
            List that stores protocols and their associated data which will be inserted into the database.
    """
    session = connect_to_database()

    try:
        for protocol in protocols:
            protocol_id = protocol["id"]
            protocol_name = protocol["name"]
            protocol_assigned = 1 if protocol["assigned"] else 0

            # Insert protocols
            protocol_entity = session.query(ProtocolEntity).get(protocol_id)
            if protocol_entity is None:
                protocol_entity = ProtocolEntity(id=protocol_id, name=protocol_name, assigned=protocol_assigned)
                session.add(protocol_entity)

            # Insert protocol data
            for pdata in protocol["protocolData"]:
                protocol_data_entity = session.query(ProtocolDataEntity).filter_by(id=pdata["id"],
                                                                                   protocol=protocol_id).first()
                if protocol_data_entity is None:
                    protocol_data_entity = ProtocolDataEntity(
                        id=pdata["id"], aggregation_method=pdata["aggregationMethod"], can_id=pdata["canId"],
                        divisor=pdata["divisor"], mode=pdata["mode"], multiplier=pdata["multiplier"],
                        name=pdata["name"], num_bits=pdata["numBits"], offset_value=pdata["offsetValue"],
                        start_bit=pdata["startBit"], transmit_interval=pdata["transmitInterval"], unit=pdata["unit"],
                        protocol=protocol_id
                    )
                    session.add(protocol_data_entity)

        session.commit()
    except Exception:
        # Rollback the transaction in case of error
        session.rollback()
    finally:
        session.close()


def remove_protocols(protocol_ids):
    """
    Function that removes data from protocol and protocol data tables after the user submits changes in
    cloud configuration.

    Args:
    ----
        protocol_ids: list
            List that stores protocol IDs which will be deleted from the database.
    """
    session = connect_to_database()

    try:
        # Enable cascade delete
        session.execute(text('PRAGMA foreign_keys=ON;'))

        protocol_data_entities = session.query(ProtocolDataEntity).filter(
            ProtocolDataEntity.protocol.in_(protocol_ids)
        ).all()

        # If user removed protocol in cloud configuration, stop the thread
        for data_entity in protocol_data_entities:
            if data_entity.id in processed_ids:
                processed_ids[data_entity.id]["stopped"] = True

        # Delete protocols
        session.query(ProtocolEntity).filter(ProtocolEntity.id.in_(protocol_ids)).delete(synchronize_session=False)
        session.commit()
    except Exception:
        # Rollback the transaction in case of error
        session.rollback()
    finally:
        session.close()


def update_protocols_on_startup(protocols):
    """
    Updates protocol and protocol data databases on startup.

    Parameters
    ----------
    protocols: list
        List of protocols to insert/update.
    """
    try:
        session = connect_to_database()
        session.execute(text('PRAGMA foreign_keys=ON;'))

        # Clear existing records
        session.query(ProtocolEntity).delete(synchronize_session=False)

        for protocol in protocols:
            # Create a new ProtocolEntity instance
            protocol_entity = ProtocolEntity(
                id=protocol['id'],
                name=protocol['name'],
                assigned=1  # Default assigned value or modify as needed
            )

            # Add the ProtocolEntity instance to the session
            session.add(protocol_entity)
            session.flush()  # Flush to get the ID and ensure the entity is added

            # Add associated ProtocolDataEntity records
            for data in protocol.get('protocolData', []):
                try:
                    protocol_data_entity = ProtocolDataEntity(
                        id=data['id'],  # Ensure this ID is unique
                        aggregation_method=data['aggregationMethod'],
                        can_id=data['canId'],
                        divisor=data['divisor'],
                        mode=data['mode'],
                        multiplier=data['multiplier'],
                        name=data['name'],
                        num_bits=data['numBits'],
                        offset_value=data['offsetValue'],
                        start_bit=data['startBit'],
                        transmit_interval=data['transmitInterval'],
                        unit=data.get('unit'),
                        protocol=protocol_entity.id
                    )
                    session.add(protocol_data_entity)
                except Exception as e:
                    print(f"Error adding ProtocolDataEntity: {e}")

        # Commit the transaction
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()


def get_data_by_can_id(can_id):
    """
    Function to fetch data from protocol_data_entity table based on the received can_id.
    Used from can service module.

    Parameters
    ----------
    can_id : int
        CAN identifier.

    Returns
    -------
    results : list
        List of ProtocolDataEntity objects which have a certain CAN ID.
    """
    session = connect_to_database()
    try:
        results = session.query(ProtocolDataEntity).filter_by(can_id=can_id).all()
    finally:
        session.close()

    return results


def start_protocol_client(config, main_execution_flag):
    """
    Start Protocol MQTT subscriber client which receives data about protocol assignment/removal from the cloud.

    Parameters
    ----------
    main_execution_flag : Event
        Indicator for termination request for main loop.
    config : Config
        Enables reading parameters from config file.
    """
    client = mqtt_util.gcb_init_subscriber(
        "protocol-client-id",
        config.gateway_cloud_broker_iot_username,
        config.gateway_cloud_broker_iot_password)
    client.connect(config.gateway_cloud_broker_address, config.gateway_cloud_broker_port, keepalive=60)
    mqtt_util.gcb_on_topic_subscribe(client, GCB_PROTOCOL_TOPIC)
    # Flag passed from app module, so MQTT client doesn't run infinitely on app shutdown.
    while not main_execution_flag.is_set():
        client.loop(0.1)
    client.disconnect()


def get_data_by_id(id):
    """
    Function to fetch data from protocol_data_entity table based on the received id.

    Parameters
    ----------
    id : int
        Protocol data identifier.

    Returns
    -------
    results : ProtocolDataEntity
        ProtocolDataEntity object which has unique id parameter.
    """
    session = connect_to_database()
    try:
        result = session.query(ProtocolDataEntity).filter_by(id=id).first()
    finally:
        session.close()

    return result


def send_update_protocol_request():
    """
    Start Protocol MQTT startup publisher client which sends MQTT request to the cloud to get updated protocol data.

    Parameters
    ----------
    config : Config
        Enables reading parameters from config file.
    """
    config = Config(CONF_PATH, errorLogger, customLogger)
    config.try_open()
    client = mqtt_util.gcb_init_publisher("startup-protocol-client-id",
                                          config.gateway_cloud_broker_iot_username,
                                          config.gateway_cloud_broker_iot_password)
    mqtt_util.gcb_connect(client, config.gateway_cloud_broker_address, config.gateway_cloud_broker_port)
    client.publish("gateway/protocol-startup", "", 2)
    client.loop_start()
    # Without sleep client disconnects too fast and doesn't send MQTT message, must be a thread
    time.sleep(1)
    client.loop_stop()
    client.disconnect()


def start_protocol_mqtt(main_execution_flag):
    """
    Start Protocol MQTT startup module, function called from app module.

    Parameters
    ----------
    main_execution_flag : Event
        Indicator for termination request for main loop.
    """
    # Create database structure if it doesn't exist.
    set_up_database()
    config = Config(CONF_PATH, errorLogger, customLogger)
    config.try_open()
    # Start threads for MQTT clients.
    thread1 = threading.Thread(target=start_protocol_client, args=(config, main_execution_flag, ))
    thread2 = threading.Thread(target=send_update_protocol_request, args=())
    thread1.start()
    thread2.start()
    thread2.join()
    thread1.join()
