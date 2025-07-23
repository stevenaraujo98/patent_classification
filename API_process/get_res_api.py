import requests
import pandas as pd
import json
import time
import os # Para la creación de directorios
from dotenv import dotenv_values

config = dotenv_values(".env")

# --- Configuración ---
year = 2005
apiKey = config["API_KEY"]
affiliation_id = config["AFFILIATION_ID"]
base_url = config["CONTENT_SEARCH_URL"]
count_per_page = 100
start_index = 0
total_results_processed = 0

dict_value = {
    "eid": [], "title": [], "identifier": [], "url": [], "urlPage": [],
    "doi": [], "aggregationType": [], "subtypeDescription": [],
    "affiliation": [], "publicationName": [], "coverDate": [],
    "sourceId": [], "openaccess": [], "eIssn/issn/isbn": [],
}

print(f"Iniciando búsqueda para el año {year} y AF-ID {affiliation_id}...")

while True:
    query_params = {
        "start": start_index,
        "count": count_per_page,
        "query": f"AF-ID({affiliation_id}) AND PUBYEAR IS {year}",
        "apiKey": apiKey,
    }

    try:
        response = requests.get(base_url, params=query_params)
        response.raise_for_status()  # Lanza una excepción para códigos de error HTTP (4XX o 5XX)
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud a la API: {e}")
        print(f"URL intentada: {response.url if 'response' in locals() else 'No disponible'}")
        break
    except json.JSONDecodeError:
        print("Error al decodificar la respuesta JSON.")
        print(f"Respuesta recibida: {response.text if 'response' in locals() else 'No disponible'}")
        break

    search_results = data.get('search-results', {})
    if not search_results:
        print("La respuesta JSON no contiene 'search-results'. Finalizando.")
        break

    total_results_api = int(search_results.get("opensearch:totalResults", 0))
    current_items_per_page = int(search_results.get("opensearch:itemsPerPage", 0))
    api_start_index = int(search_results.get("opensearch:startIndex", 0))

    if start_index == 0: # En la primera solicitud
        print(f"Total de resultados encontrados por la API: {total_results_api}")
        if total_results_api == 0:
            print("No se encontraron resultados para los criterios dados.")
            break

    entries = search_results.get("entry", [])
    if not entries:
        print("No hay más entradas para procesar.")
        break

    print(f"Procesando {len(entries)} resultados de la página actual (índice {api_start_index} de {total_results_api})...")

    for element in entries:
        # # Filtrar solo los que son openaccess (según tu lógica original)
        # if element.get('openaccess') == "1":
        dict_value["eid"].append(element.get('eid'))
        dict_value["title"].append(element.get('dc:title'))
        dict_value["identifier"].append(element.get('dc:identifier'))
        dict_value["url"].append(element.get('prism:url'))

        eid_val = element.get('eid')
        urlPage = f"https://www.scopus.com/record/display.uri?eid={eid_val}&origin=resultslist" if eid_val else None
        dict_value["urlPage"].append(urlPage)

        dict_value["doi"].append(element.get('prism:doi'))
        dict_value["aggregationType"].append(element.get('prism:aggregationType'))
        dict_value["subtypeDescription"].append(element.get('subtypeDescription'))

        # Convertir la afiliación a una cadena JSON si existe, sino None
        affiliation_data = element.get("affiliation")
        dict_value["affiliation"].append(json.dumps(affiliation_data) if affiliation_data else None)

        dict_value["publicationName"].append(element.get('prism:publicationName'))
        dict_value["coverDate"].append(element.get('prism:coverDate'))
        dict_value["año"].append(year)
        dict_value["sourceId"].append(element.get('source-id'))
        dict_value["openaccess"].append(element.get('openaccess'))

        # Lógica para eIssn/issn/isbn
        res_eissn_val = None
        if element.get('prism:eIssn'):
            res_eissn_val = element['prism:eIssn']
        elif element.get('prism:issn'):
            res_eissn_val = element['prism:issn']
        elif element.get('prism:isbn'):
            isbn_data = element['prism:isbn']
            if isinstance(isbn_data, list) and isbn_data:
                if isinstance(isbn_data[0], dict) and "$" in isbn_data[0]:
                    res_eissn_val = isbn_data[0]["$"]
                elif isinstance(isbn_data[0], str):
                    res_eissn_val = isbn_data[0]
                else: # Representación de cadena si la estructura es inesperada
                    res_eissn_val = str(isbn_data[0])
            elif isinstance(isbn_data, str):
                res_eissn_val = isbn_data
        dict_value["eIssn/issn/isbn"].append(res_eissn_val)
        total_results_processed +=1

    start_index += current_items_per_page

    if start_index >= total_results_api or current_items_per_page == 0:
        print("Se han procesado todos los resultados o no hay más páginas.")
        break

    time.sleep(0.5) # Pausa para ser respetuoso con la API

print(f"\nProcesamiento completado. Total de artículos Open Access procesados: {total_results_processed}")

# --- Guardar en CSV ---
if total_results_processed > 0:
    df = pd.DataFrame(dict_value)

    output_dir = "../data/create/"
    # Crear el directorio si no existe
    try:
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{year}_AFID_{affiliation_id}.csv")
        df.to_csv(file_path, index=False)
        print(f"Resultados guardados en: {file_path}")
    except OSError as e:
        print(f"Error al crear el directorio o guardar el archivo: {e}")
        print("Mostrando DataFrame en consola:")
        print(df.head())

else:
    print("No se procesaron artículos Open Access, no se generará archivo CSV.")