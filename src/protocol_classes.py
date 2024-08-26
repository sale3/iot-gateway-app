"""
protocol_classes
============
Module that provides protocol and protocol data classes to work with SQLAlchemy, as well as creating database if it
doesn't exist.

Classes
---------
    ProtocolEntity: A class that represents entities stored in protocol_entity table in SQLite database.
    ProtocolDataEntity: A class that represents entities stored in protocol_data_entity table in SQLite database.

Functions
---------
create_database_engine(db_folder, db_filename)
    Function that creates and returns an SQLAlchemy engine connected to the specified SQLite database.
set_up_database()
    Function that creates all tables in the SQLite database if they do not already exist.
"""
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import os

Base = declarative_base()


class ProtocolEntity(Base):
    """
    A class that represents entities stored in protocol_entity table in SQLite database.

    Attributes
    ----------
    id : int
        Primary key for the protocol entity.
    name : str
        Name of the protocol entity. Must be unique.
    assigned : int
        Status of the protocol entity, should be either 0 or 1.

    Table Constraints
    -----------------
    - The `assigned` column must have a value of either 0 or 1 (check constraint).
    """
    __tablename__ = 'protocol_entity'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    assigned = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint('assigned IN (0, 1)', name='check_assigned'),
    )


class ProtocolDataEntity(Base):
    """
    A class that represents entities stored in protocol_data_entity table in SQLite database.

    Attributes
    ----------
    id : int
        Primary key for the protocol data entity.
    aggregation_method : str
        Method of aggregation used for protocol data.
    can_id : int
        CAN ID associated with the protocol data.
    divisor : int
        Divisor used in the protocol data.
    mode : str
        Mode of operation for the protocol data.
    multiplier : int
        Multiplier used in the protocol data.
    name : str
        Name of the protocol data entity.
    num_bits : int
        Number of bits in the protocol data.
    offset_value : int
        Offset value used in the protocol data.
    start_bit : int
        Starting bit position for the protocol data.
    transmit_interval : int
        Interval for transmitting protocol data.
    unit : str
        Unit of measurement for the protocol data.
    protocol : int
        Foreign key referencing the id in protocol_entity, linking the protocol data to a specific protocol.

    Relationships
    --------------
    protocol_entity : ProtocolEntity
        Reference to the ProtocolEntity instance associated with this protocol data entity.
    """
    __tablename__ = 'protocol_data_entity'

    id = Column(Integer, primary_key=True, autoincrement=True)
    aggregation_method = Column(String, nullable=False)
    can_id = Column(Integer, nullable=False)
    divisor = Column(Integer, nullable=False)
    mode = Column(String, nullable=False)
    multiplier = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    num_bits = Column(Integer, nullable=False)
    offset_value = Column(Integer, nullable=False)
    start_bit = Column(Integer, nullable=False)
    transmit_interval = Column(Integer, nullable=False)
    unit = Column(String)
    protocol = Column(Integer, ForeignKey('protocol_entity.id', ondelete='CASCADE'), nullable=False)
    protocol_entity = relationship('ProtocolEntity', backref='protocol_data')


def create_database_engine(db_folder='database', db_filename='modular-protocols.db'):
    """
    Function that creates and returns an SQLAlchemy engine connected to the specified SQLite database.

    Parameters
    ----------
    db_folder : str
        Folder where the SQLite database file will be located.
    db_filename : str
        Name of the SQLite database file.

    Returns
    -------
    : sqlalchemy.engine.base.Engine
        SQLAlchemy engine connected to the database.
    """

    # Ensure the database folder exists
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)

    # Construct the full path to the database file
    db_url = f'sqlite:///{os.path.join(db_folder, db_filename)}'
    engine = create_engine(db_url, echo=True)
    return engine


def set_up_database():
    """
    Function that creates all tables in the SQLite database if they do not already exist.

    Returns
    -------
    None
    """
    engine = create_database_engine()
    Base.metadata.create_all(engine)
