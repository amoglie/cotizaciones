from flask import Flask, render_template_string, jsonify
import requests
import pandas as pd
import plotly.express as px
import plotly.io as pio
import logging
from pycoingecko import CoinGeckoAPI

app = Flask(__name__)
cg = CoinGeckoAPI()

# Configuración de registros
logging.basicConfig(level=logging.INFO)

def get_crypto_data():
    try:
        # Obtener las 10 principales criptomonedas por capitalización de mercado
        coins = cg.get_coins_markets(vs_currency='usd', order='market_cap_desc', per_page=10, page=1, sparkline=False)
        
        # Crear un DataFrame con los datos relevantes
        df_crypto = pd.DataFrame(coins)[['name', 'image', 'current_price', 'price_change_percentage_24h']]
        df_crypto.columns = ['Nombre', 'Logo', 'Precio (USD)', 'Cambio 24h (%)']
        
        return df_crypto
    except Exception as e:
        logging.error(f"Error al obtener datos de criptomonedas: {e}")
        return pd.DataFrame()

def get_usdt_data():
    try:
        # Obtener datos de la API de criptoya
        response = requests.get("https://criptoya.com/api/usdt/ars")
        data = response.json()
        
        # Opciones permitidas
        opciones_permitidas = [
            'lemoncash', 'belo', 'fiwind', 'buenbit', 'bybit', 
            'tiendacrypto', 'letsbit', 'cocos crypto', 'ripio', 'binance'
        ]
        
        # Crear DataFrame con los datos relevantes
        df = pd.DataFrame([(exchange, info['ask'], info['bid']) 
                           for exchange, info in data.items() 
                           if isinstance(info, dict) and 'ask' in info and 'bid' in info and exchange in opciones_permitidas],
                          columns=['Exchange', 'Compra (ARS)', 'Venta (ARS)'])
        
        # Identificar mejores opciones
        mejor_compra = df.loc[df['Compra (ARS)'].idxmin()]
        mejor_venta = df.loc[df['Venta (ARS)'].idxmax()]
        
        return df, mejor_compra, mejor_venta
    except Exception as e:
        logging.error(f"Error al obtener datos de USDT: {e}")
        return pd.DataFrame(), None, None

