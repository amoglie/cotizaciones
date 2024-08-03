import requests
import pandas as pd
import plotly.express as px

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

# Mostrar las figuras
fig_usdt.show()
fig_dolar.show()
