"""Data service utilities.

data_services
============
Module containing logic for sending collected and processed data to cloud services.

Functions
---------
handle_protocol_data(protocol_data_entity, data, time_format)
    Summarizing collected protocol data and forwarding result to cloud service.

Constants
---------
EMPTY_PAYLOAD: dict
    Empty dictionary that is returned if there is some kind of error
    in data processing.
"""
import time
import sys
import logging.config

logging.config.fileConfig('logging.conf')
errorLogger = logging.getLogger('customErrorLogger')
customLogger = logging.getLogger('customConsoleLogger')

EMPTY_PAYLOAD = {}


def handle_protocol_data(protocol_data_entity, data, time_format):
    """
    Processes protocol data and generates a summarized payload based on the aggregation method.

    Extracts relevant values from the data and applies transformations based on the
    provided protocol parameters. Computes summary statistics (average, sum, min, max)
    of the processed data values and returns a payload including the aggregated result
    and the current time.

    Parameters
    ----------
    protocol_data_entity: ProtocolDataEntity
        Object containing information for handling data.
    data: list of float
        List containing float values.
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
    data_sum = 0
    max_value = sys.float_info.min
    min_value = sys.float_info.max
    # For each info in data apply operations extracted from the database
    for value in data:
        value += protocol_data_entity.offset_value
        if protocol_data_entity.multiplier > 0:
            value *= protocol_data_entity.multiplier
        if protocol_data_entity.divisor > 0:
            value /= protocol_data_entity.divisor
        if value > max_value:
            max_value = value
        if value < min_value:
            min_value = value
        data_sum += value

    time_value = time.strftime(time_format, time.localtime())

    # Considering aggregation method return result
    match protocol_data_entity.aggregation_method:
        case 'AVG': return {"dataId": protocol_data_entity.id, "value": round(data_sum / len(data), 2),
                            "time": time_value}
        case 'SUM': return {"dataId": protocol_data_entity.id, "value": data_sum, "time": time_value}
        case 'MIN': return {"dataId": protocol_data_entity.id, "value": min_value, "time": time_value}
        case 'MAX': return {"dataId": protocol_data_entity.id, "value": max_value, "time": time_value}
