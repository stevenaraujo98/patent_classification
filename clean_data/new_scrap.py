from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService # Renombrado para claridad
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import re
import time
import pandas as pd

def percentil_a_cuartil(texto_percentil):
    if not texto_percentil or not isinstance(texto_percentil, str):
        return ""
    try:
        match = re.search(r'(\d+)', texto_percentil)
        if not match:
            match_num_only = re.match(r'^(\d+)$', texto_percentil)
            if not match_num_only: return ""
            percentil_num = int(match_num_only.group(1))
        else:
            percentil_num = int(match.group(1))

        if percentil_num >= 75: return "Q1"
        elif percentil_num >= 50: return "Q2"
        elif percentil_num >= 25: return "Q3"
        elif percentil_num >= 0: return "Q4"
        else: return ""
    except ValueError: return ""
    except Exception as e:
        print(f"Error inesperado en percentil_a_cuartil con '{texto_percentil}': {e}")
        return ""

def clean_authors_text(raw_text):
    if not raw_text:
        return ""

    text_to_process = raw_text.replace("Save all to author list", "").strip()
    # Split by semicolon, which seems to be the main delimiter between author entries.
    # Allow for optional newline and spaces around the semicolon.
    author_entries = re.split(r';\s*\n?', text_to_process)

    cleaned_names = []
    for entry in author_entries:
        if not entry.strip():
            continue
        # The name is typically the first line of the entry.
        name = entry.strip().split('\n')[0].strip()
        if name:
            cleaned_names.append(name)

    return "; ".join(cleaned_names)

def clean_affiliations_text(raw_text):
    if not raw_text:
        return ""

    cleaned_text = raw_text.replace("Hide additional affiliations", "").strip()
    affiliation_lines = cleaned_text.split('\n')

    cleaned_affiliations = []
    for line in affiliation_lines:
        stripped_line = line.strip()
        if stripped_line:
            cleaned_affiliations.append(stripped_line)

    return "; ".join(cleaned_affiliations)

