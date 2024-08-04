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
            'CCL': data_dolar['ccl'],
            'Tarjeta': data_dolar['tarjeta'],
            'MEP': data_dolar['mep']['al30']['24hs'],
            'USDT': data_dolar['cripto']['usdt']
        }

        # Crear DataFrame
        df_dolar = pd.DataFrame(tipos_dolar).T
        df_dolar = df_dolar[['ask', 'price']] if 'price' in df_dolar.columns else df_dolar[['ask']]

        # Visualización
        fig_dolar = px.bar(df_dolar, x=df_dolar.index, y='ask', title='Precio de compra de diferentes tipos de dólar y USDT')

        # Convertir las figuras a HTML
        dolar_plot_html = pio.to_html(fig_dolar, full_html=False)

        # Renderizar los gráficos en una página HTML
        html = f"""
        <html>
        <head><title>Dashboard</title></head>
        <body>
        <h1>Dashboard</h1>
        <h2>Precio de compra de diferentes tipos de dólar y USDT</h2>
        {dolar_plot_html}
        </body>
        </html>
        """
        return render_template_string(html)
    
    except Exception as e:
        logging.error(f"Error en el servidor: {e}")
        return jsonify({'error': 'Error en el servidor'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
