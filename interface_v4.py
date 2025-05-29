import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import os
import platform
from airSpace import *
from navSegment import get_origin_number, get_destination_number, get_distance
from kml_generator import generate_airspace_kml, generate_path_kml, generate_neighbors_kml, save_kml_to_file
from music_generator import (MusicPlayer)
import music_generator
from PIL import Image, ImageTk, ImageFilter  # Añadir ImageFilter para el efecto de desenfoque
from path import find_shortest_path_astar, find_multiple_paths_astar  # Importar el algoritmo A*
import math

# Variables globales
espacio_aereo = None
ultimo_archivo_nav = "Cat_nav.txt"
ultimo_archivo_seg = "Cat_seg.txt"
ultimo_archivo_aer = "Cat_aer.txt"
reproductor_musica = None  # Variable global para controlar el reproductor de música

# Función para calcular la distancia entre dos puntos geográficos usando la fórmula haversine
def calcular_distancia_entre_puntos(punto1, punto2):
    """
    Calcula la distancia en kilómetros entre dos puntos geográficos usando la fórmula haversine.
    """
    # Radio de la Tierra en kilómetros
    R = 6371.0

    # Convertir latitud y longitud de grados a radianes
    lat1 = math.radians(punto1.latitude)
    lon1 = math.radians(punto1.longitude)
    lat2 = math.radians(punto2.latitude)
    lon2 = math.radians(punto2.longitude)

    # Diferencia de longitud y latitud
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # Fórmula haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance

# Temas de la aplicación
LIGHT_THEME = {
    "bg": "#f0f2f5",
    "fg": "#333333",
    "button_bg": "#4a6fa5",  # Azul más elegante
    "button_fg": "white",
    "button_active_bg": "#3a5a80",  # Color cuando se presiona
    "button_hover_bg": "#5a7fb5",   # Color al pasar el mouse
    "entry_bg": "white",
    "entry_fg": "#333333",
    "highlight_bg": "#e3f2fd",
    "frame_bg": "#f0f2f5",
    "text_bg": "white",
    "text_fg": "#333333",
    "plot_bg": "#f5f5f5",
    "plot_fg": "#333333",
    "grid_color": "#cccccc",
    "labelframe_bg": "#f0f2f5",  # Igual al fondo
    "labelframe_fg": "#333333",
    "status_bg": "#dcdcdc",
    "status_fg": "#333333",
    "font_family": "Segoe UI" if platform.system() == "Windows" else "Helvetica Neue",
    "font_size_normal": 10,
    "font_size_title": 12,
    "font_size_header": 22,
    "button_padx": 12,
    "button_pady": 6,
    "relief": tk.RAISED,
    "borderwidth": 1
}

DARK_THEME = {
    "bg": "#1a1a2e",
    "fg": "#e0e0e0",
    "button_bg": "#3a506b",  # Azul medio elegante
    "button_fg": "#ffffff",
    "button_active_bg": "#2a405b",  # Color cuando se presiona
    "button_hover_bg": "#4a607b",   # Color al pasar el mouse
    "entry_bg": "#16213e",
    "entry_fg": "#e0e0e0",
    "highlight_bg": "#1e3a5f",
    "frame_bg": "#1a1a2e",
    "text_bg": "#16213e",
    "text_fg": "#e0e0e0",
    "plot_bg": "#16213e",
    "plot_fg": "#e0e0e0",
    "grid_color": "#333333",
    "labelframe_bg": "#1a1a2e",  # Igual al fondo
    "labelframe_fg": "#e0e0e0",
    "status_bg": "#16213e",
    "status_fg": "#e0e0e0",
    "font_family": "Segoe UI" if platform.system() == "Windows" else "Helvetica Neue",
    "font_size_normal": 10,
    "font_size_title": 12,
    "font_size_header": 22,
    "button_padx": 12,
    "button_pady": 6,
    "relief": tk.RAISED,
    "borderwidth": 1
}

# Funciones de utilidad para obtener puntos y segmentos
def get_navpoint_by_name(airspace, name):
    """Obtiene un objeto NavPoint por su nombre."""
    for point in airspace.navpoints.values():
        if point.name == name:
            return point
    return None

def get_navpoint_by_number(airspace, number):
    """Obtiene un objeto NavPoint por su número."""
    return airspace.navpoints.get(number)

def get_navairport_by_name(airspace, name):
    """Obtiene un objeto NavAirport por su nombre."""
    return airspace.navairports.get(name)

def get_navsegment_by_number(airspace, number):
    """Obtiene un objeto NavSegment por su número."""
    return airspace.navsegments.get(number)

def explorar_archivo(variable_texto):
    nombre_archivo = filedialog.askopenfilename(
        initialdir=".",
        title="Seleccione un archivo",
        filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")) )

    if nombre_archivo:
        variable_texto.set(nombre_archivo)

def explorar_archivo_nav(app, archivo_nav):
    explorar_archivo(archivo_nav)

def explorar_archivo_seg(app, archivo_seg):
    explorar_archivo(archivo_seg)

def explorar_archivo_aer(app, archivo_aer):
    explorar_archivo(archivo_aer)

def cargar_datos_wrapper(app, archivo_nav, archivo_seg, archivo_aer, ventana):
    nav = archivo_nav.get()
    seg = archivo_seg.get()
    aer = archivo_aer.get()
    cargar_datos(app, nav, seg, aer, ventana)

def cargar_datos(app, archivo_nav, archivo_seg, archivo_aer, ventana):
    global espacio_aereo
    global ultimo_archivo_nav, ultimo_archivo_seg, ultimo_archivo_aer

    try:
        espacio_aereo = AirSpace()

        exito = load_from_files(espacio_aereo, archivo_nav, archivo_seg, archivo_aer)

        if exito:
            # Actualizar los últimos archivos cargados
            ultimo_archivo_nav = archivo_nav
            ultimo_archivo_seg = archivo_seg
            ultimo_archivo_aer = archivo_aer

            messagebox.showinfo("Éxito", f"Datos cargados correctamente.\n\nPuntos de navegación: {len(espacio_aereo.navpoints)}\nSegmentos: {len(espacio_aereo.navsegments)}\nAeropuertos: {len(espacio_aereo.navairports)}", parent=ventana)
            ventana.destroy()

            app.status.config(text=f"Datos cargados: {len(espacio_aereo.navpoints)} puntos, {len(espacio_aereo.navsegments)} segmentos, {len(espacio_aereo.navairports)} aeropuertos")

            # Habilitar el botón de exportación cuando se cargan los datos
            if hasattr(app, 'export_btn'):
                app.export_btn.config(state=tk.NORMAL)
        else:
            messagebox.showerror("Error", "No se pudieron cargar los datos correctamente.", parent=ventana)
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar datos: {str(e)}", parent=ventana)

def limpiar_contenido(app):
    content_window = tk.Toplevel(app)
    content_window.title("Contenido de Espacio Aéreo")
    content_window.geometry("700x500")
    return content_window

def cargar_espacio_aereo(app):
    global espacio_aereo

    load_window = tk.Toplevel(app)
    load_window.title("Cargar Datos de Espacio Aéreo")
    load_window.geometry("450x250")
    load_window.configure(bg=app.tema["bg"])  # Aplicar el color de fondo del tema actual

    file_frame = tk.Frame(load_window, bg=app.tema["bg"])
    file_frame.pack(fill=tk.X, pady=10, padx=10)

    nav_label = tk.Label(file_frame, text="Archivo de Puntos de Navegación:",
                         bg=app.tema["bg"], fg=app.tema["fg"],
                         font=(app.tema["font_family"], app.tema["font_size_normal"]))
    nav_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

    nav_file = tk.StringVar(value=ultimo_archivo_nav)
    nav_entry = tk.Entry(file_frame, textvariable=nav_file, width=30,
                         bg=app.tema["entry_bg"], fg=app.tema["entry_fg"],
                         insertbackground=app.tema["entry_fg"])
    nav_entry.grid(row=0, column=1, padx=5, pady=5)

    nav_browse = tk.Button(file_frame, text="...",
                        command=lambda: explorar_archivo_nav(app, nav_file),
                        bg=app.tema["button_bg"], fg=app.tema["button_fg"],
                        activebackground=app.tema["button_active_bg"])
    nav_browse.grid(row=0, column=2, padx=5, pady=5)

    seg_label = tk.Label(file_frame, text="Archivo de Segmentos:",
                       bg=app.tema["bg"], fg=app.tema["fg"],
                       font=(app.tema["font_family"], app.tema["font_size_normal"]))
    seg_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)

    seg_file = tk.StringVar(value=ultimo_archivo_seg)
    seg_entry = tk.Entry(file_frame, textvariable=seg_file, width=30,
                       bg=app.tema["entry_bg"], fg=app.tema["entry_fg"],
                       insertbackground=app.tema["entry_fg"])
    seg_entry.grid(row=1, column=1, padx=5, pady=5)

    seg_browse = tk.Button(file_frame, text="...",
                        command=lambda: explorar_archivo_seg(app, seg_file),
                        bg=app.tema["button_bg"], fg=app.tema["button_fg"],
                        activebackground=app.tema["button_active_bg"])
    seg_browse.grid(row=1, column=2, padx=5, pady=5)

    air_label = tk.Label(file_frame, text="Archivo de Aeropuertos:",
                       bg=app.tema["bg"], fg=app.tema["fg"],
                       font=(app.tema["font_family"], app.tema["font_size_normal"]))
    air_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)

    air_file = tk.StringVar(value=ultimo_archivo_aer)
    air_entry = tk.Entry(file_frame, textvariable=air_file, width=30,
                       bg=app.tema["entry_bg"], fg=app.tema["entry_fg"],
                       insertbackground=app.tema["entry_fg"])
    air_entry.grid(row=2, column=1, padx=5, pady=5)


    air_browse = tk.Button(file_frame, text="...",
                        command=lambda: explorar_archivo_aer(app, air_file),
                        bg=app.tema["button_bg"], fg=app.tema["button_fg"],
                        activebackground=app.tema["button_active_bg"])
    air_browse.grid(row=2, column=2, padx=5, pady=5)


    load_button = tk.Button(load_window, text="Cargar Datos",
                         command=lambda: cargar_datos_wrapper(app, nav_file, seg_file, air_file, load_window),
                         bg=app.tema["button_bg"], fg=app.tema["button_fg"],
                         activebackground=app.tema["button_active_bg"],
                         font=(app.tema["font_family"], app.tema["font_size_normal"]),
                         padx=app.tema["button_padx"], pady=app.tema["button_pady"])
    load_button.pack(pady=10)

def crear_espacio_aereo_vacio(app):
    """Crea un espacio aéreo vacío desde cero."""
    global espacio_aereo

    espacio_aereo = AirSpace()

    # Mostrar el espacio aéreo vacío, indicando que está permitido que esté vacío
    mostrar_espacio_aereo(app, permitir_vacio=True)

    # Actualizar el estado
    app.status.config(text="Espacio aéreo vacío creado. Use los controles para añadir elementos.")

    # Habilitar el botón de exportación
    if hasattr(app, 'export_btn'):
        app.export_btn.config(state=tk.NORMAL)

