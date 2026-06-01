import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os
import re
import pygame
import datetime
from airport import *
from aircraft import *
from LEBL import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    import tkintermapview

    MAPVIEW_AVAILABLE = True
except ImportError:
    MAPVIEW_AVAILABLE = False

modo_oscuro_activo = False
color_fondo = "#F4F6F7"
color_paneles = "#FFFFFF"
color_texto = "black"

estilo_base = {
    "bg": "#B0BEC5",
    "fg": "black",
    "font": ("Helvetica", 9, "bold"),
    "relief": tk.FLAT,
    "cursor": "hand2",
    "activebackground": "#90A4AE"
}

mis_aeropuertos = []
vuelos = []
bcn_airport = None
mi_ap = None

def registrar_evento(mensaje):
    hora = datetime.datetime.now().strftime("%H:%M:%S")
    texto = f"[{hora}] {mensaje}\n"
    consola_registro.config(state=tk.NORMAL)
    consola_registro.insert(tk.END, texto)
    consola_registro.see(tk.END)
    consola_registro.config(state=tk.DISABLED)


def alternar_modo_oscuro():
    global modo_oscuro_activo, color_fondo, color_paneles, color_texto
    modo_oscuro_activo = not modo_oscuro_activo

    if modo_oscuro_activo:
        color_fondo = "#2C3E50"
        color_paneles = "#34495E"
        color_texto = "#ECF0F1"
        btn_tema.config(text="☀️ Modo Claro")
    else:
        color_fondo = "#F4F6F7"
        color_paneles = "#FFFFFF"
        color_texto = "black"
        btn_tema.config(text="🌙 Modo Oscuro")

    root.configure(bg=color_fondo)

    def actualizar_hijos(widget_padre):
        for w in widget_padre.winfo_children():
            if isinstance(w, tk.LabelFrame):
                w.configure(bg=color_fondo, fg=color_texto)
            elif isinstance(w, tk.Frame):
                if w.master == root:
                    w.configure(bg=color_fondo)
                else:
                    w.configure(bg=color_paneles)
            elif isinstance(w, tk.Label):
                w.configure(bg=w.master.cget('bg'), fg=color_texto)
            elif isinstance(w, tk.Listbox):
                w.configure(bg=color_paneles, fg=color_texto)
            elif isinstance(w, tk.Entry):
                w.configure(bg=color_paneles, fg=color_texto, insertbackground=color_texto)
            actualizar_hijos(w)

    actualizar_hijos(root)

    style = ttk.Style()
    if modo_oscuro_activo:
        style.configure("Treeview", background=color_paneles, foreground=color_texto, fieldbackground=color_paneles)
        style.configure("Treeview.Heading", background="#1ABC9C", foreground="black")
    else:
        style.configure("Treeview", background="white", foreground="black", fieldbackground="white")
        style.configure("Treeview.Heading", background="#D5D8DC", foreground="black")

    registrar_evento(f"INFO: Tema cambiado a {'Oscuro' if modo_oscuro_activo else 'Claro'}.")


def mostrar_tabla_arribos():
    if not vuelos:
        registrar_evento("ADVERTENCIA: Intento de abrir tabla sin vuelos cargados.")
        messagebox.showwarning("Aviso", "No hay vuelos cargados. Carga el archivo primero.")
        return

    for widget in frame_grafico.winfo_children():
        widget.destroy()

    titulo = tk.Label(frame_grafico, text="✈️ TABLÓN DE VUELOS - LEBL / BCN", bg=color_paneles, fg=color_texto,
                      font=("Helvetica", 14, "bold"))
    titulo.pack(pady=10)

    frame_buscador = tk.Frame(frame_grafico, bg=color_paneles)
    frame_buscador.pack(fill=tk.X, padx=15, pady=5)

    tk.Label(frame_buscador, text="🔍 Buscar Vuelo / Origen:", bg=color_paneles, fg=color_texto,
             font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=5)
    entrada_busqueda = tk.Entry(frame_buscador, width=40, relief=tk.SOLID, bd=1, font=("Helvetica", 10),
                                bg=color_paneles, fg=color_texto, insertbackground=color_texto)
    entrada_busqueda.pack(side=tk.LEFT, padx=5)

    style = ttk.Style()
    style.theme_use("clam")

    if modo_oscuro_activo:
        style.configure("Treeview", background=color_paneles, foreground=color_texto, fieldbackground=color_paneles,
                        rowheight=30, font=("Helvetica", 10))
        style.configure("Treeview.Heading", background="#1ABC9C", foreground="black", font=("Helvetica", 11, "bold"))
    else:
        style.configure("Treeview", background="white", foreground="black", fieldbackground="white", rowheight=30,
                        font=("Helvetica", 10))
        style.configure("Treeview.Heading", background="#D5D8DC", foreground="black", font=("Helvetica", 11, "bold"))

    style.map("Treeview", background=[('selected', "#90A4AE")])

    scroll_y = tk.Scrollbar(frame_grafico, orient=tk.VERTICAL)
    scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    columnas = ("id", "compania", "origen", "hora")
    tabla = ttk.Treeview(frame_grafico, columns=columnas, show="headings", style="Treeview",
                         yscrollcommand=scroll_y.set)
    scroll_y.config(command=tabla.yview)

    tabla.heading("id", text="FLIGHT")
    tabla.heading("compania", text="AIRLINE")
    tabla.heading("origen", text="FROM")
    tabla.heading("hora", text="ARRIVAL TIME")

    tabla.column("id", width=120, anchor="center")
    tabla.column("compania", width=150, anchor="center")
    tabla.column("origen", width=150, anchor="center")
    tabla.column("hora", width=120, anchor="center")

    vuelos_ordenados = sorted(vuelos, key=lambda x: getattr(x, 'time', '00:00') if getattr(x, 'time', '') else '99:99')

    def poblar_tabla(filtro=""):
        tabla.delete(*tabla.get_children())
        filtro = filtro.lower()
        contador = 0
        for v in vuelos_ordenados:
            origen_mostrar = v.origin if v.origin else "LEBL (Salida)"
            hora_mostrar = v.time if v.time else "--:--"

            if filtro in v.id.lower() or filtro in v.company.lower() or filtro in origen_mostrar.lower():
                tag = 'par' if contador % 2 == 0 else 'impar'
                tabla.insert("", tk.END, values=(v.id, v.company, origen_mostrar, hora_mostrar), tags=(tag,))
                contador += 1

    def on_buscar(event):
        poblar_tabla(entrada_busqueda.get())

    entrada_busqueda.bind("<KeyRelease>", on_buscar)

    if modo_oscuro_activo:
        tabla.tag_configure('par', background="#2C3E50")
        tabla.tag_configure('impar', background="#34495E")
    else:
        tabla.tag_configure('par', background="#F9F9F9")
        tabla.tag_configure('impar', background="#FFFFFF")

    tabla.pack(expand=True, fill="both", padx=15, pady=15)

    poblar_tabla()
    registrar_evento("INFO: Tablón de vuelos visualizado con buscador activo.")


