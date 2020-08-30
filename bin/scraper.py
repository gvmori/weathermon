#!/usr/bin/env python3.8

import requests
from bs4 import BeautifulSoup
import sqlite3
import dateutil.parser
import datetime
from contextlib import closing
import configparser
import os

def main():    
    xml = get_xml()
    bs = BeautifulSoup(xml, 'lxml-xml')

    initial_dt = dateutil.parser.parse(
        bs.griddedForecast.forecastCreationTime.get_text().strip()
    )

    # current_dt = datetime.datetime.now(datetime.timezone.utc)
    default_dt = datetime.datetime(day=initial_dt.day, month=initial_dt.month, year=initial_dt.year)
    periods = []

    for day in bs.find_all('forecastDay'):
        date_text = day.validDate.get_text().strip()
        if date_text == 'Jan 01' and initial_dt.month != 1:
            default_dt = datetime.datetime(day=initial_dt.day, month=initial_dt.month, year=initial_dt.year + 1)

        date = dateutil.parser.parse(date_text, default=default_dt)

        day_periods = parse_periods(date, day)
        periods.extend(day_periods)

    load_data(periods)


def get_xml():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'scraper.ini'))

    url = f"https://www.wrh.noaa.gov/forecast/xml/xml.php?duration={config['url_params']['duration']}&interval={config['url_params']['interval']}&lat={config['url_params']['lat']}&lon={config['url_params']['lon']}"

    response = requests.get(url)
    if not response.ok:
        raise Exception(f'Unable to get url {url}: {response.status_code} {response.reason}')

    return response.text


def parse_periods(date, day):
    periods = []
    for period in day.find_all('period'):
        if period.temperature.get_text().strip() == "-999":
            continue
        period_dt = date.replace(hour=int(period.validTime.get_text().strip()))

        parsed_period = (
            int(period_dt.timestamp()),
            int(period.temperature.get_text().strip()),
            int(period.dewpoint.get_text().strip()),
            int(period.rh.get_text().strip()),
            int(period.skyCover.get_text().strip()),
            int(period.windSpeed.get_text().strip()),
            int(period.windDirection.get_text().strip()),
            int(period.windGust.get_text().strip()),
            int(period.pop.get_text().strip()),
            float(period.qpf.get_text().strip()),
            float(period.snowAmt.get_text().strip()),
            int(period.snowLevel.get_text().strip()),
        )

        periods.append(parsed_period)

    return periods


def load_data(periods):
    del_sql = "delete from weather"

    load_sql = """
        INSERT INTO weather
        VALUES 
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    with closing(sqlite3.connect('weathermon.db')) as conn:
        cursor = conn.cursor()
        cursor.execute(del_sql)
        cursor.executemany(load_sql, periods)
        conn.commit()


if __name__ == '__main__':
    main()
