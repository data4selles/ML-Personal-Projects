import requests
from lxml import html
import pandas as pd

# Definir el rango de años del que vamos a descargar los datos
start_year = 2018
end_year = 2024  # Puedes cambiar este año a la actualidad

# URL base sin el año
base_url = 'https://espndeportes.espn.com/basquetbol/nba/jugador/juego-a-juego/_/id/1966/tipo/nba/ano/'

# Definir headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}

# Crear una lista para almacenar todos los datos
all_data = []

for year in range(start_year, end_year + 1):
    if year == 2020:
        print('En el 2020 no hay datos')
        continue

    url = f'{base_url}{year}'
    print(f"Descargando datos para el año {year}...")

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        tree = html.fromstring(response.content)
        
        # Usar el contenedor principal según el año
        if year >= 2023:
            # Nuevo XPath para 2023 y 2024
            container_xpath = '//*[@id="fittPageContainer"]/div[2]/div/div[5]/div/div/div[1]/div'
        else:
            # XPath original para años anteriores
            container_xpath = '//*[@id="fittPageContainer"]/div[2]/div/div[5]/div/div[1]/div[1]/div/div[2]'
        
        # Obtener el contenedor
        container = tree.xpath(container_xpath)

        if container:
            # Buscar las tablas dentro del contenedor
            tables = container[0].xpath('.//table')
            if not tables:
                print(f"No se encontraron tablas para el año {year}. Puede que el formato de la página haya cambiado.")
                continue  # Pasar al siguiente año si no hay tablas

            for i, table in enumerate(tables, start=1):
                rows = table.xpath('.//tr')

                for row in rows:
                    cells = []
                    for idx, cell in enumerate(row.xpath('.//td')):
                        if idx == 1:
                            value = cell.xpath('.//span/span[3]/a/text()')
                        elif idx == 2:
                            value1 = cell.xpath('.//a/div/span/text()')
                            value2 = cell.xpath('.//a/div/div/div/text()')
                            value = [value1, value2]
                        else:
                            value = cell.xpath('.//text()')
                        
                        if value:
                            cells.append(value[0])
                            if idx == 2 and len(value) > 1:
                                cells.append(value[1])

                    if cells:
                        # Insertar el año al principio de la fila
                        year_range = f"{year}/{year - 1}"
                        cells.insert(0, year_range)
                        all_data.append(cells)
            print(f"Tabla {i} del año {year} procesada.")
        else:
            print(f"Contenedor no encontrado para el año {year}.")
    else:
        print(f"Error al acceder a la página para el año {year}: {response.status_code}")

# Convertir la lista de datos a DataFrame
df = pd.DataFrame(all_data)
csv_file = 'lebron_puntos_juego_a_juego5.csv'
df.to_csv(csv_file, index=False, header=['Año'] + [f'Tabla {i+1}' for i in range(len(df.columns) - 1)])

print(f"Datos guardados en {csv_file}")