def cargar_archivo():
    ruta_archivo = filedialog.askopenfilename(title="Seleccionar archivo de aeropuertos",
                                              filetypes=[("Text files", "*.txt")])
    if ruta_archivo:
        datos_temporales = LoadAirports(ruta_archivo)
        mis_aeropuertos.clear()
        mis_aeropuertos.extend(datos_temporales)
        registrar_evento(f"ÉXITO: Se han cargado {len(mis_aeropuertos)} aeropuertos del archivo.")
    global mi_ap
    datos_temporales = LoadAirports("Airports.txt")
    mis_aeropuertos[:] = []
    for aeropuerto in datos_temporales:
        mis_aeropuertos.append(aeropuerto)

    mi_ap = LoadAirportStructure("LEBL.txt")

    #messagebox.showinfo("Carga",f"Se han cargado {len(mis_aeropuertos)} aeropuertos y la estructura táctica de LEBL con éxito.")

def ver_mapa_diques_dinamico():
    if mi_ap is None:
        messagebox.showwarning("Sin estructura", "Primero debes cargar el archivo de datos (Cargar TXT).")
        return
    PlotTerminalPiers(mi_ap)

def marcar_schengen():
    for apt in mis_aeropuertos:
        SetSchengen(apt)
    registrar_evento("INFO: Estado Schengen evaluado para todos los aeropuertos en memoria.")


def ver_datos():
    if len(mis_aeropuertos) == 0:
        registrar_evento("ADVERTENCIA: Intento de ver lista de aeropuertos vacía.")
        messagebox.showwarning("Vacío", "La lista está vacía. Carga el archivo primero.")
        return

    for widget in frame_grafico.winfo_children():
        widget.destroy()

    titulo = tk.Label(frame_grafico, text="🌍 DIRECTORIO DE AEROPUERTOS", bg=color_paneles, fg=color_texto,
                      font=("Helvetica", 14, "bold"))
    titulo.pack(pady=10)

    frame_buscador = tk.Frame(frame_grafico, bg=color_paneles)
    frame_buscador.pack(fill=tk.X, padx=15, pady=5)

    tk.Label(frame_buscador, text="🔍 Buscar Código / Estado:", bg=color_paneles, fg=color_texto,
             font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=5)
    entrada_busqueda = tk.Entry(frame_buscador, width=40, relief=tk.SOLID, bd=1, font=("Helvetica", 10),
                                bg=color_paneles, fg=color_texto, insertbackground=color_texto)
    entrada_busqueda.pack(side=tk.LEFT, padx=5)

    barra_scroll = tk.Scrollbar(frame_grafico)
    barra_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    lista_visual = tk.Listbox(frame_grafico, yscrollcommand=barra_scroll.set, font=("Courier", 10), bg=color_paneles,
                              fg=color_texto, relief=tk.FLAT)
    lista_visual.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)
    barra_scroll.config(command=lista_visual.yview)

    def poblar_lista(filtro=""):
        lista_visual.delete(0, tk.END)
        filtro = filtro.lower()
        for apt in mis_aeropuertos:
            estado = "Schengen" if apt.schengen else "No Schengen"
            texto_fila = f"{apt.codigo}: {apt.latitud:.2f}, {apt.longitud:.2f}   |   ZONA: {estado}"
            if filtro in apt.codigo.lower() or filtro in estado.lower():
                lista_visual.insert(tk.END, texto_fila)

    def on_buscar(event):
        poblar_lista(entrada_busqueda.get())

    entrada_busqueda.bind("<KeyRelease>", on_buscar)
    poblar_lista()
    registrar_evento("INFO: Lista de aeropuertos visualizada con buscador activo.")


def guardar_txt():
    resultado = SaveSchengenAirports(mis_aeropuertos, "SchengenAirports.txt")
    if resultado == 0:
        registrar_evento("ÉXITO: Archivo SchengenAirports.txt generado correctamente.")
    else:
        registrar_evento("ERROR: Fallo al guardar SchengenAirports.txt.")
        messagebox.showerror("Error", "No se pudo guardar la lista de aeropuertos.")


def agregar_nuevo():
    codigo = entrada_codigo.get()
    try:
        lat = float(entrada_lat.get())
        lon = float(entrada_lon.get())
        nuevo_apt = Airport(codigo.upper(), lat, lon)
        SetSchengen(nuevo_apt)
        AddAirport(mis_aeropuertos, nuevo_apt)
        registrar_evento(f"ÉXITO: Aeropuerto {codigo.upper()} añadido manualmente.")
        entrada_codigo.delete(0, tk.END)
        entrada_lat.delete(0, tk.END)
        entrada_lon.delete(0, tk.END)
    except ValueError:
        registrar_evento("ERROR: Intento de añadir aeropuerto con datos inválidos.")
        messagebox.showerror("Error", "Asegúrate de poner números válidos en latitud y longitud.")


def eliminar_existente():
    codigo = entrada_codigo.get()
    resultado = RemoveAirport(mis_aeropuertos, codigo.upper())
    if resultado == 0:
        registrar_evento(f"ÉXITO: Aeropuerto {codigo.upper()} borrado de la lista.")
        entrada_codigo.delete(0, tk.END)
    else:
        registrar_evento(f"ERROR: No se encontró el aeropuerto {codigo.upper()} para borrar.")
        messagebox.showerror("Error", "No se encontró el aeropuerto en la lista.")


def cargar_vuelos_archivo():
    global vuelos
    ruta_archivo = filedialog.askopenfilename(title="Seleccionar archivo de Arrivals",
                                              filetypes=[("Text files", "*.txt")])
    if ruta_archivo:
        try:
            vuelos = LoadArrivals(ruta_archivo)
            registrar_evento(f"ÉXITO: Arrivals cargados. Total en memoria: {len(vuelos)} vuelos.")
        except Exception as e:
            registrar_evento(f"ERROR: Fallo al cargar Arrivals. Detalles: {e}")
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")


