import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import colorsys
import matplotlib.colors as mcolors

def generate_chroma_palette(hex_color, steps=100):
    """
    Generate an ascending chroma palette from a given hex color.
    
    Parameters:
        hex_color (str): The input color in hex format (e.g., '#3498db').
        steps (int): Number of colors to generate (default is 20).
        
    Returns:
        dict: A dictionary with step indices as keys and hex colors as values.
    """
    # Convert hex to RGB (0-1 scale)
    rgb = mcolors.hex2color(hex_color)
    
    # Convert RGB to HLS
    h, l, s = colorsys.rgb_to_hls(*rgb)
    
    # Generate colors with ascending lightness
    palette = {}
    for i in range(steps):
        new_l = min(1, l + (1 - l) * (i / (steps - 1)))  # Increase lightness gradually
        new_rgb = colorsys.hls_to_rgb(h, new_l, s)
        new_hex = mcolors.to_hex(new_rgb)
        palette[steps-i] = new_hex
    
    return palette


def plot_map(data_geojson, id_column, name_column, value_column, color_map, line_color='#F3F3F3', line_width=1, mostrar_nombres=True):
    """
    Función para generar mapas con datos geoespaciales y valores asociados.

    Parámetros:
    - data_geojson: GeoDataFrame con datos geoespaciales y valores a mapear.
    - id_column: Nombre de la columna que contiene los códigos únicos de las unidades geográficas.
    - name_column: Nombre de la columna con los nombres de las unidades geográficas.
    - value_column: Nombre de la columna con los valores a mapear (usado para color).
    - color_map: Diccionario que asigna colores a los valores del `value_column`.
    - line_color: Color del borde de los polígonos.
    - line_width: Ancho del borde de los polígonos.
    - mostrar_nombres: Booleano para indicar si se deben mostrar los nombres en el mapa.

    Retorna:
    - fig, ax: Figura y ejes de Matplotlib con el mapa generado.
    """
    fig, ax = plt.subplots()

    # Filtrar datos válidos con geometría
    data_to_plot = data_geojson.dropna(subset=['geometry'])

    # Dibujar los polígonos
    data_to_plot.plot(ax=ax, edgecolor=line_color, linewidth=line_width,aspect=1)

    # Anotaciones en los centroides
    for _, row in data_to_plot.iterrows():
        centroid = row.geometry.centroid
        text = f"{row[id_column]}\n{row[name_column]}" if mostrar_nombres else f"{row[id_column]}"
        ax.annotate(text=text, xy=(centroid.x, centroid.y),
                    xytext=(3, 3), textcoords="offset points",
                    ha='center', va='center', fontsize=3 if mostrar_nombres else 8, weight='bold')

    # Colorear el mapa según los valores
    data_to_plot.plot(ax=ax, linewidth=line_width,
                      color=[color_map.get(x, "#FFFFFF") for x in data_to_plot[value_column]],
                      edgecolor=line_color)

    # Configuración del gráfico
    ax.set_title("")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor('none')
    fig.patch.set_alpha(0.0)
    for spine in ax.spines.values():
        spine.set_visible(False)

    return fig, ax

def assign_quintiles(series: pd.Series) -> pd.Series:
    """
    Asigna un número del 1 al 5 a cada valor de la serie dependiendo del quintil en el que se encuentre.
    """
    return np.ceil(series / 1).astype(int)



