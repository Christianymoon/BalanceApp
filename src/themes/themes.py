class Theme():
    pass


# class DarkMode(Theme):
#     bg = "#04060A"
#     fg = "#0A0E15"
#     text_primary = "#FFFFFF"
#     text_secondary = "#d3d3d3"
#     green_color = "#3DDC97"
#     red_color = "#FF6B6B"
#     blue_color = "#00C2FF"
#     purple_color = "#B18CFF"


class DarkMode(Theme):
    bg = "#121212"
    fg = "#1E1E1E"
    text_primary = "#D5D5D5"
    text_secondary = "#8A8A8A"
    green_color = "#7A9E7E"
    red_color = "#C07070"
    blue_color = "#7E9BB5"
    purple_color = "#9A8EAD"


class LigthMode(Theme):
    bg = "#FFFFFF"          # Fondo principal blanco
    fg = "#F4F4F4"          # Superficie / cards gris suave
    text_primary = "#000000"   # Texto principal negro puro
    text_secondary = "#666666"  # Texto secundario / subtítulos
    green_color = "#00E676"    # Verde positivo / ganancias (GBM)
    red_color = "#FF5252"      # Rojo negativo / pérdidas (GBM)
    blue_color = "#00C2FF"     # Azul índigo acento principal (GBM+)
    purple_color = "#B18CFF"