def cargar_salidas_archivo():
    global vuelos
    if not vuelos:
        registrar_evento("ADVERTENCIA: Intento de cruzar Departures sin Arrivals cargados.")
        messagebox.showwarning("Aviso", "Es necesario cargar primero los Arrivals antes de cruzar Departures.")
        return

    ruta_archivo = filedialog.askopenfilename(title="Seleccionar archivo de Departures",
                                              filetypes=[("Text files", "*.txt")])
    if ruta_archivo:
        try:
            vuelos_salida, status = LoadDepartures(ruta_archivo)
            if status == 0:
                vuelos_fusionados = MergeMovements(vuelos, vuelos_salida)
                if vuelos_fusionados != -1:
                    vuelos = vuelos_fusionados
                    registrar_evento(f"ÉXITO: Vuelos fusionados correctamente. Total: {len(vuelos)} vuelos.")
                else:
                    registrar_evento("ERROR: Fallo interno en la función MergeMovements.")
                    messagebox.showerror("Error", "Fallo interno al fusionar los movimientos.")
            else:
                registrar_evento("ERROR: Estructura del archivo Departures no válida.")
                messagebox.showerror("Error", "No se pudo leer la estructura del archivo de salidas.")
        except Exception as e:
            registrar_evento(f"ERROR: Excepción inesperada al cargar Departures: {e}")
            messagebox.showerror("Error", f"Error inesperado: {e}")


def guardar_vuelos_archivo():
    if not vuelos:
        registrar_evento("ADVERTENCIA: Intento de guardar vuelos con la memoria vacía.")
        messagebox.showwarning("Aviso", "No hay vuelos para guardar.")
        return
    ruta_archivo = filedialog.asksaveasfilename(title="Guardar vuelos como...", defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt")])
    if ruta_archivo:
        try:
            if SaveFlights(vuelos, ruta_archivo) == 0:
                registrar_evento(f"ÉXITO: Archivo de vuelos guardado en {ruta_archivo}.")
            else:
                registrar_evento("ERROR: La función SaveFlights retornó fallo.")
                messagebox.showerror("Error", "No se pudo guardar el archivo.")
        except Exception as e:
            registrar_evento(f"ERROR: Excepción al guardar vuelos: {e}")
            messagebox.showerror("Error", f"Excepción al guardar: {e}")


def agregar_vuelo_manual():
    v_id = entrada_id.get()
    v_orig = entrada_orig.get()
    v_time = entrada_time.get()
    v_comp = entrada_comp.get()
    if v_id and v_time:
        try:
            nuevo_vuelo = Aircraft(v_id, v_comp, v_orig, v_time)
            vuelos.append(nuevo_vuelo)
            registrar_evento(f"ÉXITO: Vuelo {v_id} añadido manualmente a la lista temporal.")
            entrada_id.delete(0, tk.END)
            entrada_orig.delete(0, tk.END)
            entrada_time.delete(0, tk.END)
            entrada_comp.delete(0, tk.END)
        except Exception as e:
            registrar_evento(f"ERROR: Fallo al añadir vuelo manualmente: {e}")
            messagebox.showerror("Error", f"No se pudo añadir el vuelo: {e}")
    else:
        registrar_evento("ADVERTENCIA: Intento de añadir vuelo sin ID o Tiempo.")
        messagebox.showwarning("Advertencia", "ID y Tiempo son obligatorios.")


def configurar_mapa(map_widget):
    map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=es&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)


def mapa_puntos():
    if not mis_aeropuertos:
        registrar_evento("ADVERTENCIA: Intento de mapear sin aeropuertos en memoria.")
        messagebox.showwarning("Aviso", "No hay aeropuertos para mapear.")
        return
    MapAirports(mis_aeropuertos)
    if MAPVIEW_AVAILABLE:
        for widget in frame_grafico.winfo_children():
            widget.destroy()
        map_widget = tkintermapview.TkinterMapView(frame_grafico, corner_radius=0)
        map_widget.pack(fill=tk.BOTH, expand=True)
        configurar_mapa(map_widget)
        map_widget.set_position(48.0, 10.0)
        map_widget.set_zoom(4)

        for apt in mis_aeropuertos:
            if apt.schengen:
                estado = "Schengen"
                color_borde = "#2874A6"
                color_centro = "#85C1E9"
            else:
                estado = "No Schengen"
                color_borde = "#B03A2E"
                color_centro = "#F1948A"

            info_popup = f"📍 Aeropuerto: {apt.codigo}\nZona: {estado}\nLat: {apt.latitud:.2f}\nLon: {apt.longitud:.2f}"

            map_widget.set_marker(
                apt.latitud, apt.longitud,
                marker_color_outside=color_borde,
                marker_color_circle=color_centro,
                command=lambda m, msg=info_popup: messagebox.showinfo("Info Aeropuerto", msg)
            )
        registrar_evento("INFO: Mapa interactivo de aeropuertos generado.")
    else:
        registrar_evento("ERROR: Librería tkintermapview no detectada al generar mapa.")
        messagebox.showerror("Error de Librería",
                             "La librería interactiva no está instalada.\nEjecuta: pip install tkintermapview")


def mapa_rutas():
    if not vuelos:
        registrar_evento("ADVERTENCIA: Intento de mapear rutas sin vuelos cargados.")
        messagebox.showwarning("Aviso", "No hay vuelos para mapear.")
        return
    MapFlights(vuelos)
    if MAPVIEW_AVAILABLE:
        for widget in frame_grafico.winfo_children():
            widget.destroy()
        map_widget = tkintermapview.TkinterMapView(frame_grafico, corner_radius=0)
        map_widget.pack(fill=tk.BOTH, expand=True)
        configurar_mapa(map_widget)
        lat_lebl, lon_lebl = 41.297445, 2.0832941
        map_widget.set_position(45.0, 5.0)
        map_widget.set_zoom(4)
        lista_aeropuertos = LoadAirports("Airports.txt")

        for flight in vuelos:
            aero = next((a for a in lista_aeropuertos if a.codigo == flight.origin), None)
            if aero:
                es_schengen = IsSchengenAirport(flight.origin)
                color_ruta = "#2E86C1" if es_schengen else "#CB4335"
                color_borde = "#2874A6" if es_schengen else "#B03A2E"
                color_centro = "#85C1E9" if es_schengen else "#F1948A"

                info_popup = f"✈️ Vuelo: {flight.id}\nOrigen: {flight.origin} ({'Schengen' if es_schengen else 'No Schengen'})\nAerolínea: {flight.company}"

                map_widget.set_marker(
                    aero.latitud, aero.longitud,
                    marker_color_outside=color_borde,
                    marker_color_circle=color_centro,
                    command=lambda m, msg=info_popup: messagebox.showinfo("Info Vuelo", msg)
                )
                map_widget.set_path([(aero.latitud, aero.longitud), (lat_lebl, lon_lebl)], color=color_ruta, width=2)

        map_widget.set_marker(lat_lebl, lon_lebl, marker_color_outside="#1E8449", marker_color_circle="#82E0AA",
                              command=lambda m: messagebox.showinfo("Destino", "📍 LEBL - Barcelona"))
        registrar_evento("INFO: Mapa interactivo de rutas generado.")
    else:
        registrar_evento("ERROR: Librería tkintermapview no detectada.")
        messagebox.showerror("Error de Librería",
                             "La librería interactiva no está instalada.\nEjecuta: pip install tkintermapview")


