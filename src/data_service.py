"""Data service utilities.

data_services
============
Module containing logic for sending collected and processed data to cloud services.

Functions
---------
handle_temperature_data(data, url, jwt, time_format)
    Summarizing collected temperature data and forwarding result to cloud service.
handle_load_data(data, url, jwt, time_format)
    Summarizing load temperature data and forwarding result to cloud service.
handle_fuel_data(data, limit, url, jwt, time_format)
    Filtering collected temperature data and forwarding result to cloud service.
parse_incoming_data(data, type)
    Parsing all types of data that come from sources

Constants
---------
DATA_PATTERN
    Request body data pattern.

QOS
    Quality of Service of MQTT broker.
TEMP_ALARM_TOPIC: str
    MQTT alarm topic for temperature alarms.
LOAD_ALARM_TOPIC: str
    MQTT alarm topic for load alarms.
FUEL_ALARM_TOPIC: str
    MQTT alarm topic for fuel alarms.
EMPTY_PAYLOAD: dict
    Empty dictionary that is returned if there is some kind of error
    in data processing.
"""
import time
import sys
import re
import ast
import logging.config

logging.config.fileConfig('logging.conf')
errorLogger = logging.getLogger('customErrorLogger')
customLogger = logging.getLogger('customConsoleLogger')

DATA_PATTERN = "[ value={} , time={} , unit={} ]"

QOS = 2
TEMP_ALARM_TOPIC = "alarms/temperature"
LOAD_ALARM_TOPIC = "alarms/load"
FUEL_ALARM_TOPIC = "alarms/fuel"

EMPTY_PAYLOAD = {}


def parse_incoming_data(data, data_type):
    """
    Parsing all types of data that come from sources

    Args:
    ----
        data: str
            Data to be parsed
        data_type: str
            Data type (Temperature, Load, Fuel) for console output

    Returns:
    -------
        data_sum: double
            Parsed data value
        unit: str
            Unit of the parsed data
    """
    data_sum = 0.0
    # summarizing collected data
    try:
        tokens = data.split(" ")
        data_sum += float(tokens[1].split("=")[1])
    except BaseException:
        errorLogger.error("Invalid " + data_type + " data format! - " + data)
    unit = "unknown"
    try:
        unit = data.split(" ")[6].split("=")[1]
    except BaseException:
        errorLogger.error("Invalid " + data_type + " data format! - " + data)
    return data_sum, unit


def handle_protocol_data(data, time_format):
    """
    Processes protocol data and generates a summarized payload based on the aggregation method.

    Extracts relevant values from the data and applies transformations based on the
    provided protocol parameters. Computes summary statistics (average, sum, min, max)
    of the processed data values and returns a payload including the aggregated result
    and the current time.

    Parameters
    ----------
    data: list of str
        List containing protocol data, where each element is a string representation
        of the data in a specific format.
    time_format: str
        Time format string to format the current time according to the requirements
        of the cloud services.

    Returns
    -------
    payload: dict
        Dictionary containing the aggregated result and the current time. The structure
        of the dictionary varies based on the specified aggregation method.
    """
    # Extract tuple from received data
    match = re.search(r"data=\((.*)\)", data[0])
    data_str = "(" + match.group(1) + ")"
    data_tuple = ast.literal_eval(data_str)

    id = data_tuple[0]
    aggregation_method = data_tuple[1]
    divisor = data_tuple[3]
    multiplier = data_tuple[5]
    offset = data_tuple[8]
    data_sum = 0
    max_value = sys.float_info.min
    min_value = sys.float_info.max
    # For each info in data apply operations extracted from the database
    for info in data:
        data_value, parsed_unit = parse_incoming_data(str(info), "protocol_data")
        data_sum += offset
        if multiplier > 0:
            data_value *= multiplier
        if divisor > 0:
            data_value /= divisor
        if data_value > max_value:
            max_value = data_value
        if data_value < min_value:
            min_value = data_value

    time_value = time.strftime(time_format, time.localtime())

    # Considering aggregation method return result
    match aggregation_method:
        case 'AVG':
            return {"dataId":id, "value": round(data_sum / len(data), 2), "time": time_value}
        case 'SUM':
            return {"dataId":id, "value": data_sum, "time": time_value}
        case 'MIN':
            return {"dataId":id, "value": min_value, "time": time_value}
        case 'MAX':
            return {"dataId":id, "value": max_value, "time": time_value}


def handle_temperature_data(data, time_format):
    """
    Summarizes collected temperature data and forms payload.

    Triggered periodically.

    Parameters
    ----------
    data: list
        Collected temperature data.
    time_format: str
        Cloud services' time format.

    Returns
    -------
    payload: dict
    """
    data_sum = 0.0
    unit = "Unknown"
    for info in data:
        data_value, parsed_unit = parse_incoming_data(info, "temperature")
        unit = parsed_unit
        data_sum += data_value

    time_value = time.strftime(time_format, time.localtime())
    payload = {"value": round(data_sum / len(data), 2), "time": time_value, "unit": unit}
    return payload


def handle_load_data(data, time_format):
    """
    Summarizes collected load data and forms payload.

    Triggered periodically  (variable interval).

    Parameters
    ----------
    data: list
        Collected load data.
    time_format: str
        Cloud services' time format.

    Returns
    -------
    payload: dict
    """
    data_sum = 0.0
    unit = "Unknown"
    for info in data:
        data_value, parsed_unit = parse_incoming_data(info, "load")
        unit = parsed_unit
        data_sum += data_value

    time_value = time.strftime(time_format, time.localtime())
    payload = {"value": round(data_sum, 2), "time": time_value, "unit": unit}
    return payload


def handle_fuel_data(data, limit, time_format, alarm_client):
    """

    Summarizes collected fuel, forms payload and sends alarm.

    Triggered periodically.

    Parameters
    ----------
    data: list
     Collected load data.
    limit: double
     Critical fuel level.
    time_format: str
     Cloud services' time format.
    alarm_client: MQTTClient
     MQTT broker alarm client

    Returns
    -------
    http status code
    """
    value, unit = parse_incoming_data(str(data), "fuel")
    if value == 0.0:
        return EMPTY_PAYLOAD
    if value <= limit:
        customLogger.info("Fuel is below the designated limit! Sounding the alarm")
        alarm_client.publish(FUEL_ALARM_TOPIC, True, QOS)

    time_value = time.strftime(time_format, time.localtime())

    payload = {"value": round(value, 2), "time": time_value, "unit": unit}
    return payload
