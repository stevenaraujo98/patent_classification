from webdriver_manager.chrome import ChromeDriverManager # se encarga de instalar o usar o descargar

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
import time
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

service = Service(ChromeDriverManager().install())
option = webdriver.ChromeOptions()
# option.add_argument("--headless")
option.add_argument("--window-size=1920,1080")

driver = Chrome(service=service, options=option)

# url = "https://www.scopus.com/record/display.uri?eid=2-s2.0-85183507942&origin=resultslist"
# url = "https://www.scopus.com/record/display.uri?eid=2-s2.0-85050088624"
# url = "https://www.scopus.com/record/display.uri?eid=2-s2.0-85095976176&origin=inward&txGid=525d31c39dc85540040ed8a7a474cfca"


# ==========================================================================================
url = "https://www.scopus.com/record/display.uri?eid=2-s2.0-85196167691&origin=resultslist"
# url = "https://www.scopus.com/record/display.uri?eid=2-s2.0-85192762875&origin=resultslist"
# url = "https://www.scopus.com/record/display.uri?eid=2-s2.0-85214989060&origin=resultslist"
# url = "https://www.scopus.com/record/display.uri?eid=2-s2.0-85190596063&origin=resultslist"
# url = "https://www.scopus.com/record/display.uri?eid=2-s2.0-85189504323&origin=resultslist"
# url = "https://www.scopus.com/record/display.uri?eid=2-s2.0-85218309210&origin=resultslist"
# ==========================================================================================


driver.get(url)

def percentil_a_cuartil(texto_percentil):
    """
    Convierte una cadena de texto de percentil (ej. "59th percentile") a su cuartil.

    Args:
        texto_percentil (str): El percentil en formato de cadena,
                               por ejemplo, "20th percentile", "75th percentile".

    Returns:
        str: El cuartil correspondiente (ej. "Q1", "Q2", "Q3", "Q4")
             o un mensaje de error si la entrada es inválida.
    """
    # Extraer el número del percentil usando expresiones regulares
    match = re.match(r"(\d+)(?:st|nd|rd|th)\s+percentile", texto_percentil.lower())

    if not match:
        return "Formato de percentil inválido. Use el formato como '59th percentile'."

    percentil = int(match.group(1))

    if not (0 <= percentil <= 100):
        return "El valor del percentil debe estar entre 0 y 100."

    if percentil <= 25:
        return "Q1"
    elif percentil <= 50:
        return "Q2"
    elif percentil <= 75:
        return "Q3"
    else: # percentil <= 100
        return "Q4"

dic_resp = {"title": [], "abstract": [], "key_words": [], "doi": [], "issn": [], "isbn":[], "cuartil": [], "url": [], "document_type": [], "text_source_type": [], "language": [], "publisher": [], "sponsors": []}
dic_resp["url"] = url

titulo = driver.find_element(By.CLASS_NAME, "Highlight-module__MMPyY")
print(titulo.text)
dic_resp["title"] = titulo.text

abstract = driver.find_element(By.XPATH, "//div[@class='Abstract-module__pTWiT']")
print(abstract.text)
dic_resp["abstract"] = abstract.text

key_words = driver.find_elements(By.XPATH, "//div[@class='Stack-module__tT3r4 Stack-module___CTfk']/div/span")
str_key_words = ""
for key_word in key_words:
    if key_word.text.find(";") == -1:
        str_key_words += key_word.text + ", "
    else:
        str_key_words += key_word.text.split(";")[0] + ", "

dic_resp["key_words"] = str_key_words[:-2]

info_more = driver.find_element(By.XPATH, "//div[@data-testid='publication-information-bar']")
print(info_more.text) 
# 'IntercienciaVolume 49, Issue 4, Pages 235 - 247April 2024'
# 'Proceedings of the LACCEI international Multi-conference for Engineering, Education and Technology2024 Article number 5284th LACCEI International Multiconference on Entrepreneurship, Innovation and Regional Development, LEIRD 2024Virtual, Online2 December 2024through 4 December 2024Code 205662'
# 85214989060 = Procedia Computer ScienceOpen AccessVolume 251, Pages 170 - 1772024 15th International Conference on Emerging Ubiquitous Systems and Pervasive Networks / 14th International Conference on Current and Future Trends of Information and Communication Technologies in Healthcare, EUSPN/ICTH 2024Leuven28 October 2024through 30 October 2024Code 205414
# New Disease ReportsOpen AccessVolume 49, Issue 2April 2024 Article number e12265
# Microbiology Resource AnnouncementsOpen AccessVolume 13, Issue 4April 2024
# E3S Web of ConferencesOpen AccessVolume 5326 June 2024 Article number 020032nd International Conference of Applied Industrial Engineering: Intelligent Production Automation and its Sustainable Development, CIIA 2024Guayaquil28 May 2024through 30 May 2024Code 200093

