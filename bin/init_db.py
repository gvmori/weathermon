#!/usr/bin/env python3.8

import sqlite3
from contextlib import closing

def main():
    create_statement = """
        CREATE TABLE weather
        (
            dt integer UNIQUE,
            temperature integer,
            dewpoint integer,
            humidity integer,
            sky_cover integer,
            wind_speed integer,
            wind_direction integer,
            wind_gust integer,
            pop integer,
            qpf real,
            snow_amount real,
            snow_level integer
        )
    """

    with closing(sqlite3.connect('weathermon.db')) as conn:
        cursor = conn.cursor()
        cursor.execute(create_statement)
        conn.commit()

if __name__ == '__main__':
    main()