def mapa_lejano():
    if not vuelos:
        registrar_evento("ADVERTENCIA: Intento de mapear vuelos lejanos sin datos.")
        messagebox.showwarning("Aviso", "No hay vuelos para mapear.")
        return
    lejanos = LongDistanceArrivals(vuelos)
    if lejanos:
        MapFlights(lejanos)
        if MAPVIEW_AVAILABLE:
            for widget in frame_grafico.winfo_children():
                widget.destroy()
            map_widget = tkintermapview.TkinterMapView(frame_grafico, corner_radius=0)
            map_widget.pack(fill=tk.BOTH, expand=True)
            configurar_mapa(map_widget)
            lat_lebl, lon_lebl = 41.297445, 2.0832941
            map_widget.set_position(35.0, -10.0)
            map_widget.set_zoom(3)
            lista_aeropuertos = LoadAirports("Airports.txt")

            for flight in lejanos:
                aero = next((a for a in lista_aeropuertos if a.codigo == flight.origin), None)
                if aero:
                    es_schengen = IsSchengenAirport(flight.origin)
                    color_ruta = "#2E86C1" if es_schengen else "#CB4335"
                    color_borde = "#2874A6" if es_schengen else "#B03A2E"
                    color_centro = "#85C1E9" if es_schengen else "#F1948A"

                    info_popup = f"⚠️ ALERTA: VUELO LEJANO\n✈️ Vuelo: {flight.id}\nOrigen: {flight.origin}\nAerolínea: {flight.company}"

                    map_widget.set_marker(
                        aero.latitud, aero.longitud,
                        marker_color_outside=color_borde,
                        marker_color_circle=color_centro,
                        command=lambda m, msg=info_popup: messagebox.showwarning("Inspección Especial", msg)
                    )
                    map_widget.set_path([(aero.latitud, aero.longitud), (lat_lebl, lon_lebl)], color=color_ruta,
                                        width=2)

            map_widget.set_marker(lat_lebl, lon_lebl, marker_color_outside="#1E8449", marker_color_circle="#82E0AA",
                                  command=lambda m: messagebox.showinfo("Destino", "📍 LEBL - Barcelona"))
            registrar_evento(f"INFO: Mapa de vuelos lejanos generado. {len(lejanos)} detectados.")
        else:
            registrar_evento("ERROR: Librería tkintermapview no detectada.")
            messagebox.showerror("Error de Librería",
                                 "La librería interactiva no está instalada.\nEjecuta: pip install tkintermapview")
    else:
        registrar_evento("INFO: No se detectaron vuelos a más de 2000 km.")
        messagebox.showinfo("Aviso", "No hay vuelos de más de 2000 km.")


def ventana_gestion_aeropuertos():
    global entrada_codigo, entrada_lat, entrada_lon
    nueva_ventana = tk.Toplevel(root)
    nueva_ventana.title("Gestión de Aeropuertos")
    nueva_ventana.configure(bg=color_fondo)

    frame_inputs = tk.LabelFrame(nueva_ventana, text=" Añadir / Borrar Aeropuertos ", bg=color_paneles, fg=color_texto,
                                 font=("Helvetica", 9, "bold"))
    frame_inputs.pack(padx=20, pady=20)

    tk.Label(frame_inputs, text="Código:", bg=color_paneles, fg=color_texto).grid(row=0, column=0, padx=5, pady=10)
    entrada_codigo = tk.Entry(frame_inputs, width=12, relief=tk.SOLID, bd=1, bg=color_paneles, fg=color_texto,
                              insertbackground=color_texto)
    entrada_codigo.grid(row=0, column=1, padx=5, pady=10)

    tk.Label(frame_inputs, text="Latitud:", bg=color_paneles, fg=color_texto).grid(row=0, column=2, padx=5, pady=10)
    entrada_lat = tk.Entry(frame_inputs, width=12, relief=tk.SOLID, bd=1, bg=color_paneles, fg=color_texto,
                           insertbackground=color_texto)
    entrada_lat.grid(row=0, column=3, padx=5, pady=10)

    tk.Label(frame_inputs, text="Longitud:", bg=color_paneles, fg=color_texto).grid(row=0, column=4, padx=5, pady=10)
    entrada_lon = tk.Entry(frame_inputs, width=12, relief=tk.SOLID, bd=1, bg=color_paneles, fg=color_texto,
                           insertbackground=color_texto)
    entrada_lon.grid(row=0, column=5, padx=5, pady=10)

    tk.Button(frame_inputs, text="Añadir a la Lista", command=agregar_nuevo, **estilo_base).grid(row=1, column=1,
                                                                                                 columnspan=2, pady=15,
                                                                                                 sticky="ew")
    tk.Button(frame_inputs, text="Borrar por Código", command=eliminar_existente, **estilo_base).grid(row=1, column=3,
                                                                                                      columnspan=2,
                                                                                                      pady=15,
                                                                                                      sticky="ew")


