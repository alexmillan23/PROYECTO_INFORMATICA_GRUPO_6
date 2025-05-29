class NavPoint:
    def __init__(self, number, name, latitude, longitude):
        # Inicializa un nuevo punto de navegación con número, nombre, latitud y longitud
        self.number = number
        self.name = name
        self.latitude = latitude
        self.longitude = longitude


def navpoint_to_str(navpoint):
    """Convierte un punto de navegación a su representación en cadena de texto"""
    # Retorna una cadena con el nombre y las coordenadas del punto de navegación
    return f"{navpoint.name}: ({navpoint.latitude}, {navpoint.longitude})"

def get_coords(navpoint):
    """Obtiene las coordenadas de un punto de navegación"""
    # Retorna una tupla con la latitud y longitud del punto de navegación
    return (navpoint.latitude, navpoint.longitude)