def procesar_url_scopus(url_articulo, diccionario_resultados, driver):
    """
    Procesa una URL de Scopus, extrae información y la agrega al diccionario_resultados.

    Args:
        url_articulo (str): La URL del artículo de Scopus a procesar.
        diccionario_resultados (dict): El diccionario donde se agregarán los datos.
                                       Debe tener listas como valores para cada clave.
    """
    # Inicializar placeholders para los datos de esta URL
    eid = url_articulo.split("eid=")[1].split("&")[0]
    titulo_texto = ""
    abstract_texto = ""
    keywords_texto = ""
    doi_texto = ""
    cuartil_texto = ""
    authors_texto_raw = ""
    authors_texto_clean = ""
    affiliations_texto_raw = ""
    affiliations_texto_clean = ""

    document_type_texto = ""
    source_type_texto = ""
    publisher_texto = ""
    language_texto = ""
    issn_texto = ""
    isbn_texto = ""
    sponsors_texto = ""
    publication_year_texto = ""
    page_count_texto = "" # Puede ser un número o un string como "N/A"
    info_more_texto_completo = ""
    citations_quartile_texto = ""
    fwci_quartile_texto = ""

    indexed_keywords_texto = ""
    topic_prominence_name_texto = ""
    topic_prominence_value_texto = "" # Podría ser un percentil o un valor
    readers_count_texto = ""
    news_mentions_count_texto = ""
    citations_scopus_count_texto = "" # Número absoluto de citas
    fwci_value_texto = ""             # Valor numérico de FWCI
    zero_hunger_texto = ""
    clean_water_texto = ""
    affordable_energy_texto = ""
    industry_innovation_texto = ""

    # Validar si la URL parece ser de un registro de Scopus
    if not url_articulo or not isinstance(url_articulo, str) or not url_articulo.startswith("https://www.scopus.com/record/display.uri"):
        print(f"URL inválida o no es de Scopus: {url_articulo}. Omitiendo.")
        # Llenar todos los campos con valores vacíos
        for key in diccionario_resultados.keys():
            if key == "url":
                diccionario_resultados[key].append(url_articulo)
            else:
                # Obtener el valor vacío correspondiente al tipo de dato esperado (string para la mayoría)
                empty_value = "" # Asumimos string para todos por simplicidad aquí
                diccionario_resultados[key].append(empty_value)
        return

    try:
        driver.get(url_articulo)
        time.sleep(10) # Espera para que la página cargue elementos dinámicos

        # --- Título ---
        try:
            titulo_element = driver.find_element(By.XPATH, "//h2[@data-testid='publication-titles']/span")
            titulo_texto = titulo_element.text.strip()
        except NoSuchElementException:
            print(f"Título no encontrado para {url_articulo}")
        except Exception as e:
            print(f"Error extrayendo título para {url_articulo}: {e}")

        # --- Authors ---
        try:
            authors_element = driver.find_element(By.XPATH, "//div[@data-testid='author-list']")
            authors_texto_raw = authors_element.text.strip()
            authors_texto_clean = clean_authors_text(authors_texto_raw)
        except NoSuchElementException:
            print(f"Authors no encontrado para {url_articulo}")
        except Exception as e:
            print(f"Error extrayendo Authors para {url_articulo}: {e}")

        # --- Abstract ---
        try:
            abstract_element = driver.find_element(By.XPATH, "//section[@id='abstractSection']//p")
            abstract_texto = abstract_element.text.strip()
        except NoSuchElementException:
            try:
                abstract_element = driver.find_element(By.XPATH, "//div[@class='Abstract-module__pTWiT']/div/p")
                abstract_texto = abstract_element.text.strip()
            except NoSuchElementException:
                 try:
                    abstract_element = driver.find_element(By.XPATH, "//div[@class='Abstract-module__pTWiT']")
                    abstract_texto = abstract_element.text.strip()
                 except NoSuchElementException:
                    print(f"Abstract no encontrado para {url_articulo}")
                 except Exception as e:
                    print(f"Error extrayendo abstract (fallback 2) para {url_articulo}: {e}")
            except Exception as e:
                print(f"Error extrayendo abstract (fallback 1) para {url_articulo}: {e}")
        except Exception as e:
            print(f"Error extrayendo abstract para {url_articulo}: {e}")

        # --- Palabras Clave (Author Keywords) ---
        try:
            keyword_elements_author = driver.find_elements(By.XPATH, "//section[@id='authorKeywords']//span[contains(@class,'Button-module__')]")
            temp_keywords_list = [el.text.strip() for el in keyword_elements_author if el.text.strip()]
            if temp_keywords_list:
                keywords_texto = ", ".join(temp_keywords_list)
            else: # Fallback a otro selector si el primero no da resultados
                keyword_elements_original = driver.find_elements(By.XPATH, "//div[@class='Stack-module__tT3r4 Stack-module___CTfk']/div/span") # Este era tu original
                str_key_words_temp = ""
                for key_word in keyword_elements_original:
                    kw_text = key_word.text.strip()
                    if kw_text: str_key_words_temp += kw_text.split(";")[0].strip() + ", " if ";" in kw_text else kw_text + ", "
                if str_key_words_temp: keywords_texto = str_key_words_temp[:-2]
        except: pass

        # --- DOI ---
        try:
            doi_element = driver.find_element(By.XPATH, "//dl[@data-testid='source-info-entry-doi']/dd")
            doi_texto = doi_element.text.strip()
        except NoSuchElementException:
            print(f"DOI no encontrado para {url_articulo}")
        except Exception as e:
            print(f"Error extrayendo DOI para {url_articulo}: {e}")

        # --- ISSN (ya estaba, pero lo muevo cerca de los otros datos de fuente) ---
        try:
            issn_element = driver.find_element(By.XPATH, "//dl[@data-testid='source-info-entry-issn']/dd")
            issn_texto = issn_element.text.strip()
        except NoSuchElementException:
            # A veces el ISSN está en la sección "more info", así que no imprimimos error aún
            pass
        except Exception as e:
            print(f"Error extrayendo ISSN (principal) para {url_articulo}: {e}")

        # --- Affiliations ---
        try:
            # Intenta hacer clic en el botón para mostrar afiliaciones adicionales si existe
            try:
                show_affiliations_button = driver.find_element(By.XPATH, "//button[@id='show-additional-affiliations-button']")
                driver.execute_script("arguments[0].click();", show_affiliations_button)
                time.sleep(1) # Espera a que se carguen
            except NoSuchElementException:
                # No es un error si el botón no existe (todas las afiliaciones podrían estar visibles)
                pass

            affiliations_element = driver.find_element(By.XPATH, "//div[@id='affiliation-section']")
            affiliations_texto_raw = affiliations_element.text.strip()
            affiliations_texto_clean = clean_affiliations_text(affiliations_texto_raw)
        except NoSuchElementException:
            print(f"Affiliations section no encontrada para {url_articulo}")
        except Exception as e:
            print(f"Error extrayendo Affiliations para {url_articulo}: {e}")

        # PANEL LEFT
        # --- Click en "Show additional source info" y extraer más datos ---
        try:
            button_more = driver.find_element(By.XPATH, "//button[@data-testid='button-show-additional-source-info']")
            driver.execute_script("arguments[0].click();", button_more) # Usar JS click si el normal falla
            time.sleep(1) # Espera a que se cargue la información adicional

            # document-type
            try:
                text_document_type = driver.find_element(By.XPATH, "//dl[@data-testid='source-info-entry-document-type']/dd")
                document_type_texto = text_document_type.text.strip()
            except NoSuchElementException:
                print(f"Tipo de documento no encontrado para {url_articulo}")
            except Exception as e:
                print(f"Error extrayendo tipo de documento para {url_articulo}: {e}")

            # source-type
            try:
                text_source_type = driver.find_element(By.XPATH, "//dl[@data-testid='source-info-entry-source-type']/dd")
                source_type_texto = text_source_type.text.strip()
            except NoSuchElementException:
                print(f"Tipo de fuente no encontrado para {url_articulo}")
            except Exception as e:
                print(f"Error extrayendo tipo de fuente para {url_articulo}: {e}")

            # publisher
            try:
                text_publisher = driver.find_element(By.XPATH, "//dl[@data-testid='source-info-entry-publisher']/dd")
                publisher_texto = text_publisher.text.strip()
            except NoSuchElementException:
                print(f"Editorial no encontrada para {url_articulo}")
            except Exception as e:
                print(f"Error extrayendo editorial para {url_articulo}: {e}")

            # language
            try:
                text_language = driver.find_element(By.XPATH, "//dl[@data-testid='source-info-entry-original-language']/dd")
                language_texto = text_language.text.strip()
            except NoSuchElementException:
                print(f"Idioma original no encontrado para {url_articulo}")
            except Exception as e:
                print(f"Error extrayendo idioma para {url_articulo}: {e}")

            # Si el ISSN no se encontró antes, intentarlo aquí
            if not issn_texto:
                try:
                    issn_element_more = driver.find_element(By.XPATH, "//dl[@data-testid='source-info-entry-issn']/dd")
                    issn_texto = issn_element_more.text.strip()
                except NoSuchElementException:
                    print(f"ISSN no encontrado (ni en principal ni en 'more info') para {url_articulo}")
                except Exception as e:
                    print(f"Error extrayendo ISSN (en 'more info') para {url_articulo}: {e}")

            try:
                text_isbn = driver.find_element(By.XPATH, "//dl[@data-testid='source-info-entry-isbn']/dd")
                isbn_texto = text_isbn.text.strip()
            except NoSuchElementException:
                # El ISBN no siempre está presente, así que no es necesariamente un error
                # print(f"ISBN no encontrado para {url_articulo}")
                pass
            except Exception as e:
                print(f"Error extrayendo ISBN para {url_articulo}: {e}")
        
            # --- Sponsors ---
            try:
                text_sponsors_element = driver.find_element(By.XPATH, "//dl[@data-testid='source-info-entry-sponsors']/dd")
                sponsors_texto = text_sponsors_element.text.strip()
            except NoSuchElementException:
                # No todos los artículos tienen patrocinadores, así que esto es común
                # print(f"Sponsors no encontrados para {url_articulo}")
                pass
            except Exception as e:
                print(f"Error extrayendo sponsors para {url_articulo}: {e}")
        except NoSuchElementException:
            print(f"Botón 'Show additional source info' no encontrado para {url_articulo}")
        except Exception as e:
            print(f"Error al hacer clic o procesar 'Show additional source info' para {url_articulo}: {e}")


        # --- Información de publicación (info_more) año, paginas---
        try:
            info_more_element = driver.find_element(By.XPATH, "//div[@data-testid='publication-information-bar']")
            info_more_texto_completo = info_more_element.text.strip()

            # Intentar extraer año de publicación
            year_match = re.search(r'\b(19\d{2}|20\d{2})\b', info_more_texto_completo)
            if year_match:
                # Tomar la última ocurrencia del año, que suele ser la de publicación
                publication_year_texto = year_match.groups()[-1]

            # Intentar extraer número de páginas
            # Caso 1: Pages xxx - yyy
            pages_match = re.search(r'Pages\s*(\d+)\s*-\s*(\d+)', info_more_texto_completo, re.IGNORECASE)
            if pages_match:
                start_page = pages_match.group(1)
                end_page = pages_match.group(2)

                # si end no es mayor entonces deberia estar en como numero normal por lo cual seria la misma cantidad y va el else
                if len(end_page) > 4 and (len(end_page) - 4) > len(start_page): #  9 - 172011 
                    end_page_2 = end_page[:len(end_page) - 4]
                    date_number = end_page[len(end_page) - 4:]
                    page_count_texto = str(int(end_page_2) - int(start_page) + 1)

                    # si no obtuvo el year_match lo saca del valor en conjunto con la pagina, ya que sino esta en conjunto la expresion regular la obtendrá
                    if not(year_match): 
                        publication_year_texto = date_number
                elif len(end_page) > (len(start_page) + 1) : # 586 - 59130, 123 - 23910, 91 - 9930
                    end_page_2 = end_page[:len(start_page)]
                    date_number = end_page[len(start_page):]

                    if int(end_page_2) < int(start_page): # # 83 - 1081,  6 - 1125 
                        end_page_2 = end_page[:len(start_page) + 1]
                        date_number = end_page[len(start_page) + 1:]
                    page_count_texto = str(int(end_page_2) - int(start_page) + 1)

                    # si no obtuvo el year_match lo saca del valor en conjunto con la pagina, ya que sino esta en conjunto la expresion regular la obtendrá
                    if not(year_match): 
                        publication_year_texto = date_number
                else:
                    # cuando son la misma cantidad de len en ambos casos o end y start usan tal cual
                    page_count_texto = str(int(end_page) - int(start_page) + 1)
            else:
                # Caso 2: Article number (no es un rango de páginas)
                article_number_match = re.search(r'Article number\s*([a-zA-Z0-9]+)', info_more_texto_completo, re.IGNORECASE)
                if article_number_match:
                    page_count_texto = f"Art. No. {article_number_match.group(1)}"
                # Podrías añadir más patrones aquí si es necesario
                # else:
                # print(f"Formato de páginas no reconocido en '{info_more_texto_completo}' para {url_articulo}")
        except NoSuchElementException:
            print(f"Barra de información de publicación no encontrada para {url_articulo}")
        except Exception as e:
            print(f"Error extrayendo o parseando 'info_more' para {url_articulo}: {e}")


        # CURTAINS BOTTOM
        # --- Indexed Keywords ---
        try:
            driver.find_element(By.XPATH, "//button[@data-testid='button-indexed-keywords']").click()
            time.sleep(1)
            indexed_keyword_elements = driver.find_elements(By.XPATH, "//div[@data-testid='indexed-keywords']//dd/span") # //dd puede tener spans adentro
            if not indexed_keyword_elements: # Fallback si los spans no están o están directamente en dd
                indexed_keyword_elements = driver.find_elements(By.XPATH, "//div[@data-testid='indexed-keywords']//dd")
            temp_indexed_keywords = [el.text.strip() for el in indexed_keyword_elements if el.text.strip()]
            if temp_indexed_keywords:
                indexed_keywords_texto = ", ".join(temp_indexed_keywords)
        except: pass
            
        # --- Topics of Prominence ---
        try:
            driver.find_element(By.XPATH, "//button[@data-testid='button-topics-of-prominence']").click()
            time.sleep(1)
            topic_elements = driver.find_elements(By.XPATH, "//div[@data-testid='topics-of-prominence']//dd")
            if len(topic_elements) >= 1:
                topic_prominence_name_texto = topic_elements[0].text.strip()
            if len(topic_elements) >= 2:
                # El valor puede tener " percentile" o ser solo un número.
                raw_value = topic_elements[1].text.strip()
                # Intentar extraer solo el número si hay texto adicional
                match_val = re.search(r'([\d\.]+)', raw_value)
                if match_val:
                    topic_prominence_value_texto = match_val.group(1)
                else:
                    topic_prominence_value_texto = raw_value # Tomar el texto como está si no se puede parsear
        except: pass

        # --- Clics en botones de Métricas y SDG (si existen) ---
        try:
            driver.find_element(By.XPATH, "//button[@data-testid='button-metrics']").click()
            time.sleep(1) # Espera a que la sección de métricas se cargue/actualice
        except: pass # No es un error si no está
        try:
            driver.find_element(By.XPATH, "//button[@data-testid='button-sustainable-development-goals']").click()
            time.sleep(0.5)
        except: pass # No es un error si no está

        # --- Extracción de Métricas Adicionales (Readers, News, Citations Count, FWCI Value) ---
        # Esta sección puede estar bajo "Metrics" o visible por defecto en algunos casos
        try:
            metric_items = driver.find_elements(By.XPATH, "//div[contains(@data-testid, 'metric-panel-body')]//div[@data-testid='count-label-and-value']")
            if not metric_items: # Fallback a un selector más general si el anterior no funciona
                metric_items = driver.find_elements(By.XPATH, "//div[@data-testid='count-label-and-value']")

            for item in metric_items:
                try:
                    list_value = item.text.split("\n")
                    item_0 = list_value[0].lower()
                    item_1 = list_value[1].lower()
                except: continue # Si no hay label, saltar este item

                if "Zero hunger" in item_0 or "zero hunger" in item_0: # Para "Zero Hunger":
                    zero_hunger_texto = item_1
                elif "Zero hunger" in item_1 or "zero hunger" in item_1: # Para "Zero Hunger":
                    zero_hunger_texto = item_0
                elif "Clean water and sanitation" in item_0 or "clean water and sanitation" in item_0: # Para "Clean Water and Sanitation":
                    clean_water_texto = item_1
                elif "Clean water and sanitation" in item_1 or "clean water and sanitation" in item_1: # Para "Clean Water and Sanitation":	
                    clean_water_texto = item_0
                elif "Affordable and clean energy" in item_0 or "affordable and clean energy" in item_0: # Para "Affordable and Clean Energy":
                    affordable_energy_texto = item_1
                elif "Affordable and clean energy" in item_1 or "affordable and clean energy" in item_1: # Para "Affordable and Clean Energy":
                    affordable_energy_texto = item_0
                elif "Industry, innovation and infrastructure" in item_0 or "industry, innovation and infrastructure" in item_0: # Para "Industry, Innovation and Infrastructure":
                    industry_innovation_texto = item_1
                elif "Industry, innovation and infrastructure" in item_1 or "industry, innovation and infrastructure" in item_1: # Para "Industry, Innovation and Infrastructure":
                    industry_innovation_texto = item_0
                elif "citations" in item_0 and "scopus" in item_0: # Para "Citations in Scopus"
                    for element in driver.find_elements(By.XPATH, "//span[@data-testid='clickable-count']"):
                        len_tmp = len(element.text)
                        if item_1[:len_tmp] == element.text:
                            citations_scopus_count_texto = item_1[:len_tmp]
                            break
                        else:
                            citations_scopus_count_texto = item_1
                elif "citations" in item_1 and "scopus" in item_1: # Para "Citations in Scopus"
                    for element in driver.find_elements(By.XPATH, "//span[@data-testid='clickable-count']"):
                        len_tmp = len(element.text)
                        if item_0[:len_tmp] == element.text:
                            citations_scopus_count_texto = item_0[:len_tmp]
                            break
                        else:
                            citations_scopus_count_texto = item_1
                elif "field-weighted citation impact" in item_0 or "fwci" in item_0:
                    fwci_value_texto = item_1
                elif "field-weighted citation impact" in item_1 or "fwci" in item_1:
                    fwci_value_texto = item_0
                elif "readers" in item_0 or "mendeley" in item_0: # Para "Readers on Mendeley"
                    readers_count_texto = item_1
                elif "readers" in item_1 or "mendeley" in item_1: # Para "Readers on Mendeley"
                    readers_count_texto = item_0
                elif "news" in item_0 and "mentions" in item_0: # Para "News Mentions"
                    news_mentions_count_texto = item_1
                elif "news" in item_1 and "mentions" in item_1: # Para "News Mentions"
                    news_mentions_count_texto = item_0
        except Exception as e:
            print(f"Error extrayendo métricas adicionales para {url_articulo}: {e}")


        # --- Cuartiles (CiteScore, Citations, FWCI) basados en percentiles ---
        # (Mantenemos esta lógica ya que los percentiles son la base para los cuartiles)
        texto_citescore_percentil_raw = ""
        texto_citations_percentil_raw = ""
        texto_fwci_percentil_raw = ""
        try:
            # 1. Percentil de CiteScore (más prominente)
            percentile_element = driver.find_element(By.XPATH, "//a[@data-testid='percentile-link']/span/span")
            texto_citescore_percentil_raw = percentile_element.text.strip()
        except: pass

        try:
            # 2. Lista general de métricas de impacto (para Citations y FWCI percentiles, y fallback para CiteScore)
            list_perce_citaImpact_elements = driver.find_elements(By.XPATH, "//div[@data-testid='order']/div/div/a/span/span")
            if len(list_perce_citaImpact_elements) > 0:
                texto_citations_percentil_raw = list_perce_citaImpact_elements[0].text.strip()
            if not texto_citescore_percentil_raw and len(list_perce_citaImpact_elements) > 1:
                texto_citescore_percentil_raw = list_perce_citaImpact_elements[1].text.strip()
            if len(list_perce_citaImpact_elements) > 2:
                texto_fwci_percentil_raw = list_perce_citaImpact_elements[2].text.strip()
        except: pass

        if texto_citescore_percentil_raw:
            cuartil_texto = percentil_a_cuartil(texto_citescore_percentil_raw)
        if texto_citations_percentil_raw:
            citations_quartile_texto = percentil_a_cuartil(texto_citations_percentil_raw)
        if texto_fwci_percentil_raw:
            fwci_quartile_texto = percentil_a_cuartil(texto_fwci_percentil_raw)
    
    except TimeoutException:
        print(f"Timeout al cargar la URL: {url_articulo}")
    except WebDriverException as e:
        print(f"Error de WebDriver (ej. página no accesible, URL inválida para el driver): {url_articulo} - {e}")
    except Exception as e:
        print(f"Error inesperado procesando {url_articulo}: {e}")
    finally:
        # Agregar los datos (o vacíos si hubo error) al diccionario principal
        diccionario_resultados["url"].append(url_articulo)
        diccionario_resultados["eid"].append(eid)
        diccionario_resultados["title"].append(titulo_texto)
        diccionario_resultados["abstract"].append(abstract_texto)
        diccionario_resultados["key_words"].append(keywords_texto)
        diccionario_resultados["cuartil"].append(cuartil_texto)

        diccionario_resultados["authors_raw"].append(authors_texto_raw)
        diccionario_resultados["authors"].append(authors_texto_clean)
        diccionario_resultados["affiliations_raw"].append(affiliations_texto_raw)
        diccionario_resultados["affiliations"].append(affiliations_texto_clean)

        # LEFT PANEL
        diccionario_resultados["doi"].append(doi_texto)
        diccionario_resultados["issn"].append(issn_texto)
        diccionario_resultados["document_type"].append(document_type_texto)
        diccionario_resultados["source_type"].append(source_type_texto)
        diccionario_resultados["publisher"].append(publisher_texto)
        diccionario_resultados["language"].append(language_texto)
        diccionario_resultados["isbn"].append(isbn_texto)
        diccionario_resultados["sponsors"].append(sponsors_texto)
        # INFO MORE
        diccionario_resultados["publication_year"].append(publication_year_texto)
        diccionario_resultados["page_count"].append(page_count_texto)
        diccionario_resultados["info_more_full"].append(info_more_texto_completo)
        # CURTAINS BOTTOM
        diccionario_resultados["citations_quartile"].append(citations_quartile_texto)
        diccionario_resultados["fwci_quartile"].append(fwci_quartile_texto)
        
        diccionario_resultados["indexed_keywords"].append(indexed_keywords_texto)
        
        diccionario_resultados["topic_prominence_name"].append(topic_prominence_name_texto)
        diccionario_resultados["topic_prominence_value"].append(topic_prominence_value_texto)

        diccionario_resultados["zero_hunger"].append(zero_hunger_texto)
        diccionario_resultados["clean_water"].append(clean_water_texto)
        diccionario_resultados["affordable_energy"].append(affordable_energy_texto)
        diccionario_resultados["industry_innovation"].append(industry_innovation_texto)
        diccionario_resultados["readers_count"].append(readers_count_texto)
        diccionario_resultados["news_mentions_count"].append(news_mentions_count_texto)

        diccionario_resultados["citations_scopus_count"].append(citations_scopus_count_texto)
        diccionario_resultados["fwci_value"].append(fwci_value_texto)

