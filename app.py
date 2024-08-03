from flask import Flask, render_template_string
import requests
import pandas as pd
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)

@app.route('/')
def index():
    # Endpoints de las APIs
    usdt_url = "https://criptoya.com/api/usdt/ars"
    dolar_url = "https://criptoya.com/api/dolar"

    # Obtener datos de la API de USDT
    response_usdt = requests.get(usdt_url)
    data_usdt = response_usdt.json()
    df_usdt = pd.DataFrame(data_usdt).T
    df_usdt = df_usdt[['ask']]

    # Obtener datos de la API del dólar
    response_dolar = requests.get(dolar_url)
    data_dolar = response_dolar.json()
    tipos_dolar = ['CCL', 'Tarjeta', 'MEP']
    df_dolar = pd.DataFrame({k: data_dolar[k] for k in tipos_dolar}).T
    df_dolar = df_dolar[['ask']]

    # Visualización
    fig_usdt = px.bar(df_usdt, x=df_usdt.index, y='ask', title='Precio de compra de USDT en diferentes exchanges')
    fig_dolar = px.bar(df_dolar, x=df_dolar.index, y='ask', title='Precio de compra de diferentes tipos de dólar')

    # Convertir las figuras a HTML
    usdt_plot_html = pio.to_html(fig_usdt, full_html=False)
    dolar_plot_html = pio.to_html(fig_dolar, full_html=False)

    # Renderizar los gráficos en una página HTML
    html = f"""
    <html>
    <head><title>Dashboard</title></head>
    <body>
    <h1>Dashboard</h1>
    <h2>Precio de compra de USDT en diferentes exchanges</h2>
    {usdt_plot_html}
    <h2>Precio de compra de diferentes tipos de dólar</h2>
    {dolar_plot_html}
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
