import sqlite3
import pytest


from classes.equipment import Equipment
from classes.operator import Operator
from classes.equipment_operator import Equipment_Operator
from classes.maintenance_event import Maintenance_event
from classes.maintenance_type import Maintenance_Type

@pytest.fixture
def db():
    """Opens a connection to your database file."""
    conn = sqlite3.connect('data/equipment_management.db')
    cursor = conn.cursor()
    yield cursor
    conn.close()

def test_equipment(db):
    db.execute("SELECT id, name, model FROM equipment LIMIT 1")
    row = db.fetchone()
    if row:
        obj = Equipment(id=row[0], name=row[1], model=row[2])
        assert obj.id == row[0]
        assert obj.name == row[1]

def test_operator(db):
    db.execute("SELECT id, name FROM operator LIMIT 1")
    row = db.fetchone()
    if row:
        obj = Operator(id=row[0], name=row[1])
        assert obj.id == row[0]
        assert obj.name == row[1]

def test_equipment_operator(db):
    db.execute("SELECT equipment_id, operator_id FROM equipment_operator LIMIT 1")
    row = db.fetchone()
    if row:
        obj = Equipment_Operator(equipment_id=row[0], operator_id=row[1])
        assert obj.equipment_id == row[0]
        assert obj.operator_id == row[1]

def test_maintenance_event(db):
    db.execute("SELECT id, equipment_id, date FROM maintenance_event LIMIT 1")
    row = db.fetchone()
    if row:
        obj = Maintenance_Event(id=row[0], equipment_id=row[1], date=row[2])
        assert obj.id == row[0]
        assert obj.equipment_id == row[1]

def test_maintenance_type(db):
    db.execute("SELECT id, description FROM maintenance_type LIMIT 1")
    row = db.fetchone()
    if row:
        obj = Maintenance_Type(id=row[0], description=row[1])
        assert obj.description == row[1]