def gestion_arrivals():
    global entrada_id, entrada_orig, entrada_time, entrada_comp
    ventana_vuelos = tk.Toplevel(root)
    ventana_vuelos.title("Gestión de Vuelos (Arrivals)")
    ventana_vuelos.configure(bg=color_fondo)

    frame_guardado = tk.LabelFrame(ventana_vuelos, text=" Gestión de Vuelos ", bg=color_paneles, fg=color_texto,
                                   font=("Helvetica", 9, "bold"))
    frame_guardado.pack(padx=15, pady=15)

    tk.Label(frame_guardado, text="ID Vuelo:", bg=color_paneles, fg=color_texto).grid(row=0, column=0, padx=5, pady=5)
    entrada_id = tk.Entry(frame_guardado, width=15, relief=tk.SOLID, bd=1, bg=color_paneles, fg=color_texto,
                          insertbackground=color_texto)
    entrada_id.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_guardado, text="Origen:", bg=color_paneles, fg=color_texto).grid(row=0, column=2, padx=5, pady=5)
    entrada_orig = tk.Entry(frame_guardado, width=15, relief=tk.SOLID, bd=1, bg=color_paneles, fg=color_texto,
                            insertbackground=color_texto)
    entrada_orig.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(frame_guardado, text="Hora (H:M):", bg=color_paneles, fg=color_texto).grid(row=1, column=0, padx=5, pady=5)
    entrada_time = tk.Entry(frame_guardado, width=15, relief=tk.SOLID, bd=1, bg=color_paneles, fg=color_texto,
                            insertbackground=color_texto)
    entrada_time.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(frame_guardado, text="Compañía:", bg=color_paneles, fg=color_texto).grid(row=1, column=2, padx=5, pady=5)
    entrada_comp = tk.Entry(frame_guardado, width=15, relief=tk.SOLID, bd=1, bg=color_paneles, fg=color_texto,
                            insertbackground=color_texto)
    entrada_comp.grid(row=1, column=3, padx=5, pady=5)

    tk.Button(frame_guardado, text="Añadir Vuelo", command=agregar_vuelo_manual, **estilo_base).grid(row=2, column=1,
                                                                                                     columnspan=2,
                                                                                                     pady=10,
                                                                                                     sticky="ew")
    tk.Button(frame_guardado, text="Guardar Vuelos a TXT", command=guardar_vuelos_archivo, **estilo_base).grid(row=3,
                                                                                                               column=1,
                                                                                                               columnspan=2,
                                                                                                               pady=10,
                                                                                                               sticky="ew")


def cargar_estructura_lebl():
    global bcn_airport
    ruta = filedialog.askopenfilename(title="1. Seleccionar Estructura Base (ej. LEBL.txt)",
                                      filetypes=[("Text files", "*.txt")])
    if ruta:
        resultado = LoadAirportStructure(ruta)
        if resultado != -1:
            bcn_airport = resultado
            registrar_evento(f"ÉXITO: Estructura interna de {bcn_airport.code} procesada.")
        else:
            registrar_evento("ERROR: Archivo de estructura LEBL no válido.")
            messagebox.showerror("Error", "No se pudo procesar el archivo de estructura base.")


def cargar_aerolineas_terminal(t_name):
    global bcn_airport
    if not bcn_airport:
        registrar_evento("ADVERTENCIA: Intento de cargar aerolíneas sin estructura base.")
        messagebox.showwarning("Aviso", "Primero debes cargar la estructura general del aeropuerto.")
        return

    terminal_obj = next((t for t in bcn_airport.terminals if t.name == t_name), None)
    if not terminal_obj:
        registrar_evento(f"ERROR: La terminal {t_name} no existe en memoria.")
        messagebox.showerror("Error", f"La terminal {t_name} no existe en la estructura mapeada.")
        return

    ruta = filedialog.askopenfilename(title=f"Seleccionar aerolíneas para {t_name}",
                                      filetypes=[("Text files", "*.txt")])
    if ruta:
        try:
            with open(ruta, 'r', encoding='utf-8') as file:
                terminal_obj.airlines = [line.strip().split('\t')[1].strip() for line in file if
                                         line.strip() and len(line.split('\t')) >= 2]
            registrar_evento(f"ÉXITO: Base de datos de aerolíneas actualizada para la {t_name}.")
        except Exception as e:
            registrar_evento(f"ERROR: Fallo al leer archivo de aerolíneas: {e}")
            messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")


def asignar_puertas_vuelos():
    global bcn_airport, vuelos
    if not bcn_airport:
        messagebox.showwarning("Aviso", "Falta cargar la estructura de LEBL.")
        return
    if not vuelos:
        messagebox.showwarning("Aviso", "No hay vuelos cargados para asignar puertas.")
        return

    historial_asignaciones = []
    exitos = 0
    fallos = 0
    for vuelo in vuelos:
        res = AssignGate(bcn_airport, vuelo)
        if res == 0:
            historial_asignaciones.append(f"Vuelo {vuelo.id}: Asignado OK")
            exitos += 1
        else:
            historial_asignaciones.append(f"Vuelo {vuelo.id}: Fallo (Sin puerta libre o aerolínea no encontrada)")
            fallos += 1

    for widget in frame_grafico.winfo_children():
        widget.destroy()
    txt = tk.Text(frame_grafico, wrap=tk.WORD, font=("Courier", 9), bg=color_paneles, fg=color_texto, relief=tk.FLAT)
    txt.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    for linea in historial_asignaciones:
        txt.insert(tk.END, linea + "\n")
    txt.config(state=tk.DISABLED)
    registrar_evento(f"INFO: Asignación global finalizada. Éxitos: {exitos} | Fallos: {fallos}.")


def ver_ocupacion_puertas():
    global bcn_airport
    if not bcn_airport:
        messagebox.showwarning("Aviso", "No se ha inicializado la estructura de LEBL.")
        return
    lista_ocupacion = GateOccupancy(bcn_airport)
    for widget in frame_grafico.winfo_children():
        widget.destroy()

    titulo = tk.Label(frame_grafico, text="🚪 ESTADO DE PUERTAS - LEBL", bg=color_paneles, fg=color_texto,
                      font=("Helvetica", 14, "bold"))
    titulo.pack(pady=10)

    frame_buscador = tk.Frame(frame_grafico, bg=color_paneles)
    frame_buscador.pack(fill=tk.X, padx=15, pady=5)

    tk.Label(frame_buscador, text="🔍 Buscar Puerta / Vuelo:", bg=color_paneles, fg=color_texto,
             font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=5)
    entrada_busqueda = tk.Entry(frame_buscador, width=40, relief=tk.SOLID, bd=1, font=("Helvetica", 10),
                                bg=color_paneles, fg=color_texto, insertbackground=color_texto)
    entrada_busqueda.pack(side=tk.LEFT, padx=5)

    barra = tk.Scrollbar(frame_grafico)
    barra.pack(side=tk.RIGHT, fill=tk.Y)
    lista_visual = tk.Listbox(frame_grafico, yscrollcommand=barra.set, font=("Courier", 10), bg=color_paneles,
                              fg=color_texto, relief=tk.FLAT)
    lista_visual.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)
    barra.config(command=lista_visual.yview)

    def poblar_lista(filtro=""):
        lista_visual.delete(0, tk.END)
        filtro = filtro.lower()
        for gate_name, occupied, aircraft_id in lista_ocupacion:
            estado = f"OCUPADA [{aircraft_id}]" if occupied else "LIBRE"
            texto_fila = f"Puerta {gate_name:<15}: {estado}"
            if filtro in gate_name.lower() or filtro in estado.lower() or (
                    aircraft_id and filtro in aircraft_id.lower()):
                lista_visual.insert(tk.END, texto_fila)

    def on_buscar(event):
        poblar_lista(entrada_busqueda.get())

    entrada_busqueda.bind("<KeyRelease>", on_buscar)
    poblar_lista()
    registrar_evento("INFO: Vista de estado de puertas generada con buscador.")


