import math

class Path:
    """
    Clase que representa un camino en el espacio aéreo.
    Utilizada en el algoritmo A* para encontrar la ruta más corta.
    """
    def __init__(self, nodes=None):
        self.nodes = nodes or []
        self.real_cost = 0.0  # Costo real del camino (suma de distancias de segmentos)
        self.estimated_cost = 0.0  # Costo estimado total (real + estimación heurística)
    
    def copy(self):
        """Crea una copia del camino"""
        new_path = Path(self.nodes.copy())
        new_path.real_cost = self.real_cost
        new_path.estimated_cost = self.estimated_cost
        return new_path
    
    def add_node(self, node, segment_distance):
        """
        Añade un nodo al camino y actualiza el costo real
        """
        self.nodes.append(node)
        self.real_cost += segment_distance
    
    def contains_node(self, node):
        """
        Verifica si el nodo ya está en el camino
        """
        return node in self.nodes
    
    def get_last_node(self):
        """
        Retorna el último nodo del camino
        """
        if not self.nodes:
            return None
        return self.nodes[-1]
    
    def cost_to_node(self, node):
        """
        Retorna el costo desde el origen hasta un nodo específico en el camino.
        Retorna -1 si el nodo no está en el camino.
        """
        if not self.contains_node(node):
            return -1
        
        index = self.nodes.index(node)
        if index == 0:
            return 0
        
        # Calcular la suma de distancias hasta el nodo
        cost = 0.0
        for i in range(index):
            segment_cost = calculate_segment_distance(self.nodes[i], self.nodes[i+1])
            cost += segment_cost
        
        return cost
    
    def __str__(self):
        """Representación en string del camino"""
        node_names = [str(node) for node in self.nodes]
        return "[" + " - ".join(node_names) + "]"

def euclidean_distance(point1, point2):
    """
    Calcula la distancia euclidiana entre dos puntos
    """
    dx = point1.longitude - point2.longitude
    dy = point1.latitude - point2.latitude
    return math.sqrt(dx*dx + dy*dy)

def calculate_segment_distance(point1, point2):
    """
    Obtiene la distancia del segmento entre dos puntos.
    Devuelve únicamente la distancia definida en el segmento si existe.
    """
    # Buscamos el segmento directo entre los puntos
    for segment in point1.airspace.navsegments:
        if ((segment.origin_number == point1.number and segment.destination_number == point2.number) or
            (segment.destination_number == point1.number and segment.origin_number == point2.number)):
            return segment.distance
    
    # Si no hay segmento directo, devolvemos un valor alto
    return float('inf')