text_doi = driver.find_element(By.XPATH, "//dl[@data-testid='source-info-entry-doi']/dd")
print(text_doi.text)
dic_resp["doi"] = text_doi.text


button_more = driver.find_element(By.XPATH, "//button[@data-testid='button-show-additional-source-info']")
button_more.click()

# First click
text_document_type = driver.find_element(By.XPATH, "//dl[@data-testid='source-info-entry-document-type']/dd")
print(text_document_type.text)
dic_resp["document_type"] = text_document_type.text

text_source_type = driver.find_element(By.XPATH, "//dl[@data-testid='source-info-entry-source-type']/dd")
print(text_source_type.text)
dic_resp["text_source_type"] = text_source_type.text

text_publisher = driver.find_element(By.XPATH, "//dl[@data-testid='source-info-entry-publisher']/dd")
print(text_publisher.text)
dic_resp["publisher"] = text_publisher.text

text_sponsors = driver.find_element(By.XPATH, "//dl[@data-testid='source-info-entry-sponsors']/dd")
print(text_sponsors.text)
dic_resp["sponsors"] = text_sponsors.text

text_language = driver.find_element(By.XPATH, "//dl[@data-testid='source-info-entry-original-language']/dd")
print(text_language.text)
dic_resp["language"] = text_language.text

text_issn = driver.find_element(By.XPATH, "//dl[@data-testid='source-info-entry-issn']/dd")
print(text_issn.text)
dic_resp["issn"] = text_issn.text

text_isbn = driver.find_element(By.XPATH, "//dl[@data-testid='source-info-entry-isbn']/dd")
print(text_isbn.text)
dic_resp["isbn"] = text_isbn.text



list_perce_citaImpact = driver.find_elements(By.XPATH, "//div[@data-testid='order']/div/div/a/span/span")
print(list_perce_citaImpact[1].text, list_perce_citaImpact[2].text)
dic_resp["cuartil"] = percentil_a_cuartil(list_perce_citaImpact[1].text)
dic_resp["citatations"] = percentil_a_cuartil(list_perce_citaImpact[0].text)
dic_resp["fwci"] = percentil_a_cuartil(list_perce_citaImpact[2].text)


# //button[@data-testid='button-indexed-keywords']
# driver.find_element(By.XPATH, "//button[@data-testid='button-indexed-keywords']").click()
# //div[@data-testid='indexed-keywords']//dd
# For y guardar todos los keys
# driver.find_elements(By.XPATH, "//div[@data-testid='indexed-keywords']//dd")


# //button[@data-testid='button-topics-of-prominence']
# driver.find_element(By.XPATH, "//button[@data-testid='button-topics-of-prominence']").click()
# //div[@data-testid='topics-of-prominence']//dd
# driver.find_elements(By.XPATH, "//div[@data-testid='topics-of-prominence']//dd")
# driver.find_elements(By.XPATH, "//div[@data-testid='topics-of-prominence']//dd")[0].text # Topic name
# driver.find_elements(By.XPATH, "//div[@data-testid='topics-of-prominence']//dd")[1].text.split("\n")[0] # float


# Click en los dos botones si es que hay
# //button[@data-testid='button-sustainable-development-goals']
# driver.find_element(By.XPATH, "//button[@data-testid='button-sustainable-development-goals']").click()
# //button[@data-testid='button-metrics']
# driver.find_element(By.XPATH, "//button[@data-testid='button-metrics']").click()

# sacar las siguientes metricas
# //div[@data-testid='count-label-and-value']//div[@data-testid='order']
# driver.find_elements(By.XPATH, "//div[@data-testid='count-label-and-value']//div[@data-testid='order']")
# Readers
# News Mentions
# Citations in Scopus
    # - Num cites
    # - Cuartil
# Field-Weighted citation impact (FWCI)




time.sleep(5)

driver.quit()

print(dic_resp)
