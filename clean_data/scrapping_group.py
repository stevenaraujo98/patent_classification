import pandas as pd
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

df_orig = pd.read_csv("..\\data\\originals\\sample2.csv")
df_scopu = df_orig[(~df_orig["URL"].isna() & df_orig["URL"].str.contains("scopus.com"))]

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

dic_resp = {"title": [], "abstract": [], "key_words": [], "doi": [], "issn": [], "cuartil": [], "url": []}
lis_urls_fail = []

for url in df_scopu["URL"]:
    try:
        print("Process:", url)
        driver.get(url)

        titulo = driver.find_element(By.CLASS_NAME, "Highlight-module__MMPyY")
        # print(titulo.text)

        abstract = driver.find_element(By.XPATH, "//div[@class='Abstract-module__pTWiT']")
        # print(abstract.text)

        key_words = driver.find_elements(By.XPATH, "//div[@class='Stack-module__tT3r4 Stack-module___CTfk']/div/span")
        str_key_words = ""
        for key_word in key_words:
            if key_word.text.find(";") == -1:
                str_key_words += key_word.text + ", "
            else:
                str_key_words += key_word.text.split(";")[0] + ", "


        text_doi = driver.find_element(By.XPATH, "//dl[@data-testid='source-info-entry-doi']/dd")
        # print(text_doi.text)

        text_issn = driver.find_element(By.XPATH, "//dl[@data-testid='source-info-entry-issn']/dd")
        # print(text_issn.text)

        list_perce_citaImpact = driver.find_elements(By.XPATH, "//div[@data-testid='order']/div/div/a/span/span")
        # print(list_perce_citaImpact[1].text, list_perce_citaImpact[2].text)

        dic_resp["url"].append(url)
        dic_resp["title"].append(titulo.text)
        dic_resp["abstract"].append(abstract.text)
        dic_resp["key_words"].append(str_key_words[:-2])
        dic_resp["doi"].append(text_doi.text)
        dic_resp["issn"].append(text_doi.text)
        dic_resp["cuartil"].append(percentil_a_cuartil(list_perce_citaImpact[1].text))
        print("Argregado todos los parametros")

        time.sleep(15)
    except:
        print("Fail", url)
        lis_urls_fail.append(url)

driver.quit()
print(dic_resp)
df = pd.DataFrame(dic_resp)
df.to_csv("../data/scrap.csv")

print(lis_urls_fail)