def find_shortest_path_astar(airspace, origin, destination, max_iterations=5000, debug=False, custom_cost_func=None, recursion_level=0):
    """
    Implementación del algoritmo A* para encontrar la ruta más corta
    entre dos puntos en el espacio aéreo.
    
    Args:
        airspace: Instancia de AirSpace
        origin: Punto de origen (número, NavPoint o código de aeropuerto)
        destination: Punto de destino (número, NavPoint o código de aeropuerto)
        max_iterations: Número máximo de iteraciones
        debug: Si es True, imprime información de depuración
        custom_cost_func: Función opcional para calcular el costo de un segmento.
                          Recibe (nodo1, nodo2, distancia_base) y retorna un costo.
        recursion_level: Nivel de recursión para prevenir llamadas infinitas
    
    Returns:
        Una tupla con (camino, distancia_total) donde camino es una lista
        de NavPoint y distancia_total es la distancia total en km.
    """
    # Verificar si origin o destination son códigos de aeropuerto
    origin_is_airport = isinstance(origin, str) and origin.startswith(("LE", "LF"))
    dest_is_airport = isinstance(destination, str) and destination.startswith(("LE", "LF"))
    
    # Prevenir recursión infinita
    if recursion_level > 1:
        print(f"ERROR: Recursión excesiva en find_shortest_path_astar (nivel {recursion_level})")
        return [], 0
    
    # Manejar aeropuertos
    if origin_is_airport or dest_is_airport:
        if debug:
            print(f"Procesando búsqueda con aeropuertos: Origen={origin}, Destino={destination}")
        
        # Buscar la mejor ruta entre todos los pares posibles de SIDs y STARs
        best_path = []
        best_distance = float('inf')
        
        # Obtener el aeropuerto de origen si es necesario
        origin_airport = None
        origin_points = []
        if origin_is_airport:
            origin_airport = airspace.navairports.get(origin)
            if debug:
                print(f"Aeropuerto origen: {origin}, encontrado: {origin_airport is not None}")
                if origin_airport:
                    print(f"SIDs de {origin}: {origin_airport.sids}")
            
            if origin_airport and origin_airport.sids:
                # Usar los SIDs como puntos de origen
                for sid_num in origin_airport.sids:
                    sid_point = airspace.navpoints.get(sid_num)
                    if sid_point:
                        origin_points.append(sid_point)
                        if debug:
                            print(f"Punto SID encontrado: {sid_point.name} (#{sid_point.number})")
            
            if not origin_points:
                if debug:
                    print(f"No se encontraron SIDs para el aeropuerto {origin}")
                return [], 0
        else:
            # Convertir número a objeto NavPoint si es necesario
            if isinstance(origin, int):
                origin = airspace.navpoints.get(origin)
            origin_points = [origin]
        
        # Obtener el aeropuerto de destino si es necesario
        dest_airport = None
        dest_points = []
        if dest_is_airport:
            dest_airport = airspace.navairports.get(destination)
            if debug:
                print(f"Aeropuerto destino: {destination}, encontrado: {dest_airport is not None}")
                if dest_airport:
                    print(f"STARs de {destination}: {dest_airport.stars}")
            
            if dest_airport and dest_airport.stars:
                # Usar los STARs como puntos de destino
                for star_num in dest_airport.stars:
                    star_point = airspace.navpoints.get(star_num)
                    if star_point:
                        dest_points.append(star_point)
                        if debug:
                            print(f"Punto STAR encontrado: {star_point.name} (#{star_point.number})")
            
            if not dest_points:
                if debug:
                    print(f"No se encontraron STARs para el aeropuerto {destination}")
                return [], 0
        else:
            # Convertir número a objeto NavPoint si es necesario
            if isinstance(destination, int):
                destination = airspace.navpoints.get(destination)
            dest_points = [destination]
        
        # Probar todas las combinaciones de puntos de origen y destino
        for o_point in origin_points:
            for d_point in dest_points:
                if debug:
                    print(f"Probando ruta desde {o_point.name} (#{o_point.number}) a {d_point.name} (#{d_point.number})")
                
                # Usar el A* estándar entre estos dos puntos (SIN RECURSIÓN)
                path, distance = find_shortest_path_astar(
                    airspace, o_point, d_point, max_iterations, debug, custom_cost_func, 
                    recursion_level=recursion_level+1
                )
                
                # Si encontramos una ruta mejor, la guardamos
                if path and distance < best_distance:
                    best_path = path
                    best_distance = distance
                    
                    if debug:
                        print(f"Nueva mejor ruta encontrada: {distance} km")
        
        # Si se encontró alguna ruta, la devolvemos
        if best_path:
            if debug:
                print(f"Ruta final: {len(best_path)} puntos, {best_distance} km")
            return best_path, best_distance
        
        # Si no se encontró ninguna ruta
        return [], 0
    
    # El resto de la función para búsqueda entre puntos normales
    # Convertir números a objetos NavPoint si es necesario
    if isinstance(origin, int):
        origin = airspace.navpoints.get(origin)
    if isinstance(destination, int):
        destination = airspace.navpoints.get(destination)
    
    if not origin or not destination:
        return [], 0
    
    if debug:
        print(f"Buscando ruta de {origin.name} (#{origin.number}) a {destination.name} (#{destination.number})")
    
    # Si origen y destino son el mismo punto
    if origin.number == destination.number:
        return [origin], 0
    
    # Inicializar el camino inicial con solo el nodo de origen
    initial_path = Path([origin])
    
    # Usamos distancia de segmento para heurística. Si no hay segmento, usamos un valor bajo
    # para que al menos se considere esta ruta
    try:
        heuristic_distance = calculate_segment_distance(origin, destination)
        if heuristic_distance == float('inf'):
            # Si no hay segmento directo, usamos un valor bajo como heurística
            heuristic_distance = 1.0  # Valor bajo para que no descarte esta ruta
    except:
        heuristic_distance = 1.0  # Valor bajo por defecto
    
    initial_path.estimated_cost = heuristic_distance
    
    # Lista de caminos a explorar
    current_paths = [initial_path]
    
    # Conjunto de nodos visitados para evitar ciclos
    visited = set()
    
    # Contador para limitar el número de iteraciones
    iterations = 0
    
    while current_paths and iterations < max_iterations:
        iterations += 1
        
        # Encontrar el camino con menor costo estimado
        current_paths.sort(key=lambda p: p.estimated_cost)
        current_path = current_paths.pop(0)
        
        # Obtener el último nodo del camino actual
        current_node = current_path.get_last_node()
        
        if debug and iterations % 100 == 0:
            print(f"Iteración {iterations}, explorando {current_node.name}, caminos restantes: {len(current_paths)}")
        
        # Si ya hemos llegado al destino, retornamos el camino
        if current_node.number == destination.number:
            if debug:
                print(f"¡Ruta encontrada! Longitud: {len(current_path.nodes)}, Distancia: {current_path.real_cost}")
            return current_path.nodes, current_path.real_cost
        
        # Marcar el nodo como visitado
        visited.add(current_node.number)
        
        # Obtener los vecinos del nodo actual
        neighbors = []
        
        # Primero, añadir segmentos en la dirección correcta
        for segment in airspace.navsegments:
            if segment.origin_number == current_node.number:
                neighbors.append((segment.destination_number, segment.distance))  
        
        if debug and len(neighbors) == 0:
            print(f"¡Advertencia! El nodo {current_node.name} no tiene segmentos conectados")
        
        # Expandir el camino con cada vecino
        for neighbor_number, segment_distance in neighbors:
            # Evitar nodos ya visitados
            if neighbor_number in visited:
                continue
            
            # Evitar nodos que ya están en el camino para prevenir ciclos
            if any(node.number == neighbor_number for node in current_path.nodes):
                continue
            
            neighbor = airspace.navpoints.get(neighbor_number)
            if not neighbor:
                if debug:
                    print(f"¡Error! Vecino {neighbor_number} no encontrado en el mapa")
                continue
            
            # Crear una copia del camino actual
            new_path = current_path.copy()
            
            # Aplicar función de costo personalizada si se proporciona
            if custom_cost_func:
                adjusted_distance = custom_cost_func(current_node, neighbor, segment_distance)
            else:
                adjusted_distance = segment_distance
            
            # Añadir el nuevo nodo al camino
            new_path.add_node(neighbor, adjusted_distance)
            
            # Calcular el costo estimado total (real + heurística simplificada)
            # Usamos como heurística solo un valor constante pequeño para priorizar rutas más cortas
            # pero sin distorsionar la búsqueda del camino más corto
            heuristic = 1.0  # Valor constante bajo en lugar de distancia euclidiana
            new_path.estimated_cost = new_path.real_cost + heuristic
            
            # Añadir el nuevo camino a la lista de caminos a explorar
            current_paths.append(new_path)
    
    # Si no encontramos un camino
    if debug:
        print(f"No se encontró ruta después de {iterations} iteraciones")
        if iterations >= max_iterations:
            print("Se alcanzó el límite máximo de iteraciones")
    
    return [], 0


