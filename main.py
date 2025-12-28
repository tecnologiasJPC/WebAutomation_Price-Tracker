import time
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as ch
import datetime
import sqlite3

ruta = "https://www.mercadolibre.com.mx/motocicleta-chopper-italika-tc-300-negra/up/MLMU3007051693"


def guardar_datos(date: str, price: int):
    conexion = sqlite3.connect('C:/Users/john_/Documents/TrackingPrices/datos.db')
    cursor = conexion.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS motocicleta(
    fecha TEXT,
    precio INTEGER
    )
    ''')
    cursor.execute("INSERT INTO motocicleta (fecha, precio) VALUES (?, ?)", (date, price))
    conexion.commit()
    conexion.close()


def time_taken(func):
    def wrapper():
        t1 = time.time()
        func()
        t2 = time.time()
        dt = t2 - t1
        print(f"Este proceso requirio de {int(dt)} segundos")
    return wrapper


@time_taken
def open_webpages():
    tiempo = datetime.datetime.now()
    fecha = str(tiempo).split('.')[0]
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--windows-size=1280,720")
    # options.add_argument("--headless")
    # driver = Chrome(service=service, options=options)
    driver = ch.Chrome(options=options)
    driver.get(ruta)
    time.sleep(2)
    elemento = driver.find_element(By.CLASS_NAME, "ui-pdp-price__second-line")
    precio = elemento.text.split('\n')[1].replace(',', '')
    print(f"Este es el precio obtenido {int(precio)} en {fecha}")
    guardar_datos(fecha, int(precio))
    driver.quit()


if __name__ == '__main__':
    open_webpages()
    print("Proceso conluido")
