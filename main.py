from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
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

products = {'motorcycle': "https://www.mercadolibre.com.mx/motocicleta-chopper-italika-tc-300-negra/up/MLMU3007051693",
            'ram': "https://www.mercadolibre.com.mx/memoria-ram-ddr5-16gb-5600mts-kingston-fury-impact-1x16gb-laptop-negro-kf556s40ib-16/p/MLM25390982"}


def save_data(product: str, date: str, price: int):   # save the data in a database file
    data = os.path.join(os.path.dirname(__file__), 'datos.db')  # it is required to define absolute path
    connection = sqlite3.connect(data)
    cursor = connection.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {product}(fecha TEXT, precio INTEGER)")
    cursor.execute(f"INSERT INTO {product} (fecha, precio) VALUES (?, ?)", (date, price))
    connection.commit()
    connection.close()


def graph_data(table):
    data = os.path.join(os.path.dirname(__file__), 'datos.db')
    conn = sqlite3.connect(data)

    query = f"SELECT * FROM {table}"
    df = pd.read_sql_query(query, conn)
    conn.close()

    x_ax, y_ax = [], []
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


class BasePage:

    def __new__(cls, driver, liga):
        if 'mercadolibre.com' in liga:
            return super(BasePage, MercadoLibrePage).__new__(MercadoLibrePage)
        elif 'amazon.com' in liga:
            return super(BasePage, AmazonPage).__new__(AmazonPage)
        return super(BasePage, cls).__new__(cls)

    def __init__(self, driver, liga):
        self.__driver = driver
        self.__wait = WebDriverWait(driver, 3)
        self.link = liga
        self.open_page(liga)

    def open_page(self, link):
        self.__driver.get(link)

    def find_element(self, method, name):
        try:
            return self.__wait.until(EC.presence_of_element_located((method, name)))
        except TimeoutException:
            print(f"Element {name} is not found")
            return None

    def close_page(self):
        self.__driver.close()

    def close_browser(self):
        self.__driver.quit()


class MercadoLibrePage(BasePage):
    __locator = By.CLASS_NAME
    __name = "ui-pdp-price__second-line"

    def get_price(self):
        super().open_page(self.link)
        text_price = super().find_element(self.__locator, self.__name)
        if text_price is None:
            return None
        else:
            return text_price.text.split('\n')[1].replace(',', '')


class AmazonPage(BasePage):
    __locator = By.CLASS_NAME
    __name = "a-price-whole"

    def get_price(self):
        super().open_page(self.link)
        super().find_element(By.CLASS_NAME, "a-button-text").click()
        text_price = super().find_element(self.__locator, self.__name)
        return text_price.text.replace(',', '')


if __name__ == '__main__':
    #open_webpages()
    #graph_data(list(products.keys())[0])
    #sys.exit()

    items = list(products.keys())
    options = webdriver.ChromeOptions()
    driver = ch.Chrome(options=options, version_main=144)
    driver.maximize_window()

    for item in items:
        pag1 = BasePage(driver, products[item])
        price = pag1.get_price()
        moment = datetime.datetime.now()
        date = str(moment).split('.')[0]
        if price is not None:
            print(f"For {item} in {date} the price is ${price}")
            save_data(item, date, int(price))
        else:
            print(f"Product {item} not available")
        time.sleep(3)
    pag1.close_browser()

