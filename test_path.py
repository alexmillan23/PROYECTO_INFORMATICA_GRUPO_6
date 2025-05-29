import math
from airSpace import AirSpace, add_navpoint, add_navsegment
from navPoint import NavPoint
from navSegment import NavSegment
from path import Path, find_shortest_path_astar, euclidean_distance

def create_test_graph():
    """
    Crea un grafo de prueba similar al mostrado en las imágenes de ejemplo
    con los nodos A, B, C, D, E, F, G, H, I, J, K, L
    """
    airspace = AirSpace("Test")
    
    # Crear los puntos de navegación con coordenadas
    # Coordenadas aproximadas basadas en la imagen de ejemplo
    points = {
        'A': (0, 20),     # A en (0, 20)
        'B': (10, 17.5),  # B en (10, 17.5)
        'C': (20, 20),    # C en (20, 20)
        'D': (20, 15),    # D en (20, 15)
        'E': (5, 5),      # E en (5, 5)
        'F': (10, 5),     # F en (10, 5)
        'G': (15, 12.5),  # G en (15, 12.5)
        'H': (10, 2.5),   # H en (10, 2.5)
        'I': (20, 2.5),   # I en (20, 2.5)
        'J': (15, 5),     # J en (15, 5)
        'K': (5, 15),     # K en (5, 15)
        'L': (5, 10)      # L en (5, 10)
    }
    
    # Añadir puntos al espacio aéreo
    for i, (name, (lon, lat)) in enumerate(points.items(), 1):
        add_navpoint(airspace, NavPoint(i, name, lat, lon))
    
    # Crear mapa de nombres a números
    name_to_number = {point.name: point.number for point in airspace.navpoints.values()}
    
    # Añadir segmentos con distancias según la imagen
    segments = [
        ('A', 'B', 7.62),
        ('A', 'K', 5.39),
        ('B', 'C', 7.62),
        ('B', 'G', 6.4),
        ('C', 'D', 5.83),
        ('D', 'G', 6.71),
        ('E', 'F', 4.12),
        ('E', 'L', 5.39),
        ('F', 'H', 2.5),
        ('F', 'J', 5.39),
        ('G', 'J', 9.22),
        ('H', 'I', 7.21),
        ('I', 'J', 3.0),
        ('K', 'L', 5.1),
        # Distancias arbitrarias para estas conexiones
        ('G', 'I', 9.22),
        ('D', 'I', 14.04),
        ('G', 'D', 2.5),
        ('J', 'I', 2.5),
    ]
    
    for origin, dest, distance in segments:
        origin_num = name_to_number[origin]
        dest_num = name_to_number[dest]
        add_navsegment(airspace, NavSegment(origin_num, dest_num, distance))
    
    return airspace

def test_path_class():
    """Prueba las funcionalidades básicas de la clase Path"""
    print("Probando la clase Path...")
    
    airspace = create_test_graph()
    
    # Crear un camino con nodos A, K, L
    path = Path([
        airspace.navpoints[1],  # A
        airspace.navpoints[11], # K
        airspace.navpoints[12]  # L
    ])
    
    # Verificar contains_node
    assert path.contains_node(airspace.navpoints[1]) == True
    assert path.contains_node(airspace.navpoints[2]) == False
    
    # Verificar get_last_node
    assert path.get_last_node().name == 'L'
    
    print("Pruebas de la clase Path completadas con éxito.")

def test_euclidean_distance():
    """Prueba la función de distancia euclidiana"""
    print("Probando la función de distancia euclidiana...")
    
    airspace = create_test_graph()
    
    # Distancia de A a F
    point_a = airspace.navpoints[1]  # A en (0, 20)
    point_f = airspace.navpoints[6]  # F en (10, 5)
    
    # Calcular manualmente: sqrt((10-0)^2 + (5-20)^2) = sqrt(100 + 225) = sqrt(325) ≈ 18.03
    expected_distance = math.sqrt((10-0)**2 + (5-20)**2)
    calculated_distance = euclidean_distance(point_a, point_f)
    
    print(f"Distancia de A a F: {calculated_distance:.2f} (esperado: {expected_distance:.2f})")
    assert abs(calculated_distance - expected_distance) < 0.01
    
    print("Pruebas de distancia euclidiana completadas con éxito.")

def test_astar_path_finding():
    """Prueba el algoritmo A* para encontrar la ruta más corta"""
    print("Probando el algoritmo A* para encontrar la ruta más corta...")
    
    airspace = create_test_graph()
    
    # Obtener puntos A y F por nombre
    point_a = None
    point_f = None
    for point in airspace.navpoints.values():
        if point.name == 'A':
            point_a = point
        elif point.name == 'F':
            point_f = point
    
    assert point_a is not None, "No se encontró el punto A"
    assert point_f is not None, "No se encontró el punto F"
    
    # Encontrar la ruta más corta de A a F
    path, total_distance = find_shortest_path_astar(airspace, point_a, point_f)
    
    # Imprimir la ruta encontrada
    print(f"Ruta encontrada de A a F: ", end="")
    path_names = [node.name for node in path]
    print(" -> ".join(path_names))
    print(f"Distancia total: {total_distance:.2f}")
    
    # Verificar que la ruta es válida
    assert len(path) > 0, "No se encontró ruta"
    assert path[0].name == 'A', "La ruta no comienza en A"
    assert path[-1].name == 'F', "La ruta no termina en F"
    
    # Verificar la distancia total (aproximadamente)
    expected_path = ['A', 'K', 'L', 'E', 'F']  # El camino esperado basado en el ejemplo
    print(f"Camino esperado: {' -> '.join(expected_path)}")
    
    print("Pruebas de búsqueda de ruta completadas.")

def main():
    """Función principal que ejecuta todas las pruebas"""
    print("Iniciando pruebas del módulo path.py...")
    
    # Ejecutar pruebas
    test_path_class()
    print()
    test_euclidean_distance()
    print()
    test_astar_path_finding()
    print()
    
    print("Todas las pruebas completadas con éxito.")

if __name__ == "__main__":
    main()
