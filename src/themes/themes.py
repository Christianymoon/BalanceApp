class Theme():
    pass


class DarkMode(Theme):
    bg = "#04060A"             # Fondo principal oscuro
    fg = "#0A0E15"             # Superficie muy oscura para separar cards
    text_primary = "#FFFFFF"   # Texto principal gris claro
    text_secondary = "#d3d3d3"  # Texto secundario gris más claro
    green_color = "#3DDC97"    # Verde neón para ganancias
    red_color = "#FF6B6B"      # Rojo para pérdidas
    blue_color = "#00C2FF"     # Azul neón para acentos
    purple_color = "#B18CFF"


class LigthMode(Theme):
    bg = "#FFFFFF"          # Fondo principal blanco
    fg = "#F4F4F4"          # Superficie / cards gris suave
    text_primary = "#000000"   # Texto principal negro puro
    text_secondary = "#666666"  # Texto secundario / subtítulos
    green_color = "#00E676"    # Verde positivo / ganancias (GBM)
    red_color = "#FF5252"      # Rojo negativo / pérdidas (GBM)
    blue_color = "#00C2FF"     # Azul índigo acento principal (GBM+)
    purple_color = "#B18CFF"