def ejecutar_asignacion_nocturna():
    global bcn_airport, vuelos
    if not bcn_airport:
        messagebox.showwarning("Aviso", "Falta cargar la estructura de LEBL.")
        return
    if not vuelos:
        messagebox.showwarning("Aviso", "No hay vuelos cargados para evaluar pernoctas.")
        return

    resultado = AssignNightGates(bcn_airport, vuelos)
    if resultado == 0:
        registrar_evento("ÉXITO: Algoritmo de asignación nocturna procesado.")
        ver_ocupacion_puertas()
    else:
        registrar_evento("ERROR: Problema interno al calcular pernoctas.")
        messagebox.showerror("Error", "Hubo un problema al procesar las puertas nocturnas.")


def abrir_ventana_simulacion_hora():
    global bcn_airport, vuelos
    if not bcn_airport:
        messagebox.showwarning("Aviso", "Primero debes cargar la estructura de LEBL.")
        return

    ventana_hora = tk.Toplevel(root)
    ventana_hora.title("Simular Franja Horaria")
    ventana_hora.configure(bg=color_fondo)

    tk.Label(ventana_hora, text="Introduce la hora a simular (HH:00):", bg=color_fondo, fg=color_texto,
             font=("Helvetica", 10)).pack(pady=10)

    entrada_hora_sim = tk.Entry(ventana_hora, width=10, font=("Courier", 11), justify="center", relief=tk.SOLID, bd=1,
                                bg=color_paneles, fg=color_texto, insertbackground=color_texto)
    entrada_hora_sim.insert(0, "08:00")
    entrada_hora_sim.pack(pady=5)

    def procesar_hora():
        hora_texto = entrada_hora_sim.get().strip()
        if not re.match(r"^\d{2}:\d{2}$", hora_texto):
            registrar_evento(f"ERROR: Formato de hora simulada inválido ({hora_texto}).")
            messagebox.showerror("Error", "Formato de hora inválido. Usa HH:MM")
            return

        vuelos_rechazados = AssignGatesAtTime(bcn_airport, vuelos, hora_texto)
        ver_ocupacion_puertas()
        registrar_evento(f"INFO: Simulación ejecutada a las {hora_texto}. Rechazados: {vuelos_rechazados}")
        ventana_hora.destroy()

    tk.Button(ventana_hora, text="Simular", command=procesar_hora, **estilo_base).pack(pady=10, padx=20, fill=tk.X)


def renderizar_en_interfaz(funcion_plot, datos):
    if not datos:
        registrar_evento("ADVERTENCIA: Faltan datos para mostrar el gráfico solicitado.")
        messagebox.showwarning("Aviso", "Faltan datos para mostrar el gráfico.")
        return
    for widget in frame_grafico.winfo_children():
        widget.destroy()
    fig = funcion_plot(datos)
    if fig is None:
        tk.Label(frame_grafico, text="No se pudo generar el gráfico.", bg=color_paneles, fg=color_texto).pack(pady=20)
        registrar_evento("ERROR: La función de graficado retornó nulo.")
        return
    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    registrar_evento("INFO: Gráfico renderizado correctamente.")


def renderizar_ocupacion_24h():
    global bcn_airport, vuelos
    if not bcn_airport or not vuelos:
        messagebox.showwarning("Aviso", "Se requiere cargar la estructura LEBL y los vuelos.")
        return
    renderizar_en_interfaz(lambda d: PlotDayOccupancy(bcn_airport, d), vuelos)


pygame.mixer.init()
lista_musica = ["musica1.mp3", "musica2.mp3", "musica3.mp3"]
indice_actual = 0


def reproducir_cancion():
    global indice_actual
    try:
        cancion = lista_musica[indice_actual]
        if os.path.exists(cancion):
            pygame.mixer.music.load(cancion)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.8)
            lbl_contador.config(text=f"{indice_actual + 1}/{len(lista_musica)}")
        else:
            pass
    except Exception as e:
        pass

