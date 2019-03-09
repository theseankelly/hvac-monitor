import os
import sqlite3

class Database:
    """
    Helper for acessing the database backing the HVAC Monitor.

    Methods
    -------
    __init__(filepath='/var/lib/hvacmon', filename='hvacmon.db')
        Initializes the object and creates the database tables (if needed).
    append_zone_data(starttime, endtime, zoneinfo)
        Inserts a zoneinfo entry into the database.
    append_temperature_data(timestamp, temperature)
        Inserts a temperature entry into the database.
    """
    def __init__(self, filepath='/var/lib/hvacmon', filename='hvacmon.db'):
        """
        Initializes the object.

        Parameters
        ----------
        filepath : str
            Location on the filesystem where the database is stored.

        filename : str
            Name of the SQLite3 database file at the location described by
            `filepath`.
        """
        self._filename = os.path.join(filepath, filename)

        # Create the tables if they don't already exist
        with sqlite3.connect(self._filename) as db:
            cursor = db.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS "zone_readings"(
                    starttime TEXT, endtime TEXT,
                    one_call INTEGER, one_valve INTEGER,
                    two_call INTEGER, two_valve INTEGER,
                    three_call INTEGER, three_valve INTEGER,
                    four_call INTEGER, four_valve INTEGER)''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS "temperature_readings"(
                    timestamp TEXT, temperature REAL)''')
            db.commit()

    def append_zone_data(self, starttime, endtime, zoneinfo):
        """
        Inserts a zoneinfo entry into the database.

        Parameters
        ----------
        starttime : str
            Timestamp describing when this HVAC status began

        starttime : str
            Timestamp describing when this HVAC status ended

        zoneinfo : 4x2 numpy.ndarray
            Array of status indicators where each row is a zone.
            The first column indicates whether the thermostat is calling.
            The second column indicates whether the zone valve is open.
        """
        with sqlite3.connect(self._filename) as db:
            cursor = db.cursor()
            cursor.execute('''
                INSERT INTO zone_readings(starttime, endtime,
                                          one_call, one_valve,
                                          two_call, two_valve,
                                          three_call, three_valve,
                                          four_call, four_valve)
                VALUES(?,?,?,?,?,?,?,?,?,?)''',
                (str(starttime), str(endtime),
                 int(zoneinfo[0,0]), int(zoneinfo[0,1]),
                 int(zoneinfo[1,0]), int(zoneinfo[1,1]),
                 int(zoneinfo[2,0]), int(zoneinfo[2,1]),
                 int(zoneinfo[3,0]), int(zoneinfo[3,1])))
            db.commit()

    def append_temperature_data(self, timestamp, temperature):
        """
        Inserts a temperature entry into the database.

        Parameters
        ----------
        timestamp : str
            Time at which the temperature reading was obtained.

        temperature : float
            Temperature reading in degrees F.
        """
        with sqlite3.connect(self._filename) as db:
            cursor = db.cursor()
            cursor.execute('''
                INSERT INTO temperature_readings(timestamp, temperature)
                VALUES(?,?)''', (str(timestamp), float(temperature)))
            db.commit()
