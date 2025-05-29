from navPoint import NavPoint
from navSegment import NavSegment
from navAirport import NavAirport, add_sid, add_star
import math
import time

class AirSpace:
    def __init__(self, name=""):
        self.name = name
        self.navpoints = {}  # Dictionary of NavPoints keyed by number
        self.navsegments = []  # List of NavSegments
        self.navairports = {}  # Dictionary of NavAirports keyed by name


def add_navpoint(airspace, navpoint):
    airspace.navpoints[navpoint.number] = navpoint
    
def add_navsegment(airspace, navsegment):
    airspace.navsegments.append(navsegment)
    
def add_navairport(airspace, navairport):
    airspace.navairports[navairport.name] = navairport


def get_navpoint_by_number(airspace, number):
    return airspace.navpoints.get(number)


def get_navpoint_by_name(airspace, name):
    for point in airspace.navpoints.values():
        if point.name == name:
            return point
    return None


def get_navairport_by_name(airspace, name):
    return airspace.navairports.get(name)


def load_from_files(airspace, nav_file, seg_file, aer_file):
    try:
        if nav_file.startswith(("Cat_", "cat_")):
            airspace.name = "Catalunya"
        elif nav_file.startswith(("Esp_", "esp_")):
            airspace.name = "España"
        elif nav_file.startswith(("Eur_", "eur_")):
            airspace.name = "Europe"

        with open(nav_file, 'r') as f:
            first_line = f.readline().strip()
            f.seek(0)
            
            try:
                parts = first_line.split()
                if len(parts) >= 4:
                    int(parts[0])
                    float(parts[2])
                    float(parts[3])
                    is_header = False
                else:
                    is_header = True
            except (ValueError, IndexError):
                is_header = True
                
            if is_header:
                next(f)
                
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split()
                if len(parts) >= 4:
                    number = int(parts[0])
                    name = parts[1]
                    latitude = float(parts[2])
                    longitude = float(parts[3])
                    add_navpoint(airspace, NavPoint(number, name, latitude, longitude))

        with open(seg_file, 'r') as f:
            first_line = f.readline().strip()
            f.seek(0)
            
            try:
                parts = first_line.split()
                if len(parts) >= 3:
                    int(parts[0])
                    int(parts[1])
                    float(parts[2])
                    is_header = False
                else:
                    is_header = True
            except (ValueError, IndexError):
                is_header = True
                
            if is_header:
                next(f)
                
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split()
                if len(parts) >= 3:
                    origin = int(parts[0])
                    destination = int(parts[1])
                    distance = float(parts[2])
                    add_navsegment(airspace, NavSegment(origin, destination, distance))

        with open(aer_file, 'r') as f:
            first_line = f.readline().strip()
            f.seek(0)
            
            try:
                parts = first_line.split()
                if len(parts) < 1 or parts[0].startswith('#'):
                    is_header = True
                else:
                    is_header = False
            except:
                is_header = True
                
            if is_header:
                next(f)
            
            current_airport = None
            
            # Leer el archivo línea por línea
            lines = [line.strip() for line in f if line.strip()]
            i = 0
            
            while i < len(lines):
                line = lines[i]
                
                # Si es un código de aeropuerto
                if line.startswith(("LE", "LF")) and not "." in line:
                    airport_code = line
                    current_airport = NavAirport(airport_code)
                    
                    # Verificar si hay suficientes líneas para SID y STAR
                    if i + 2 < len(lines):
                        # La siguiente línea debería ser el SID (.D)
                        sid_line = lines[i + 1]
                        # La siguiente a esa debería ser el STAR (.A)
                        star_line = lines[i + 2]
                        
                        # Verificar que el formato sea correcto
                        if sid_line.endswith(".D") and star_line.endswith(".A"):
                            # Buscar los puntos por nombre
                            sid_name = sid_line
                            star_name = star_line
                            
                            # Encontrar los números de punto correspondientes
                            sid_point = None
                            star_point = None
                            
                            for point_num, point in airspace.navpoints.items():
                                if point.name == sid_name:
                                    sid_point = point_num
                                if point.name == star_name:
                                    star_point = point_num
                            
                            # Añadir SID y STAR si se encontraron
                            if sid_point:
                                add_sid(current_airport, sid_point)
                                print(f"Agregado SID {sid_name} (#{sid_point}) al aeropuerto {airport_code}")
                            
                            if star_point:
                                add_star(current_airport, star_point)
                                print(f"Agregado STAR {star_name} (#{star_point}) al aeropuerto {airport_code}")
                    
                    # Añadir el aeropuerto al espacio aéreo
                    add_navairport(airspace, current_airport)
                    print(f"Aeropuerto {airport_code} añadido con {len(current_airport.sids)} SIDs y {len(current_airport.stars)} STARs")
                    
                    # Avanzar a la siguiente entrada (saltando las líneas de SID y STAR)
                    i += 3
                else:
                    # Si no es un aeropuerto, simplemente avanzar
                    i += 1
        
        return True
    
    except Exception as e:
        print(f"Error loading airspace data: {e}")
        return False