@app.route('/')
def index():
    try:
        # Endpoint de la API del dólar
        dolar_url = "https://criptoya.com/api/dolar"

        # Obtener datos de la API del dólar
        response_dolar = requests.get(dolar_url)
        if response_dolar.status_code != 200:
            logging.error(f"Error al obtener datos del dólar: {response_dolar.status_code}")
            return jsonify({'error': 'Error al obtener datos del dólar'}), 500

        data_dolar = response_dolar.json()
        logging.info(f"Datos del dólar recibidos: {data_dolar}")

        # Filtrar los datos relevantes
        tipos_dolar = {
            'CCL': {'compra': data_dolar['ccl']['al30']['24hs']['price'], 'venta': data_dolar['ccl']['al30']['ci']['price']},
            'Tarjeta': {'compra': data_dolar['tarjeta']['price'], 'venta': data_dolar['tarjeta']['price']},
            'MEP': {'compra': data_dolar['mep']['al30']['24hs']['price'], 'venta': data_dolar['mep']['al30']['ci']['price']},
            'USDT': {'compra': data_dolar['cripto']['usdt']['ask'], 'venta': data_dolar['cripto']['usdt']['bid']}
        }

        # Crear DataFrame
        df_dolar = pd.DataFrame(tipos_dolar).T

        # Identificar la mejor opción de compra
        mejor_opcion = df_dolar['compra'].idxmin()
        mejor_precio = df_dolar.loc[mejor_opcion, 'compra']

        # Crear tabla HTML para datos del dólar
        tabla_html = df_dolar.style.apply(lambda x: ['background-color: #48bb78' if v == mejor_precio else '' for v in x], subset=['compra']).to_html()

        # Visualización: Gráfico de barras para los precios de compra (compra)
        fig_dolar = px.bar(df_dolar, x=df_dolar.index, y='compra', text='compra', title='Precio de compra de diferentes tipos de dólar y USDT', height=300)
        fig_dolar.update_layout(yaxis=dict(title='Precio (ARS)'), xaxis=dict(title='Tipo de Cambio'))
        fig_dolar.update_traces(texttemplate='%{text:.2f}', textposition='outside')

        # Visualización: Gráfico de barras para los precios de venta (venta)
        fig_venta = px.bar(df_dolar, x=df_dolar.index, y='venta', text='venta', title='Precio de venta de diferentes tipos de dólar y USDT', height=300)
        fig_venta.update_layout(yaxis=dict(title='Precio (ARS)'), xaxis=dict(title='Tipo de Cambio'))
        fig_venta.update_traces(texttemplate='%{text:.2f}', textposition='outside')

        # Convertir las figuras a HTML
        dolar_plot_html = pio.to_html(fig_dolar, full_html=False)
        venta_plot_html = pio.to_html(fig_venta, full_html=False)

        # Obtener datos de criptomonedas
        df_crypto = get_crypto_data()
        
        # Crear tabla HTML para datos de criptomonedas con logos e iconos
        crypto_rows = []
        for _, row in df_crypto.iterrows():
            change = row['Cambio 24h (%)']
            icon = '▲' if change > 0 else '▼'
            color = 'text-green-500' if change > 0 else 'text-red-500'
            crypto_rows.append(f"""
                <tr>
                <td><img src="{row['Logo']}" alt="{row['Nombre']}" class="w-8 h-8"></td>
                <td>{row['Nombre']}</td>
                <td>${row['Precio (USD)']:.2f}</td>
                <td class="{color}">{icon} {change:.2f}%</td>
                </tr>
            """)
        tabla_crypto_html = f"""
        <table class="table-auto w-full text-left border-collapse">
        <thead>
        <tr>
        <th>Logo</th>
        <th>Nombre</th>
        <th>Precio (USD)</th>
        <th>Cambio 24h</th>
        </tr>
        </thead>
        <tbody>
        {''.join(crypto_rows)}
        </tbody>
        </table>
        """
        
        # Obtener datos de USDT
        df_usdt, mejor_compra, mejor_venta = get_usdt_data()
        
        # Crear tabla HTML para datos de USDT
        usdt_rows = []
        for _, row in df_usdt.iterrows():
            compra_class = 'bg-green-500' if row['Exchange'] == mejor_compra['Exchange'] else ''
            venta_class = 'bg-blue-500' if row['Exchange'] == mejor_venta['Exchange'] else ''
            usdt_rows.append(f"""
                <tr>
                <td>{row['Exchange']}</td>
                <td class="{compra_class}">${row['Compra (ARS)']:.2f}</td>
                <td class="{venta_class}">${row['Venta (ARS)']:.2f}</td>
                </tr>
            """)
        tabla_usdt_html = f"""
        <table class="table-auto w-full text-left border-collapse">
        <thead>
        <tr>
        <th>Exchange</th>
        <th>Compra (ARS)</th>
        <th>Venta (ARS)</th>
        </tr>
        </thead>
        <tbody>
        {''.join(usdt_rows)}
        </tbody>
        </table>
        """

        # Renderizar la página HTML con Tailwind CSS
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500&display=swap" rel="stylesheet">
        <style>
        body {{ font-family: 'Space Grotesk', monospace; background-color: #1a202c; color: #cbd5e0; }}
        .container {{ max-width: 1200px; margin: auto; }}
        .card {{ background-color: #2d3748; border-radius: 0.5rem; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #4a5568; padding: 0.5rem; text-align: left; }}
        th {{ background-color: #2d3748; }}
        tr:nth-child(even) {{ background-color: #2d3748; }}
        .bg-green-500 {{ background-color: #48bb78; }}
        .bg-blue-500 {{ background-color: #63b3ed; }}
        </style>
        </head>
        <body>
        <div class="container mx-auto p-4">
        <h1 class="text-3xl font-bold mb-6">Dashboard</h1>
        <button onclick="window.location.reload();" class="bg-blue-500 text-white px-4 py-2 rounded">Actualizar</button>
        <div class="card mt-6 p-4">
        <h2 class="text-2xl font-semibold mb-4">Cotizaciones del Dólar</h2>
        {tabla_html}
        <p class="mt-2">Mejor opción de compra: {mejor_opcion} con un precio de ${mejor_precio:.2f}</p>
        </div>
        <div class="card mt-6 p-4">
        <h2 class="text-2xl font-semibold mb-4">Precio de compra de diferentes tipos de dólar y USDT</h2>
        {dolar_plot_html}
        </div>
        <div class="card mt-6 p-4">
        <h2 class="text-2xl font-semibold mb-4">Precio de venta de diferentes tipos de dólar y USDT</h2>
        {venta_plot_html}
        </div>
        <div class="card mt-6 p-4">
        <h2 class="text-2xl font-semibold mb-4">Top 10 Criptomonedas</h2>
        {tabla_crypto_html}
        </div>
        <div class="card mt-6 p-4">
        <h2 class="text-2xl font-semibold mb-4">Cotizaciones USDT en Exchanges Argentinos</h2>
        {tabla_usdt_html}
        <p class="mt-2">Mejor opción para comprar USDT: {mejor_compra['Exchange']} a ${mejor_compra['Compra (ARS)']:.2f}</p>
        <p>Mejor opción para vender USDT: {mejor_venta['Exchange']} a ${mejor_venta['Venta (ARS)']:.2f}</p>
        </div>
        </div>
        </body>
        </html>
        """
        return render_template_string(html)
    except Exception as e:
        logging.error(f"Error en el servidor: {e}")
        return jsonify({'error': 'Error en el servidor'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
