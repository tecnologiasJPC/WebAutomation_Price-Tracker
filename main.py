from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as ch
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import sqlite3
import time
import os
import sys
import numpy as np

# link for the product to be monitored
ruta = "https://www.mercadolibre.com.mx/motocicleta-chopper-italika-tc-300-negra/up/MLMU3007051693"


def save_data(date: str, price: int):   # save the data in a database file
    data = os.path.join(os.path.dirname(__file__), 'datos.db')  # it is required to define absolute path
    connection = sqlite3.connect(data)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS motocicleta(fecha TEXT,precio INTEGER)")
    cursor.execute("INSERT INTO motocicleta (fecha, precio) VALUES (?, ?)", (date, price))
    connection.commit()
    connection.close()


def open_webpages():    # open the webpage to get the price of the product in MercadoLibre
    moment = datetime.datetime.now()
    date = str(moment).split('.')[0]
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--windows-size=1280,720")
    #options.add_argument("--headless")
    driver = ch.Chrome(options=options, version_main=144)
    driver.get(ruta)
    wait = WebDriverWait(driver, 10)
    try:
        wait.until(ec.presence_of_element_located((By.CLASS_NAME, "ui-pdp-price__second-line")))
        element = driver.find_element(By.CLASS_NAME, "ui-pdp-price__second-line")
        price = element.text.split('\n')[1].replace(',', '')
        print(f"This is current price ${int(price)} at {date}")
        save_data(date, int(price))
    except TimeoutError:
        print(f"El tiempo de espera se excedio")
    finally:
        driver.quit()


def graph_data():
    data = os.path.join(os.path.dirname(__file__), 'datos.db')
    conn = sqlite3.connect(data)

    table = 'motocicleta'
    query = f"SELECT * FROM {table}"
    df = pd.read_sql_query(query, conn)
    conn.close()

    x_ax = []
    y_ax = []
    for f in range(len(df['fecha'])):
        if f == 0:
            x_ax.append(df['fecha'][f].split(' ')[0])
            y_ax.append(df['precio'][f])
        else:
            prev = df['fecha'][f-1].split(' ')[0]
            now = df['fecha'][f].split(' ')[0]
            if prev != now:
                x_ax.append(now)
                y_ax.append(df['precio'][f])

    plt.plot(x_ax, y_ax, label='Price data')
    plt.xlabel('date')
    plt.xticks(rotation=90)
    plt.ylabel('price')
    plt.title(f'Chart of price')
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    #open_webpages()
    graph_data()