def calculate_distance(airspace, point1, point2):
    R = 6371.0
    lat1 = math.radians(point1.latitude)
    lon1 = math.radians(point1.longitude)
    lat2 = math.radians(point2.latitude)
    lon2 = math.radians(point2.longitude)

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance


def find_neighbors(airspace, navpoint_number):
    neighbors = []
    
    for segment in airspace.navsegments:
        if segment.origin_number == navpoint_number:
            neighbors.append(segment.destination_number)
        elif segment.destination_number == navpoint_number:
            neighbors.append(segment.origin_number)
            
    return neighbors


def find_shortest_path(airspace, start_number, end_number):

    import heapq

    if start_number not in airspace.navpoints or end_number not in airspace.navpoints:
        return [], 0

    distances = {node: float('infinity') for node in airspace.navpoints}
    distances[start_number] = 0

    previous = {node: None for node in airspace.navpoints}

    priority_queue = [(0, start_number)]
    
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_node == end_number:
            break

        if current_distance > distances[current_node]:
            continue

        neighbors = find_neighbors(airspace, current_node)
        
        for neighbor in neighbors:
            segment = None
            for seg in airspace.navsegments:
                if (seg.origin_number == current_node and seg.destination_number == neighbor) or \
                   (seg.destination_number == current_node and seg.origin_number == neighbor):
                    segment = seg
                    break
            
            if segment:
                distance = current_distance + segment.distance

                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    heapq.heappush(priority_queue, (distance, neighbor))

    path = []
    current_node = end_number
    
    while current_node is not None:
        path.append(current_node)
        current_node = previous[current_node]

    path.reverse()
    

    if not path or (len(path) == 1 and path[0] == start_number):
        return [], 0

    total_distance = distances[end_number]
    
    return path, total_distance


def find_multiple_paths(airspace, start_number, end_number, max_paths=3):
    """
    Encuentra múltiples rutas entre dos puntos, ordenadas por distancia total.
    """
    paths = []
    start_time = time.time()
    MAX_TIME = 2  # segundos máximos de búsqueda
    
    def find_path_with_restrictions(current, target, current_path, restricted_segments, max_depth=20):
        if time.time() - start_time > MAX_TIME:
            return None
            
        if current == target:
            total_distance = 0
            for i in range(len(current_path) - 1):
                point1 = get_navpoint_by_number(airspace, current_path[i])
                point2 = get_navpoint_by_number(airspace, current_path[i + 1])
                total_distance += calculate_distance(airspace, point1, point2)
            return (total_distance, current_path[:])
        
        if len(paths) >= max_paths or len(current_path) > max_depth:
            return None
            
        # Obtener vecinos
        neighbors = find_neighbors(airspace, current)
        if not neighbors:
            return None
            
        # Ordenar vecinos por distancia al objetivo
        neighbor_distances = []
        target_point = get_navpoint_by_number(airspace, target)
        for neighbor in neighbors:
            neighbor_point = get_navpoint_by_number(airspace, neighbor)
            dist = calculate_distance(airspace, neighbor_point, target_point)
            neighbor_distances.append((dist, neighbor))
        
        neighbor_distances.sort()
        
        for _, next_point in neighbor_distances:
            segment = tuple(sorted([current, next_point]))
            if next_point not in current_path and segment not in restricted_segments:
                current_path.append(next_point)
                restricted_segments.add(segment)
                result = find_path_with_restrictions(next_point, target, current_path, restricted_segments, max_depth)
                if result:
                    return result
                current_path.pop()
                restricted_segments.remove(segment)
        return None
    
    # Encontrar la primera ruta (la más corta)
    shortest_result = find_shortest_path(airspace, start_number, end_number)
    if shortest_result:
        shortest_path, total_distance = shortest_result
        paths.append((total_distance, shortest_path))
    
    # Encontrar rutas alternativas
    attempts = 0
    max_attempts = 5
    while len(paths) < max_paths and attempts < max_attempts:
        restricted_segments = set()
        for _, path in paths:
            for i in range(len(path) - 1):
                restricted_segments.add(tuple(sorted([path[i], path[i + 1]])))
        
        result = find_path_with_restrictions(start_number, end_number, [start_number], restricted_segments)
        if result:
            # Verificar que la ruta es significativamente diferente
            new_distance, new_path = result
            is_different = True
            for existing_distance, existing_path in paths:
                if len(set(new_path) & set(existing_path)) / len(new_path) > 0.7:  # Si comparten más del 70% de puntos
                    is_different = False
                    break
            if is_different:
                paths.append(result)
        attempts += 1
        
        if time.time() - start_time > MAX_TIME:
            break
    
    # Ordenar rutas por distancia
    paths.sort(key=lambda x: x[0])
    return paths
