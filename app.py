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

@app.route('/')
def index():
    try:
        # ... (el código para los datos del dólar permanece igual)

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
                        <h2 class="text-xl font-semibold mb-2">Contenido Futuro</h2>
                        <p>Aquí se añadirá contenido adicional en el futuro.</p>
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
