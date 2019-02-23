import sqlite3


def append_zone_data(starttime, endtime, zoneinfo):

    with sqlite3.connect('/home/pi/databases/hvacmon.db') as db:
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO zone_readings(starttime, endtime, one_call, one_valve, two_call,
                                      two_valve, three_call, three_valve,
                                      four_call, four_valve)
            VALUES(?,?,?,?,?,?,?,?,?,?)''', (starttime, endtime,
                                             zoneinfo[0,0], zoneinfo[0,1],
                                             zoneinfo[1,0], zoneinfo[1,1],
                                             zoneinfo[2,0], zoneinfo[2,1],
                                             zoneinfo[3,0], zoneinfo[3,1]))
        db.commit()
