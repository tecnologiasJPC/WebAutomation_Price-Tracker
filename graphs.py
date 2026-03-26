import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
import os

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
    plt.title(f'Chart of price for {table}')
    plt.tight_layout()
    plt.grid(True)
    plt.show()

graph_data('ram')

