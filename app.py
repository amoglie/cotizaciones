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
        
        # Crear DataFrame con los datos relevantes
        df = pd.DataFrame([(exchange, info['ask'], info['bid']) for exchange, info in data.items() if isinstance(info, dict) and 'ask' in info and 'bid' in info],
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
        # ... (el código para los datos del dólar y criptomonedas permanece igual)

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
            </style>
        </head>
        <body>
            <div class="container p-4">
                <h1 class="text-2xl font-bold mb-4">Dashboard</h1>
                <div class="mb-4 text-right">
                    <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" onclick="location.reload()">Actualizar</button>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    <div class="card p-4 rounded-lg">
                        <h2 class="text-xl font-semibold mb-2">Cotizaciones del Dólar</h2>
                        {tabla_html}
                    </div>
                    <div class="card p-4 rounded-lg">
                        <h2 class="text-xl font-semibold mb-2">Mejor opción de compra</h2>
                        <p class="text-lg">La mejor opción de compra es <span class="font-bold">{mejor_opcion}</span> con un precio de <span class="font-bold">${mejor_precio:.2f}</span></p>
                    </div>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    <div class="card p-4 rounded-lg">
                        <h2 class="text-xl font-semibold mb-2">Precio de compra de diferentes tipos de dólar y USDT</h2>
                        {dolar_plot_html}
                    </div>
                    <div class="card p-4 rounded-lg">
                        <h2 class="text-xl font-semibold mb-2">Precio de venta de diferentes tipos de dólar y USDT</h2>
                        {venta_plot_html}
                    </div>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    <div class="card p-4 rounded-lg">
                        <h2 class="text-xl font-semibold mb-2">Top 10 Criptomonedas</h2>
                        {tabla_crypto_html}
                    </div>
                    <div class="card p-4 rounded-lg">
                        <h2 class="text-xl font-semibold mb-2">Cotizaciones USDT en Exchanges Argentinos</h2>
                        {tabla_usdt_html}
                        <div class="mt-4">
                            <p class="font-semibold">Mejor opción para comprar USDT:</p>
                            <p>{mejor_compra['Exchange']} a ${mejor_compra['Compra (ARS)']:.2f}</p>
                            <p class="font-semibold mt-2">Mejor opción para vender USDT:</p>
                            <p>{mejor_venta['Exchange']} a ${mejor_venta['Venta (ARS)']:.2f}</p>
                        </div>
                    </div>
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