def mostrar_espacio_aereo(app, punto_destacado=None, vecinos=None, ruta=None, permitir_vacio=False, alcanzables=None):
    global espacio_aereo

    if not espacio_aereo:
        messagebox.showwarning("Advertencia", "No hay datos de espacio aéreo cargados. Por favor cargue los datos primero.")
        return

    # Si es un espacio vacío pero está permitido, continuamos sin mostrar advertencia
    is_empty = not espacio_aereo.navpoints
    if not permitir_vacio and is_empty:
        messagebox.showwarning("Advertencia", "No hay datos de espacio aéreo cargados. Por favor cargue los datos primero.")
        return

    map_window = tk.Toplevel(app)
    map_window.title("Mapa de Espacio Aéreo")
    map_window.geometry("1200x900")

    # Aplicar estilo consistente a la ventana emergente
    map_window.configure(bg=app.tema["bg"])

    # Frame para el título y opciones principales
    title_frame = tk.Frame(map_window, bg=app.tema["bg"])
    title_frame.pack(fill=tk.X, padx=10, pady=5)

    # Título de la ventana con mensaje adecuado
    if permitir_vacio and is_empty:
        title_label = tk.Label(title_frame, text="Espacio Aéreo Vacío - Añada elementos para construir su grafo",
                              font=(app.tema["font_family"], app.tema["font_size_header"]),
                              bg=app.tema["bg"], fg=app.tema["fg"])
    else:
        title_label = tk.Label(title_frame, text="Visualización de Espacio Aéreo",
                              font=(app.tema["font_family"], app.tema["font_size_header"]),
                              bg=app.tema["bg"], fg=app.tema["fg"])
    title_label.pack(side=tk.LEFT, padx=10, pady=10)

    # Frame para controles del mapa
    control_frame = tk.Frame(map_window, bg=app.tema["bg"])
    control_frame.pack(fill=tk.X, padx=10, pady=5)

    # Opciones de visualización
    options_frame = tk.LabelFrame(control_frame, text="Opciones de Visualización",
                               bg=app.tema["bg"], fg=app.tema["fg"],
                               font=(app.tema["font_family"], app.tema["font_size_normal"]))
    options_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)

    # Variables para controlar la visibilidad de elementos
    show_nodes = tk.BooleanVar(value=True)
    show_segments = tk.BooleanVar(value=True)
    show_distances = tk.BooleanVar(value=True)

    # Botón para mostrar/ocultar nodos
    nodes_check = tk.Checkbutton(options_frame, text="Mostrar Nodos", variable=show_nodes,
                                font=(app.tema["font_family"], app.tema["font_size_normal"]),
                                bg=app.tema["bg"], fg=app.tema["fg"],
                                selectcolor=app.tema["bg"] if platform.system() == "Darwin" else None)
    nodes_check.pack(side=tk.LEFT, padx=10)

    # Botón para mostrar/ocultar segmentos
    segments_check = tk.Checkbutton(options_frame, text="Mostrar Segmentos", variable=show_segments,
                                   font=(app.tema["font_family"], app.tema["font_size_normal"]),
                                   bg=app.tema["bg"], fg=app.tema["fg"],
                                   selectcolor=app.tema["bg"] if platform.system() == "Darwin" else None)
    segments_check.pack(side=tk.LEFT, padx=10)

    # Botón para mostrar/ocultar distancias
    distances_check = tk.Checkbutton(options_frame, text="Mostrar Distancias", variable=show_distances,
                                    font=(app.tema["font_family"], app.tema["font_size_normal"]),
                                    bg=app.tema["bg"], fg=app.tema["fg"],
                                    selectcolor=app.tema["bg"] if platform.system() == "Darwin" else None)
    distances_check.pack(side=tk.LEFT, padx=10)

    # Botón para añadir nodo
    add_node_btn = tk.Button(control_frame, text="Añadir Nodo",
                            font=(app.tema["font_family"], app.tema["font_size_normal"]),
                            bg=app.tema["button_bg"], fg=app.tema["button_fg"],
                            command=lambda: mostrar_dialogo_anadir_nodo())
    add_node_btn.pack(side=tk.LEFT, padx=10)

    # Botón para añadir segmento
    add_segment_btn = tk.Button(control_frame, text="Añadir Segmento",
                              font=(app.tema["font_family"], app.tema["font_size_normal"]),
                              bg=app.tema["button_bg"], fg=app.tema["button_fg"],
                              command=lambda: mostrar_dialogo_anadir_segmento())
    add_segment_btn.pack(side=tk.LEFT, padx=10)

    # Botón para eliminar nodo
    delete_node_btn = tk.Button(control_frame, text="Eliminar Nodo",
                              font=(app.tema["font_family"], app.tema["font_size_normal"]),
                              bg=app.tema["button_bg"], fg=app.tema["button_fg"],
                              command=lambda: mostrar_dialogo_eliminar_nodo())
    delete_node_btn.pack(side=tk.LEFT, padx=10)

    # Botón para exportar mapa editado
    export_map_btn = tk.Button(control_frame, text="Exportar Gráfico",
                             font=(app.tema["font_family"], app.tema["font_size_normal"]),
                             bg=app.tema["button_bg"], fg=app.tema["button_fg"],
                             command=lambda: mostrar_dialogo_exportar_mapa())
    export_map_btn.pack(side=tk.LEFT, padx=10)

    fig = Figure(figsize=(15, 12), dpi=100)
    ax = fig.add_subplot(111)

    is_neighbor_view = bool(punto_destacado and vecinos)

    lon_values = []
    lat_values = []

    point_cache = {}

    for num, point in espacio_aereo.navpoints.items():
        lon_values.append(point.longitude)
        lat_values.append(point.latitude)
        point_cache[point.number] = point


    margin = 0.1

    # Si no hay puntos (espacio vacío), establecer límites predeterminados
    if not lon_values or not lat_values:
        # Valores predeterminados centrados en España
        lon_min, lon_max = -7.0, 4.0  # Aproximadamente desde Galicia hasta Cataluña
        lat_min, lat_max = 36.0, 44.0  # Aproximadamente desde Andalucía hasta los Pirineos
    else:
        lon_min = min(lon_values) - margin
        lon_max = max(lon_values) + margin
        lat_min = min(lat_values) - margin
        lat_max = max(lat_values) + margin


    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)
    ax.set_autoscale_on(False)  # Disable autoscaling
    ax.set_clip_on(True)
    ax.set_clip_box(ax.bbox)  # Add clip box

    segment_color = 'cyan'
    point_color = 'black'
    highlight_color = 'red'
    neighbor_color = highlight_color
    path_color = '#00CCCC'

    fig.subplots_adjust(left=0.05, right=0.95, top=0.92, bottom=0.05)

    canvas = FigureCanvasTkAgg(fig, master=map_window)  # A tk.DrawingArea.

    # Create a proper layout for the canvas and toolbar
    canvas_frame = tk.Frame(map_window)
    canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    toolbar = NavigationToolbar2Tk(canvas, canvas_frame)
    toolbar.update()

    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Función para obtener el siguiente número disponible para un nodo
    def get_next_node_number():
        existing_numbers = list(espacio_aereo.navpoints.keys())
        if not existing_numbers:
            return 1
        return max(existing_numbers) + 1

    # Función para mostrar el diálogo para añadir un nuevo nodo
    def mostrar_dialogo_anadir_nodo():
        # Crear un diálogo para obtener información del nodo
        dialog = tk.Toplevel(map_window)
        dialog.title("Añadir Nuevo Nodo")
        dialog.geometry("300x200")
        dialog.configure(bg=app.tema["bg"])
        dialog.grab_set()  # Hacer que el diálogo sea modal

        # Frame para el formulario
        form_frame = tk.Frame(dialog, bg=app.tema["bg"])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Campos del formulario
        tk.Label(form_frame, text="Nombre del nodo:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = tk.Entry(form_frame, width=20)
        name_entry.grid(row=0, column=1, pady=5)
        name_entry.focus_set()

        tk.Label(form_frame, text="Longitud:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=1, column=0, sticky=tk.W, pady=5)
        lon_entry = tk.Entry(form_frame, width=20)
        lon_entry.grid(row=1, column=1, pady=5)

        tk.Label(form_frame, text="Latitud:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=2, column=0, sticky=tk.W, pady=5)
        lat_entry = tk.Entry(form_frame, width=20)
        lat_entry.grid(row=2, column=1, pady=5)

        status_label = tk.Label(form_frame, text="", bg=app.tema["bg"], fg="red")
        status_label.grid(row=3, column=0, columnspan=2, pady=5)

        # Destacar nodos alcanzables si existen
        if alcanzables:
            # Obtener el nodo de origen
            if punto_destacado and punto_destacado in point_cache:
                # Dibujar el nodo de origen con un color distintivo
                origen = point_cache[punto_destacado]
                ax.plot(origen.longitude, origen.latitude, 'o', color='red', markersize=10, zorder=10,
                        label='Nodo de Origen')

                # Dibujar líneas desde el origen a cada nodo alcanzable
                for num in alcanzables:
                    if num in point_cache:
                        punto = point_cache[num]
                        # Dibujar el nodo alcanzable
                        ax.plot(punto.longitude, punto.latitude, 'o', color='green', markersize=8, zorder=9)
                        # Dibujar una línea desde el origen hasta el nodo alcanzable
                        ax.plot([origen.longitude, punto.longitude], [origen.latitude, punto.latitude],
                                '-', color='green', linewidth=1.5, alpha=0.7, zorder=5)

                # Añadir una leyenda para los nodos alcanzables si no está ya
                if 'Nodos Alcanzables' not in [label.get_text() for label in
                                               ax.get_legend().get_texts()] if ax.get_legend() else []:
                    ax.plot([], [], 'o', color='green', markersize=8, label='Nodos Alcanzables')

        # Función para guardar el nuevo nodo
        def guardar_nodo():
            try:
                nombre = name_entry.get().strip()

                # Validar longitud y latitud
                try:
                    longitud = float(lon_entry.get())
                    latitud = float(lat_entry.get())
                except ValueError:
                    status_label.config(text="Error: Las coordenadas deben ser números")
                    return

                if not nombre:
                    status_label.config(text="Error: El nombre no puede estar vacío")
                    return

                # Verificar si el nombre ya existe
                for _, point in espacio_aereo.navpoints.items():
                    if point.name == nombre:
                        status_label.config(text="Error: El nombre ya existe")
                        return

                # Crear el nuevo nodo
                next_number = get_next_node_number()

                # Importar la clase NavPoint
                from navPoint import NavPoint

                # Crear el nuevo punto de navegación con tipo "W" (waypoint) por defecto
                nuevo_nodo = NavPoint(next_number, nombre, latitud, longitud)

                # Añadir al espacio aéreo
                espacio_aereo.navpoints[next_number] = nuevo_nodo
                point_cache[next_number] = nuevo_nodo

                # Cerrar el diálogo y redibujar el mapa
                dialog.destroy()
                redraw_map()

                # Mostrar mensaje de éxito
                messagebox.showinfo("Éxito", f"Nodo '{nombre}' añadido correctamente")

            except Exception as e:
                status_label.config(text=f"Error: {str(e)}")

        # Botones
        button_frame = tk.Frame(form_frame, bg=app.tema["bg"])
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        save_button = tk.Button(button_frame, text="Guardar", command=guardar_nodo,
                              bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        save_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(button_frame, text="Cancelar", command=dialog.destroy,
                                bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        cancel_button.pack(side=tk.LEFT, padx=5)

    # Función para mostrar el diálogo para añadir un nuevo segmento
    def mostrar_dialogo_anadir_segmento():
        # Crear un diálogo para obtener información del segmento
        dialog = tk.Toplevel(map_window)
        dialog.title("Añadir Nuevo Segmento")
        dialog.geometry("350x220")
        dialog.configure(bg=app.tema["bg"])
        dialog.grab_set()  # Hacer que el diálogo sea modal

        # Frame para el formulario
        form_frame = tk.Frame(dialog, bg=app.tema["bg"])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Campos del formulario
        tk.Label(form_frame, text="Nombre del nodo de origen:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=0, column=0, sticky=tk.W, pady=5)
        origin_entry = tk.Entry(form_frame, width=20)
        origin_entry.grid(row=0, column=1, pady=5)
        origin_entry.focus_set()

        tk.Label(form_frame, text="Nombre del nodo de destino:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=1, column=0, sticky=tk.W, pady=5)
        dest_entry = tk.Entry(form_frame, width=20)
        dest_entry.grid(row=1, column=1, pady=5)

        # Variable para almacenar la opción de cálculo de distancia
        calc_distance = tk.BooleanVar(value=True)

        # Checkbox para calcular automáticamente la distancia
        calc_check = tk.Checkbutton(form_frame, text="Calcular distancia automáticamente",
                                  variable=calc_distance,
                                  bg=app.tema["bg"], fg=app.tema["fg"],
                                  selectcolor=app.tema["bg"] if platform.system() == "Darwin" else None,
                                  command=lambda: toggle_distance_entry())
        calc_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)

        tk.Label(form_frame, text="Distancia:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=3, column=0, sticky=tk.W, pady=5)
        distance_entry = tk.Entry(form_frame, width=20, state=tk.DISABLED)
        distance_entry.grid(row=3, column=1, pady=5)

        status_label = tk.Label(form_frame, text="", bg=app.tema["bg"], fg="red")
        status_label.grid(row=4, column=0, columnspan=2, pady=5)

        # Función para habilitar/deshabilitar el campo de distancia
        def toggle_distance_entry():
            if calc_distance.get():
                distance_entry.config(state=tk.DISABLED)
            else:
                distance_entry.config(state=tk.NORMAL)

        # Función para validar los nodos
        def validar_nodos():
            try:
                origin_name = origin_entry.get().strip().upper()
                dest_name = dest_entry.get().strip().upper()

                if not origin_name:
                    status_label.config(text="Error: El nombre del nodo de origen no puede estar vacío")
                    return None, None

                if not dest_name:
                    status_label.config(text="Error: El nombre del nodo de destino no puede estar vacío")
                    return None, None

                # Buscar los nodos por nombre
                origin_node = None
                dest_node = None
                origin_num = None
                dest_num = None

                for num, point in espacio_aereo.navpoints.items():
                    if point.name.upper() == origin_name:
                        origin_node = point
                        origin_num = num
                    if point.name.upper() == dest_name:
                        dest_node = point
                        dest_num = num

                if not origin_node:
                    status_label.config(text=f"Error: No existe un nodo con el nombre '{origin_name}'")
                    return None, None

                if not dest_node:
                    status_label.config(text=f"Error: No existe un nodo con el nombre '{dest_name}'")
                    return None, None

                if origin_num == dest_num:
                    status_label.config(text="Error: El origen y destino no pueden ser iguales")
                    return None, None

                # Verificar si ya existe un segmento entre estos nodos
                for segment in espacio_aereo.navsegments:
                    if (segment.origin_number == origin_num and segment.destination_number == dest_num) or \
                       (segment.origin_number == dest_num and segment.destination_number == origin_num):
                        status_label.config(text=f"Error: Ya existe un segmento entre {origin_name} y {dest_name}")
                        return None, None

                return (origin_node, origin_num), (dest_node, dest_num)
            except Exception as e:
                status_label.config(text=f"Error: {str(e)}")
                return None, None

        # Función para guardar el nuevo segmento
        def guardar_segmento():
            origin_data, dest_data = validar_nodos()
            if not origin_data or not dest_data:
                return

            try:
                origin_node, origin_num = origin_data
                dest_node, dest_num = dest_data

                # Obtener la distancia
                if calc_distance.get():
                    # Calcular la distancia automáticamente
                    distance = calcular_distancia_entre_puntos(origin_node, dest_node)
                else:
                    # Usar la distancia proporcionada por el usuario
                    try:
                        distance = float(distance_entry.get())
                        if distance <= 0:
                            status_label.config(text="Error: La distancia debe ser mayor que 0")
                            return
                    except ValueError:
                        status_label.config(text="Error: La distancia debe ser un número")
                        return

                # Importar la clase NavSegment
                from navSegment import NavSegment

                # Crear el nuevo segmento
                nuevo_segmento = NavSegment(origin_num, dest_num, distance)

                # Añadir al espacio aéreo
                espacio_aereo.navsegments.append(nuevo_segmento)

                # Cerrar el diálogo y redibujar el mapa
                dialog.destroy()
                redraw_map()

                # Mostrar mensaje de éxito
                messagebox.showinfo("Éxito", f"Segmento entre {origin_node.name} y {dest_node.name} añadido correctamente")

            except Exception as e:
                status_label.config(text=f"Error: {str(e)}")

        # Botones de acción
        button_frame = tk.Frame(form_frame, bg=app.tema["bg"])
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        save_button = tk.Button(button_frame, text="Guardar", command=guardar_segmento,
                              bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        save_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(button_frame, text="Cancelar", command=dialog.destroy,
                                bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        cancel_button.pack(side=tk.LEFT, padx=5)

    # Función para mostrar el diálogo para eliminar un nodo
    def mostrar_dialogo_eliminar_nodo():
        # Crear un diálogo para obtener el nombre del nodo a eliminar
        dialog = tk.Toplevel(map_window)
        dialog.title("Eliminar Nodo")
        dialog.geometry("300x180")
        dialog.configure(bg=app.tema["bg"])
        dialog.grab_set()  # Hacer que el diálogo sea modal

        # Frame para el formulario
        form_frame = tk.Frame(dialog, bg=app.tema["bg"])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Campos del formulario
        tk.Label(form_frame, text="Nombre del nodo a eliminar:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=0, column=0, sticky=tk.W, pady=5)
        node_entry = tk.Entry(form_frame, width=20)
        node_entry.grid(row=0, column=1, pady=5)
        node_entry.focus_set()

        # Variable para almacenar la opción de eliminar segmentos relacionados
        delete_segments = tk.BooleanVar(value=True)

        # Checkbox para eliminar segmentos relacionados
        segments_check = tk.Checkbutton(form_frame, text="Eliminar segmentos conectados",
                                       variable=delete_segments,
                                       bg=app.tema["bg"], fg=app.tema["fg"],
                                       selectcolor=app.tema["bg"] if platform.system() == "Darwin" else None)
        segments_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)

        status_label = tk.Label(form_frame, text="", bg=app.tema["bg"], fg="red")
        status_label.grid(row=2, column=0, columnspan=2, pady=5)

        # Función para validar y eliminar el nodo
        def eliminar_nodo():
            try:
                node_name = node_entry.get().strip().upper()

                if not node_name:
                    status_label.config(text="Error: El nombre del nodo no puede estar vacío")
                    return

                # Buscar el nodo por nombre
                node_to_delete = None
                node_number = None

                for num, point in espacio_aereo.navpoints.items():
                    if point.name.upper() == node_name:
                        node_to_delete = point
                        node_number = num
                        break

                if not node_to_delete:
                    status_label.config(text=f"Error: No existe un nodo con el nombre '{node_name}'")
                    return

                # Buscar segmentos conectados al nodo
                connected_segments = []
                for segment in espacio_aereo.navsegments:
                    if segment.origin_number == node_number or segment.destination_number == node_number:
                        connected_segments.append(segment)

                # Verificar si hay segmentos conectados y el usuario no desea eliminarlos
                if connected_segments and not delete_segments.get():
                    status_label.config(text=f"Error: El nodo tiene {len(connected_segments)} segmentos conectados")
                    return

                # Eliminar segmentos conectados si es necesario
                if connected_segments and delete_segments.get():
                    # Crear una nueva lista sin los segmentos que vamos a eliminar
                    espacio_aereo.navsegments = [s for s in espacio_aereo.navsegments
                                               if s.origin_number != node_number and s.destination_number != node_number]

                # Eliminar el nodo
                del espacio_aereo.navpoints[node_number]

                # Cerrar el diálogo y redibujar el mapa
                dialog.destroy()
                redraw_map()

                # Mostrar mensaje de éxito
                if connected_segments and delete_segments.get():
                    messagebox.showinfo("Éxito", f"Nodo '{node_to_delete.name}' y {len(connected_segments)} segmento(s) conectado(s) eliminados correctamente")
                else:
                    messagebox.showinfo("Éxito", f"Nodo '{node_to_delete.name}' eliminado correctamente")

            except Exception as e:
                status_label.config(text=f"Error: {str(e)}")

        # Botones de acción
        button_frame = tk.Frame(form_frame, bg=app.tema["bg"])
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        delete_button = tk.Button(button_frame, text="Eliminar", command=eliminar_nodo,
                                bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        delete_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(button_frame, text="Cancelar", command=dialog.destroy,
                                bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        cancel_button.pack(side=tk.LEFT, padx=5)

    # Función para redibujar el mapa según las opciones de visibilidad
    # Función para redibujar el mapa según las opciones de visibilidad
    def redraw_map():
        ax.clear()

        # Verificar si estamos en modo de visualización de alcanzabilidad
        is_reachability_view = bool(punto_destacado and alcanzables)

        # Recalcular los límites del mapa para incluir todos los puntos
        lon_values = []
        lat_values = []

        for num, point in espacio_aereo.navpoints.items():
            lon_values.append(point.longitude)
            lat_values.append(point.latitude)

        if lon_values and lat_values:  # Si hay puntos, usar sus límites
            margin = 0.1
            lon_min = min(lon_values) - margin
            lon_max = max(lon_values) + margin
            lat_min = min(lat_values) - margin
            lat_max = max(lat_values) + margin

            ax.set_xlim(lon_min, lon_max)
            ax.set_ylim(lat_min, lat_max)
        else:  # Si no hay puntos, usar límites predeterminados
            ax.set_xlim(-7.0, 4.0)  # Aproximadamente desde Galicia hasta Cataluña
            ax.set_ylim(36.0, 44.0)  # Aproximadamente desde Andalucía hasta los Pirineos

        ax.set_autoscale_on(False)
        ax.set_clip_on(True)
        ax.set_clip_box(ax.bbox)

        # Dibujar segmentos si están habilitados
        if show_segments.get():
            for segment in espacio_aereo.navsegments:
                origin_number = get_origin_number(segment)
                destination_number = get_destination_number(segment)

                if origin_number in espacio_aereo.navpoints and destination_number in espacio_aereo.navpoints:
                    point1 = espacio_aereo.navpoints[origin_number]
                    point2 = espacio_aereo.navpoints[destination_number]

                    draw_this_segment = False
                    current_line_color = segment_color
                    current_line_width = 1.0

                    if is_reachability_view:
                        # Solo dibujar segmentos que salen desde el nodo origen hacia los nodos alcanzables
                        if origin_number == punto_destacado and destination_number in alcanzables:
                            draw_this_segment = True
                            current_line_color = 'green'  # Color verde para segmentos alcanzables
                            current_line_width = 1.5
                    elif is_neighbor_view:
                        neighbor_numbers = [n[0].number for n in vecinos]
                        if (point1.number == punto_destacado.number and point2.number in neighbor_numbers) or \
                                (point2.number == punto_destacado.number and point1.number in neighbor_numbers):
                            current_line_color = segment_color
                            current_line_width = 1.0
                            draw_this_segment = True
                    else:
                        if ruta:
                            draw_this_segment = False
                            for i in range(len(ruta) - 1):
                                if ((ruta[i].number == point1.number and ruta[i + 1].number == point2.number) or
                                        (ruta[i].number == point2.number and ruta[i + 1].number == point1.number)):
                                    draw_this_segment = True
                                    current_line_color = '#00CCCC'
                                    current_line_width = 1.5

                                    if ruta[i].number == point1.number and ruta[i + 1].number == point2.number:
                                        start_point = (point1.longitude, point1.latitude)
                                        end_point = (point2.longitude, point2.latitude)
                                    else:
                                        start_point = (point2.longitude, point2.latitude)
                                        end_point = (point1.longitude, point1.latitude)
                                    break
                        else:
                            draw_this_segment = True
                            current_line_color = segment_color
                            current_line_width = 1.0

                    if draw_this_segment:
                        start_point = (point1.longitude, point1.latitude)
                        end_point = (point2.longitude, point2.latitude)

                        # Usar ax.plot en lugar de ax.annotate para mejorar el comportamiento al hacer zoom
                        x_coords = [start_point[0], end_point[0]]
                        y_coords = [start_point[1], end_point[1]]
                        line = ax.plot(x_coords, y_coords, color=current_line_color,
                                       linewidth=current_line_width,
                                       clip_on=True, zorder=5)[0]

                        # Añadir una flecha de dirección
                        mid_point = 0.5  # Punto medio del segmento
                        arrow_props = dict(arrowstyle='-|>', color=current_line_color,
                                           shrinkA=0, shrinkB=0,
                                           lw=current_line_width * 1.5,
                                           mutation_scale=12,  # Aumentar el tamaño de la punta de flecha
                                           clip_on=True)
                        ax.annotate('',
                                    xy=(x_coords[0] + mid_point * (x_coords[1] - x_coords[0]),
                                        y_coords[0] + mid_point * (y_coords[1] - y_coords[0])),
                                    xytext=(x_coords[0] + (mid_point - 0.02) * (x_coords[1] - x_coords[0]),
                                            y_coords[0] + (mid_point - 0.02) * (y_coords[1] - y_coords[0])),
                                    arrowprops=arrow_props,
                                    clip_on=True)

                        # Mostrar distancias si están habilitadas
                        if show_distances.get():
                            mid_x = (point1.longitude + point2.longitude) / 2
                            mid_y = (point1.latitude + point2.latitude) / 2
                            ax.text(mid_x, mid_y, f"{segment.distance:.1f}",
                                    fontsize=6, ha='center', va='center',
                                    bbox=dict(facecolor='white', alpha=0.5, pad=0.5), zorder=2, clip_on=True)

        # Dibujar nodos si están habilitados
        if show_nodes.get():
            for num, point in espacio_aereo.navpoints.items():
                this_color = point_color
                this_size = 5
                this_alpha = 1.0
                this_zorder = 10

                if is_reachability_view:
                    if num == punto_destacado:
                        # Destacar el nodo de origen
                        this_color = 'red'
                        this_size = 30
                        this_zorder = 30
                    elif num in alcanzables:
                        # Destacar los nodos alcanzables
                        this_color = 'green'
                        this_size = 20
                        this_zorder = 20
                    else:
                        # No dibujar otros nodos
                        continue  # Saltar a la siguiente iteración sin dibujar
                elif ruta and any(p.number == point.number for p in ruta):
                    this_color = '#00CCCC'
                    this_size = 10
                    this_zorder = 20
                elif ruta:
                    this_alpha = 0.5
                    this_size = 4
                elif is_neighbor_view:
                    neighbor_numbers = [n[0].number for n in vecinos]
                    if point.number == punto_destacado.number:
                        this_color = highlight_color
                        this_size = 30
                    elif point.number in neighbor_numbers:
                        this_color = neighbor_color
                        this_size = 20
                    else:
                        this_color = 'gray'
                        this_size = 5

                ax.scatter(point.longitude, point.latitude, color=this_color, s=this_size, alpha=this_alpha,
                           zorder=this_zorder, clip_on=True)

                ax.text(point.longitude + 0.01, point.latitude + 0.01, point.name,
                        fontsize=6, ha='left', va='bottom', zorder=6, clip_on=True)

        if not is_neighbor_view and not ruta and not is_reachability_view:
            ax.grid(True, linestyle=':', alpha=0.7, color='red')

        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_edgecolor('black')
            spine.set_linewidth(0.5)

        # Configurar título según el modo de visualización
        if is_reachability_view:
            ax.set_title(
                f"Nodo {espacio_aereo.navpoints[punto_destacado].name} (#{punto_destacado}) y sus {len(alcanzables)} nodos alcanzables",
                fontsize=14, pad=20, y=1.02)
        elif ruta:
            total_cost = 0
            for i in range(len(ruta) - 1):
                current_point = ruta[i]
                next_point = ruta[i + 1]

                # Buscar el segmento entre los puntos y sumar su distancia
                for segment in espacio_aereo.navsegments:
                    if ((get_origin_number(segment) == current_point.number and get_destination_number(
                            segment) == next_point.number) or
                            (get_origin_number(segment) == next_point.number and get_destination_number(
                                segment) == current_point.number)):
                        total_cost += get_distance(segment)
                        break

            ax.set_title(f"Gráfico con camino. Coste = {total_cost:.8f}", pad=20, y=1.02)
        elif is_neighbor_view:
            ax.set_title(f"Grafico con los vecinos del nodo {punto_destacado.name}", fontsize=14, pad=20, y=1.02)

        canvas.draw()

    # Conectar los comandos a los checkbuttons
    nodes_check.config(command=redraw_map)
    segments_check.config(command=redraw_map)
    distances_check.config(command=redraw_map)

    # Dibujo inicial del mapa
    redraw_map()

    instructions_text = "Utilice la barra de herramientas para navegar por el mapa y los controles de visibilidad para personalizar la vista."
    instructions_label = tk.Label(map_window, text=instructions_text, font=("Arial", 10), bg=app.tema["bg"], fg=app.tema["fg"])
    instructions_label.pack(pady=5)

    # Frame para botones de control
    control_frame = tk.Frame(map_window, bg=app.tema["bg"])
    control_frame.pack(fill=tk.X, padx=10, pady=5)

    status_message = "Mostrando mapa de espacio aéreo"
    if punto_destacado:
        # Verificar si punto_destacado es un número o un objeto
        if isinstance(punto_destacado, int) and punto_destacado in espacio_aereo.navpoints:
            nombre_punto = espacio_aereo.navpoints[punto_destacado].name
            status_message += f" - Destacando punto: {nombre_punto} (#{punto_destacado})"
        elif hasattr(punto_destacado, 'name'):
            status_message += f" - Destacando punto: {punto_destacado.name}"
    elif vecinos:
        status_message += f" - Mostrando {len(vecinos)} vecinos"
    elif ruta:
        status_message += f" - Mostrando ruta con {len(ruta)} puntos"

    app.status.config(text=status_message)

    # Frame para botones de edición
    edit_frame = tk.LabelFrame(map_window, text="Edición",
                           bg=app.tema["bg"], fg=app.tema["fg"],
                           font=(app.tema["font_family"], app.tema["font_size_normal"]))
    edit_frame.pack(fill=tk.X, padx=10, pady=5)

    # Botones de edición específicos para espacio aéreo vacío
    add_point_btn = tk.Button(edit_frame, text="Añadir Punto de Navegación",
                           command=lambda: añadir_punto(),
                           bg=app.tema["button_bg"], fg=app.tema["button_fg"],
                           font=(app.tema["font_family"], app.tema["font_size_normal"]))
    add_point_btn.pack(side=tk.LEFT, padx=5, pady=5)

    add_segment_btn = tk.Button(edit_frame, text="Añadir Segmento",
                             command=lambda: añadir_segmento(),
                             bg=app.tema["button_bg"], fg=app.tema["button_fg"],
                             font=(app.tema["font_family"], app.tema["font_size_normal"]))
    add_segment_btn.pack(side=tk.LEFT, padx=5, pady=5)

    # Botón para exportar mapa editado
    export_map_btn = tk.Button(edit_frame, text="Exportar Gráfico",
                            command=lambda: mostrar_dialogo_exportar_mapa(),
                            bg=app.tema["button_bg"], fg=app.tema["button_fg"],
                            font=(app.tema["font_family"], app.tema["font_size_normal"]))
    export_map_btn.pack(side=tk.LEFT, padx=5, pady=5)


    # Función para añadir un nuevo punto al espacio aéreo
    def añadir_punto():
        dialogo = tk.Toplevel(map_window)
        dialogo.title("Añadir Punto de Navegación")
        dialogo.geometry("400x300")
        dialogo.configure(bg=app.tema["bg"])
        dialogo.grab_set()  # Hacer modal

        # Frame para el formulario
        frame_form = tk.Frame(dialogo, bg=app.tema["bg"])
        frame_form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Campos del formulario
        tk.Label(frame_form, text="Nombre del punto:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=0, column=0, sticky=tk.W, pady=5)
        nombre_punto = tk.StringVar()
        tk.Entry(frame_form, textvariable=nombre_punto).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_form, text="Número:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=1, column=0, sticky=tk.W, pady=5)
        numero_punto = tk.StringVar()
        tk.Entry(frame_form, textvariable=numero_punto).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame_form, text="Latitud:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=2, column=0, sticky=tk.W, pady=5)
        latitud = tk.StringVar()
        tk.Entry(frame_form, textvariable=latitud).grid(row=2, column=1, padx=5, pady=5)

        tk.Label(frame_form, text="Longitud:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=3, column=0, sticky=tk.W, pady=5)
        longitud = tk.StringVar()
        tk.Entry(frame_form, textvariable=longitud).grid(row=3, column=1, padx=5, pady=5)

        # Función para guardar el punto
        def guardar_punto():
            try:
                nombre = nombre_punto.get().strip()
                numero = int(numero_punto.get().strip())
                lat = float(latitud.get().strip())
                lon = float(longitud.get().strip())

                if not nombre:
                    messagebox.showwarning("Error", "El nombre no puede estar vacío", parent=dialogo)
                    return

                # Verificar si el número ya existe
                if numero in espacio_aereo.navpoints:
                    messagebox.showwarning("Error", f"Ya existe un punto con el número {numero}", parent=dialogo)
                    return

                # Crear el nuevo punto
                nuevo_punto = NavPoint(numero, nombre, lat, lon)
                espacio_aereo.navpoints[numero] = nuevo_punto

                # Cerrar el diálogo
                dialogo.destroy()

                # Actualizar el mapa
                redraw_map()

                messagebox.showinfo("Éxito", f"Punto {nombre} añadido correctamente")
            except ValueError:
                messagebox.showwarning("Error", "Por favor ingrese valores numéricos válidos para número, latitud y longitud", parent=dialogo)

        # Botones de acción
        frame_botones = tk.Frame(frame_form, bg=app.tema["bg"])
        frame_botones.grid(row=4, column=0, columnspan=2, pady=10)

        tk.Button(frame_botones, text="Guardar", command=guardar_punto,
                bg=app.tema["button_bg"], fg=app.tema["button_fg"]).pack(side=tk.LEFT, padx=5)

        tk.Button(frame_botones, text="Cancelar", command=dialogo.destroy,
                bg=app.tema["button_bg"], fg=app.tema["button_fg"]).pack(side=tk.LEFT, padx=5)

    # Función para añadir un nuevo segmento al espacio aéreo
    def añadir_segmento():
        dialogo = tk.Toplevel(map_window)
        dialogo.title("Añadir Segmento")
        dialogo.geometry("400x300")
        dialogo.configure(bg=app.tema["bg"])
        dialogo.grab_set()  # Hacer modal

        # Frame para el formulario
        frame_form = tk.Frame(dialogo, bg=app.tema["bg"])
        frame_form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Comprobar si hay suficientes puntos
        if len(espacio_aereo.navpoints) < 2:
            tk.Label(frame_form, text="Se necesitan al menos 2 puntos para crear un segmento.\nPrimero añada puntos de navegación.",
                   bg=app.tema["bg"], fg="red", wraplength=300).pack(pady=20)

            tk.Button(frame_form, text="Cerrar", command=dialogo.destroy,
                    bg=app.tema["button_bg"], fg=app.tema["button_fg"]).pack(pady=10)
            return

        # Campos del formulario
        tk.Label(frame_form, text="Origen (número):", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=0, column=0, sticky=tk.W, pady=5)
        origen = tk.StringVar()

        # Crear lista de puntos disponibles
        puntos_disponibles = list(map(str, espacio_aereo.navpoints.keys()))

        # Combobox para origen
        combo_origen = ttk.Combobox(frame_form, textvariable=origen, values=puntos_disponibles)
        combo_origen.grid(row=0, column=1, padx=5, pady=5)
        if puntos_disponibles:
            combo_origen.current(0)

        tk.Label(frame_form, text="Destino (número):", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=1, column=0, sticky=tk.W, pady=5)
        destino = tk.StringVar()

        # Combobox para destino
        combo_destino = ttk.Combobox(frame_form, textvariable=destino, values=puntos_disponibles)
        combo_destino.grid(row=1, column=1, padx=5, pady=5)
        if len(puntos_disponibles) > 1:
            combo_destino.current(1)
        else:
            combo_destino.current(0)

        tk.Label(frame_form, text="Distancia (km):", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=2, column=0, sticky=tk.W, pady=5)
        distancia = tk.StringVar()
        tk.Entry(frame_form, textvariable=distancia).grid(row=2, column=1, padx=5, pady=5)

        # Función para calcular distancia automáticamente
        def calcular_distancia_auto():
            try:
                num_origen = int(origen.get())
                num_destino = int(destino.get())

                if num_origen not in espacio_aereo.navpoints or num_destino not in espacio_aereo.navpoints:
                    messagebox.showwarning("Error", "Seleccione puntos válidos", parent=dialogo)
                    return

                punto_origen = espacio_aereo.navpoints[num_origen]
                punto_destino = espacio_aereo.navpoints[num_destino]

                # Calcular distancia usando la fórmula haversine
                dist = calcular_distancia_entre_puntos(punto_origen, punto_destino)
                distancia.set(f"{dist:.2f}")

            except ValueError:
                messagebox.showwarning("Error", "Seleccione puntos válidos", parent=dialogo)

        # Botón para calcular distancia
        tk.Button(frame_form, text="Calcular Distancia", command=calcular_distancia_auto,
                bg=app.tema["button_bg"], fg=app.tema["button_fg"]).grid(row=3, column=0, columnspan=2, pady=5)

        # Función para guardar el segmento
        def guardar_segmento():
            try:
                num_origen = int(origen.get())
                num_destino = int(destino.get())
                dist = float(distancia.get())

                if num_origen not in espacio_aereo.navpoints or num_destino not in espacio_aereo.navpoints:
                    messagebox.showwarning("Error", "Seleccione puntos válidos", parent=dialogo)
                    return

                if num_origen == num_destino:
                    messagebox.showwarning("Error", "El origen y destino no pueden ser el mismo punto", parent=dialogo)
                    return

                if dist <= 0:
                    messagebox.showwarning("Error", "La distancia debe ser mayor que cero", parent=dialogo)
                    return

                # Verificar si ya existe este segmento
                for seg in espacio_aereo.navsegments:
                    orig = get_origin_number(seg)
                    dest = get_destination_number(seg)
                    if (orig == num_origen and dest == num_destino) or (orig == num_destino and dest == num_origen):
                        messagebox.showwarning("Error", "Ya existe un segmento entre estos puntos", parent=dialogo)
                        return

                # Crear el nuevo segmento (como tupla para mantener la compatibilidad)
                nuevo_segmento = (num_origen, num_destino, dist)
                espacio_aereo.navsegments.append(nuevo_segmento)

                # Cerrar el diálogo
                dialogo.destroy()

                # Actualizar el mapa
                redraw_map()

                messagebox.showinfo("Éxito", "Segmento añadido correctamente")
            except ValueError:
                messagebox.showwarning("Error", "Por favor ingrese valores numéricos válidos", parent=dialogo)

        # Botones de acción
        frame_botones = tk.Frame(frame_form, bg=app.tema["bg"])
        frame_botones.grid(row=4, column=0, columnspan=2, pady=10)

        tk.Button(frame_botones, text="Guardar", command=guardar_segmento,
                bg=app.tema["button_bg"], fg=app.tema["button_fg"]).pack(side=tk.LEFT, padx=5)

        tk.Button(frame_botones, text="Cancelar", command=dialogo.destroy,
                bg=app.tema["button_bg"], fg=app.tema["button_fg"]).pack(side=tk.LEFT, padx=5)

    # Función para mostrar el diálogo para exportar el mapa editado
    def mostrar_dialogo_exportar_mapa():
        # Crear un diálogo para obtener información de exportación
        dialog = tk.Toplevel(map_window)
        dialog.title("Exportar Mapa Editado")
        dialog.geometry("450x280")
        dialog.configure(bg=app.tema["bg"])
        dialog.grab_set()  # Hacer que el diálogo sea modal

        # Frame para el formulario
        form_frame = tk.Frame(dialog, bg=app.tema["bg"])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Variables para los nombres de archivo
        nav_filename = tk.StringVar(value="nuevos_nodos.txt")
        seg_filename = tk.StringVar(value="nuevos_segmentos.txt")

        # Campos del formulario
        tk.Label(form_frame, text="Exportar a archivos:", font=(app.tema["font_family"], app.tema["font_size_normal"], "bold"),
               bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=10)

        tk.Label(form_frame, text="Archivo de nodos:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=1, column=0, sticky=tk.W, pady=5)
        nav_entry = tk.Entry(form_frame, width=30, textvariable=nav_filename)
        nav_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(form_frame, text="Archivo de segmentos:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=2, column=0, sticky=tk.W, pady=5)
        seg_entry = tk.Entry(form_frame, width=30, textvariable=seg_filename)
        seg_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # Frame para la información de exportación
        info_frame = tk.Frame(form_frame, bg=app.tema["bg"])
        info_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)

        # Mostrar información de nodos y segmentos
        num_nodes = len(espacio_aereo.navpoints)
        num_segments = len(espacio_aereo.navsegments)
        info_text = f"Se exportarán {num_nodes} nodos y {num_segments} segmentos."
        tk.Label(info_frame, text=info_text, bg=app.tema["bg"], fg=app.tema["fg"]).pack(anchor=tk.W)

        status_label = tk.Label(form_frame, text="", bg=app.tema["bg"], fg="red")
        status_label.grid(row=4, column=0, columnspan=2, pady=5)

        # Función para exportar los datos
        def exportar_datos():
            try:
                nav_file = nav_entry.get().strip()
                seg_file = seg_entry.get().strip()

                if not nav_file or not seg_file:
                    status_label.config(text="Error: Los nombres de archivo no pueden estar vacíos")
                    return

                # Exportar nodos
                with open(nav_file, 'w') as f:
                    f.write("# Número Nombre Latitud Longitud\n")
                    for num, point in espacio_aereo.navpoints.items():
                        f.write(f"{num} {point.name} {point.latitude} {point.longitude}\n")

                # Exportar segmentos
                with open(seg_file, 'w') as f:
                    f.write("# Origen Destino Distancia\n")
                    for segment in espacio_aereo.navsegments:
                        origen = get_origin_number(segment)
                        destino = get_destination_number(segment)
                        distancia = get_distance(segment)
                        f.write(f"{origen} {destino} {distancia}\n")

                # Cerrar el diálogo
                dialog.destroy()

                # Mostrar mensaje de éxito
                messagebox.showinfo("Éxito", f"Mapa exportado correctamente a los archivos:\n{nav_file}\n{seg_file}")

            except Exception as e:
                status_label.config(text=f"Error: {str(e)}")

        # Función para seleccionar la ubicación del archivo de nodos
        def seleccionar_archivo_nodos():
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                initialfile=nav_filename.get()
            )
            if filename:
                nav_filename.set(filename)

        # Función para seleccionar la ubicación del archivo de segmentos
        def seleccionar_archivo_segmentos():
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                initialfile=seg_filename.get()
            )
            if filename:
                seg_filename.set(filename)

        # Botones de navegación para seleccionar archivos
        nav_browse_btn = tk.Button(form_frame, text="...", command=seleccionar_archivo_nodos,
                                 bg=app.tema["button_bg"], fg=app.tema["button_fg"], width=2)
        nav_browse_btn.grid(row=1, column=2, pady=5)

        seg_browse_btn = tk.Button(form_frame, text="...", command=seleccionar_archivo_segmentos,
                                 bg=app.tema["button_bg"], fg=app.tema["button_fg"], width=2)
        seg_browse_btn.grid(row=2, column=2, pady=5)

        # Botones de acción
        button_frame = tk.Frame(form_frame, bg=app.tema["bg"])
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        export_button = tk.Button(button_frame, text="Exportar", command=exportar_datos,
                              bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        export_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(button_frame, text="Cancelar", command=dialog.destroy,
                                bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        cancel_button.pack(side=tk.LEFT, padx=5)

    # Función para mostrar el diálogo para exportar el mapa editado
    def mostrar_dialogo_exportar_mapa():
        # Crear un diálogo para obtener información de exportación
        dialog = tk.Toplevel(map_window)
        dialog.title("Exportar Mapa Editado")
        dialog.geometry("450x280")
        dialog.configure(bg=app.tema["bg"])
        dialog.grab_set()  # Hacer que el diálogo sea modal

        # Frame para el formulario
        form_frame = tk.Frame(dialog, bg=app.tema["bg"])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Variables para los nombres de archivo
        nav_filename = tk.StringVar(value="nuevos_nodos.txt")
        seg_filename = tk.StringVar(value="nuevos_segmentos.txt")

        # Campos del formulario
        tk.Label(form_frame, text="Exportar a archivos:", font=(app.tema["font_family"], app.tema["font_size_normal"], "bold"),
               bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=10)

        tk.Label(form_frame, text="Archivo de nodos:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=1, column=0, sticky=tk.W, pady=5)
        nav_entry = tk.Entry(form_frame, width=30, textvariable=nav_filename)
        nav_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(form_frame, text="Archivo de segmentos:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=2, column=0, sticky=tk.W, pady=5)
        seg_entry = tk.Entry(form_frame, width=30, textvariable=seg_filename)
        seg_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # Frame para la información de exportación
        info_frame = tk.Frame(form_frame, bg=app.tema["bg"])
        info_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)

        # Mostrar información de nodos y segmentos
        num_nodes = len(espacio_aereo.navpoints)
        num_segments = len(espacio_aereo.navsegments)
        info_text = f"Se exportarán {num_nodes} nodos y {num_segments} segmentos."
        tk.Label(info_frame, text=info_text, bg=app.tema["bg"], fg=app.tema["fg"]).pack(anchor=tk.W)

        status_label = tk.Label(form_frame, text="", bg=app.tema["bg"], fg="red")
        status_label.grid(row=4, column=0, columnspan=2, pady=5)

        # Función para exportar los datos
        def exportar_datos():
            try:
                nav_file = nav_entry.get().strip()
                seg_file = seg_entry.get().strip()

                if not nav_file or not seg_file:
                    status_label.config(text="Error: Los nombres de archivo no pueden estar vacíos")
                    return

                # Exportar nodos
                with open(nav_file, 'w') as f:
                    f.write("# Número Nombre Latitud Longitud\n")
                    for num, point in espacio_aereo.navpoints.items():
                        f.write(f"{num} {point.name} {point.latitude} {point.longitude}\n")

                # Exportar segmentos
                with open(seg_file, 'w') as f:
                    f.write("# Origen Destino Distancia\n")
                    for segment in espacio_aereo.navsegments:
                        origen = get_origin_number(segment)
                        destino = get_destination_number(segment)
                        distancia = get_distance(segment)
                        f.write(f"{origen} {destino} {distancia}\n")

                # Cerrar el diálogo
                dialog.destroy()

                # Mostrar mensaje de éxito
                messagebox.showinfo("Éxito", f"Mapa exportado correctamente a los archivos:\n{nav_file}\n{seg_file}")

            except Exception as e:
                status_label.config(text=f"Error: {str(e)}")

        # Función para seleccionar la ubicación del archivo de nodos
        def seleccionar_archivo_nodos():
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                initialfile=nav_filename.get()
            )
            if filename:
                nav_filename.set(filename)

        # Función para seleccionar la ubicación del archivo de segmentos
        def seleccionar_archivo_segmentos():
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                initialfile=seg_filename.get()
            )
            if filename:
                seg_filename.set(filename)

        # Botones de navegación para seleccionar archivos
        nav_browse_btn = tk.Button(form_frame, text="...", command=seleccionar_archivo_nodos,
                                 bg=app.tema["button_bg"], fg=app.tema["button_fg"], width=2)
        nav_browse_btn.grid(row=1, column=2, pady=5)

        seg_browse_btn = tk.Button(form_frame, text="...", command=seleccionar_archivo_segmentos,
                                 bg=app.tema["button_bg"], fg=app.tema["button_fg"], width=2)
        seg_browse_btn.grid(row=2, column=2, pady=5)

        # Botones de acción
        button_frame = tk.Frame(form_frame, bg=app.tema["bg"])
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        export_button = tk.Button(button_frame, text="Exportar", command=exportar_datos,
                              bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        export_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(button_frame, text="Cancelar", command=dialog.destroy,
                                bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        cancel_button.pack(side=tk.LEFT, padx=5)

    # Función para mostrar el diálogo para exportar el mapa editado
    def mostrar_dialogo_exportar_mapa():
        # Crear un diálogo para obtener información de exportación
        dialog = tk.Toplevel(map_window)
        dialog.title("Exportar Mapa Editado")
        dialog.geometry("450x280")
        dialog.configure(bg=app.tema["bg"])
        dialog.grab_set()  # Hacer que el diálogo sea modal

        # Frame para el formulario
        form_frame = tk.Frame(dialog, bg=app.tema["bg"])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Variables para los nombres de archivo
        nav_filename = tk.StringVar(value="nuevos_nodos.txt")
        seg_filename = tk.StringVar(value="nuevos_segmentos.txt")

        # Campos del formulario
        tk.Label(form_frame, text="Exportar a archivos:", font=(app.tema["font_family"], app.tema["font_size_normal"], "bold"),
               bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=10)

        tk.Label(form_frame, text="Archivo de nodos:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=1, column=0, sticky=tk.W, pady=5)
        nav_entry = tk.Entry(form_frame, width=30, textvariable=nav_filename)
        nav_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(form_frame, text="Archivo de segmentos:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=2, column=0, sticky=tk.W, pady=5)
        seg_entry = tk.Entry(form_frame, width=30, textvariable=seg_filename)
        seg_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # Frame para la información de exportación
        info_frame = tk.Frame(form_frame, bg=app.tema["bg"])
        info_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)

        # Mostrar información de nodos y segmentos
        num_nodes = len(espacio_aereo.navpoints)
        num_segments = len(espacio_aereo.navsegments)
        info_text = f"Se exportarán {num_nodes} nodos y {num_segments} segmentos."
        tk.Label(info_frame, text=info_text, bg=app.tema["bg"], fg=app.tema["fg"]).pack(anchor=tk.W)

        status_label = tk.Label(form_frame, text="", bg=app.tema["bg"], fg="red")
        status_label.grid(row=4, column=0, columnspan=2, pady=5)

        # Función para exportar los datos
        def exportar_datos():
            try:
                nav_file = nav_entry.get().strip()
                seg_file = seg_entry.get().strip()

                if not nav_file or not seg_file:
                    status_label.config(text="Error: Los nombres de archivo no pueden estar vacíos")
                    return

                # Exportar nodos
                with open(nav_file, 'w') as f:
                    f.write("# Número Nombre Latitud Longitud\n")
                    for num, point in espacio_aereo.navpoints.items():
                        f.write(f"{num} {point.name} {point.latitude} {point.longitude}\n")

                # Exportar segmentos
                with open(seg_file, 'w') as f:
                    f.write("# Origen Destino Distancia\n")
                    for segment in espacio_aereo.navsegments:
                        origen = get_origin_number(segment)
                        destino = get_destination_number(segment)
                        distancia = get_distance(segment)
                        f.write(f"{origen} {destino} {distancia}\n")

                # Cerrar el diálogo
                dialog.destroy()

                # Mostrar mensaje de éxito
                messagebox.showinfo("Éxito", f"Mapa exportado correctamente a los archivos:\n{nav_file}\n{seg_file}")

            except Exception as e:
                status_label.config(text=f"Error: {str(e)}")

        # Función para seleccionar la ubicación del archivo de nodos
        def seleccionar_archivo_nodos():
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                initialfile=nav_filename.get()
            )
            if filename:
                nav_filename.set(filename)

        # Función para seleccionar la ubicación del archivo de segmentos
        def seleccionar_archivo_segmentos():
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                initialfile=seg_filename.get()
            )
            if filename:
                seg_filename.set(filename)

        # Botones de navegación para seleccionar archivos
        nav_browse_btn = tk.Button(form_frame, text="...", command=seleccionar_archivo_nodos,
                                 bg=app.tema["button_bg"], fg=app.tema["button_fg"], width=2)
        nav_browse_btn.grid(row=1, column=2, pady=5)

        seg_browse_btn = tk.Button(form_frame, text="...", command=seleccionar_archivo_segmentos,
                                 bg=app.tema["button_bg"], fg=app.tema["button_fg"], width=2)
        seg_browse_btn.grid(row=2, column=2, pady=5)

        # Botones de acción
        button_frame = tk.Frame(form_frame, bg=app.tema["bg"])
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        export_button = tk.Button(button_frame, text="Exportar", command=exportar_datos,
                              bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        export_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(button_frame, text="Cancelar", command=dialog.destroy,
                                bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        cancel_button.pack(side=tk.LEFT, padx=5)

    # Función para mostrar el diálogo para exportar el mapa editado
    def mostrar_dialogo_exportar_mapa():
        # Crear un diálogo para obtener información de exportación
        dialog = tk.Toplevel(map_window)
        dialog.title("Exportar Mapa Editado")
        dialog.geometry("450x280")
        dialog.configure(bg=app.tema["bg"])
        dialog.grab_set()  # Hacer que el diálogo sea modal

        # Frame para el formulario
        form_frame = tk.Frame(dialog, bg=app.tema["bg"])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Variables para los nombres de archivo
        nav_filename = tk.StringVar(value="nuevos_nodos.txt")
        seg_filename = tk.StringVar(value="nuevos_segmentos.txt")

        # Campos del formulario
        tk.Label(form_frame, text="Exportar a archivos:", font=(app.tema["font_family"], app.tema["font_size_normal"], "bold"),
               bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=10)

        tk.Label(form_frame, text="Archivo de nodos:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=1, column=0, sticky=tk.W, pady=5)
        nav_entry = tk.Entry(form_frame, width=30, textvariable=nav_filename)
        nav_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(form_frame, text="Archivo de segmentos:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=2, column=0, sticky=tk.W, pady=5)
        seg_entry = tk.Entry(form_frame, width=30, textvariable=seg_filename)
        seg_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # Frame para la información de exportación
        info_frame = tk.Frame(form_frame, bg=app.tema["bg"])
        info_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)

        # Mostrar información de nodos y segmentos
        num_nodes = len(espacio_aereo.navpoints)
        num_segments = len(espacio_aereo.navsegments)
        info_text = f"Se exportarán {num_nodes} nodos y {num_segments} segmentos."
        tk.Label(info_frame, text=info_text, bg=app.tema["bg"], fg=app.tema["fg"]).pack(anchor=tk.W)

        status_label = tk.Label(form_frame, text="", bg=app.tema["bg"], fg="red")
        status_label.grid(row=4, column=0, columnspan=2, pady=5)

        # Función para exportar los datos
        def exportar_datos():
            try:
                nav_file = nav_entry.get().strip()
                seg_file = seg_entry.get().strip()

                if not nav_file or not seg_file:
                    status_label.config(text="Error: Los nombres de archivo no pueden estar vacíos")
                    return

                # Exportar nodos
                with open(nav_file, 'w') as f:
                    f.write("# Número Nombre Latitud Longitud\n")
                    for num, point in espacio_aereo.navpoints.items():
                        f.write(f"{num} {point.name} {point.latitude} {point.longitude}\n")

                # Exportar segmentos
                with open(seg_file, 'w') as f:
                    f.write("# Origen Destino Distancia\n")
                    for segment in espacio_aereo.navsegments:
                        origen = get_origin_number(segment)
                        destino = get_destination_number(segment)
                        distancia = get_distance(segment)
                        f.write(f"{origen} {destino} {distancia}\n")

                # Cerrar el diálogo
                dialog.destroy()

                # Mostrar mensaje de éxito
                messagebox.showinfo("Éxito", f"Mapa exportado correctamente a los archivos:\n{nav_file}\n{seg_file}")

            except Exception as e:
                status_label.config(text=f"Error: {str(e)}")

        # Función para seleccionar la ubicación del archivo de nodos
        def seleccionar_archivo_nodos():
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                initialfile=nav_filename.get()
            )
            if filename:
                nav_filename.set(filename)

        # Función para seleccionar la ubicación del archivo de segmentos
        def seleccionar_archivo_segmentos():
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                initialfile=seg_filename.get()
            )
            if filename:
                seg_filename.set(filename)

        # Botones de navegación para seleccionar archivos
        nav_browse_btn = tk.Button(form_frame, text="...", command=seleccionar_archivo_nodos,
                                 bg=app.tema["button_bg"], fg=app.tema["button_fg"], width=2)
        nav_browse_btn.grid(row=1, column=2, pady=5)

        seg_browse_btn = tk.Button(form_frame, text="...", command=seleccionar_archivo_segmentos,
                                 bg=app.tema["button_bg"], fg=app.tema["button_fg"], width=2)
        seg_browse_btn.grid(row=2, column=2, pady=5)

        # Botones de acción
        button_frame = tk.Frame(form_frame, bg=app.tema["bg"])
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        export_button = tk.Button(button_frame, text="Exportar", command=exportar_datos,
                              bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        export_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(button_frame, text="Cancelar", command=dialog.destroy,
                                bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        cancel_button.pack(side=tk.LEFT, padx=5)

    # Función para mostrar el diálogo para exportar el mapa editado
    def mostrar_dialogo_exportar_mapa():
        # Crear un diálogo para obtener información de exportación
        dialog = tk.Toplevel(map_window)
        dialog.title("Exportar Mapa Editado")
        dialog.geometry("450x280")
        dialog.configure(bg=app.tema["bg"])
        dialog.grab_set()  # Hacer que el diálogo sea modal

        # Frame para el formulario
        form_frame = tk.Frame(dialog, bg=app.tema["bg"])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Variables para los nombres de archivo
        nav_filename = tk.StringVar(value="nuevos_nodos.txt")
        seg_filename = tk.StringVar(value="nuevos_segmentos.txt")

        # Campos del formulario
        tk.Label(form_frame, text="Exportar a archivos:", font=(app.tema["font_family"], app.tema["font_size_normal"], "bold"),
               bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=10)

        tk.Label(form_frame, text="Archivo de nodos:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=1, column=0, sticky=tk.W, pady=5)
        nav_entry = tk.Entry(form_frame, width=30, textvariable=nav_filename)
        nav_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(form_frame, text="Archivo de segmentos:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=2, column=0, sticky=tk.W, pady=5)
        seg_entry = tk.Entry(form_frame, width=30, textvariable=seg_filename)
        seg_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # Frame para la información de exportación
        info_frame = tk.Frame(form_frame, bg=app.tema["bg"])
        info_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)

        # Mostrar información de nodos y segmentos
        num_nodes = len(espacio_aereo.navpoints)
        num_segments = len(espacio_aereo.navsegments)
        info_text = f"Se exportarán {num_nodes} nodos y {num_segments} segmentos."
        tk.Label(info_frame, text=info_text, bg=app.tema["bg"], fg=app.tema["fg"]).pack(anchor=tk.W)

        status_label = tk.Label(form_frame, text="", bg=app.tema["bg"], fg="red")
        status_label.grid(row=4, column=0, columnspan=2, pady=5)

        # Función para exportar los datos
        def exportar_datos():
            try:
                nav_file = nav_entry.get().strip()
                seg_file = seg_entry.get().strip()

                if not nav_file or not seg_file:
                    status_label.config(text="Error: Los nombres de archivo no pueden estar vacíos")
                    return

                # Exportar nodos
                with open(nav_file, 'w') as f:
                    f.write("# Número Nombre Latitud Longitud\n")
                    for num, point in espacio_aereo.navpoints.items():
                        f.write(f"{num} {point.name} {point.latitude} {point.longitude}\n")

                # Exportar segmentos
                with open(seg_file, 'w') as f:
                    f.write("# Origen Destino Distancia\n")
                    for segment in espacio_aereo.navsegments:
                        origen = get_origin_number(segment)
                        destino = get_destination_number(segment)
                        distancia = get_distance(segment)
                        f.write(f"{origen} {destino} {distancia}\n")

                # Cerrar el diálogo
                dialog.destroy()

                # Mostrar mensaje de éxito
                messagebox.showinfo("Éxito", f"Mapa exportado correctamente a los archivos:\n{nav_file}\n{seg_file}")

            except Exception as e:
                status_label.config(text=f"Error: {str(e)}")

        # Función para seleccionar la ubicación del archivo de nodos
        def seleccionar_archivo_nodos():
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                initialfile=nav_filename.get()
            )
            if filename:
                nav_filename.set(filename)

        # Función para seleccionar la ubicación del archivo de segmentos
        def seleccionar_archivo_segmentos():
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                initialfile=seg_filename.get()
            )
            if filename:
                seg_filename.set(filename)

        # Botones de navegación para seleccionar archivos
        nav_browse_btn = tk.Button(form_frame, text="...", command=seleccionar_archivo_nodos,
                                 bg=app.tema["button_bg"], fg=app.tema["button_fg"], width=2)
        nav_browse_btn.grid(row=1, column=2, pady=5)

        seg_browse_btn = tk.Button(form_frame, text="...", command=seleccionar_archivo_segmentos,
                                 bg=app.tema["button_bg"], fg=app.tema["button_fg"], width=2)
        seg_browse_btn.grid(row=2, column=2, pady=5)

        # Botones de acción
        button_frame = tk.Frame(form_frame, bg=app.tema["bg"])
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        export_button = tk.Button(button_frame, text="Exportar", command=exportar_datos,
                              bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        export_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(button_frame, text="Cancelar", command=dialog.destroy,
                                bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        cancel_button.pack(side=tk.LEFT, padx=5)

    # Función para mostrar el diálogo para exportar el mapa editado
    def mostrar_dialogo_exportar_mapa():
        # Crear un diálogo para obtener información de exportación
        dialog = tk.Toplevel(map_window)
        dialog.title("Exportar Mapa Editado")
        dialog.geometry("450x280")
        dialog.configure(bg=app.tema["bg"])
        dialog.grab_set()  # Hacer que el diálogo sea modal

        # Frame para el formulario
        form_frame = tk.Frame(dialog, bg=app.tema["bg"])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Variables para los nombres de archivo
        nav_filename = tk.StringVar(value="nuevos_nodos.txt")
        seg_filename = tk.StringVar(value="nuevos_segmentos.txt")

        # Campos del formulario
        tk.Label(form_frame, text="Exportar a archivos:", font=(app.tema["font_family"], app.tema["font_size_normal"], "bold"),
               bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=10)

        tk.Label(form_frame, text="Archivo de nodos:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=1, column=0, sticky=tk.W, pady=5)
        nav_entry = tk.Entry(form_frame, width=30, textvariable=nav_filename)
        nav_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(form_frame, text="Archivo de segmentos:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=2, column=0, sticky=tk.W, pady=5)
        seg_entry = tk.Entry(form_frame, width=30, textvariable=seg_filename)
        seg_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # Frame para la información de exportación
        info_frame = tk.Frame(form_frame, bg=app.tema["bg"])
        info_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)

        # Mostrar información de nodos y segmentos
        num_nodes = len(espacio_aereo.navpoints)
        num_segments = len(espacio_aereo.navsegments)
        info_text = f"Se exportarán {num_nodes} nodos y {num_segments} segmentos."
        tk.Label(info_frame, text=info_text, bg=app.tema["bg"], fg=app.tema["fg"]).pack(anchor=tk.W)

        status_label = tk.Label(form_frame, text="", bg=app.tema["bg"], fg="red")
        status_label.grid(row=4, column=0, columnspan=2, pady=5)

        # Función para exportar los datos
        def exportar_datos():
            try:
                nav_file = nav_entry.get().strip()
                seg_file = seg_entry.get().strip()

                if not nav_file or not seg_file:
                    status_label.config(text="Error: Los nombres de archivo no pueden estar vacíos")
                    return

                # Exportar nodos
                with open(nav_file, 'w') as f:
                    f.write("# Número Nombre Latitud Longitud\n")
                    for num, point in espacio_aereo.navpoints.items():
                        f.write(f"{num} {point.name} {point.latitude} {point.longitude}\n")

                # Exportar segmentos
                with open(seg_file, 'w') as f:
                    f.write("# Origen Destino Distancia\n")
                    for segment in espacio_aereo.navsegments:
                        origen = get_origin_number(segment)
                        destino = get_destination_number(segment)
                        distancia = get_distance(segment)
                        f.write(f"{origen} {destino} {distancia}\n")

                # Cerrar el diálogo
                dialog.destroy()

                # Mostrar mensaje de éxito
                messagebox.showinfo("Éxito", f"Mapa exportado correctamente a los archivos:\n{nav_file}\n{seg_file}")

            except Exception as e:
                status_label.config(text=f"Error: {str(e)}")

        # Función para seleccionar la ubicación del archivo de nodos
        def seleccionar_archivo_nodos():
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                initialfile=nav_filename.get()
            )
            if filename:
                nav_filename.set(filename)

        # Función para seleccionar la ubicación del archivo de segmentos
        def seleccionar_archivo_segmentos():
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                initialfile=seg_filename.get()
            )
            if filename:
                seg_filename.set(filename)

        # Botones de navegación para seleccionar archivos
        nav_browse_btn = tk.Button(form_frame, text="...", command=seleccionar_archivo_nodos,
                                 bg=app.tema["button_bg"], fg=app.tema["button_fg"], width=2)
        nav_browse_btn.grid(row=1, column=2, pady=5)

        seg_browse_btn = tk.Button(form_frame, text="...", command=seleccionar_archivo_segmentos,
                                 bg=app.tema["button_bg"], fg=app.tema["button_fg"], width=2)
        seg_browse_btn.grid(row=2, column=2, pady=5)

        # Botones de acción
        button_frame = tk.Frame(form_frame, bg=app.tema["bg"])
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        export_button = tk.Button(button_frame, text="Exportar", command=exportar_datos,
                              bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        export_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(button_frame, text="Cancelar", command=dialog.destroy,
                                bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        cancel_button.pack(side=tk.LEFT, padx=5)

    # Función para mostrar el diálogo para exportar el mapa editado
    def mostrar_dialogo_exportar_mapa():
        # Crear un diálogo para obtener información de exportación
        dialog = tk.Toplevel(map_window)
        dialog.title("Exportar Mapa Editado")
        dialog.geometry("450x280")
        dialog.configure(bg=app.tema["bg"])
        dialog.grab_set()  # Hacer que el diálogo sea modal

        # Frame para el formulario
        form_frame = tk.Frame(dialog, bg=app.tema["bg"])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Variables para los nombres de archivo
        nav_filename = tk.StringVar(value="nuevos_nodos.txt")
        seg_filename = tk.StringVar(value="nuevos_segmentos.txt")

        # Campos del formulario
        tk.Label(form_frame, text="Exportar a archivos:", font=(app.tema["font_family"], app.tema["font_size_normal"], "bold"),
               bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=10)

        tk.Label(form_frame, text="Archivo de nodos:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=1, column=0, sticky=tk.W, pady=5)
        nav_entry = tk.Entry(form_frame, width=30, textvariable=nav_filename)
        nav_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(form_frame, text="Archivo de segmentos:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=2, column=0, sticky=tk.W, pady=5)
        seg_entry = tk.Entry(form_frame, width=30, textvariable=seg_filename)
        seg_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # Frame para la información de exportación
        info_frame = tk.Frame(form_frame, bg=app.tema["bg"])
        info_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)

        # Mostrar información de nodos y segmentos
        num_nodes = len(espacio_aereo.navpoints)
        num_segments = len(espacio_aereo.navsegments)
        info_text = f"Se exportarán {num_nodes} nodos y {num_segments} segmentos."
        tk.Label(info_frame, text=info_text, bg=app.tema["bg"], fg=app.tema["fg"]).pack(anchor=tk.W)

        status_label = tk.Label(form_frame, text="", bg=app.tema["bg"], fg="red")
        status_label.grid(row=4, column=0, columnspan=2, pady=5)

        # Función para exportar los datos
        def exportar_datos():
            try:
                nav_file = nav_entry.get().strip()
                seg_file = seg_entry.get().strip()

                if not nav_file or not seg_file:
                    status_label.config(text="Error: Los nombres de archivo no pueden estar vacíos")
                    return

                # Exportar nodos
                with open(nav_file, 'w') as f:
                    f.write("# Número Nombre Latitud Longitud\n")
                    for num, point in espacio_aereo.navpoints.items():
                        f.write(f"{num} {point.name} {point.latitude} {point.longitude}\n")

                # Exportar segmentos
                with open(seg_file, 'w') as f:
                    f.write("# Origen Destino Distancia\n")
                    for segment in espacio_aereo.navsegments:
                        origen = get_origin_number(segment)
                        destino = get_destination_number(segment)
                        distancia = get_distance(segment)
                        f.write(f"{origen} {destino} {distancia}\n")

                # Cerrar el diálogo
                dialog.destroy()

                # Mostrar mensaje de éxito
                messagebox.showinfo("Éxito", f"Mapa exportado correctamente a los archivos:\n{nav_file}\n{seg_file}")

            except Exception as e:
                status_label.config(text=f"Error: {str(e)}")

        # Función para seleccionar la ubicación del archivo de nodos
        def seleccionar_archivo_nodos():
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                initialfile=nav_filename.get()
            )
            if filename:
                nav_filename.set(filename)

        # Función para seleccionar la ubicación del archivo de segmentos
        def seleccionar_archivo_segmentos():
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                initialfile=seg_filename.get()
            )
            if filename:
                seg_filename.set(filename)

        # Botones de navegación para seleccionar archivos
        nav_browse_btn = tk.Button(form_frame, text="...", command=seleccionar_archivo_nodos,
                                 bg=app.tema["button_bg"], fg=app.tema["button_fg"], width=2)
        nav_browse_btn.grid(row=1, column=2, pady=5)

        seg_browse_btn = tk.Button(form_frame, text="...", command=seleccionar_archivo_segmentos,
                                 bg=app.tema["button_bg"], fg=app.tema["button_fg"], width=2)
        seg_browse_btn.grid(row=2, column=2, pady=5)

        # Botones de acción
        button_frame = tk.Frame(form_frame, bg=app.tema["bg"])
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        export_button = tk.Button(button_frame, text="Exportar", command=exportar_datos,
                              bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        export_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(button_frame, text="Cancelar", command=dialog.destroy,
                                bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        cancel_button.pack(side=tk.LEFT, padx=5)

    # Función para mostrar el diálogo para exportar el mapa editado
    def mostrar_dialogo_exportar_mapa():
        # Crear un diálogo para obtener información de exportación
        dialog = tk.Toplevel(map_window)
        dialog.title("Exportar Mapa Editado")
        dialog.geometry("450x280")
        dialog.configure(bg=app.tema["bg"])
        dialog.grab_set()  # Hacer que el diálogo sea modal

        # Frame para el formulario
        form_frame = tk.Frame(dialog, bg=app.tema["bg"])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Variables para los nombres de archivo
        nav_filename = tk.StringVar(value="nuevos_nodos.txt")
        seg_filename = tk.StringVar(value="nuevos_segmentos.txt")

        # Campos del formulario
        tk.Label(form_frame, text="Exportar a archivos:", font=(app.tema["font_family"], app.tema["font_size_normal"], "bold"),
               bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=10)

        tk.Label(form_frame, text="Archivo de nodos:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=1, column=0, sticky=tk.W, pady=5)
        nav_entry = tk.Entry(form_frame, width=30, textvariable=nav_filename)
        nav_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(form_frame, text="Archivo de segmentos:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=2, column=0, sticky=tk.W, pady=5)
        seg_entry = tk.Entry(form_frame, width=30, textvariable=seg_filename)
        seg_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # Frame para la información de exportación
        info_frame = tk.Frame(form_frame, bg=app.tema["bg"])
        info_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)

        # Mostrar información de nodos y segmentos
        num_nodes = len(espacio_aereo.navpoints)
        num_segments = len(espacio_aereo.navsegments)
        info_text = f"Se exportarán {num_nodes} nodos y {num_segments} segmentos."
        tk.Label(info_frame, text=info_text, bg=app.tema["bg"], fg=app.tema["fg"]).pack(anchor=tk.W)

        status_label = tk.Label(form_frame, text="", bg=app.tema["bg"], fg="red")
        status_label.grid(row=4, column=0, columnspan=2, pady=5)

        # Función para exportar los datos
        def exportar_datos():
            try:
                nav_file = nav_entry.get().strip()
                seg_file = seg_entry.get().strip()

                if not nav_file or not seg_file:
                    status_label.config(text="Error: Los nombres de archivo no pueden estar vacíos")
                    return

                # Exportar nodos
                with open(nav_file, 'w') as f:
                    f.write("# Número Nombre Latitud Longitud\n")
                    for num, point in espacio_aereo.navpoints.items():
                        f.write(f"{num} {point.name} {point.latitude} {point.longitude}\n")

                # Exportar segmentos
                with open(seg_file, 'w') as f:
                    f.write("# Origen Destino Distancia\n")
                    for segment in espacio_aereo.navsegments:
                        origen = get_origin_number(segment)
                        destino = get_destination_number(segment)
                        distancia = get_distance(segment)
                        f.write(f"{origen} {destino} {distancia}\n")

                # Cerrar el diálogo
                dialog.destroy()

                # Mostrar mensaje de éxito
                messagebox.showinfo("Éxito", f"Mapa exportado correctamente a los archivos:\n{nav_file}\n{seg_file}")

            except Exception as e:
                status_label.config(text=f"Error: {str(e)}")

        # Función para seleccionar la ubicación del archivo de nodos
        def seleccionar_archivo_nodos():
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                initialfile=nav_filename.get()
            )
            if filename:
                nav_filename.set(filename)

        # Función para seleccionar la ubicación del archivo de segmentos
        def seleccionar_archivo_segmentos():
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                initialfile=seg_filename.get()
            )
            if filename:
                seg_filename.set(filename)

        # Botones de navegación para seleccionar archivos
        nav_browse_btn = tk.Button(form_frame, text="...", command=seleccionar_archivo_nodos,
                                 bg=app.tema["button_bg"], fg=app.tema["button_fg"], width=2)
        nav_browse_btn.grid(row=1, column=2, pady=5)

        seg_browse_btn = tk.Button(form_frame, text="...", command=seleccionar_archivo_segmentos,
                                 bg=app.tema["button_bg"], fg=app.tema["button_fg"], width=2)
        seg_browse_btn.grid(row=2, column=2, pady=5)

        # Botones de acción
        button_frame = tk.Frame(form_frame, bg=app.tema["bg"])
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        export_button = tk.Button(button_frame, text="Exportar", command=exportar_datos,
                              bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        export_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(button_frame, text="Cancelar", command=dialog.destroy,
                                bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        cancel_button.pack(side=tk.LEFT, padx=5)

    # Función para mostrar el diálogo para exportar el mapa editado
    def mostrar_dialogo_exportar_mapa():
        # Crear un diálogo para obtener información de exportación
        dialog = tk.Toplevel(map_window)
        dialog.title("Exportar Mapa Editado")
        dialog.geometry("450x280")
        dialog.configure(bg=app.tema["bg"])
        dialog.grab_set()  # Hacer que el diálogo sea modal

        # Frame para el formulario
        form_frame = tk.Frame(dialog, bg=app.tema["bg"])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Variables para los nombres de archivo
        nav_filename = tk.StringVar(value="nuevos_nodos.txt")
        seg_filename = tk.StringVar(value="nuevos_segmentos.txt")

        # Campos del formulario
        tk.Label(form_frame, text="Exportar a archivos:", font=(app.tema["font_family"], app.tema["font_size_normal"], "bold"),
               bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=10)

        tk.Label(form_frame, text="Archivo de nodos:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=1, column=0, sticky=tk.W, pady=5)
        nav_entry = tk.Entry(form_frame, width=30, textvariable=nav_filename)
        nav_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(form_frame, text="Archivo de segmentos:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=2, column=0, sticky=tk.W, pady=5)
        seg_entry = tk.Entry(form_frame, width=30, textvariable=seg_filename)
        seg_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # Frame para la información de exportación
        info_frame = tk.Frame(form_frame, bg=app.tema["bg"])
        info_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)

        # Mostrar información de nodos y segmentos
        num_nodes = len(espacio_aereo.navpoints)
        num_segments = len(espacio_aereo.navsegments)
        info_text = f"Se exportarán {num_nodes} nodos y {num_segments} segmentos."
        tk.Label(info_frame, text=info_text, bg=app.tema["bg"], fg=app.tema["fg"]).pack(anchor=tk.W)

        status_label = tk.Label(form_frame, text="", bg=app.tema["bg"], fg="red")
        status_label.grid(row=4, column=0, columnspan=2, pady=5)

        # Función para exportar los datos
        def exportar_datos():
            try:
                nav_file = nav_entry.get().strip()
                seg_file = seg_entry.get().strip()

                if not nav_file or not seg_file:
                    status_label.config(text="Error: Los nombres de archivo no pueden estar vacíos")
                    return

                # Exportar nodos
                with open(nav_file, 'w') as f:
                    f.write("# Número Nombre Latitud Longitud\n")
                    for num, point in espacio_aereo.navpoints.items():
                        f.write(f"{num} {point.name} {point.latitude} {point.longitude}\n")

                # Exportar segmentos
                with open(seg_file, 'w') as f:
                    f.write("# Origen Destino Distancia\n")
                    for segment in espacio_aereo.navsegments:
                        origen = get_origin_number(segment)
                        destino = get_destination_number(segment)
                        distancia = get_distance(segment)
                        f.write(f"{origen} {destino} {distancia}\n")

                # Cerrar el diálogo
                dialog.destroy()

                # Mostrar mensaje de éxito
                messagebox.showinfo("Éxito", f"Mapa exportado correctamente a los archivos:\n{nav_file}\n{seg_file}")

            except Exception as e:
                status_label.config(text=f"Error: {str(e)}")

        # Función para seleccionar la ubicación del archivo de nodos
        def seleccionar_archivo_nodos():
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                initialfile=nav_filename.get()
            )
            if filename:
                nav_filename.set(filename)

        # Función para seleccionar la ubicación del archivo de segmentos
        def seleccionar_archivo_segmentos():
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                initialfile=seg_filename.get()
            )
            if filename:
                seg_filename.set(filename)

        # Botones de navegación para seleccionar archivos
        nav_browse_btn = tk.Button(form_frame, text="...", command=seleccionar_archivo_nodos,
                                 bg=app.tema["button_bg"], fg=app.tema["button_fg"], width=2)
        nav_browse_btn.grid(row=1, column=2, pady=5)

        seg_browse_btn = tk.Button(form_frame, text="...", command=seleccionar_archivo_segmentos,
                                 bg=app.tema["button_bg"], fg=app.tema["button_fg"], width=2)
        seg_browse_btn.grid(row=2, column=2, pady=5)

        # Botones de acción
        button_frame = tk.Frame(form_frame, bg=app.tema["bg"])
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        export_button = tk.Button(button_frame, text="Exportar", command=exportar_datos,
                              bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        export_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(button_frame, text="Cancelar", command=dialog.destroy,
                                bg=app.tema["button_bg"], fg=app.tema["button_fg"])
        cancel_button.pack(side=tk.LEFT, padx=5)

def mostrar_vecinos(app):
    global espacio_aereo

    if not espacio_aereo or not espacio_aereo.navpoints:
        messagebox.showwarning("Advertencia",
                               "No hay datos de espacio aéreo cargados. Por favor cargue los datos primero.")
        return

    neighbors_window = tk.Toplevel(app)
    neighbors_window.title("Encontrar Vecinos")
    neighbors_window.geometry("500x400")

    # Aplicar el tema actual a la ventana
    tema = app.tema
    neighbors_window.configure(bg=tema["bg"])

    input_frame = tk.Frame(neighbors_window, bg=tema["bg"])
    input_frame.pack(fill=tk.X, pady=10, padx=10)

    point_label = tk.Label(input_frame, text="Punto de Navegación:", bg=tema["bg"], fg=tema["fg"])
    point_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

    nav_point = tk.StringVar()
    point_entry = tk.Entry(input_frame, textvariable=nav_point, width=20, bg=tema["entry_bg"], fg=tema["entry_fg"])
    point_entry.grid(row=0, column=1, padx=5, pady=5)

    results_text = tk.Text(neighbors_window, width=50, height=15, bg=tema["text_bg"], fg=tema["text_fg"])
    results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    scrollbar = tk.Scrollbar(results_text)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    results_text.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=results_text.yview)

    button_frame = tk.Frame(neighbors_window, bg=tema["bg"])
    button_frame.pack(fill=tk.X, pady=5)

    find_button = tk.Button(button_frame, text="Encontrar Vecinos",
                            command=lambda: encontrar_y_mostrar_vecinos(app, results_text, nav_point),
                            bg=tema["button_bg"], fg=tema["button_fg"])
    find_button.pack(side=tk.LEFT, padx=5, pady=5)

    # Botón para exportar vecinos a Google Earth
    export_button = tk.Button(button_frame, text="Exportar a Google Earth",
                              command=lambda: exportar_vecinos_a_google_earth(app, nav_point),
                              state=tk.DISABLED if not espacio_aereo else tk.NORMAL,
                              bg=tema["button_bg"], fg=tema["button_fg"])
    export_button.pack(side=tk.LEFT, padx=5, pady=5)


def encontrar_y_mostrar_vecinos(app, results_text, nav_point):
    global espacio_aereo

    results_text.delete(1.0, tk.END)

    nav_name = nav_point.get().strip()

    if not nav_name:
        messagebox.showwarning("Advertencia", "Por favor ingrese un nombre de punto de navegación.")
        return

    found_point = get_navpoint_by_name(espacio_aereo, nav_name)

    if not found_point:
        results_text.insert(tk.END, f"Punto de navegación '{nav_name}' no encontrado.")
        return

    vecinos = []
    for segment in espacio_aereo.navsegments:
        if get_origin_number(segment) == found_point.number:
            destination_number = get_destination_number(segment)
            if destination_number in espacio_aereo.navpoints:
                vecino = espacio_aereo.navpoints[destination_number]
                distancia = get_distance(segment)
                vecinos.append((vecino, distancia))

    vecinos.sort(key=lambda x: x[0].name)

    result_text = f"Vecinos de {found_point.name} (Número: {found_point.number}):\n"
    result_text += f"Ubicación: ({found_point.latitude}, {found_point.longitude})\n\n"

    if vecinos:
        for neighbor_info in vecinos:
            neighbor = neighbor_info[0]
            distance = neighbor_info[1]
            result_text += f"{neighbor.name} (Número: {neighbor.number}) - Distancia: {distance:.2f}\n"
    else:
        result_text += "No se encontraron vecinos."

    results_text.insert(tk.END, result_text)

    mostrar_espacio_aereo(app, punto_destacado=found_point, vecinos=vecinos)

    app.status.config(text=f"Encontrados {len(vecinos)} vecinos para {found_point.name}")

    # Guardar los vecinos encontrados para posible exportación
    app.last_neighbors_data = (found_point, vecinos)

def exportar_vecinos_a_google_earth(app, nav_point):
    global espacio_aereo

    nav_name = nav_point.get().strip()

    if not nav_name:
        messagebox.showwarning("Advertencia", "Por favor ingrese un nombre de punto de navegación.")
        return

    # Intentar obtener el punto de navegación
    found_point = get_navpoint_by_name(espacio_aereo, nav_name)

    if not found_point:
        messagebox.showwarning("Advertencia", f"Punto de navegación '{nav_name}' no encontrado.")
        return

    # Buscar vecinos del punto
    vecinos = []
    for segment in espacio_aereo.navsegments:
        if get_origin_number(segment) == found_point.number:
            destination_number = get_destination_number(segment)
            if destination_number in espacio_aereo.navpoints:
                vecino = espacio_aereo.navpoints[destination_number]
                distancia = get_distance(segment)
                vecinos.append((vecino, distancia))

    if not vecinos:
        messagebox.showwarning("Advertencia", f"No se encontraron vecinos para '{nav_name}'.")
        return

    # Verificar si tenemos vecinos antes de intentar exportar
    if not vecinos:
        messagebox.showwarning("Advertencia", f"No se encontraron vecinos para '{nav_name}'.")
        return

    try:
        # Importar el módulo kml_generator.py
        import kml_generator

        # Crear contenido KML utilizando el módulo kml_generator
        kml_content = kml_generator.generate_neighbors_kml(found_point, vecinos, espacio_aereo)

        # Solicitar ubicación para guardar
        filename = filedialog.asksaveasfilename(
            defaultextension=".kml",
            filetypes=[("Archivos KML", "*.kml"), ("Todos los archivos", "*.*")],
            title=f"Guardar vecinos de {nav_name} como KML"
        )

        if not filename:
            return  # Usuario canceló el diálogo

        # Asegurarse de que el archivo tenga extensión .kml
        if not filename.lower().endswith('.kml'):
            filename += '.kml'

        # Guardar el archivo utilizando kml_generator
        if kml_generator.save_kml_to_file(kml_content, filename):
            messagebox.showinfo("Éxito", f"Vecinos de {nav_name} exportados a {filename}")

            # Preguntar si quiere abrir en Google Earth
            if messagebox.askyesno("Abrir en Google Earth", "¿Desea abrir el archivo en Google Earth?"):
                try:
                    os.startfile(filename)
                except Exception as e:
                    messagebox.showwarning("Error",
                                           f"No se pudo abrir Google Earth automáticamente: {str(e)}\nPor favor, abra el archivo manualmente.")
        else:
            messagebox.showerror("Error", f"No se pudo guardar el archivo.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al exportar vecinos: {str(e)}")

def encontrar_ruta(app):
    """Abre una ventana para encontrar una ruta entre dos puntos."""
    global espacio_aereo

    if not espacio_aereo:
        messagebox.showerror("Error", "No hay datos cargados.")
        return

    ventana = tk.Toplevel(app)
    ventana.title("Encontrar Ruta")
    ventana.geometry("600x500")
    ventana.configure(bg=app.tema["bg"])

    # Frame para entrada de datos
    frame_entrada = tk.Frame(ventana, bg=app.tema["bg"])
    frame_entrada.pack(fill="x", padx=20, pady=10)

    # Etiquetas y entradas para origen y destino
    tk.Label(frame_entrada, text="Origen:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=0, column=0, padx=5, pady=5)
    origin_point = tk.StringVar()
    entrada_origen = tk.Entry(frame_entrada, textvariable=origin_point, bg=app.tema["entry_bg"],
                              fg=app.tema["entry_fg"])
    entrada_origen.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_entrada, text="Destino:", bg=app.tema["bg"], fg=app.tema["fg"]).grid(row=1, column=0, padx=5, pady=5)
    dest_point = tk.StringVar()
    entrada_destino = tk.Entry(frame_entrada, textvariable=dest_point, bg=app.tema["entry_bg"], fg=app.tema["entry_fg"])
    entrada_destino.grid(row=1, column=1, padx=5, pady=5)

    # Frame para botones
    frame_botones = tk.Frame(ventana, bg=app.tema["bg"])
    frame_botones.pack(fill="x", padx=20, pady=5)

    # Botón para encontrar ruta más corta
    tk.Button(
        frame_botones,
        text="Encontrar Ruta Más Corta",
        command=lambda: encontrar_y_mostrar_ruta(app, path_text, origin_point, dest_point),
        bg=app.tema["button_bg"],
        fg=app.tema["button_fg"],
        font=("Segoe UI", 10),
        padx=12,
        pady=6
    ).pack(side=tk.LEFT, padx=5)

    # Botón para exportar a Google Earth
    tk.Button(
        frame_botones,
        text="Exportar a Google Earth",
        command=lambda: exportar_ruta_a_google_earth_helper(app, app.last_path_data[0]) if hasattr(app,
                                                                                                   'last_path_data') and app.last_path_data else messagebox.showinfo(
            "Información", "Primero debes calcular una ruta para poder exportarla."),
        bg=app.tema["button_bg"],
        fg=app.tema["button_fg"],
        font=("Segoe UI", 10),
        padx=12,
        pady=6
    ).pack(side=tk.LEFT, padx=5)

    # Botón para comparar rutas
    tk.Button(
        frame_botones,
        text="Comparar Rutas Alternativas",
        command=lambda: comparar_rutas(app, origin_point, dest_point),
        bg=app.tema["button_bg"],
        fg=app.tema["button_fg"],
        font=("Segoe UI", 10),
        padx=12,
        pady=6
    ).pack(side=tk.LEFT, padx=5)

    # Área de texto para mostrar resultados
    path_text = tk.Text(ventana, height=15, bg=app.tema["text_bg"], fg=app.tema["text_fg"])
    path_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)


def encontrar_y_mostrar_ruta(app, path_text, origin_point, dest_point):
    path_text.delete(1.0, tk.END)

    origin_name = origin_point.get().strip()
    dest_name = dest_point.get().strip()

    if not origin_name or not dest_name:
        messagebox.showwarning("Advertencia", "Por favor ingrese nombres para el origen y destino.")
        return

    # Verificar si el origen es un aeropuerto
    origin_is_airport = origin_name.startswith(("LE", "LF"))
    if origin_is_airport:
        origin_airport = get_navairport_by_name(espacio_aereo, origin_name)
        if not origin_airport:
            path_text.insert(tk.END, f"ERROR: No se encontró ningún aeropuerto con el código '{origin_name}'.\n")
            path_text.insert(tk.END, "Por favor verifique que el código del aeropuerto de origen sea correcto.\n")
            return
        origin = origin_name  # Usamos el código del aeropuerto directamente
    else:
        # Buscar como punto de navegación normal
        origin = get_navpoint_by_name(espacio_aereo, origin_name)
        if not origin:
            path_text.insert(tk.END, f"ERROR: No se encontró ningún punto con el nombre '{origin_name}'.\n")
            path_text.insert(tk.END, "Por favor verifique que el nombre del punto de origen sea correcto.\n")
            return

    # Verificar si el destino es un aeropuerto
    dest_is_airport = dest_name.startswith(("LE", "LF"))
    if dest_is_airport:
        dest_airport = get_navairport_by_name(espacio_aereo, dest_name)
        if not dest_airport:
            path_text.insert(tk.END, f"ERROR: No se encontró ningún aeropuerto con el código '{dest_name}'.\n")
            path_text.insert(tk.END, "Por favor verifique que el código del aeropuerto de destino sea correcto.\n")
            return
        dest = dest_name  # Usamos el código del aeropuerto directamente
    else:
        # Buscar como punto de navegación normal
        dest = get_navpoint_by_name(espacio_aereo, dest_name)
        if not dest:
            path_text.insert(tk.END, f"ERROR: No se encontró ningún punto con el nombre '{dest_name}'.\n")
            path_text.insert(tk.END, "Por favor verifique que el nombre del punto de destino sea correcto.\n")
            return

    # Si son puntos de navegación normales, verificar si tienen segmentos conectados
    if not origin_is_airport and not dest_is_airport:
        origin_has_segments = False
        dest_has_segments = False

        for segment in espacio_aereo.navsegments:
            if segment.origin_number == origin.number or segment.destination_number == origin.number:
                origin_has_segments = True
            if segment.origin_number == dest.number or segment.destination_number == dest.number:
                dest_has_segments = True

        if not origin_has_segments:
            path_text.insert(tk.END, f"ERROR: El punto '{origin.name}' no está conectado a ningún segmento.\n")
            path_text.insert(tk.END,
                             "Este punto está aislado en el grafo de navegación y no puede ser utilizado para ruteo.\n")
            return

        if not dest_has_segments:
            path_text.insert(tk.END, f"ERROR: El punto '{dest.name}' no está conectado a ningún segmento.\n")
            path_text.insert(tk.END,
                             "Este punto está aislado en el grafo de navegación y no puede ser utilizado para ruteo.\n")
            return

    # Mensaje personalizado según los tipos de origen y destino
    if origin_is_airport and dest_is_airport:
        path_text.insert(tk.END,
                         f"Buscando ruta del aeropuerto {origin_name} al aeropuerto {dest_name} usando algoritmo A*...\n\n")

        # Mostrar información de los aeropuertos para depuración
        path_text.insert(tk.END, f"[Debug] Aeropuerto origen ({origin_name}):\n")
        if origin_airport.sids:
            path_text.insert(tk.END, f"  SIDs: {origin_airport.sids}\n")
        else:
            path_text.insert(tk.END, "  No tiene SIDs definidos\n")

        path_text.insert(tk.END, f"[Debug] Aeropuerto destino ({dest_name}):\n")
        if dest_airport.stars:
            path_text.insert(tk.END, f"  STARs: {dest_airport.stars}\n")
        else:
            path_text.insert(tk.END, "  No tiene STARs definidos\n")

        path_text.insert(tk.END, "\n")
    elif origin_is_airport:
        path_text.insert(tk.END,
                         f"Buscando ruta del aeropuerto {origin_name} al punto {dest_name} usando algoritmo A*...\n\n")
    elif dest_is_airport:
        path_text.insert(tk.END,
                         f"Buscando ruta del punto {origin_name} al aeropuerto {dest_name} usando algoritmo A*...\n\n")
    else:
        path_text.insert(tk.END,
                         f"Buscando ruta de {origin_name} a {dest_name} usando algoritmo A*...\n\n")

    # Usar el algoritmo A* para encontrar la ruta (con depuración activada)
    path_points, total_distance = find_shortest_path_astar(espacio_aereo, origin, dest, debug=True)

    if not path_points:
        path_text.insert(tk.END, "No se encontró ninguna ruta entre estos puntos.\n")
        if origin_is_airport or dest_is_airport:
            path_text.insert(tk.END,
                             "Esto puede deberse a que no existen SIDs o STARs que permitan conectar los aeropuertos,\n")
            path_text.insert(tk.END,
                             "o a que se encuentran en componentes desconectados del grafo de navegación.\n")
        else:
            path_text.insert(tk.END,
                             "Ambos puntos tienen segmentos conectados, pero no existe un camino que los una.\n")
            path_text.insert(tk.END,
                             "Esto puede deberse a que se encuentran en componentes desconectados del grafo de navegación.\n")
        return

    path_text.insert(tk.END, f"Ruta encontrada: {len(path_points)} puntos\n")
    path_text.insert(tk.END, f"Distancia total: {total_distance:.2f} km\n\n")

    path_text.insert(tk.END, "Puntos de la ruta:\n")
    for i, point in enumerate(path_points):
        path_text.insert(tk.END, f"{i + 1}. {point.name} (#{point.number})\n")

    # Mostrar la ruta en el mapa
    mostrar_espacio_aereo(app, ruta=path_points)

    # Guardar los datos de la ruta para exportación posterior
    app.last_path_data = (path_points, total_distance)


def comparar_rutas(app, origin_point=None, dest_point=None):
    """Abre una nueva ventana para comparar diferentes rutas entre dos puntos."""
    ventana_comparacion = tk.Toplevel(app)
    ventana_comparacion.title("Comparar Rutas")
    ventana_comparacion.geometry("800x600")
    ventana_comparacion.configure(bg=app.tema["bg"])

    # Frame principal
    frame_principal = tk.Frame(ventana_comparacion, bg=app.tema["bg"])
    frame_principal.pack(fill="both", expand=True, padx=20, pady=10)

    # Frame para entrada de datos
    frame_entrada = tk.Frame(frame_principal, bg=app.tema["bg"])
    frame_entrada.pack(fill="x", pady=10)

    # Etiquetas y entradas para origen y destino
    tk.Label(frame_entrada, text="Origen:", bg=app.tema["bg"], fg=app.tema["fg"]).pack(side=tk.LEFT, padx=5)
    origen = tk.StringVar(value=origin_point.get() if origin_point else "")
    entrada_origen = tk.Entry(frame_entrada, textvariable=origen, bg=app.tema["entry_bg"], fg=app.tema["entry_fg"])
    entrada_origen.pack(side=tk.LEFT, padx=5)

    tk.Label(frame_entrada, text="Destino:", bg=app.tema["bg"], fg=app.tema["fg"]).pack(side=tk.LEFT, padx=5)
    destino = tk.StringVar(value=dest_point.get() if dest_point else "")
    entrada_destino = tk.Entry(frame_entrada, textvariable=destino, bg=app.tema["entry_bg"], fg=app.tema["entry_fg"])
    entrada_destino.pack(side=tk.LEFT, padx=5)

    # Frame para resultados
    frame_resultados = tk.Frame(frame_principal, bg=app.tema["bg"])
    frame_resultados.pack(fill="both", expand=True, pady=10)

    # Área de texto para mostrar resultados
    resultados_text = tk.Text(frame_resultados, height=10, bg=app.tema["text_bg"], fg=app.tema["text_fg"])
    resultados_text.pack(fill="both", expand=True)

    # Frame para botones
    frame_botones = tk.Frame(frame_principal, bg=app.tema["bg"])
    frame_botones.pack(fill="x", pady=10)

    # Frame para botones de acción (búsqueda y exportación)
    frame_acciones = tk.Frame(frame_entrada, bg=app.tema["bg"])
    frame_acciones.pack(side=tk.LEFT, padx=5)

    # Botón de búsqueda
    tk.Button(
        frame_acciones,
        text="Buscar Rutas",
        command=lambda: buscar_rutas(app, origen, destino, resultados_text, frame_botones),
        bg=app.tema["button_bg"],
        fg=app.tema["button_fg"],
        font=("Segoe UI", 10)
    ).pack(side=tk.LEFT, padx=5)


def buscar_rutas(app, origen, destino, path_text, frame_botones):
    """Busca y muestra múltiples rutas entre dos puntos."""
    global espacio_aereo

    try:
        # Limpiar el texto anterior
        path_text.delete(1.0, tk.END)

        # Limpiar botones anteriores
        for widget in frame_botones.winfo_children():
            widget.destroy()

        # Obtener nombres de origen y destino
        origin_name = origen.get().strip()
        dest_name = destino.get().strip()

        if not origin_name or not dest_name:
            messagebox.showwarning("Advertencia", "Por favor ingrese nombres para el origen y destino.")
            return

        # Verificar si el origen es un aeropuerto
        origin_is_airport = origin_name.startswith(("LE", "LF"))
        if origin_is_airport:
            origin_airport = get_navairport_by_name(espacio_aereo, origin_name)
            if not origin_airport:
                path_text.insert(tk.END, f"ERROR: No se encontró ningún aeropuerto con el código '{origin_name}'.\n")
                path_text.insert(tk.END, "Por favor verifique que el código del aeropuerto de origen sea correcto.\n")
                return
            origin = origin_name  # Usamos el código del aeropuerto directamente
        else:
            # Buscar como punto de navegación normal
            origin = get_navpoint_by_name(espacio_aereo, origin_name)
            if not origin:
                path_text.insert(tk.END, f"ERROR: No se encontró ningún punto con el nombre '{origin_name}'.\n")
                path_text.insert(tk.END, "Por favor verifique que el nombre del punto de origen sea correcto.\n")
                return

        # Verificar si el destino es un aeropuerto
        dest_is_airport = dest_name.startswith(("LE", "LF"))
        if dest_is_airport:
            dest_airport = get_navairport_by_name(espacio_aereo, dest_name)
            if not dest_airport:
                path_text.insert(tk.END, f"ERROR: No se encontró ningún aeropuerto con el código '{dest_name}'.\n")
                path_text.insert(tk.END, "Por favor verifique que el código del aeropuerto de destino sea correcto.\n")
                return
            dest = dest_name  # Usamos el código del aeropuerto directamente
        else:
            # Buscar como punto de navegación normal
            dest = get_navpoint_by_name(espacio_aereo, dest_name)
            if not dest:
                path_text.insert(tk.END, f"ERROR: No se encontró ningún punto con el nombre '{dest_name}'.\n")
                path_text.insert(tk.END, "Por favor verifique que el nombre del punto de destino sea correcto.\n")
                return

        # Si son puntos de navegación normales, verificar si tienen segmentos conectados
        if not origin_is_airport and not dest_is_airport:
            origin_has_segments = False
            dest_has_segments = False

            for segment in espacio_aereo.navsegments:
                if segment.origin_number == origin.number or segment.destination_number == origin.number:
                    origin_has_segments = True
                if segment.origin_number == dest.number or segment.destination_number == dest.number:
                    dest_has_segments = True

            if not origin_has_segments:
                path_text.insert(tk.END, f"ERROR: El punto '{origin.name}' no está conectado a ningún segmento.\n")
                path_text.insert(tk.END,
                                 "Este punto está aislado en el grafo de navegación y no puede ser utilizado para ruteo.\n")
                return

            if not dest_has_segments:
                path_text.insert(tk.END, f"ERROR: El punto '{dest.name}' no está conectado a ningún segmento.\n")
                path_text.insert(tk.END,
                                 "Este punto está aislado en el grafo de navegación y no puede ser utilizado para ruteo.\n")
                return

        # Mensaje personalizado según los tipos de origen y destino
        if origin_is_airport and dest_is_airport:
            path_text.insert(tk.END,
                             f"Buscando rutas alternativas del aeropuerto {origin_name} al aeropuerto {dest_name} usando algoritmo A*...\n\n")
        elif origin_is_airport:
            path_text.insert(tk.END,
                             f"Buscando rutas alternativas del aeropuerto {origin_name} al punto {dest_name} usando algoritmo A*...\n\n")
        elif dest_is_airport:
            path_text.insert(tk.END,
                             f"Buscando rutas alternativas del punto {origin_name} al aeropuerto {dest_name} usando algoritmo A*...\n\n")
        else:
            path_text.insert(tk.END,
                             f"Buscando rutas alternativas de {origin_name} a {dest_name} usando algoritmo A*...\n\n")

        # Encontrar múltiples rutas usando A*
        rutas = find_multiple_paths_astar(espacio_aereo, origin, dest)

        if not rutas:
            path_text.insert(tk.END, "No se encontraron rutas entre estos puntos.\n")
            if origin_is_airport or dest_is_airport:
                path_text.insert(tk.END,
                                 "Esto puede deberse a que no existen SIDs o STARs que permitan conectar los aeropuertos,\n")
                path_text.insert(tk.END,
                                 "o a que se encuentran en componentes desconectados del grafo de navegación.\n")
            else:
                path_text.insert(tk.END,
                                 "Esto puede deberse a que se encuentran en componentes desconectados del grafo.\n")
            return

        # Almacenar las rutas para su posterior exportación
        app.rutas_alternativas = []

        # Mostrar cada ruta encontrada
        for i, (distancia, ruta_nums) in enumerate(rutas):
            if not isinstance(ruta_nums, list) or not isinstance(distancia, (int, float)):
                continue

            # Convertir números de puntos a objetos NavPoint
            ruta = []
            for num in ruta_nums:
                navpoint = get_navpoint_by_number(espacio_aereo, num)
                if navpoint:
                    ruta.append(navpoint)

            if len(ruta) != len(ruta_nums):
                continue  # Si algún punto no se encontró, saltamos esta ruta

            # Almacenar la ruta
            app.rutas_alternativas.append((ruta, distancia))

            # Mostrar información de la ruta
            path_text.insert(tk.END, f"\nRuta {i + 1}:\n")
            path_text.insert(tk.END, f"Distancia: {float(distancia):.2f} km\n")
            path_text.insert(tk.END, "Puntos de la ruta:\n")

            for punto in ruta:
                path_text.insert(tk.END, f"- {punto.name} (#{punto.number})\n")

            # Crear botón para ver esta ruta
            btn_frame = tk.Frame(frame_botones, bg=app.tema["bg"])
            btn_frame.pack(side=tk.LEFT, padx=5)

            tk.Button(
                btn_frame,
                text=f"Ver Ruta {i + 1}",
                command=lambda r=ruta: mostrar_espacio_aereo(app, ruta=r),
                bg=app.tema["button_bg"],
                fg=app.tema["button_fg"],
                font=("Segoe UI", 10)
            ).pack(side=tk.LEFT, padx=2)

            # Botón para exportar esta ruta específica
            tk.Button(
                btn_frame,
                text=f"Exportar Ruta {i + 1}",
                command=lambda r=ruta: exportar_ruta_a_google_earth_helper(app, r),
                bg=app.tema["button_bg"],
                fg=app.tema["button_fg"],
                font=("Segoe UI", 10)
            ).pack(side=tk.LEFT, padx=2)

    except Exception as e:
        messagebox.showerror("Error", f"Error al buscar rutas: {str(e)}")


def calcular_distancia_ruta(ruta):
    distancia_total = 0
    for i in range(len(ruta) - 1):
        distancia_total += calcular_distancia_entre_puntos(ruta[i], ruta[i + 1])
    return distancia_total

def exportar_ruta_a_google_earth(app, origin_point, dest_point):
    global espacio_aereo

    if not espacio_aereo:
        messagebox.showwarning("Advertencia", "No hay datos de espacio aéreo cargados.")
        return

    origin_name = origin_point.get().strip()
    dest_name = dest_point.get().strip()

    if not origin_name or not dest_name:
        messagebox.showwarning("Advertencia", "Por favor ingrese ambos puntos de origen y destino.")
        return

    origin = get_navpoint_by_name(espacio_aereo, origin_name)
    destination = get_navpoint_by_name(espacio_aereo, dest_name)

    if not origin:
        messagebox.showwarning("Advertencia", f"Punto de origen '{origin_name}' no encontrado.")
        return

    if not destination:
        messagebox.showwarning("Advertencia", f"Punto de destino '{dest_name}' no encontrado.")
        return

    # Usar el algoritmo A* para encontrar la ruta
    path_points, total_distance = find_shortest_path_astar(espacio_aereo, origin, dest)

    if not path_points:
        messagebox.showwarning("Advertencia", "No se encontró ninguna ruta entre estos puntos.")
        return

    # Mostrar la ruta en el mapa
    mostrar_espacio_aereo(app, ruta=path_points)

    # Guardar la ruta para exportación posterior
    app.last_path_data = (path_points, total_distance)

    # Exportar ruta a Google Earth
    exportar_ruta_a_google_earth_helper(app, path_points)


def exportar_ruta_a_google_earth_helper(app, ruta):
    """Función auxiliar para exportar ruta a Google Earth"""
    if not ruta or len(ruta) < 2:
        messagebox.showwarning("Advertencia", "No hay una ruta válida para exportar.")
        return

    # Importar el módulo kml_generator.py
    import kml_generator

    # Crear contenido KML para la ruta
    path_name = f"Ruta de {ruta[0].name} a {ruta[-1].name}"
    kml_content = kml_generator.generate_path_kml(path_name, ruta)

    # Solicitar ubicación para guardar
    filename = filedialog.asksaveasfilename(
        defaultextension=".kml",
        filetypes=[("KML files", "*.kml"), ("All files", "*.*")],
        title="Guardar Ruta como KML"
    )

    if filename:
        # Asegurarse de que el archivo tenga extensión .kml
        if not filename.lower().endswith('.kml'):
            filename += '.kml'

        try:
            # Guardar el archivo utilizando kml_generator
            if kml_generator.save_kml_to_file(kml_content, filename):
                messagebox.showinfo("Éxito", f"Ruta exportada a {filename}")

                # Preguntar si quiere abrir en Google Earth
                if messagebox.askyesno("Abrir en Google Earth", "¿Desea abrir el archivo en Google Earth?"):
                    try:
                        os.startfile(filename)
                    except:
                        messagebox.showwarning("Error",
                                               "No se pudo abrir Google Earth automáticamente. Por favor, abra el archivo manualmente.")
            else:
                messagebox.showerror("Error", f"No se pudo guardar el archivo.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(e)}")

def exportar_a_google_earth(app, ruta=None, punto_destacado=None, vecinos=None):
    """Exporta el espacio aéreo a un archivo KML para visualización en Google Earth."""
    global espacio_aereo

    if not espacio_aereo or not espacio_aereo.navpoints:
        messagebox.showwarning("Advertencia", "No hay datos de espacio aéreo para exportar.")
        return

    try:
        # Importar el módulo kml_generator.py
        import kml_generator

        # Utilizar el módulo kml_generator para generar el contenido KML
        kml_content = kml_generator.generate_airspace_kml(espacio_aereo)

        # Solicitar ubicación para guardar
        filename = filedialog.asksaveasfilename(
            defaultextension=".kml",
            filetypes=[("Archivos KML", "*.kml"), ("Todos los archivos", "*.*")],
            title="Guardar espacio aéreo como KML"
        )

        if not filename:
            return  # Usuario canceló el diálogo

        # Asegurarse de que el archivo tenga extensión .kml
        if not filename.lower().endswith('.kml'):
            filename += '.kml'

        # Guardar el archivo utilizando kml_generator
        if kml_generator.save_kml_to_file(kml_content, filename):
            messagebox.showinfo("Éxito", f"Espacio aéreo exportado a {filename}")

            # Preguntar si quiere abrir en Google Earth
            if messagebox.askyesno("Abrir en Google Earth", "¿Desea abrir el archivo en Google Earth?"):
                try:
                    os.startfile(filename)
                except Exception as e:
                    messagebox.showwarning("Error", f"No se pudo abrir Google Earth automáticamente: {str(e)}\nPor favor, abra el archivo manualmente.")
        else:
            messagebox.showerror("Error", f"No se pudo guardar el archivo.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al exportar a Google Earth: {str(e)}")


def encontrar_alcanzabilidad(airspace, start_number):
    """
    Encuentra todos los nodos alcanzables desde un nodo de origen.
    Solo considera segmentos en la dirección correcta (origen->destino).
    """
    if start_number not in airspace.navpoints:
        return []

    # Conjunto para almacenar nodos alcanzables
    alcanzables = set()
    # Cola para BFS (Breadth-First Search)
    cola = [start_number]
    # Conjunto para nodos visitados
    visitados = set([start_number])

    while cola:
        nodo_actual = cola.pop(0)
        alcanzables.add(nodo_actual)

        # Encontrar vecinos directos (solo en dirección correcta)
        for segmento in airspace.navsegments:
            if segmento.origin_number == nodo_actual:
                destino = segmento.destination_number
                if destino not in visitados:
                    visitados.add(destino)
                    cola.append(destino)

    # Eliminar el nodo de origen de la lista de alcanzables
    if start_number in alcanzables:
        alcanzables.remove(start_number)

    return sorted(list(alcanzables))

def encontrar_nodo_por_texto(airspace, texto):
    # Intentar convertir a número
    try:
        numero = int(texto)
        # Si es un número, verificar si existe
        if numero in airspace.navpoints:
            return numero
    except ValueError:
        pass

    # Buscar por nombre (texto exacto)
    for num, punto in airspace.navpoints.items():
        if punto.name.upper() == texto.upper():
            return num

    # No se encontró el nodo
    return None

def mostrar_alcanzabilidad(app):
    """Abre una ventana para encontrar la alcanzabilidad de un nodo (todos los nodos alcanzables desde él)."""
    global espacio_aereo

    if not espacio_aereo or not espacio_aereo.navpoints:
        messagebox.showwarning("Advertencia", "No hay datos de espacio aéreo cargados.")
        return

    alcance_window = tk.Toplevel(app)
    alcance_window.title("Encontrar Alcanzabilidad de un Nodo")
    alcance_window.geometry("450x500")
    alcance_window.configure(bg=app.tema["bg"])

    # Frame para la selección de nodo
    select_frame = tk.Frame(alcance_window, bg=app.tema["bg"])
    select_frame.pack(fill="x", padx=20, pady=10)

    # Label e input para el nodo de origen
    tk.Label(select_frame, text="Nodo de origen:",
             bg=app.tema["bg"], fg=app.tema["fg"],
             font=(app.tema["font_family"], app.tema["font_size_normal"])).grid(row=0, column=0, padx=5, pady=5,
                                                                                sticky="w")

    # Entrada de texto para el nodo de origen
    tk.Label(select_frame, text="Número o nombre del nodo:",
             bg=app.tema["bg"], fg=app.tema["fg"],
             font=(app.tema["font_family"], app.tema["font_size_normal"])).grid(row=0, column=0, padx=5, pady=5,
                                                                                sticky="w")

    # Campo de entrada para escribir el nodo
    origin_entry = tk.Entry(select_frame, width=30,
                            bg=app.tema["entry_bg"], fg=app.tema["entry_fg"],
                            font=(app.tema["font_family"], app.tema["font_size_normal"]))
    origin_entry.grid(row=0, column=1, padx=5, pady=5)
    origin_entry.focus_set()  # Poner el foco aquí para que el usuario empiece a escribir

    # Texto de ayuda debajo del campo
    ayuda_label = tk.Label(select_frame,
                           text="Introduce el número de nodo o su nombre exacto (ej: 'LEIB' o '123')",
                           bg=app.tema["bg"], fg=app.tema["fg"],
                           font=(app.tema["font_family"], app.tema["font_size_normal"] - 1))
    ayuda_label.grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky="w")

    # Frame para los resultados
    results_frame = tk.Frame(alcance_window, bg=app.tema["bg"])
    results_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Área de texto para mostrar los resultados
    alcance_text = tk.Text(results_frame, wrap=tk.WORD, width=50, height=20,
                           bg=app.tema["text_bg"], fg=app.tema["text_fg"],
                           font=(app.tema["font_family"], app.tema["font_size_normal"]))
    alcance_text.pack(fill="both", expand=True, side=tk.LEFT)

    # Scrollbar para el área de texto
    scrollbar = tk.Scrollbar(results_frame, command=alcance_text.yview)
    scrollbar.pack(fill="y", side=tk.RIGHT)
    alcance_text.config(yscrollcommand=scrollbar.set)

    # Frame para botones
    button_frame = tk.Frame(alcance_window, bg=app.tema["bg"])
    button_frame.pack(fill="x", padx=20, pady=10)

    # Botón para buscar la alcanzabilidad
    buscar_button = tk.Button(
        button_frame,
        text="Buscar Alcanzabilidad",
        command=lambda: encontrar_y_mostrar_alcanzabilidad(app, alcance_text, origin_entry.get()),
        bg=app.tema["button_bg"],
        fg=app.tema["button_fg"],
        font=(app.tema["font_family"], app.tema["font_size_normal"]),
        padx=app.tema["button_padx"],
        pady=app.tema["button_pady"],
        relief=app.tema["relief"],
        borderwidth=app.tema["borderwidth"],
        cursor="hand2"
    )
    buscar_button.pack(side=tk.LEFT, padx=5)

    # Botón para visualizar en el mapa
    visualizar_button = tk.Button(
        button_frame,
        text="Visualizar en Mapa",
        command=lambda: visualizar_alcanzabilidad(app, origin_entry.get()),
        bg=app.tema["button_bg"],
        fg=app.tema["button_fg"],
        font=(app.tema["font_family"], app.tema["font_size_normal"]),
        padx=app.tema["button_padx"],
        pady=app.tema["button_pady"],
        relief=app.tema["relief"],
        borderwidth=app.tema["borderwidth"],
        cursor="hand2"
    )
    visualizar_button.pack(side=tk.LEFT, padx=5)


def encontrar_y_mostrar_alcanzabilidad(app, alcance_text, origen_texto):
    """
    Encuentra y muestra la alcanzabilidad de un nodo seleccionado.
    """
    global espacio_aereo

    try:
        # Limpiar el área de texto
        alcance_text.delete(1.0, tk.END)

        # Imprimir información de depuración
        alcance_text.insert(tk.END, f"Buscando nodo: '{origen_texto}'\n\n")

        # Buscar el nodo por texto
        origen_numero = encontrar_nodo_por_texto(espacio_aereo, origen_texto)

        if origen_numero is None:
            alcance_text.insert(tk.END, f"Error: No se encontró ningún nodo con el texto '{origen_texto}'\n")
            return

        # Obtener el punto de origen
        origen_punto = espacio_aereo.navpoints.get(origen_numero)

        # Encontrar nodos alcanzables
        nodos_alcanzables = encontrar_alcanzabilidad(espacio_aereo, origen_numero)

        # Mostrar resultados
        alcance_text.insert(tk.END, f"Análisis de Alcanzabilidad\n")
        alcance_text.insert(tk.END, f"======================\n\n")
        alcance_text.insert(tk.END, f"Nodo de origen: {origen_punto.name} (#{origen_numero})\n")
        alcance_text.insert(tk.END,
                            f"Coordenadas: Lat {origen_punto.latitude:.6f}, Lon {origen_punto.longitude:.6f}\n\n")

        if not nodos_alcanzables:
            alcance_text.insert(tk.END, "No hay nodos alcanzables desde este punto.\n")
            return

        alcance_text.insert(tk.END, f"Nodos alcanzables: {len(nodos_alcanzables)}\n\n")

        # Mostrar lista de nodos alcanzables
        alcance_text.insert(tk.END, "Lista de nodos alcanzables:\n")

        for i, num in enumerate(nodos_alcanzables, 1):
            punto = espacio_aereo.navpoints.get(num)
            if punto:
                distancia = calcular_distancia_entre_puntos(origen_punto, punto)
                alcance_text.insert(tk.END, f"{i}. {punto.name} (#{num}) - Distancia: {distancia:.2f} km\n")

    except Exception as e:
        # Capturar y mostrar cualquier error
        alcance_text.insert(tk.END, f"Error inesperado: {str(e)}\n")
        import traceback
        alcance_text.insert(tk.END, traceback.format_exc())

def visualizar_alcanzabilidad(app, origen_texto):
    global espacio_aereo

    # Buscar el nodo por texto
    origen_numero = encontrar_nodo_por_texto(espacio_aereo, origen_texto)

    if origen_numero is None:
        messagebox.showerror("Error", f"No se encontró ningún nodo con el texto '{origen_texto}'")
        return

    # Encontrar nodos alcanzables
    nodos_alcanzables = encontrar_alcanzabilidad(espacio_aereo, origen_numero)

    # Mostrar en el mapa
    mostrar_espacio_aereo(app, punto_destacado=origen_numero, alcanzables=nodos_alcanzables)

def reproducir_musica_directa(app=None):
    """Inicia la reproducción de música directamente, sin comprobar estado previo."""
    global reproductor_musica

    try:
        # Inicializar el reproductor si no existe
        if reproductor_musica is None:
            reproductor_musica = inicializar_reproductor_musica()
            if reproductor_musica is None:
                if app:
                    app.status.config(text="Error: No se pudo inicializar el reproductor de música")
                messagebox.showerror("Error", "No se pudo inicializar el reproductor de música")
                return

        # Intentar reproducir música (forzar detener primero para reiniciar)
        music_generator.detener()
        exito = music_generator.reproducir_cancion_de_carpeta()

        if not exito:
            # Si no hay archivos, intentar con sonido generado
            music_generator.crear_sonido()
            exito = music_generator.reproducir()

        # Actualizar interfaz basado en el resultado
        if app:
            if exito:
                app.status.config(text="Reproduciendo música")
                app.music_button.config(text="Detener Música", bg="#E53935",
                                       command=lambda: detener_musica(app))
            else:
                app.status.config(text="Error: No se pudo reproducir música")

    except Exception as e:
        mensaje = f"Error al reproducir música: {str(e)}"
        if app:
            app.status.config(text=mensaje)
        print(mensaje)

def detener_musica(app=None):
    """Detiene la reproducción de música."""
    global reproductor_musica

    try:
        music_generator.detener()

        # Actualizar interfaz
        if app:
            app.status.config(text="Música detenida")
            app.music_button.config(text="Reproducir Música", bg="#1E88E5",
                                   command=lambda: reproducir_musica_directa(app))

    except Exception as e:
        mensaje = f"Error al detener música: {str(e)}"
        if app:
            app.status.config(text=mensaje)
        print(mensaje)

def inicializar_reproductor_musica():
    """Inicializa el reproductor de música y carga un archivo de música."""
    global reproductor_musica

    # Inicializar el reproductor si no existe
    if reproductor_musica is None:
        # Asegurarse que existe la carpeta de música
        music_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "music")
        if not os.path.exists(music_folder):
            try:
                os.makedirs(music_folder)
                print(f"Carpeta de música creada: {music_folder}")
            except Exception as e:
                print(f"Error al crear carpeta de música: {str(e)}")

        # Inicializar componentes de pygame
        music_generator.inicializar_reproductor()

        # Crear la instancia del reproductor
        reproductor_musica = MusicPlayer()

        # Intentar cargar una canción de la carpeta
        files_exist = music_generator.reproducir_cancion_de_carpeta()

        # Si no se encontraron archivos, detener inmediatamente para que comience detenido
        if not files_exist:
            music_generator.detener()

    return reproductor_musica

def toggle_musica(app=None):
    """Alterna entre reproducir y detener la música."""
    global reproductor_musica

    try:
        # Inicializar el reproductor si no existe
        if reproductor_musica is None:
            reproductor_musica = inicializar_reproductor_musica()
            if reproductor_musica is None:
                if app:
                    app.status.config(text="Error: No se pudo inicializar el reproductor de música")
                messagebox.showerror("Error", "No se pudo inicializar el reproductor de música")
                return

        # Comprobar el texto del botón para determinar qué acción realizar
        reproducir = True  # Por defecto, intentamos reproducir música

        if hasattr(app, 'music_button'):
            boton_texto = app.music_button.cget("text")
            # Si el botón dice "Detener Música", entonces detenemos
            if boton_texto == "Detener Música":
                reproducir = False

        # Ejecutar la acción correspondiente
        if reproducir:
            # Reproducir música
            exito = music_generator.reproducir_cancion_de_carpeta()

            if exito:
                # Actualizar la interfaz
                if app:
                    app.status.config(text="Reproduciendo música")
                    if hasattr(app, 'music_button'):
                        app.music_button.config(text="Detener Música", bg="#E53935")
                print("Reproduciendo música")
            else:
                # Intentar con sonido generado como respaldo
                music_generator.crear_sonido()
                exito = music_generator.reproducir()

                if exito:
                    if app:
                        app.status.config(text="Reproduciendo música generada")
                        if hasattr(app, 'music_button'):
                            app.music_button.config(text="Detener Música", bg="#E53935")
                    print("Reproduciendo música generada")
                else:
                    if app:
                        app.status.config(text="Error: No se pudo reproducir música")
                    print("Error: No se pudo reproducir música")
        else:
            # Detener música
            music_generator.detener()

            # Actualizar la interfaz
            if app:
                app.status.config(text="Música detenida")
                if hasattr(app, 'music_button'):
                    app.music_button.config(text="Reproducir Música", bg="#1E88E5")
            print("Música detenida")

    except Exception as e:
        mensaje = f"Error al controlar la música: {str(e)}"
        if app:
            app.status.config(text=mensaje)
        print(mensaje)

def toggle_tema(app):
    try:
        # Cambiar el tema actual
        app.tema_oscuro = not app.tema_oscuro
        tema = DARK_THEME if app.tema_oscuro else LIGHT_THEME

        # Actualizar el tema de la aplicación
        app.tema = tema
        app.configure(bg=tema["bg"])

        # Actualizar todos los widgets recursivamente
        update_widget_theme(app.main_frame, tema)

        # Actualizar el botón de tema
        if app.tema_oscuro:
            app.theme_button.config(text="☀️ Modo Claro", bg=tema["button_bg"], fg=tema["button_fg"])
        else:
            app.theme_button.config(text="🌙 Modo Oscuro", bg=tema["button_bg"], fg=tema["button_fg"])

        # Actualizar el botón de música si existe
        if hasattr(app, 'music_button'):
            from music_generator import playing
            if playing:
                app.music_button.config(text="Detener Música", bg="#E53935", fg="white")
            else:
                app.music_button.config(text="Reproducir Música", bg=tema["button_bg"], fg=tema["button_fg"])

        # Actualizar las instrucciones
        if hasattr(app, 'instructions'):
            app.instructions.config(bg=tema["bg"], fg=tema["fg"])

        # Mostrar mensaje de estado
        if app.tema_oscuro:
            app.status.config(text="Tema oscuro activado")
        else:
            app.status.config(text="Tema claro activado")

    except Exception as e:
        print(f"Error al cambiar el tema: {str(e)}")
        if hasattr(app, 'status'):
            app.status.config(text=f"Error al cambiar el tema: {str(e)}")

def update_widget_theme(widget, tema):
    try:
        if isinstance(widget, tk.Button):
            if widget.cget("text") == "Detener Música":
                # No cambiar el botón de detener música
                pass
            else:
                widget.config(bg=tema["button_bg"], fg=tema["button_fg"])
        elif isinstance(widget, tk.Label):
            widget.config(bg=tema["bg"], fg=tema["fg"])
        elif isinstance(widget, tk.Entry) or isinstance(widget, tk.Text):
            widget.config(bg=tema["text_bg"], fg=tema["text_fg"], insertbackground=tema["fg"])
        elif isinstance(widget, tk.Frame):
            widget.config(bg=tema["bg"])
            # Actualizar widgets dentro de frames
            for child in widget.winfo_children():
                update_widget_theme(child, tema)
        elif isinstance(widget, ttk.Frame) or isinstance(widget, ttk.LabelFrame):
            # No podemos cambiar directamente el fondo de widgets ttk
            # pero podemos actualizar sus hijos
            for child in widget.winfo_children():
                update_widget_theme(child, tema)
        elif isinstance(widget, ttk.Button):
            # No podemos cambiar directamente el color de los botones ttk
            pass
        elif isinstance(widget, ttk.Label):
            # Intentar actualizar el estilo del label ttk
            style_name = widget.cget("style") or "TLabel"
            widget.configure(style=style_name)
    except Exception as e:
        print(f"Error al actualizar widget {widget}: {str(e)}")

def mostrar_info_equipo(app):
    info_window = tk.Toplevel(app)
    info_window.title("Información del Equipo")
    info_window.geometry("600x500")
    info_window.configure(bg=app.tema["bg"])

    # Marco principal
    main_frame = tk.Frame(info_window, bg=app.tema["bg"])
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Título
    title_label = tk.Label(
        main_frame,
        text="Equipo de Desarrollo",
        font=(app.tema["font_family"], app.tema["font_size_header"], "bold"),
        bg=app.tema["bg"],
        fg=app.tema["fg"]
    )
    title_label.pack(pady=(0, 20))

    # Información del equipo
    info_text = "Este proyecto ha sido desarrollado por:\n\n"
    info_text += "• Saoussane Ziati\n"
    info_text += "• Iu Serret\n"
    info_text += "• Alex Millán"

    info_label = tk.Label(
        main_frame,
        text=info_text,
        font=(app.tema["font_family"], app.tema["font_size_normal"]),
        justify=tk.LEFT,
        bg=app.tema["bg"],
        fg=app.tema["fg"]
    )
    info_label.pack(pady=(0, 20), anchor=tk.W)

    # Intenta cargar y mostrar la imagen del equipo
    try:
        img = Image.open("grupo_trabajo.jpg")

        # Aplicar efecto de desenfoque
        img = img.filter(ImageFilter.BLUR)

        # Redimensionar la imagen manteniendo la proporción
        basewidth = 400
        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), Image.LANCZOS)

        photo = ImageTk.PhotoImage(img)

        # Crear un panel para la imagen
        img_panel = tk.Label(main_frame, image=photo, bg=app.tema["bg"])
        img_panel.image = photo  # Mantener una referencia para evitar que se elimine
        img_panel.pack(pady=10)
    except Exception as e:
        error_label = tk.Label(
            main_frame,
            text=f"No se pudo cargar la imagen: {str(e)}",
            font=("Segoe UI", 10),
            fg="red",
            bg=app.tema["bg"]
        )
        error_label.pack(pady=10)

def debug_airport_info(app, path_text):
    """Muestra información de depuración sobre aeropuertos."""
    path_text.delete(1.0, tk.END)

    # Mostrar todos los aeropuertos en el espacio aéreo
    path_text.insert(tk.END, "INFORMACIÓN DE AEROPUERTOS:\n\n")

    if not espacio_aereo.navairports:
        path_text.insert(tk.END, "No hay aeropuertos cargados en el espacio aéreo.\n")
        return

    path_text.insert(tk.END, f"Total de aeropuertos cargados: {len(espacio_aereo.navairports)}\n\n")

    for code, airport in espacio_aereo.navairports.items():
        path_text.insert(tk.END, f"Aeropuerto: {code}\n")

        # Mostrar SIDs
        if airport.sids:
            path_text.insert(tk.END, f"  SIDs ({len(airport.sids)}):\n")
            for sid in airport.sids:
                sid_point = espacio_aereo.navpoints.get(sid)
                if sid_point:
                    path_text.insert(tk.END, f"    - #{sid} ({sid_point.name})\n")
                else:
                    path_text.insert(tk.END, f"    - #{sid} (punto no encontrado)\n")
        else:
            path_text.insert(tk.END, "  No tiene SIDs definidos\n")

        # Mostrar STARs
        if airport.stars:
            path_text.insert(tk.END, f"  STARs ({len(airport.stars)}):\n")
            for star in airport.stars:
                star_point = espacio_aereo.navpoints.get(star)
                if star_point:
                    path_text.insert(tk.END, f"    - #{star} ({star_point.name})\n")
                else:
                    path_text.insert(tk.END, f"    - #{star} (punto no encontrado)\n")
        else:
            path_text.insert(tk.END, "  No tiene STARs definidos\n")

        path_text.insert(tk.END, "\n")

def menu_file(app):
    """Crea el menú Archivo."""
    file_menu = tk.Menu(app.menu, tearoff=0)
    file_menu.add_command(label="Cargar datos", command=lambda: cargar_datos(app))
    file_menu.add_command(label="Guardar Ruta", command=lambda: guardar_ruta(app))
    file_menu.add_command(label="Exportar a Google Earth", command=lambda: exportar_a_google_earth(app))
    file_menu.add_separator()
    file_menu.add_command(label="Información de Aeropuertos", command=lambda: debug_airport_info(app, app.path_text))
    file_menu.add_separator()
    file_menu.add_command(label="Salir", command=app.quit)
    app.menu.add_cascade(label="Archivo", menu=file_menu)

class AplicacionNavegacionEspacioAereo(tk.Tk):
    def __init__(self):
        super().__init__()

        # Detectar sistema operativo
        self.sistema_operativo = platform.system()

        # Configuración general de la ventana
        self.title("FlyPath")
        self.geometry("800x700")  # Tamaño inicial más grande

        # Inicializar tema
        self.tema_oscuro = False
        self.tema = LIGHT_THEME
        self.configure(bg=self.tema["bg"])

        # Configurar estilos
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Usar un tema base que permita personalización
        self.style.configure("TLabel", background=self.tema["bg"], foreground=self.tema["fg"])
        self.style.configure("TButton", background=self.tema["button_bg"], foreground=self.tema["button_fg"])

        # Configurar estilo para LabelFrame sin borde y con fondo igual al fondo principal
        self.style.configure("TLabelFrame", background=self.tema["bg"], foreground=self.tema["fg"])
        self.style.configure("TLabelFrame.Label", background=self.tema["bg"], foreground=self.tema["fg"],
                            font=(self.tema["font_family"], 11, "bold"))

        # Quitar el borde del LabelFrame
        self.style.layout("TLabelFrame", [
            ("LabelFrame.border", {
                "sticky": "nswe",
                "children": [
                    ("LabelFrame.padding", {
                        "sticky": "nswe",
                        "children": [
                            ("LabelFrame.label", {"side": "top", "sticky": ""}),
                            ("LabelFrame.children", {"sticky": "nswe"})
                        ]
                    })
                ]
            })
        ])

        self.style.configure("Instructions.TLabel", font=(self.tema["font_family"], self.tema["font_size_normal"]),
                             background=self.tema["bg"], foreground=self.tema["fg"])

        try:
            # Intentar establecer un icono para la ventana
            self.iconbitmap("icon.ico")
        except:
            # Si no se encuentra el icono, continuar sin él
            pass

        # Enable high DPI awareness for sharper rendering on Windows
        try:
            from ctypes import windll
            if self.sistema_operativo == 'Windows':
                windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

        self.main_frame = tk.Frame(self, bg=self.tema["bg"])
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Crear un encabezado moderno
        header_frame = tk.Frame(self.main_frame, bg="#2c3e50", height=60)
        header_frame.pack(fill="x", pady=(0, 20))
        header_label = tk.Label(header_frame, text="FlyPath: Sistema de Navegación Aérea",
                              font=(self.tema["font_family"], self.tema["font_size_header"], "bold"), fg="white", bg="#2c3e50")
        header_label.pack(pady=15)

        # Usar widgets con tema para mejor apariencia
        style = ttk.Style()
        style.configure("TButton", padding=10)
        style.configure("TLabelFrame", background=self.tema["bg"])
        style.configure("TLabel", background=self.tema["bg"])

        # Sección para Datos de Prueba
        test_data_frame = tk.Frame(self.main_frame, bg=self.tema["bg"], highlightthickness=0)
        test_data_frame.pack(fill="x", pady=10)

        test_data_label = tk.Label(test_data_frame, text="Datos de Prueba",
                                   font=(self.tema["font_family"], self.tema["font_size_title"], "bold"),
                                   bg=self.tema["bg"], fg=self.tema["fg"])
        test_data_label.pack(anchor="w", pady=(0, 10))

        test_data_buttons_frame = tk.Frame(test_data_frame, bg=self.tema["bg"])
        test_data_buttons_frame.pack(fill="x", pady=5)

        # Botón para cargar datos de prueba
        load_test_button = tk.Button(
            test_data_buttons_frame,
            text="Cargar Gráfico de Prueba",
            command=self.cargar_datos_test,  # Actualizado para llamar al método correcto
            bg=self.tema["button_bg"],
            fg=self.tema["button_fg"],
            font=(self.tema["font_family"], self.tema["font_size_normal"]),
            padx=self.tema["button_padx"],
            pady=self.tema["button_pady"],
            relief=self.tema["relief"],
            borderwidth=self.tema["borderwidth"]
        )
        load_test_button.pack(side=tk.LEFT, padx=5)

        load_frame = tk.Frame(self.main_frame, bg=self.tema["bg"], highlightthickness=0)
        load_frame.pack(fill="x", pady=10)

        load_label = tk.Label(load_frame, text="Cargar, Crear y Visualizar Datos",
                              font=(self.tema["font_family"], self.tema["font_size_title"], "bold"), bg=self.tema["bg"], fg=self.tema["fg"])
        load_label.pack(anchor="w", pady=(0, 10))

        buttons_frame = tk.Frame(load_frame, bg=self.tema["bg"])
        buttons_frame.pack(fill="x", pady=5)

        # Botón para cargar archivos
        load_button = tk.Button(
            buttons_frame,
            text="Cargar Espacio Aéreo",
            command=lambda: cargar_espacio_aereo(self),
            bg=self.tema["button_bg"],
            fg=self.tema["button_fg"],
            font=(self.tema["font_family"], self.tema["font_size_normal"]),
            padx=self.tema["button_padx"],
            pady=self.tema["button_pady"],
            relief=self.tema["relief"],
            borderwidth=self.tema["borderwidth"],
            cursor="hand2"  # Cambia el cursor al pasar sobre el botón
        )
        load_button.pack(side=tk.LEFT, padx=5)

        # Botón para crear un espacio aéreo vacío
        crear_vacio_button = tk.Button(
            buttons_frame,
            text="Crear Espacio Aéreo Desde Cero",
            command=lambda: crear_espacio_aereo_vacio(self),
            bg=self.tema["button_bg"],
            fg=self.tema["button_fg"],
            font=(self.tema["font_family"], self.tema["font_size_normal"]),
            padx=self.tema["button_padx"],
            pady=self.tema["button_pady"],
            relief=self.tema["relief"],
            borderwidth=self.tema["borderwidth"],
            cursor="hand2"  # Cambia el cursor al pasar sobre el botón
        )
        crear_vacio_button.pack(side=tk.LEFT, padx=5)

        # Botón para visualizar el mapa
        visualize_button = tk.Button(
            buttons_frame,
            text="Visualizar Espacio Aéreo Actual",
            command=lambda: mostrar_espacio_aereo(self),
            bg=self.tema["button_bg"],
            fg=self.tema["button_fg"],
            font=(self.tema["font_family"], self.tema["font_size_normal"]),
            padx=self.tema["button_padx"],
            pady=self.tema["button_pady"],
            relief=self.tema["relief"],
            borderwidth=self.tema["borderwidth"],
            cursor="hand2"  # Cambia el cursor al pasar sobre el botón
        )
        visualize_button.pack(side=tk.LEFT, padx=5)


        # Configure style for accent buttons
        style.configure("Accent.TButton", font=("Helvetica", 11, "bold"))

        analysis_frame = tk.Frame(self.main_frame, bg=self.tema["bg"], highlightthickness=0)
        analysis_frame.pack(fill="x", pady=10)

        analysis_label = tk.Label(analysis_frame, text="Herramientas de Análisis",
                              font=(self.tema["font_family"], self.tema["font_size_title"], "bold"), bg=self.tema["bg"], fg=self.tema["fg"])
        analysis_label.pack(anchor="w", pady=(0, 10))

        analysis_buttons_frame = tk.Frame(analysis_frame, bg=self.tema["bg"])
        analysis_buttons_frame.pack(fill="x", pady=5)

        # Botón para encontrar vecinos
        neighbors_button = tk.Button(
            analysis_buttons_frame,
            text="Encontrar Vecinos",
            command=lambda: mostrar_vecinos(self),
            bg=self.tema["button_bg"],
            fg=self.tema["button_fg"],
            font=(self.tema["font_family"], self.tema["font_size_normal"]),
            padx=self.tema["button_padx"],
            pady=self.tema["button_pady"],
            relief=self.tema["relief"],
            borderwidth=self.tema["borderwidth"],
            cursor="hand2"  # Cambia el cursor al pasar sobre el botón
        )
        neighbors_button.pack(side=tk.LEFT, padx=5)

        # Botón para encontrar ruta óptima
        path_button = tk.Button(
            analysis_buttons_frame,
            text="Encontrar Ruta",
            command=lambda: encontrar_ruta(self),
            bg=self.tema["button_bg"],
            fg=self.tema["button_fg"],
            font=(self.tema["font_family"], self.tema["font_size_normal"]),
            padx=self.tema["button_padx"],
            pady=self.tema["button_pady"],
            relief=self.tema["relief"],
            borderwidth=self.tema["borderwidth"],
            cursor="hand2"  # Cambia el cursor al pasar sobre el botón
        )
        path_button.pack(side=tk.LEFT, padx=5)

        # Botón para encontrar alcanzabilidad
        alcanzabilidad_button = tk.Button(
            analysis_buttons_frame,  # ¡Cambiar tools_frame por analysis_buttons_frame!
            text="Encontrar Alcanzabilidad de un Nodo",
            command=lambda: mostrar_alcanzabilidad(self),
            bg=self.tema["button_bg"],
            fg=self.tema["button_fg"],
            font=(self.tema["font_family"], self.tema["font_size_normal"]),
            padx=self.tema["button_padx"],
            pady=self.tema["button_pady"],
            relief=self.tema["relief"],
            borderwidth=self.tema["borderwidth"],
            cursor="hand2"
        )
        alcanzabilidad_button.pack(side=tk.LEFT, padx=5)  # Usar side=tk.LEFT como los otros botones

        # Add export frame for KML functionality
        export_frame = tk.Frame(self.main_frame, bg=self.tema["bg"])
        export_frame.pack(fill="x", pady=10)

        export_label = tk.Label(export_frame, text="Exportar a Google Earth",
                              font=(self.tema["font_family"], self.tema["font_size_title"], "bold"), bg=self.tema["bg"], fg=self.tema["fg"])
        export_label.pack(anchor="w", pady=(0, 10))

        export_buttons_frame = tk.Frame(export_frame, bg=self.tema["bg"])
        export_buttons_frame.pack(fill="x", pady=5)

        # Botón para exportar a Google Earth
        export_kml_button = tk.Button(
            export_buttons_frame,
            text="Exportar Espacio Aéreo a Google Earth",
            command=lambda: exportar_a_google_earth(self),
            bg=self.tema["button_bg"],
            fg=self.tema["button_fg"],
            font=(self.tema["font_family"], self.tema["font_size_normal"]),
            padx=self.tema["button_padx"],
            pady=self.tema["button_pady"],
            relief=self.tema["relief"],
            borderwidth=self.tema["borderwidth"],
            cursor="hand2"  # Cambia el cursor al pasar sobre el botón
        )
        export_kml_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Etiqueta moderna de instrucciones
        self.instructions = tk.Label(
            self.main_frame,
            text="Instrucciones: Cargue los datos del espacio aéreo y elija una opción.",
            wraplength=600,
            justify="center",
            font=(self.tema["font_family"], self.tema["font_size_normal"]),
            bg=self.tema["bg"],
            fg=self.tema["fg"],
            pady=10
        )
        self.instructions.pack(pady=15, fill="x")

        # Botón de música directamente en el main_frame (no en un frame separado)
        self.music_button = tk.Button(
            self.main_frame,
            text="Reproducir Música",
            command=lambda: reproducir_musica_directa(self),
            bg="#1E88E5",  # Azul más suave
            fg="white",
            font=(self.tema["font_family"], self.tema["font_size_normal"]),
            padx=self.tema["button_padx"],
            pady=self.tema["button_pady"]
        )
        self.music_button.pack(side=tk.LEFT, anchor=tk.SW, padx=20, pady=10)

        # Botón para cambiar el tema (en la esquina inferior derecha)
        self.theme_button = tk.Button(
            self.main_frame,
            text="🌙 Modo Oscuro",
            command=lambda: toggle_tema(self),
            bg=self.tema["button_bg"],
            fg=self.tema["button_fg"],
            font=(self.tema["font_family"], self.tema["font_size_normal"]),
            padx=self.tema["button_padx"],
            pady=self.tema["button_pady"],
            relief=self.tema["relief"],
            borderwidth=self.tema["borderwidth"],
            cursor="hand2"  # Cambia el cursor al pasar sobre el botón
        )
        self.theme_button.pack(side=tk.RIGHT, padx=20, pady=10)

        # Botón para mostrar información del equipo
        self.info_button = tk.Button(
            self.main_frame,
            text="ℹ️ Info Equipo",
            command=lambda: mostrar_info_equipo(self),
            bg="#3498db",  # Azul claro
            fg="white",
            font=(self.tema["font_family"], self.tema["font_size_normal"]),
            padx=self.tema["button_padx"],
            pady=self.tema["button_pady"],
            relief=self.tema["relief"],
            borderwidth=self.tema["borderwidth"],
            cursor="hand2"
        )
        self.info_button.pack(side=tk.RIGHT, padx=5, pady=10)

        # Barra de estado mejorada
        self.status = tk.Label(self.main_frame, text="Listo", bd=2, relief=tk.SUNKEN,
                              anchor=tk.W, bg=self.tema["status_bg"], fg=self.tema["status_fg"],
                              font=(self.tema["font_family"], 9))
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        # Almacenar datos para exportación
        self.last_neighbors_data = None
        self.last_path_data = None

        global espacio_aereo
        espacio_aereo = None

    def cargar_datos_test(self):
        """
        Carga el archivo de prueba nodesegment.txt con formato simplificado
        Formato esperado:
        - Node [nombre] [x] [y]
        - Segment [nombre] [origen] [destino]
        """
        global espacio_aereo, ultimo_archivo_nav, ultimo_archivo_seg, ultimo_archivo_aer

        try:
            # Ruta completa al archivo nodesegment.txt
            archivo_test = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nodesegment.txt")

            if not os.path.exists(archivo_test):
                messagebox.showerror("Error", f"No se encontró el archivo de prueba: {archivo_test}")
                return

            espacio_aereo = AirSpace()
            espacio_aereo.name = "Datos de Prueba"

            # Diccionario para mapear nombres a números
            nodos = {}
            num_punto = 1

            # Primera pasada: leer los nodos
            with open(archivo_test, 'r') as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea:
                        continue

                    partes = linea.split()
                    if len(partes) >= 4 and partes[0] == "Node":
                        nombre = partes[1]
                        x = float(partes[2])
                        y = float(partes[3])

                        # Crear punto de navegación (usamos x,y como lat,lon)
                        nuevo_punto = NavPoint(num_punto, nombre, x, y)
                        add_navpoint(espacio_aereo, nuevo_punto)

                        # Guardar la referencia para los segmentos
                        nodos[nombre] = num_punto
                        num_punto += 1

            # Segunda pasada: leer los segmentos
            num_segmento = 1
            with open(archivo_test, 'r') as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea:
                        continue

                    partes = linea.split()
                    if len(partes) >= 4 and partes[0] == "Segment":
                        nombre_segmento = partes[1]
                        origen_nombre = partes[2]
                        destino_nombre = partes[3]

                        # Obtener números de nodos
                        if origen_nombre in nodos and destino_nombre in nodos:
                            origen = nodos[origen_nombre]
                            destino = nodos[destino_nombre]

                            # Calcular distancia aproximada (simplemente 1.0 para este ejemplo)
                            distancia = 1.0

                            # Crear segmento
                            nuevo_segmento = NavSegment(origen, destino, distancia)
                            add_navsegment(espacio_aereo, nuevo_segmento)
                            num_segmento += 1

            # Actualizar últimos archivos cargados
            ultimo_archivo_nav = archivo_test
            ultimo_archivo_seg = archivo_test
            ultimo_archivo_aer = ""

            messagebox.showinfo("Éxito",
                                f"Datos de prueba cargados correctamente.\n\nPuntos de navegación: {len(espacio_aereo.navpoints)}\nSegmentos: {len(espacio_aereo.navsegments)}\nAeropuertos: {len(espacio_aereo.navairports)}")

            self.status.config(
                text=f"Datos de prueba cargados: {len(espacio_aereo.navpoints)} puntos, {len(espacio_aereo.navsegments)} segmentos")

            # Habilitar el botón de exportación cuando se cargan los datos
            if hasattr(self, 'export_btn'):
                self.export_btn.config(state=tk.NORMAL)

            # Mostrar el gráfico después de cargar los datos
            mostrar_espacio_aereo(self)

            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos de prueba: {str(e)}")
            return False


def main():
    app = AplicacionNavegacionEspacioAereo()
    app.mainloop()

if __name__ == "__main__":
    main()
