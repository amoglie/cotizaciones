from flask import Flask, render_template_string, jsonify
import requests
import pandas as pd
import plotly.express as px
import plotly.io as pio
import logging

app = Flask(__name__)

# Configuración de registros
logging.basicConfig(level=logging.INFO)

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

        # Crear tabla HTML
        tabla_html = df_dolar.to_html(classes="table-auto w-full text-left border-collapse")

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
                th, td {{ border: 1px solid #4a5568; padding: 0.5rem; text-align: center; }}
                th {{ background-color: #2d3748; }}
                tr:nth-child(even) {{ background-color: #2d3748; }}
            </style>
        </head>
        <body>
            <div class="container p-4">
                <h1 class="text-2xl font-bold mb-4">Dashboard</h1>
                <div class="mb-4 text-right">
                    <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" onclick="location.reload()">Refrescar</button>
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
                <div class="card p-4 rounded-lg mb-6">
                    <h2 class="text-xl font-semibold mb-2">Cotizaciones</h2>
                    {tabla_html}
                </div>
                <div class="card p-4 rounded-lg">
                    <h2 class="text-xl font-semibold mb-2">Mejor opción de compra</h2>
                    <p class="text-lg">La mejor opción de compra es <span class="font-bold">{mejor_opcion}</span> con un precio de <span class="font-bold">${mejor_precio:.2f}</span></p>
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