def mostrar_tabla_salidas():
    if not vuelos:
        registrar_evento("ADVERTENCIA: Intento de abrir tabla de salidas sin vuelos cargados.")
        messagebox.showwarning("Aviso", "No hay vuelos cargados. Carga el archivo primero.")
        return
    for widget in frame_grafico.winfo_children():
        widget.destroy()
    titulo = tk.Label(frame_grafico, text="✈️ TABLÓN DE VUELOS - SALIDAS / DEPARTURES", bg=color_paneles, fg=color_texto,
                      font=("Helvetica", 14, "bold"))
    titulo.pack(pady=10)
    frame_buscador = tk.Frame(frame_grafico, bg=color_paneles)
    frame_buscador.pack(fill=tk.X, padx=15, pady=5)
    tk.Label(frame_buscador, text="🔍 Buscar Vuelo / Destino:", bg=color_paneles, fg=color_texto,
             font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=5)
    entrada_busqueda = tk.Entry(frame_buscador, width=40, relief=tk.SOLID, bd=1, font=("Helvetica", 10),
                                bg=color_paneles, fg=color_texto, insertbackground=color_texto)
    entrada_busqueda.pack(side=tk.LEFT, padx=5)
    style = ttk.Style()
    style.theme_use("clam")
    if modo_oscuro_activo:
        style.configure("Treeview", background=color_paneles, foreground=color_texto, fieldbackground=color_paneles,
                        rowheight=30, font=("Helvetica", 10))
        style.configure("Treeview.Heading", background="#1ABC9C", foreground="black", font=("Helvetica", 11, "bold"))
    else:
        style.configure("Treeview", background="white", foreground="black", fieldbackground="white", rowheight=30,
                        font=("Helvetica", 10))
        style.configure("Treeview.Heading", background="#D5D8DC", foreground="black", font=("Helvetica", 11, "bold"))

    style.map("Treeview", background=[('selected', "#90A4AE")])
    scroll_y = tk.Scrollbar(frame_grafico, orient=tk.VERTICAL)
    scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    columnas = ("id", "compania", "destino", "hora")
    tabla = ttk.Treeview(frame_grafico, columns=columnas, show="headings", style="Treeview",
                         yscrollcommand=scroll_y.set)
    scroll_y.config(command=tabla.yview)
    tabla.heading("id", text="FLIGHT")
    tabla.heading("compania", text="AIRLINE")
    tabla.heading("destino", text="TO")
    tabla.heading("hora", text="DEPARTURE TIME")
    tabla.column("id", width=120, anchor="center")
    tabla.column("compania", width=150, anchor="center")
    tabla.column("destino", width=150, anchor="center")
    tabla.column("hora", width=120, anchor="center")
    vuelos_ordenados = sorted(vuelos, key=lambda x: getattr(x, 'time', '00:00') if getattr(x, 'time', '') else '99:99')

    def poblar_tabla(filtro=""):
        tabla.delete(*tabla.get_children())
        filtro = filtro.lower()
        contador = 0
        for v in vuelos_ordenados:
            destino_mostrar = getattr(v, 'destination', 'LEBL (Llegada)') if hasattr(v, 'destination') else "Desconocido"
            hora_mostrar = v.time if v.time else "--:--"
            if filtro in v.id.lower() or filtro in v.company.lower() or filtro in destino_mostrar.lower():
                tag = 'par' if contador % 2 == 0 else 'impar'
                tabla.insert("", tk.END, values=(v.id, v.company, destino_mostrar, hora_mostrar), tags=(tag,))
                contador += 1

    def on_buscar(event):
        poblar_tabla(entrada_busqueda.get())
    entrada_busqueda.bind("<KeyRelease>", on_buscar)
    if modo_oscuro_activo:
        tabla.tag_configure('par', background="#2C3E50")
        tabla.tag_configure('impar', background="#34495E")
    else:
        tabla.tag_configure('par', background="#F9F9F9")
        tabla.tag_configure('impar', background="#FFFFFF")
    tabla.pack(expand=True, fill="both", padx=15, pady=15)
    poblar_tabla()
    registrar_evento("INFO: Tablón de salidas visualizado con buscador activo.")

def siguiente_cancion():
    global indice_actual
    indice_actual = (indice_actual + 1) % len(lista_musica)
    reproducir_cancion()


def anterior_cancion():
    global indice_actual
    indice_actual = (indice_actual - 1) % len(lista_musica)
    reproducir_cancion()


def parar_cancion():
    pygame.mixer.music.stop()
    lbl_contador.config(text=f"0/{len(lista_musica)}")


root = tk.Tk()
root.title("Panel de Control - Gestión Aeroportuaria Avanzada")
root.state('zoomed')
root.configure(bg=color_fondo)

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=6)
for i in range(8):
    root.rowconfigure(i, weight=1)

frame_controles = tk.LabelFrame(root, text="1. Carga de Archivos Globales", bg=color_paneles, fg="#34495E",
                                font=("Helvetica", 9, "bold"))
frame_controles.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
frame_controles.columnconfigure(0, weight=1)
frame_controles.columnconfigure(1, weight=1)

tk.Button(frame_controles, text="Cargar Airports", command=cargar_archivo, **estilo_base).grid(row=0, column=0, padx=5,
                                                                                               pady=5, sticky="nsew")
tk.Button(frame_controles, text="Cargar Arrivals", command=cargar_vuelos_archivo, **estilo_base).grid(row=0, column=1,
                                                                                                      padx=5, pady=5,
                                                                                                      sticky="nsew")
