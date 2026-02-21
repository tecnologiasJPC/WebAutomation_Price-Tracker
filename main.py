from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException
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
            'celular': "https://www.mercadolibre.com.mx/asus-rog-phone-9-pro-negro-512gb-16gb-celular-snapdragon-8-elite-telefono-5g-dual-sim-185-hz-gamer-phone-con-gatillos-5800mah-smartphone-android-15/p/MLM46935405",
            'ram': "https://www.amazon.com.mx/Kingston-Impact-Memoria-Laptop-Capacidad/dp/B09T95TJ1M",
            'backpack': "https://www.amazon.com.mx/dp/B074PYX59S"}

alis = ["https://es.aliexpress.com/item/1005002527423374.html?spm=a2g0o.order_list.order_list_main.11.19b1194dhpuB3C&gatewayAdapt=glo2esp",
        "https://es.aliexpress.com/item/1005009592843268.html?spm=a2g0o.order_list.order_list_main.4.27ae194d7aRR4p&gatewayAdapt=glo2esp"]

route = "https://es.aliexpress.com/item/1005002527423374.html?spm=a2g0o.order_list.order_list_main.11.19b1194dhpuB3C&gatewayAdapt=glo2esp"
route2 = "https://es.aliexpress.com/item/1005009592843268.html?spm=a2g0o.order_list.order_list_main.4.27ae194d7aRR4p&gatewayAdapt=glo2esp"


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
    plt.title(f'Chart of {table}')
    plt.tight_layout()
    plt.grid(True)
    plt.show()


class BasePage:

    @staticmethod
    def web_page(driv, liga):
        if 'mercadolibre.com' in liga:
            return MercadoLibrePage(driv, liga)
        elif 'amazon.com' in liga:
            return AmazonPage(driv, liga)
        elif 'aliexpress.com' in liga:
            return AliexpressPage(driv, liga)
        else:
            return BasePage(driv, liga)

    def __new__(cls, driver, liga):
        if 'mercadolibre.com' in liga:
            return super(BasePage, MercadoLibrePage).__new__(MercadoLibrePage)
        elif 'amazon.com' in liga:
            return super(BasePage, AmazonPage).__new__(AmazonPage)
        elif 'aliexpress.com' in liga:
            return super(BasePage, AliexpressPage).__new__(AliexpressPage)
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
        button = super().find_element(By.CLASS_NAME, "a-button-text")

        if button is not None:
            try:
                button.click()
            except ElementClickInterceptedException:
                pass
        text_price = super().find_element(self.__locator, self.__name)
        return text_price.text.replace(',', '')


class AliexpressPage(BasePage):
    __locator = By.CSS_SELECTOR
    __name = "span.price-default--original--CWcHOit"

    def get_price(self):
        super().open_page(self.link)
        span_price = super().find_element(self.__locator, self.__name)
        BDI = span_price.find_element(By.TAG_NAME, "bdi")
        decimal_value = BDI.text.split('$')[1].replace(',', '')
        integer_value = int(round(float(decimal_value)))
        return str(integer_value)

if __name__ == '__main__':
    #open_webpages()
    #graph_data(list(products.keys())[2])
    #sys.exit()

    items = list(products.keys())
    options = webdriver.ChromeOptions()
    driver = ch.Chrome(options=options, version_main=144)
    driver.maximize_window()

    for ali in alis:
        pagina = BasePage.web_page(driver, ali)
        texto = pagina.get_price()
        print(f"Este es el precio obtenido {texto}")
    driver.quit()
    sys.exit()

    for item in items:
        page = BasePage.web_page(driver, products[item])
        price = page.get_price()
        moment = datetime.datetime.now()
        date = str(moment).split('.')[0]
        if price is not None:
            print(f"For {item} in {date} the price is ${price}")
            save_data(item, date, int(price))
        else:
            print(f"Product {item} not available")
        time.sleep(3)
    page.close_browser()

