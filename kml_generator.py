"""
Módulo Generador de KML para Navegación Aérea.
Este módulo maneja la generación de archivos KML para visualización en Google Earth
de elementos del espacio aéreo incluyendo puntos de navegación, aeropuertos, segmentos y rutas.
"""

# Constantes globales para el encabezado y pie de KML
KML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n'
KML_FOOTER = '</Document>\n</kml>'

def generate_point_kml(name, longitude, latitude, description=None, icon_style=None):
    """Generar KML para un único punto"""
    kml_content = f'  <Placemark>\n    <name>{name}</name>\n'
    
    if description:
        kml_content += f'    <description>{description}</description>\n'
        
    if icon_style:
        kml_content += f'    <styleUrl>#{icon_style}</styleUrl>\n'
        
    kml_content += f'    <Point>\n      <coordinates>{longitude},{latitude},0</coordinates>\n    </Point>\n  </Placemark>\n'
    return kml_content

def generate_line_kml(name, coordinates, description=None, line_style=None, z_index=0):
    """Generar KML para una línea (ruta o segmento)"""
    kml_content = f'  <Placemark>\n    <name>{name}</name>\n'
    
    if description:
        kml_content += f'    <description>{description}</description>\n'
        
    if line_style:
        kml_content += f'    <styleUrl>#{line_style}</styleUrl>\n'
        
    # Añadir z-index para controlar el orden de renderizado    
    if z_index > 0:
        kml_content += f'    <drawOrder>{z_index}</drawOrder>\n'
        
    kml_content += '    <LineString>\n      <altitudeMode>clampToGround</altitudeMode>\n      <extrude>1</extrude>\n      <tessellate>1</tessellate>\n      <coordinates>\n'
    
    # Añadir coordenadas en formato: longitud,latitud,0
    for lon, lat in coordinates:
        kml_content += f'        {lon},{lat},0\n'
        
    kml_content += '      </coordinates>\n    </LineString>\n  </Placemark>\n'
    return kml_content

def add_style(style_id, color, icon=None, width=None):
    """Añadir una definición de estilo al KML"""
    style = f'  <Style id="{style_id}">\n'
    
    if icon:
        style += f'    <IconStyle>\n      <color>{color}</color>\n      <Icon>\n        <href>{icon}</href>\n      </Icon>\n    </IconStyle>\n'
    else:
        style += f'    <LineStyle>\n      <color>{color}</color>\n      <width>{width}</width>\n    </LineStyle>\n'
        
    style += '  </Style>\n'
    return style

def generate_airspace_kml(airspace):
    """Generar KML para todo el espacio aéreo"""
    kml_content = KML_HEADER
    
    # Añadir estilos
    kml_content += add_style("navpoint_style", "ff0000ff", icon="http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png")
    kml_content += add_style("airport_style", "ff00ff00", icon="http://maps.google.com/mapfiles/kml/shapes/airports.png")
    kml_content += add_style("segment_style", "ffffff00", width="1")  # Color celeste en formato AABBGGRR (el color aparece invertido en KML)
    kml_content += add_style("path_style", "ff800080", width="4")  # Morado verdadero (menos rosa)
    
    # Añadir puntos de navegación
    for number, point in airspace.navpoints.items():
        description = f"Punto de Navegación #{number}"
        kml_content += generate_point_kml(
            point.name, 
            point.longitude, 
            point.latitude, 
            description,
            "navpoint_style"
        )
    
    # Añadir aeropuertos
    for name, airport in airspace.navairports.items():
        # Encontrar un punto de navegación asociado con este aeropuerto para obtener coordenadas
        airport_coords = None
        for point in airspace.navpoints.values():
            if point.name == name or point.number in airport.sids or point.number in airport.stars:
                airport_coords = (point.longitude, point.latitude)
                break
        
        if airport_coords:
            description = f"Aeropuerto: {name}"
            kml_content += generate_point_kml(
                name,
                airport_coords[0],
                airport_coords[1],
                description,
                "airport_style"
            )
    
    # Añadir segmentos
    for segment in airspace.navsegments:
        origin = airspace.navpoints.get(segment.origin_number)
        destination = airspace.navpoints.get(segment.destination_number)
        
        if origin and destination:
            segment_name = f"Segmento {origin.name} - {destination.name}"
            coordinates = [(origin.longitude, origin.latitude), 
                           (destination.longitude, destination.latitude)]
            
            description = f"Distancia: {segment.distance:.2f} km"
            kml_content += generate_line_kml(
                segment_name,
                coordinates,
                description,
                "segment_style",
                z_index=1  # Z-index base para los segmentos normales
            )
    
    kml_content += KML_FOOTER
    return kml_content
    
