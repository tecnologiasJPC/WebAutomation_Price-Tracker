from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime
import tkinter as tk

ruta = "https://www.hayabusafight.com/products/hayabusa-ascend-lightweight-jiu-jitsu-gi?variant=37799664943286"

if __name__ == '__main__':
    tiempo1 = datetime.datetime.now()
    print(f'Probando selenium en {tiempo1}')
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--windows-size=1280,720")
    driver = Chrome(service=service, options=options)
    driver.get(ruta)
    elemento = driver.find_element(By.ID, "add_to_cart")
    texto = elemento.text
    print(f'Texto obtenido {texto}')
    if "ADD TO CART" in texto:
        print('Hay piezas disponibles')
        root = tk.Tk()
        root.title("Stock disponible")
        root.geometry("260x60")
        etiqueta = tk.Label(root, text="Ya hay Gis disponibles")
        etiqueta.pack(pady=20, padx=20)
        root.mainloop()
    elif "SOLD OUT" in texto:
        print('No hay piezas disponibles')
    else:
        print('No se reconoce texto')
    time.sleep(3)
    driver.quit()
    tiempo2 = datetime.datetime.now()
    delta = tiempo2 - tiempo1
    print(f'Tiempo de ejecucion total {delta}')