def find_multiple_paths_astar(airspace, origin, destination, max_paths=3, debug=False):
    """
    Encuentra múltiples rutas entre dos puntos usando el algoritmo A*.
    
    Args:
        airspace: Instancia de AirSpace
        origin: Punto de origen (número, NavPoint o código de aeropuerto)
        destination: Punto de destino (número, NavPoint o código de aeropuerto)
        max_paths: Número máximo de rutas a encontrar
    
    Returns:
        Una lista de tuplas (distancia, [número de puntos]), cada una representando una ruta.
    """
    # Verificar si origin o destination son códigos de aeropuerto
    origin_is_airport = isinstance(origin, str) and origin.startswith(("LE", "LF"))
    dest_is_airport = isinstance(destination, str) and destination.startswith(("LE", "LF"))
    
    # Si alguno es un aeropuerto, buscar todas las combinaciones de SIDs y STARs
    if origin_is_airport or dest_is_airport:
        if debug:
            print(f"Buscando múltiples rutas con aeropuertos: Origen={origin}, Destino={destination}")
        
        all_paths = []
        
        # Obtener el aeropuerto de origen si es necesario
        origin_airport = None
        origin_points = []
        if origin_is_airport:
            origin_airport = airspace.navairports.get(origin)
            if debug:
                print(f"Aeropuerto origen: {origin}, encontrado: {origin_airport is not None}")
                if origin_airport:
                    print(f"SIDs de {origin}: {origin_airport.sids}")
            
            if origin_airport and origin_airport.sids:
                # Usar los SIDs como puntos de origen
                for sid_num in origin_airport.sids:
                    sid_point = airspace.navpoints.get(sid_num)
                    if sid_point:
                        origin_points.append(sid_point)
            
            if not origin_points:
                if debug:
                    print(f"No se encontraron SIDs para el aeropuerto {origin}")
                return []
        else:
            # Convertir número a objeto NavPoint si es necesario
            if isinstance(origin, int):
                origin = airspace.navpoints.get(origin)
            origin_points = [origin]
        
        # Obtener el aeropuerto de destino si es necesario
        dest_airport = None
        dest_points = []
        if dest_is_airport:
            dest_airport = airspace.navairports.get(destination)
            if debug:
                print(f"Aeropuerto destino: {destination}, encontrado: {dest_airport is not None}")
                if dest_airport:
                    print(f"STARs de {destination}: {dest_airport.stars}")
            
            if dest_airport and dest_airport.stars:
                # Usar los STARs como puntos de destino
                for star_num in dest_airport.stars:
                    star_point = airspace.navpoints.get(star_num)
                    if star_point:
                        dest_points.append(star_point)
            
            if not dest_points:
                if debug:
                    print(f"No se encontraron STARs para el aeropuerto {destination}")
                return []
        else:
            # Convertir número a objeto NavPoint si es necesario
            if isinstance(destination, int):
                destination = airspace.navpoints.get(destination)
            dest_points = [destination]
        
        # Probar todas las combinaciones de puntos de origen y destino
        for o_point in origin_points:
            for d_point in dest_points:
                if debug:
                    print(f"Probando múltiples rutas desde {o_point.name} (#{o_point.number}) a {d_point.name} (#{d_point.number})")
                
                # Encontrar una ruta estándar A* entre estos dos puntos
                path, distance = find_shortest_path_astar(airspace, o_point, d_point, debug=debug)
                
                # Si encontramos una ruta, la agregamos a la lista
                if path:
                    path_numbers = [p.number for p in path]
                    all_paths.append((distance, path_numbers))
                    if debug:
                        print(f"Ruta encontrada: {len(path)} puntos, {distance} km")
        
        # Ordenar las rutas por distancia y devolver hasta max_paths
        all_paths.sort(key=lambda x: x[0])
        return all_paths[:max_paths]
    
    # El resto de la función para búsqueda entre puntos normales
    # Convertir números a objetos NavPoint si es necesario
    if isinstance(origin, int):
        origin = airspace.navpoints.get(origin)
    if isinstance(destination, int):
        destination = airspace.navpoints.get(destination)
    
    if not origin or not destination:
        return []
    
    # Encontrar la primera ruta (la más corta) usando A*
    first_path, first_distance = find_shortest_path_astar(airspace, origin, destination)
    
    if not first_path:
        return []  # No se encontró ninguna ruta
    
    # Extraer solo los números de los puntos para facilitar la comparación
    first_path_nums = [point.number for point in first_path]
    
    # Añadir la primera ruta a la lista de resultados
    result_paths = [(first_distance, first_path_nums)]
    
    # Conjunto de segmentos usados en la primera ruta
    used_segments = set()
    for i in range(len(first_path) - 1):
        segment = (first_path[i].number, first_path[i+1].number)
        used_segments.add(segment)
    
    # Factor de penalización para segmentos ya utilizados - incrementamos el valor inicial
    penalty_factor = 5.0
    
    # Conjunto para llevar un seguimiento de los puntos intermedios penalizados
    # Esto nos permitirá generar rutas más diversas
    penalized_points = set()
    
    # Intentar encontrar rutas adicionales
    for attempt in range(max_paths * 3):  # Aumentamos el número de intentos
        if len(result_paths) >= max_paths:
            break
            
        # Seleccionar puntos a penalizar de la ruta más reciente
        if attempt > 0 and attempt % 3 == 0:
            latest_path = [airspace.navpoints.get(num) for num in result_paths[-1][1]]
            # Seleccionar algunos puntos intermedios para penalizar
            if len(latest_path) > 3:  # Ignorar origen y destino
                # Penalizar un punto intermedio diferente en cada intento
                mid_idx = (attempt // 3) % (len(latest_path) - 2) + 1
                if mid_idx < len(latest_path) - 1:
                    mid_point = latest_path[mid_idx]
                    penalized_points.add(mid_point.number)
        
        # Función de costo personalizada que penaliza segmentos ya utilizados
        # y evita pasar por ciertos puntos intermedios
        def custom_cost_func(node1, node2, base_distance):
            # Penalizar segmentos ya utilizados
            segment = (node1.number, node2.number)
            if segment in used_segments:
                return base_distance * penalty_factor
            
            # Penalizar puntos intermedios seleccionados
            if node2.number in penalized_points and node2.number != destination.number:
                return base_distance * (penalty_factor * 1.5)
                
            return base_distance
        
        # Encontrar otra ruta con la función de costo personalizada
        next_path, next_distance = find_shortest_path_astar(
            airspace, origin, destination, custom_cost_func=custom_cost_func)
        
        if not next_path:
            break  # No se encontraron más rutas
        
        # Extraer solo los números de los puntos
        next_path_nums = [point.number for point in next_path]
        
        # Verificar si esta ruta es suficientemente diferente de las anteriores
        is_different = True
        
        # Una ruta es diferente si tiene al menos un 30% de puntos distintos a cualquier ruta anterior
        for existing_distance, existing_path in result_paths:
            # Calcular cuántos puntos diferentes hay entre las rutas
            # Excluyendo origen y destino que siempre serán iguales
            common_points = set(existing_path[1:-1]).intersection(set(next_path_nums[1:-1]))
            
            if len(next_path_nums) <= 2:
                # Si la ruta solo tiene origen y destino, no es diferente
                is_different = False
                break
                
            different_points_ratio = 1.0 - (len(common_points) / (len(next_path_nums) - 2))
            
            # Si la ruta es muy similar a una existente, no la consideramos diferente
            if different_points_ratio < 0.3:  # Al menos 30% de puntos diferentes
                is_different = False
                break
        
        if is_different:
            # Añadir la nueva ruta a los resultados
            result_paths.append((next_distance, next_path_nums))
            
            # Actualizar el conjunto de segmentos utilizados
            for i in range(len(next_path) - 1):
                segment = (next_path[i].number, next_path[i+1].number)
                used_segments.add(segment)
                
            # Reducir el factor de penalización para el próximo intento
            penalty_factor = 5.0  # Reiniciar el factor para el siguiente intento
        else:
            # Si encontramos una ruta similar, aumentamos el factor de penalización
            penalty_factor *= 1.5
            
            # Si el factor es demasiado alto, es poco probable que encontremos nuevas rutas
            if penalty_factor > 30:
                # Reiniciar el factor de penalización y cambiar la estrategia
                penalty_factor = 5.0
                
                # Si aún no tenemos suficientes rutas, podemos ser menos exigentes
                if len(result_paths) < 2 and attempt > max_paths:
                    break  # No se pueden encontrar más rutas diferentes
    
    # Ordenar las rutas por distancia
    result_paths.sort(key=lambda x: x[0])
    
    # Devolver las rutas encontradas (hasta max_paths)
    return result_paths[:max_paths]

def plot_path(graph, path):
    """
    Muestra gráficamente el camino en el grafo
    """
    if not path or len(path) < 2:
        print("No hay camino para mostrar")
        return
    
    # Esta función sería implementada según las necesidades de visualización
    print(f"Mostrando camino con {len(path)} puntos")
    for i, node in enumerate(path):
        print(f"{i+1}. {node.name} (#{node.number})")