def generate_path_kml(path_name, path_points):
    """Generar KML para una ruta específica"""
    kml_content = KML_HEADER
    
    # Añadir estilos
    kml_content += add_style("point_style", "ff0000ff", icon="http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png")
    kml_content += add_style("path_style", "ff800080", width="3")  # Morado verdadero (menos rosa)
    
    # Añadir puntos de la ruta
    for point in path_points:
        kml_content += generate_point_kml(
            point.name, 
            point.longitude, 
            point.latitude, 
            f"Punto de Navegación: {point.name}",
            "point_style"
        )
    
    # Añadir la línea de la ruta
    if len(path_points) >= 2:
        coordinates = [(point.longitude, point.latitude) for point in path_points]
        kml_content += generate_line_kml(
            path_name,
            coordinates,
            f"Ruta con {len(path_points)} puntos",
            "path_style",
            z_index=10  # Z-index alto para que se vea encima de todo
        )
    
    kml_content += KML_FOOTER
    return kml_content

def generate_neighbors_kml(central_point, neighbors, airspace=None):
    """Generar KML para un punto central y sus vecinos"""
    kml_content = KML_HEADER
    
    # Añadir estilos
    kml_content += add_style("central_point_style", "ff0000ff", icon="http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png")
    kml_content += add_style("neighbor_point_style", "ff00ff00", icon="http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png")
    kml_content += add_style("connection_style", "ffaa0000", width="3")  # Azul oscuro, más grueso
    
    # Añadir punto central
    kml_content += generate_point_kml(
        central_point.name, 
        central_point.longitude, 
        central_point.latitude, 
        f"Punto Central: {central_point.name}",
        "central_point_style"
    )
    
    # Añadir vecinos y sus conexiones al punto central
    for neighbor_info in neighbors:
        neighbor = neighbor_info[0]
        distance = neighbor_info[1]
        
        # Añadir punto vecino
        kml_content += generate_point_kml(
            neighbor.name, 
            neighbor.longitude, 
            neighbor.latitude, 
            f"Vecino: {neighbor.name}, Distancia: {distance:.2f}",
            "neighbor_point_style"
        )
        
        # Si tenemos acceso al espacio aéreo completo, usamos los segmentos originales
        if airspace:
            segment_found = False
            for segment in airspace.navsegments:
                if ((segment.origin_number == central_point.number and segment.destination_number == neighbor.number) or
                    (segment.destination_number == central_point.number and segment.origin_number == neighbor.number)):
                    
                    segment_name = f"Conexión: {central_point.name} - {neighbor.name}"
                    coordinates = [
                        (central_point.longitude, central_point.latitude),
                        (neighbor.longitude, neighbor.latitude)
                    ]
                    
                    kml_content += generate_line_kml(
                        segment_name,
                        coordinates,
                        f"Distancia: {segment.distance:.2f} km",
                        "connection_style",
                        z_index=5  # Z-index intermedio
                    )
                    segment_found = True
                    break
                    
            # Si no encontramos un segmento existente, creamos una línea directa
            if not segment_found:
                segment_name = f"Conexión: {central_point.name} - {neighbor.name}"
                coordinates = [
                    (central_point.longitude, central_point.latitude),
                    (neighbor.longitude, neighbor.latitude)
                ]
                
                kml_content += generate_line_kml(
                    segment_name,
                    coordinates,
                    f"Distancia: {distance:.2f} km",
                    "connection_style",
                    z_index=5  # Z-index intermedio
                )
        else:
            # Crear una línea directa
            segment_name = f"Conexión: {central_point.name} - {neighbor.name}"
            coordinates = [
                (central_point.longitude, central_point.latitude),
                (neighbor.longitude, neighbor.latitude)
            ]
            
            kml_content += generate_line_kml(
                segment_name,
                coordinates,
                f"Distancia: {distance:.2f} km",
                "connection_style",
                z_index=5  # Z-index intermedio
            )
    
    kml_content += KML_FOOTER
    return kml_content

def save_kml_to_file(kml_content, filename):
    """Guardar contenido KML en un archivo"""
    try:
        with open(filename, 'w') as kml_file:
            kml_file.write(kml_content)
        return True
    except Exception as e:
        print(f"Error al guardar archivo KML: {e}")
        return False
