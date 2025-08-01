
# Patentes espol
# Nuevo dataset para entrenamiento

Opciones principales:
- https://patentsview.org/download/data-download-tables
- https://patentdataset.org/  
- https://patents.google.com/
- https://zenodo.org/search?q=patent&l=list&p=2&s=10&sort=bestmatch

### HUPD (dataset) The Harvard USPTO Patent Dataset

El conjunto de datos Harvard USPTO (HUPD) es un corpus a gran escala, bien estructurado y multipropósito de solicitudes de patentes de utilidad en idioma inglés presentadas ante la Oficina de Patentes y Marcas de los Estados Unidos (USPTO) entre enero de 2004 y diciembre de 2014. [https://patentdataset.org/]

Se uso el url: https://huggingface.co/datasets/HUPD/hupd/tree/main/data en este respositorio estan los archivos dataset. Repositorio base desde https://huggingface.co/datasets/HUPD/hupd/tree/main. 

Tienen un modelo https://huggingface.co/HUPD/hupd-distilroberta-base para completar textos, con sugerencia de patentes. Usa como base el modelo para resumir textos https://huggingface.co/HUPD/hupd-t5-small .

Como cargan la data:
1. https://colab.research.google.com/drive/1_ZsI7WFTsEO0iu_0g3BLTkIkOUqPzCET?usp=sharing#scrollTo=3D3Vj_yDrgzv
2. https://colab.research.google.com/drive/1TzDDCDt368cUErH86Zc_P2aw9bXaaZy1?usp=sharing#scrollTo=oV8fqk77xeUz

### USPTO (dataset) No se usò
https://www.uspto.gov/ip-policy/economic-research/patentsview que te lleva a https://patentsview.org/download/data-download-tables  

# API
Todo por y paginado
- CONTENT_SEARCH_URL?start=0&count=100&query=AF-ID%2860072061%29+AND+PUBYEAR+IS+2025&apiKey=API_KEY

sacar el url de SELECT * FROM espol.T_DEC_INV_SCOPUS_PUBLICACION tdisp 
- https://www.scopus.com/record/display.uri?eid=2-s2.0-85083445073&origin=resultslist

Otros path del api para consultas
- CONTENT_EID_URL + 2-s2.0-85038931282
- CONTENT_SERIAL_URL + 09570233


### Scimagojr
https://www.scimagojr.com/journalrank.php


#### paraphrase-multilingual-MiniLM-L12-v2
1. Captura Semántica: Este modelo captura el significado semántico del texto, lo cual es crucial para identificar similitudes entre documentos que pueden no compartir palabras clave exactas pero sí conceptos relacionados. Esto es especialmente útil para detectar invenciones o desarrollos tecnológicos que se describen de manera diferente pero tienen la misma esencia.

2. Multilingüe: Dado que tus datos pueden contener títulos y resúmenes en español e inglés, la capacidad multilingüe del modelo es una gran ventaja. No necesitas pre-procesar los datos para traducirlos a un solo idioma, lo que simplifica el pipeline y evita posibles pérdidas de información durante la traducción.

3. Embeddings Densos: Genera embeddings densos, que son representaciones vectoriales que condensan la información semántica en un espacio de menor dimensión. Estos embeddings son ideales para tareas de clustering, ya que permiten agrupar documentos basándose en su similitud semántica.

4. Especializado en Paráfrasis: Al estar diseñado para tareas de paráfrasis, el modelo es particularmente bueno para entender y comparar el significado de diferentes oraciones. Esto es útil para identificar documentos que describen la misma invención o desarrollo tecnológico utilizando diferentes palabras.


## Structure
- API:
    - union_csv: une todos los csv generados a partit de los enlaces obtenidos del api
    - relation_api.ipynb: analiza la relacion entre el total del csv de union_csv y el de base de datos
    - process: genera el csv por cada url con toda la información
    -get_res_api: obtiene todas las url de scopu

- clean_data:
    - main: 
    - process_update: un procesamiento adicional para mejorar cierta información
    - relation_scrap: para un analisis comparativo entre el resultado de scrap y base
    - new_scrap: scrapping de las paginas desde el api
    - scrapping_individual: prueba de scraping de solo uno
    - scrapping_group: prueba de scraping de mas de uno
- data
- unsupervised_data_espol
    - 1_preprocess
    - 2_embeddigns
    - 3_analize
    - 4_reduccion
    - 5_train
    - 6_test
- supervised_data_espol
    - 1_get_data
    - 2_processing
    - 3_post_processing
    - 4_all_models




## Dataaugmentation
- Nlpaug: 
Purpose: Textual data augmentation for NLP models. 
Functionality: Introduces variations in text data (e.g., synonym replacement, word insertions) to increase the size and robustness of training datasets. 
Use cases: Improving the performance of deep learning models for tasks like text classification, named entity recognition, and question answering. 
Example: Augmenting sentences by replacing words with synonyms to create more diverse training examples.  
Uso de bert-base-multilingual-uncased  

- pandas DataFrame.sample():
Purpose: Randomly selecting rows from a DataFrame. 
Functionality: Returns a new DataFrame containing a random subset of the original DataFrame's rows. 
Use cases: Data exploration, creating smaller representative datasets for testing, or creating batches of data for model training. 
Example: Selecting 100 random rows from a DataFrame with 1000 rows to create a smaller dataset for experimentation. 

- Key Differences: 
Data Type: Nlpaug works with text data, while DataFrame.sample() works with tabular data represented in a pandas DataFrame. 
Purpose: Nlpaug is for data augmentation to improve model training, while DataFrame.sample() is for data sampling for exploration and analysis. 
Output: Nlpaug generates new text data, while DataFrame.sample() returns a subset of the original DataFrame. 

## Procesamiento
eliminamos numeros y caracteres especiales  
numeros no relevantes como fechas, codigos, referencias, etc.  
enforcarnos en patrones lingüísticos, semanticos y terminológicos realmente relevantes  

## LabelEncoder 
```
label_encoder = LabelEncoder()
y_train = label_encoder.fit_transform(train_df['value'])
y_val = label_encoder.transform(val_df['value'])
y_test = label_encoder.transform(test_df['value'])



Label_encoder = LabelEncoder()
all_labels = pd.concat([train_df['value'], val_df['value'], test_df['value']])
label_encoder.fit(all_labels)

train_labels = label_encoder.transform(train_df['value'])
val_labels = label_encoder.transform(val_df['value'])
test_labels = label_encoder.transform(test_df['value'])
```

```
label_map = {'REJECTED': 0, 'ACCEPTED': 1}
y_train = train_df['value'].map(label_map)
y_val = val_df['value'].map(label_map)
y_test = test_df['value'].map(label_map)
```

## Aplicar a futuro
```
from sklearn.model_selection import RandomizedSearchCV

# RandomizedSearchCV
random_search = RandomizedSearchCV(
    estimator=rf,
    param_distributions=param_grid,
    n_iter=10,  # número de combinaciones aleatorias a probar
    cv=5,
    scoring='accuracy',
    random_state=42,
    n_jobs=-1
)

random_search.fit(X_train, y_train)

print("Mejores parámetros:", random_search.best_params_)
print("Mejor score:", random_search.best_score_)
```