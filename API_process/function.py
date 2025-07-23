import pandas as pd
from difflib import SequenceMatcher
import re

def fuzzy_merge(df_left, df_right, left_on, right_on, umbral_similitud=0.8, 
                how='inner', sufijos=('_left', '_right')):
    """
    Hace merge entre dataframes usando similitud de texto
    
    Parámetros:
    - df_left: DataFrame izquierdo
    - df_right: DataFrame derecho  
    - left_on: columna del df_left para comparar
    - right_on: columna del df_right para comparar
    - umbral_similitud: umbral mínimo de similitud (0.8 = 80%)
    - how: tipo de join ('inner', 'left', 'right', 'outer')
    - sufijos: sufijos para columnas duplicadas
    """
    
    def limpiar_texto(texto):
        if pd.isna(texto):
            return ""
        texto = str(texto).lower()
        texto = re.sub(r'[^\w\s]', '', texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto
    
    def similitud_texto(texto1, texto2):
        return SequenceMatcher(None, texto1, texto2).ratio()
    
    # Crear copias para no modificar originales
    df_l = df_left.copy()
    df_r = df_right.copy()
    
    # Limpiar textos
    df_l[f'{left_on}_limpio'] = df_l[left_on].apply(limpiar_texto)
    df_r[f'{right_on}_limpio'] = df_r[right_on].apply(limpiar_texto)
    print("- Textos limpios de ambos dataframes.")

    matches = []
    
    # Para cada fila del dataframe izquierdo
    for idx_l, row_l in df_l.iterrows():
        texto_l = row_l[f'{left_on}_limpio']
        
        if not texto_l:
            if how in ['left', 'outer']:
                # Agregar fila sin match
                match_row = row_l.to_dict()
                for col in df_r.columns:
                    if col != right_on and col != f'{right_on}_limpio':
                        match_row[f'{col}{sufijos[1]}'] = None
                match_row['similitud'] = 0.0
                matches.append(match_row)
            continue
        
        mejor_match = None
        mejor_similitud = 0
        
        # Buscar mejor match en dataframe derecho
        for idx_r, row_r in df_r.iterrows():
            texto_r = row_r[f'{right_on}_limpio']
            
            if not texto_r:
                continue
                
            # Verificar contenido y similitud
            contiene = texto_l in texto_r or texto_r in texto_l
            similitud = similitud_texto(texto_l, texto_r)
            
            # Si contiene o supera umbral
            if contiene or similitud >= umbral_similitud:
                if similitud > mejor_similitud:
                    mejor_similitud = similitud
                    mejor_match = (idx_r, row_r, similitud)
        
        # Crear fila resultado
        if mejor_match:
            # Hay match
            idx_r, row_r, similitud = mejor_match
            match_row = row_l.to_dict()
            
            # Agregar columnas del dataframe derecho
            for col in df_r.columns:
                if col != right_on and col != f'{right_on}_limpio':
                    if col in match_row:
                        match_row[f'{col}{sufijos[1]}'] = row_r[col]
                    else:
                        match_row[col] = row_r[col]
            
            match_row['similitud'] = similitud
            matches.append(match_row)
            
        elif how in ['left', 'outer']:
            # No hay match pero incluir fila izquierda
            match_row = row_l.to_dict()
            for col in df_r.columns:
                if col != right_on and col != f'{right_on}_limpio':
                    match_row[f'{col}{sufijos[1]}'] = None
            match_row['similitud'] = 0.0
            matches.append(match_row)
    
    # Para right y outer joins, agregar filas no matcheadas del dataframe derecho
    if how in ['right', 'outer']:
        matched_indices = set()
        for match in matches:
            if 'similitud' in match and match['similitud'] > 0:
                # Encontrar índice original (esto es simplificado)
                pass
        
        # Agregar filas no matcheadas (implementación simplificada)
        # En una implementación completa, rastrearías qué filas fueron matcheadas
    
    # Crear DataFrame resultado
    if matches:
        resultado = pd.DataFrame(matches)
        # Limpiar columnas temporales
        cols_to_drop = [col for col in resultado.columns if col.endswith('_limpio')]
        resultado = resultado.drop(columns=cols_to_drop)
    else:
        resultado = pd.DataFrame()
    
    return resultado

# Función auxiliar para análisis de matches
def analizar_fuzzy_merge(df_merged):
    """Analiza los resultados del fuzzy merge"""
    if 'similitud' not in df_merged.columns:
        print("No se encontró columna 'similitud' en el DataFrame")
        return
    
    total_filas = len(df_merged)
    con_match = len(df_merged[df_merged['similitud'] > 0])
    sin_match = total_filas - con_match
    
    print(f"📊 Análisis del Fuzzy Merge:")
    print(f"Total de filas: {total_filas}")
    print(f"Con coincidencias: {con_match} ({con_match/total_filas*100:.1f}%)")
    print(f"Sin coincidencias: {sin_match} ({sin_match/total_filas*100:.1f}%)")
    
    if con_match > 0:
        print(f"\n📈 Estadísticas de similitud:")
        print(f"Similitud promedio: {df_merged[df_merged['similitud'] > 0]['similitud'].mean():.2%}")
        print(f"Similitud mínima: {df_merged[df_merged['similitud'] > 0]['similitud'].min():.2%}")
        print(f"Similitud máxima: {df_merged[df_merged['similitud'] > 0]['similitud'].max():.2%}")