# --- Ejemplo de Uso ---
if __name__ == "__main__":
    resultados_scopus = {
        "eid": [], "url": [], "title": [], "abstract": [], "key_words": [], "doi": [], "isbn": [], "issn": [],
        "authors_raw": [], "authors": [], "affiliations_raw": [], "affiliations": [],
        "cuartil": [], "document_type": [], "source_type": [], "publisher": [], "language": [], "sponsors": [], 
        "publication_year": [], "page_count": [], "info_more_full": [], 
        "citations_quartile": [], "fwci_quartile": [],
        "indexed_keywords": [], 
        "topic_prominence_name": [], "topic_prominence_value": [],
        "readers_count": [], "news_mentions_count": [], "citations_scopus_count": [], "fwci_value": [],
        "zero_hunger": [], "clean_water": [], "affordable_energy": [], "industry_innovation": []
    }
    count = 0
   

    # =========================================
    # POR 
    # column_name = "urlPage"
    # year_selected = "2010_to_2025"
    # year_selected = "2005_to_2009"
    # df_orig = pd.read_csv("..\\data\\create\\all_data_" + year_selected + ".csv")
    # year_selected = '2005'
    # df_orig = pd.read_csv("..\\data\\create\\" + year_selected + "_AFID_60072061.csv")
    # =========================================
    # DATA COMPLETA
    column_name = "urlPage"
    year_selected = ""
    df_orig = pd.read_csv("..\\data\\create\\all_data.csv")
    # =========================================
    # column_name = "url"
    # year_selected = "page_less"
    # df_orig = pd.read_csv("..\\data\\data_update\\page_less.csv")
    # =========================================
    # column_name = "url"
    # year_selected = "page_numbers"
    # df_orig = pd.read_csv("..\\data\\data_update\\scrap_numbers.csv")
    # =========================================
    df_scopu = df_orig[(~df_orig[column_name].isna() & df_orig[column_name].str.contains("scopus.com"))]

    service = ChromeService(ChromeDriverManager().install())
    option = ChromeOptions()
    # option.add_argument("--headless") # Descomentar para ejecución sin interfaz gráfica
    option.add_argument("--window-size=1920,1080")
    option.add_argument("--log-level=3") # Reducir logs de Chrome/ChromeDriver
    option.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = None

    driver = webdriver.Chrome(service=service, options=option)

    for url_actual in df_scopu[column_name]:
        # for url_actual in [
        #     "https://www.scopus.com/record/display.uri?eid=2-s2.0-84909950216&origin=resultslist",
        #     "https://www.scopus.com/record/display.uri?eid=2-s2.0-85048442723&origin=resultslist",
        #     "https://www.scopus.com/record/display.uri?eid=2-s2.0-85102849428&origin=resultslist",
        #     "https://www.scopus.com/record/display.uri?eid=2-s2.0-85187556446&origin=resultslist",
        #     "https://www.scopus.com/record/display.uri?eid=2-s2.0-84959576722&origin=resultslist",
        #     "https://www.scopus.com/record/display.uri?eid=2-s2.0-84925002674&origin=resultslist",
        #     "https://www.scopus.com/record/display.uri?eid=2-s2.0-44249108336&origin=resultslist", 
        #     "https://www.scopus.com/record/display.uri?eid=2-s2.0-80053124586&origin=resultslist",
        #     "https://www.scopus.com/record/display.uri?eid=2-s2.0-28444483175&origin=resultslist",
        #     "https://www.scopus.com/record/display.uri?eid=2-s2.0-33751302754&origin=resultslist"
        # ]:
        print(f"\n--- Procesando URL: {url_actual} ---")
        procesar_url_scopus(url_actual, resultados_scopus, driver)
        count += 1
        print(f"\nElemento {count} procesado.")
        print("-"*100)
        time.sleep(5) # Pequeña pausa para no sobrecargar el servidor
    
    if driver:
        driver.quit()

    print("\n\n--- Resultados Finales ---")
    df_resultados = pd.DataFrame(resultados_scopus)
    print(df_resultados)

    df_resultados.to_csv("../data/scrap_" + year_selected + ".csv", index=False)