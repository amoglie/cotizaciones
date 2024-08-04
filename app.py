from flask import Flask, render_template_string, jsonify
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
            'CCL': {'ask': data_dolar['ccl']['al30']['24hs']['price'], 'bid': data_dolar['ccl']['al30']['ci']['price']},
            'Tarjeta': {'ask': data_dolar['tarjeta']['price'], 'bid': data_dolar['tarjeta']['price']},
            'MEP': {'ask': data_dolar['mep']['al30']['24hs']['price'], 'bid': data_dolar['mep']['al30']['ci']['price']},
            'USDT': {'ask': data_dolar['cripto']['usdt']['ask'], 'bid': data_dolar['cripto']['usdt']['bid']}
        }

        # Crear DataFrame
        df_dolar = pd.DataFrame(tipos_dolar).T
        df_dolar['price'] = df_dolar['ask']

        # Identificar la mejor opción de compra
        mejor_opcion = df_dolar['ask'].idxmin()
        mejor_precio = df_dolar.loc[mejor_opcion, 'ask']

        # Visualización: Gráfico de barras para los precios de compra (ask)
        fig_dolar = px.bar(df_dolar, x=df_dolar.index, y='ask', title='Precio de compra de diferentes tipos de dólar y USDT', height=300)
        fig_dolar.update_layout(yaxis=dict(title='Precio (ARS)'), xaxis=dict(title='Tipo de Cambio'))

        # Visualización: Gráfico de líneas para la variación de precios (simulado)
        fig_variacion = go.Figure()
        for tipo in tipos_dolar.keys():
            fig_variacion.add_trace(go.Scatter(x=[1, 2, 3], y=[df_dolar.loc[tipo, 'ask'] * i for i in range(1, 4)], mode='lines', name=tipo))
        fig_variacion.update_layout(title='Variación de precios de compra en el tiempo', yaxis=dict(title='Precio (ARS)'), xaxis=dict(title='Tiempo'))

        # Convertir las figuras a HTML
        dolar_plot_html = pio.to_html(fig_dolar, full_html=False)
        variacion_plot_html = pio.to_html(fig_variacion, full_html=False)

        # Crear tabla HTML
        tabla_html = df_dolar.to_html(classes="table-auto w-full text-left border-collapse")

        # Renderizar la página HTML con Tailwind CSS
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dashboard</title>
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        </head>
        <body class="bg-gray-100 text-gray-800">
            <div class="container mx-auto p-4">
                <h1 class="text-2xl font-bold mb-4">Dashboard</h1>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    <div class="bg-white p-4 rounded-lg shadow">
                        <h2 class="text-xl font-semibold mb-2">Precio de compra de diferentes tipos de dólar y USDT</h2>
                        {dolar_plot_html}
                    </div>
                    <div class="bg-white p-4 rounded-lg shadow">
                        <h2 class="text-xl font-semibold mb-2">Variación de precios de compra en el tiempo</h2>
                        {variacion_plot_html}
                    </div>
                </div>
                <div class="bg-white p-4 rounded-lg shadow mb-6">
                    <h2 class="text-xl font-semibold mb-2">Cotizaciones</h2>
                    {tabla_html}
                </div>
                <div class="bg-white p-4 rounded-lg shadow">
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