tk.Button(frame_controles, text="Cargar Departures (Salidas)", command=cargar_salidas_archivo, **estilo_base).grid(
    row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

frame_5 = tk.LabelFrame(root, text="2. Edición Manual", bg=color_paneles, fg="#34495E", font=("Helvetica", 9, "bold"))
frame_5.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
frame_5.columnconfigure(0, weight=1)
frame_5.columnconfigure(1, weight=1)

tk.Button(frame_5, text="Gestionar Aeropuertos", command=ventana_gestion_aeropuertos, **estilo_base).grid(row=0,
                                                                                                          column=0,
                                                                                                          padx=5,
                                                                                                          pady=5,
                                                                                                          sticky="nsew")
tk.Button(frame_5, text="Gestionar Arrivals", command=gestion_arrivals, **estilo_base).grid(row=0, column=1, padx=5,
                                                                                            pady=5, sticky="nsew")

frame_2 = tk.LabelFrame(root, text="3. Filtros y Exportación", bg=color_paneles, fg="#34495E",
                        font=("Helvetica", 9, "bold"))
frame_2.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
for i in range(3): frame_2.columnconfigure(i, weight=1)

tk.Button(frame_2, text="Eval. Schengen", command=marcar_schengen, **estilo_base).grid(row=0, column=0, padx=2, pady=5,
                                                                                       sticky="nsew")
tk.Button(frame_2, text="Ver Lista", command=ver_datos, **estilo_base).grid(row=0, column=1, padx=2, pady=5,
                                                                            sticky="nsew")
tk.Button(frame_2, text="Guardar TXT", command=guardar_txt, **estilo_base).grid(row=0, column=2, padx=2, pady=5,
                                                                                sticky="nsew")

frame_3 = tk.LabelFrame(root, text="4. Visualización y Gráficos", bg=color_paneles, fg="#34495E",
                        font=("Helvetica", 9, "bold"))
frame_3.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
frame_3.columnconfigure(0, weight=1)
frame_3.columnconfigure(1, weight=1)

tk.Button(frame_3, text="Airports", command=lambda: renderizar_en_interfaz(PlotAirports, mis_aeropuertos),
          **estilo_base).grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
tk.Button(frame_3, text="Arrivals H", command=lambda: renderizar_en_interfaz(PlotArrivals, vuelos), **estilo_base).grid(
    row=0, column=1, padx=5, pady=5, sticky="nsew")
tk.Button(frame_3, text="Airlines", command=lambda: renderizar_en_interfaz(PlotAirlines, vuelos), **estilo_base).grid(
    row=1, column=0, padx=5, pady=5, sticky="nsew")
tk.Button(frame_3, text="Schengen V.", command=lambda: renderizar_en_interfaz(PlotFlightsType, vuelos),
          **estilo_base).grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
tk.Button(frame_3, text="Tabla Arrivals", command=mostrar_tabla_arribos, **estilo_base).grid(row=2, column=0,
                                                                                                    columnspan=1,
                                                                                                    padx=5, pady=5,
                                                                                                    sticky="nsew")
tk.Button(frame_3, text="Tabla Departures", command=mostrar_tabla_salidas, **estilo_base).grid(row=2, column=1,
                                                                                                    padx=5, pady=5,
                                                                                                    sticky="nsew")

btn_tema = tk.Button(frame_3, text="🌙 Modo Oscuro", command=alternar_modo_oscuro, **estilo_base)
btn_tema.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

frame_4 = tk.LabelFrame(root, text="5. Mapas KML e Interfaz", bg=color_paneles, fg="#34495E",
                        font=("Helvetica", 9, "bold"))
frame_4.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")
frame_4.columnconfigure(0, weight=1)
frame_4.columnconfigure(1, weight=1)

tk.Button(frame_4, text="Mapa Aeropuertos", command=mapa_puntos, **estilo_base).grid(row=0, column=0, padx=5, pady=5,
                                                                                     sticky="nsew")
tk.Button(frame_4, text="Mapa Rutas", command=mapa_rutas, **estilo_base).grid(row=0, column=1, padx=5, pady=5,
                                                                              sticky="nsew")
tk.Button(frame_4, text="Mapa Vuelos Lejanos", command=mapa_lejano, **estilo_base).grid(row=1, column=0, columnspan=2,
                                                                                        padx=5, pady=5, sticky="nsew")

frame_lebl = tk.LabelFrame(root, text="6. Gestión Interna LEBL (Barcelona)", bg=color_paneles, fg="#34495E",
                           font=("Helvetica", 9, "bold"))
frame_lebl.grid(row=5, column=0, padx=10, pady=5, sticky="nsew")
for i in range(3): frame_lebl.columnconfigure(i, weight=1)

tk.Button(frame_lebl, text="1. Estructura", command=cargar_estructura_lebl, **estilo_base).grid(row=0, column=0, padx=2,
                                                                                                pady=2, sticky="nsew")
tk.Button(frame_lebl, text="2. Aerolíneas T1", command=lambda: cargar_aerolineas_terminal("T1"), **estilo_base).grid(
    row=0, column=1, padx=2, pady=2, sticky="nsew")
tk.Button(frame_lebl, text="3. Aerolíneas T2", command=lambda: cargar_aerolineas_terminal("T2"), **estilo_base).grid(
    row=0, column=2, padx=2, pady=2, sticky="nsew")

tk.Button(frame_lebl, text="Asignar Puertas Llegadas", command=asignar_puertas_vuelos, **estilo_base).grid(row=1,
                                                                                                           column=0,
                                                                                                           columnspan=2,
                                                                                                           padx=2,
                                                                                                           pady=2,
                                                                                                           sticky="nsew")
tk.Button(frame_lebl, text="Ver Estado Puertas", command=ver_ocupacion_puertas, **estilo_base).grid(row=1, column=2,
                                                                                                    padx=2, pady=2,
                                                                                                    sticky="nsew")

tk.Button(frame_lebl, text="Asignar Pernoctas", command=ejecutar_asignacion_nocturna, **estilo_base).grid(row=2,
                                                                                                          column=0,
                                                                                                          columnspan=1,
                                                                                                          padx=2,
                                                                                                          pady=2,
                                                                                                          sticky="nsew")
tk.Button(frame_lebl, text="Simular por Hora", command=abrir_ventana_simulacion_hora, **estilo_base).grid(row=2,
                                                                                                          column=1,
                                                                                                          columnspan=1,
                                                                                                          padx=2,
                                                                                                          pady=2,
                                                                                                          sticky="nsew")
tk.Button(frame_lebl, text="Gráfico 24h", command=renderizar_ocupacion_24h, **estilo_base).grid(row=2, column=2,
                                                                                                columnspan=1, padx=2,
                                                                                                pady=2, sticky="nsew")

frame_grafico = tk.LabelFrame(root, text=" Visor Principal de Datos y Gráficos ", bg=color_paneles, fg="#34495E",
                              font=("Helvetica", 9, "bold"))
frame_grafico.grid(row=0, column=1, rowspan=6, padx=15, pady=5, sticky="nsew")

frame_log = tk.LabelFrame(root, text=" Registro de Eventos (Consola) ", bg=color_paneles, fg="#34495E",
                          font=("Helvetica", 9, "bold"))
frame_log.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

consola_registro = tk.Text(frame_log, height=5, bg="#1E1E1E", fg="#00FF00", font=("Courier", 9))
consola_registro.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
consola_registro.config(state=tk.DISABLED)

frame_musica = tk.LabelFrame(root, text=" 🎵 Reproductor de Fondo ", bg=color_paneles, fg="#34495E",
                             font=("Helvetica", 9, "bold"))
frame_musica.grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

tk.Button(frame_musica, text="⏮", command=anterior_cancion, **estilo_base).grid(row=0, column=0, padx=10, pady=5,
                                                                                ipadx=10)
tk.Button(frame_musica, text="▶", command=reproducir_cancion, **estilo_base).grid(row=0, column=1, padx=10, pady=5,
                                                                                  ipadx=10)
tk.Button(frame_musica, text="⏭", command=siguiente_cancion, **estilo_base).grid(row=0, column=2, padx=10, pady=5,
                                                                                 ipadx=10)
tk.Button(frame_musica, text="⬜", command=parar_cancion, **estilo_base).grid(row=0, column=3, padx=10, pady=5, ipadx=10)
lbl_contador = tk.Label(frame_musica, text=f"0/{len(lista_musica)}", bg=color_paneles, fg="#34495E",
                        font=("Helvetica", 9, "bold"), width=6)
lbl_contador.grid(row=0, column=4, padx=10, pady=5)

tk.Button(frame_lebl, text="🗺️ Esquema T1",command=lambda: renderizar_en_interfaz(lambda ap: PlotTerminalPiers(ap, "T1"), bcn_airport),**estilo_base).grid(row=3, column=0, columnspan=1, padx=2, pady=4, sticky="nsew")

tk.Button(frame_lebl, text="🗺️ Esquema T2",command=lambda: renderizar_en_interfaz(lambda ap: PlotTerminalPiers(ap, "T2"), bcn_airport),**estilo_base).grid(row=3, column=1, columnspan=2, padx=2, pady=4, sticky="nsew")
root.mainloop()