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
"""
import logging.config
from src.config_util import Config, CONF_PATH
import src.mqtt_util as mqtt_util
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.protocol_classes import ProtocolEntity, ProtocolDataEntity, set_up_database, create_database_engine

logging.config.fileConfig('logging.conf')
errorLogger = logging.getLogger('customErrorLogger')
customLogger = logging.getLogger('customConsoleLogger')

TRANSPORT_PROTOCOL = "tcp"
GCB_PROTOCOL_TOPIC = "gateway/protocol"


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
        # Delete protocols
        session.query(ProtocolEntity).filter(ProtocolEntity.id.in_(protocol_ids)).delete(synchronize_session=False)
        session.commit()
    except Exception:
        # Rollback the transaction in case of error
        session.rollback()
    finally:
        session.close()


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
