import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from airport import *
from aircraft import *
from LEBL import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import pygame
from tkinter import ttk
import tkintermapview


color_fondo = "#EBF5FB"
color_datos = "#A8E6CF"
color_visual = "#FFD3B6"
color_borrar = "#FFAAA5"
color_anadir = "#FFF0B3"
color_vuelos = "#ADD8E6"
color_principal = "#B0BEC5"
mis_aeropuertos = []
vuelos = []


def mostrar_tabla_arribos():
    if not vuelos:
        messagebox.showwarning("Aviso", "No hay vuelos cargados. Carga el archivo primero.")
        return
    ventana_panel = tk.Toplevel(root)
    ventana_panel.title("✈️ TABLÓN DE LLEGADAS - LEBL / BCN")
    ventana_panel.geometry("600x800")
    ventana_panel.configure(bg="black")

    titulo = tk.Label(ventana_panel, text="ARRIVALS / LLEGADAS", bg="black", fg="#C9CF1C", font=("Courier", 18, "bold"))
    titulo.pack(pady=10)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="#121016", foreground="#FFFFFF", fieldbackground="#121016", rowheight=25,font=("Courier", 11, "bold"))
    style.configure("Treeview.Heading", background="#121016", foreground="#C9CF1C", font=("Courier", 13, "bold"))

    columnas = ("id", "compania", "origen", "hora")
    tabla = ttk.Treeview(ventana_panel, columns=columnas, show="headings", style="Treeview")

    tabla.heading("id", text="FLIGHT")
    tabla.heading("compania", text="AIRLINE")
    tabla.heading("origen", text="FROM")
    tabla.heading("hora", text="TIME")

    tabla.column("id", width=100, anchor="center")
    tabla.column("compania", width=150, anchor="center")
    tabla.column("origen", width=100, anchor="center")
    tabla.column("hora", width=100, anchor="center")

    vuelos_ordenados = sorted(vuelos, key=lambda x: getattr(x, 'time', '00:00'))

    for v in vuelos_ordenados:
        tabla.insert("", tk.END, values=(v.id, v.company, v.origin, v.time))
    tabla.pack(expand=True, fill="both", padx=15, pady=15)

def cargar_archivo():
    datos_temporales = LoadAirports("Airports.txt")
    mis_aeropuertos[:] = []
    for aeropuerto in datos_temporales:
        mis_aeropuertos.append(aeropuerto)
    messagebox.showinfo("Carga", f"Se han cargado {len(mis_aeropuertos)} aeropuertos con exito.")

def marcar_schengen():
    for apt in mis_aeropuertos:
        SetSchengen(apt)
    messagebox.showinfo("Schengen", "Estado Schengen evaluado para todos los aeropuertos.")


def ver_datos():
    if len(mis_aeropuertos) == 0:
        messagebox.showwarning("Vacio", "La lista esta vacia. Carga el archivo primero.")
        return

    for widget in frame_grafico.winfo_children():
        widget.destroy()
    barra_scroll = tk.Scrollbar(frame_grafico, bg=color_fondo)
    barra_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    lista_visual = tk.Listbox(frame_grafico, yscrollcommand=barra_scroll.set, font=("Courier", 10), bg="white",fg="black")
    lista_visual.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    barra_scroll.config(command=lista_visual.yview)
    for apt in mis_aeropuertos:
        if apt.schengen:
            estado = "Schengen"
        else:
            estado = "No Schengen"
        lista_visual.insert(tk.END, f"{apt.codigo}: {apt.latitud:.2f}, {apt.longitud:.2f} ({estado})")

def guardar_txt():
    resultado = SaveSchengenAirports(mis_aeropuertos, "SchengenAirports.txt")
    if resultado == 0:
        messagebox.showinfo("Guardar", "Archivo SchengenAirports.txt generado con exito.")
    else:
        messagebox.showerror("Error", "No se pudo guardar.")


def agregar_nuevo():
    codigo = entrada_codigo.get()
    try:
        lat = float(entrada_lat.get())
        lon = float(entrada_lon.get())
        nuevo_apt = Airport(codigo.upper(), lat, lon)
        SetSchengen(nuevo_apt)
        AddAirport(mis_aeropuertos, nuevo_apt)
        messagebox.showinfo("Anadir", f"Aeropuerto {codigo.upper()} anadido a la lista.")
    except:
        messagebox.showerror("Error", "Asegurate de poner numeros validos en latitud y longitud.")

def eliminar_existente():
    codigo = entrada_codigo.get()
    resultado = RemoveAirport(mis_aeropuertos, codigo.upper())
    if resultado == 0:
        messagebox.showinfo("Borrar", f"Aeropuerto {codigo.upper()} borrado de la lista.")
    else:
        messagebox.showerror("Error", "No se encontro el aeropuerto en la lista.")

def cargar_vuelos_archivo():
    global vuelos
    ruta_archivo = filedialog.askopenfilename(title="Seleccionar archivo de vuelos", filetypes=[("Text files", "*.txt")])
    if ruta_archivo:
        try:
            vuelos = LoadArrivals(ruta_archivo)
            messagebox.showinfo("Cargar", f"Vuelos cargados correctamente desde:\n{ruta_archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")

def guardar_vuelos_archivo():
    if not vuelos:
        messagebox.showwarning("Aviso", "No hay vuelos para guardar.")
        return
    ruta_archivo = filedialog.asksaveasfilename(title="Guardar vuelos como...", defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if ruta_archivo:
        try:
            SaveFlights(vuelos, ruta_archivo)
            messagebox.showinfo("Guardar", f"Archivo guardado con éxito en:\n{ruta_archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")

def crear_kml():
    if not vuelos:
        messagebox.showwarning("Aviso", "No hay vuelos para mapear.")
        return
    try:
        MapFlights(vuelos)
        messagebox.showinfo("KML", "Archivo Rutas_Barcelona.kml creado")
    except Exception as e:
        messagebox.showerror("Error", f"Fallo al crear mapa: {e}")

def agregar_vuelo_manual():
    v_id = entrada_id.get()
    v_orig = entrada_orig.get()
    v_time = entrada_time.get()
    v_comp = entrada_comp.get()
    if v_id and v_time:
        try:
            nuevo_vuelo = Aircraft(v_id, v_comp, v_orig, v_time)
            vuelos.append(nuevo_vuelo)
            messagebox.showinfo("Añadir", f"Vuelo {v_id} añadido a la lista temporal.")
            entrada_id.delete(0, tk.END)
            entrada_orig.delete(0, tk.END)
            entrada_time.delete(0, tk.END)
            entrada_comp.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo añadir el vuelo: {e}")
    else:
        messagebox.showwarning("Advertencia", "ID y Tiempo son obligatorios.")

def mapa_vuelos_lejanos():
    if not vuelos:
        messagebox.showwarning("Aviso", "No hay vuelos para filtrar.")
        return
    vuelos_filtrados = LongDistanceArrivals(vuelos)
    if vuelos_filtrados:
        try:
            MapFlights(vuelos_filtrados)
            messagebox.showinfo("KML", "Archivo KML de Vuelos Lejanos generado. Ábrelo en Google Earth.")
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al crear mapa de vuelos lejanos: {e}")
    else:
        messagebox.showinfo("Long Distance", "No hay vuelos a más de 2000 km para mapear.")


def mostrar_mapa_interactivo(funcion_mapa, *args):
    mapa_objeto = funcion_mapa(*args)
    if mapa_objeto is None:
        messagebox.showwarning("Aviso", "No se pudo generar el mapa. Verifica que los datos estén cargados.")
        return
    for widget in frame_grafico.winfo_children():
        widget.destroy()

    try:
        home = os.path.expanduser("~")
        ruta_carpeta = os.path.join(home, "Descargas", "proyecto-informatica-grupo-6-master2")
        ruta_html = os.path.join(ruta_carpeta, "mapa_interactivo_temp.html")
        mapa_objeto.save(ruta_html)
        frame_web = HtmlFrame(frame_grafico)
        frame_web.load_file(ruta_html)
        frame_web.pack(fill=tk.BOTH, expand=True)
    except Exception as e:
        messagebox.showerror("Error de renderizado", f"No se pudo cargar el mapa en la interfaz: {e}")


def ventana_gestion_aeropuertos():
    global entrada_codigo, entrada_lat, entrada_lon
    nueva_ventana = tk.Toplevel(root)
    nueva_ventana.title("Gestión de Aeropuertos")
    nueva_ventana.configure(bg=color_fondo)

    frame_inputs = tk.LabelFrame(nueva_ventana, text=" Añadir / Borrar Aeropuertos ", bg=color_fondo, fg="black")
    frame_inputs.pack(padx=20, pady=20)


    tk.Label(frame_inputs, text="Código:", bg=color_fondo).grid(row=0, column=0, padx=5, pady=10)
    entrada_codigo = tk.Entry(frame_inputs, width=12)
    entrada_codigo.grid(row=0, column=1, padx=5, pady=10)

    tk.Label(frame_inputs, text="Latitud:", bg=color_fondo).grid(row=0, column=2, padx=5, pady=10)
    entrada_lat = tk.Entry(frame_inputs, width=12)
    entrada_lat.grid(row=0, column=3, padx=5, pady=10)

    tk.Label(frame_inputs, text="Longitud:", bg=color_fondo).grid(row=0, column=4, padx=5, pady=10)
    entrada_lon = tk.Entry(frame_inputs, width=12)
    entrada_lon.grid(row=0, column=5, padx=5, pady=10)

    tk.Button(frame_inputs, text="Añadir a la Lista", command=agregar_nuevo,
              bg=color_anadir, font=("Helvetica", 9, "bold")).grid(row=1, column=1, columnspan=2, pady=15)

    tk.Button(frame_inputs, text="Borrar por Código", command=eliminar_existente,
              bg=color_borrar, font=("Helvetica", 9, "bold")).grid(row=1, column=3, columnspan=2, pady=15)


def gestion_arrivals():
    global entrada_id, entrada_orig, entrada_time, entrada_comp

    ventana_vuelos = tk.Toplevel(root)
    ventana_vuelos.title("Gestión de Vuelos (Arrivals)")
    ventana_vuelos.configure(bg=color_fondo)


    frame_guardado = tk.LabelFrame(ventana_vuelos, text=" Gestión de Vuelos ", bg=color_fondo, fg="black")
    frame_guardado.pack(padx=15, pady=15)


    tk.Label(frame_guardado, text="ID Vuelo:", bg=color_fondo).grid(row=0, column=0, padx=5, pady=5)
    entrada_id = tk.Entry(frame_guardado, width=15)
    entrada_id.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_guardado, text="Origen:", bg=color_fondo).grid(row=0, column=2, padx=5, pady=5)
    entrada_orig = tk.Entry(frame_guardado, width=15)
    entrada_orig.grid(row=0, column=3, padx=5, pady=5)


    tk.Label(frame_guardado, text="Hora (H:M):", bg=color_fondo).grid(row=1, column=0, padx=5, pady=5)
    entrada_time = tk.Entry(frame_guardado, width=15)
    entrada_time.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(frame_guardado, text="Compañía:", bg=color_fondo).grid(row=1, column=2, padx=5, pady=5)
    entrada_comp = tk.Entry(frame_guardado, width=15)
    entrada_comp.grid(row=1, column=3, padx=5, pady=5)


    tk.Button(frame_guardado, text="Añadir Vuelo", command=agregar_vuelo_manual,
              bg=color_anadir, fg="black", font=("Helvetica", 9, "bold"), width=20).grid(row=2, column=1, columnspan=2,
                                                                                         pady=10)

    tk.Button(frame_guardado, text="Guardar Vuelos a TXT", command=guardar_vuelos_archivo,
              bg=color_datos, fg="black", font=("Helvetica", 9, "bold"), width=20).grid(row=3, column=1, columnspan=2,
                                                                                        pady=10)

bcn_airport = None

def cargar_estructura_lebl():
    global bcn_airport
    ruta = filedialog.askopenfilename(title="1. Seleccionar Estructura Base (ej. LEBL.txt)",
                                      filetypes=[("Text files", "*.txt")])
    if ruta:
        resultado = LoadAirportStructure(ruta)
        if resultado != -1:
            bcn_airport = resultado
            #messagebox.showinfo("LEBL",f"Estructura de {bcn_airport.code} cargada. Cargue las aerolíneas (T1 y T2).")
        else:
            messagebox.showerror("Error", "No se pudo procesar el archivo de estructura base.")

def cargar_aerolineas_terminal(t_name):
    global bcn_airport
    if not bcn_airport:
        messagebox.showwarning("Aviso", "Primero debes cargar la estructura general del aeropuerto.")
        return

    terminal_obj = next((t for t in bcn_airport.terminals if t.name == t_name), None)
    if not terminal_obj:
        messagebox.showerror("Error", f"La terminal {t_name} no existe en la estructura mapeada.")
        return

    ruta = filedialog.askopenfilename(title=f"Seleccionar aerolíneas para {t_name}",filetypes=[("Text files", "*.txt")])
    if ruta:
        resultado = LoadAirlines(terminal_obj, t_name)
        if resultado == 0:
            print("perfet")
            #messagebox.showinfo("Éxito", f"Fichero de aerolíneas asignado a la {t_name} correctamente.")
        else:
            try:
                with open(ruta, 'r', encoding='utf-8') as file:
                    terminal_obj.airlines = [line.strip().split('\t')[1].strip() for line in file if
                                             line.strip() and len(line.split('\t')) >= 2]
                messagebox.showinfo("Éxito", f"Aerolíneas cargadas manualmente para la {t_name}.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")

def asignar_puertas_vuelos():
    global bcn_airport, vuelos
    if not bcn_airport:
        messagebox.showwarning("Aviso", "Falta cargar la estructura y aerolíneas de LEBL.")
        return
    if not vuelos:
        messagebox.showwarning("Aviso", "No hay vuelos (Arrivals) cargados para asignar puertas.")
        return
    historial_asignaciones = []
    for vuelo in vuelos:
        vuelo.is_schengen = IsSchengenAirport(vuelo.origin)
        resultado = AssignGate(bcn_airport, vuelo)
        historial_asignaciones.append(resultado)
    for widget in frame_grafico.winfo_children():
        widget.destroy()
    txt = tk.Text(frame_grafico, wrap=tk.WORD, font=("Courier", 9), bg="white")
    txt.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    for linea in historial_asignaciones:
        txt.insert(tk.END, str(linea) + "\n")
    txt.config(state=tk.DISABLED)


def ver_ocupacion_puertas():
    global bcn_airport
    if not bcn_airport:
        messagebox.showwarning("Aviso", "No se ha inicializado la estructura de LEBL.")
        return
    lista_ocupacion = GateOccupancy(bcn_airport)
    for widget in frame_grafico.winfo_children():
        widget.destroy()
    barra = tk.Scrollbar(frame_grafico)
    barra.pack(side=tk.RIGHT, fill=tk.Y)
    lista_visual = tk.Listbox(frame_grafico, yscrollcommand=barra.set, font=("Courier", 9), bg="white")
    lista_visual.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    barra.config(command=lista_visual.yview)
    for gate_name, occupied, aircraft_id in lista_ocupacion:
        estado = f"OCUPADA [{aircraft_id}]" if occupied else "LIBRE"
        lista_visual.insert(tk.END, f"Puerta {gate_name:<15}: {estado}")


def renderizar_en_interfaz(funcion_plot, datos):
    for widget in frame_grafico.winfo_children():
        widget.destroy()
    fig = funcion_plot(datos)
    if fig is None:
        tk.Label(frame_grafico, text="No se pudo generar el gráfico o no hay datos.", bg=color_fondo).pack(pady=20)
        return
    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


def mostrar_mapa_interactivo():
    if not mis_aeropuertos or len(mis_aeropuertos) == 0:
        return
    for widget in frame_grafico.winfo_children():
        widget.destroy()

    try:
        map_widget = tkintermapview.TkinterMapView(frame_grafico, corner_radius=0)
        map_widget.pack(fill=tk.BOTH, expand=True)
        map_widget.set_position(40.4167, -3.7037)
        map_widget.set_zoom(4)

        for aeropuerto in mis_aeropuertos:
            estado = "Schengen" if aeropuerto.schengen else "No Schengen"

            map_widget.set_marker(
                aeropuerto.latitud,
                aeropuerto.longitud,
                text=f"{aeropuerto.codigo} ({estado})"
            )
    except Exception as e:
        messagebox.showerror("Error de renderizado", f"Error: {e}")


def mostrar_mapa_rutas(vuelos_a_mapear):
    if not vuelos_a_mapear:
        return
    for widget in frame_grafico.winfo_children():
        widget.destroy()
    try:
        map_widget = tkintermapview.TkinterMapView(frame_grafico, corner_radius=0)
        map_widget.pack(fill=tk.BOTH, expand=True)
        lat_lebl, lon_lebl = 41.297445, 2.0832941
        map_widget.set_position(lat_lebl, lon_lebl)
        map_widget.set_zoom(4)
        lista_aeropuertos = LoadAirports("Airports.txt")

        for flight in vuelos_a_mapear:
            aero = None
            for a in lista_aeropuertos:
                if a.codigo == flight.origin:
                    aero = a
                    break

            if aero:
                color_ruta = "blue" if IsSchengenAirport(flight.origin) else "red"
                map_widget.set_marker(aero.latitud, aero.longitud, text=f"{flight.id} ({flight.origin})")
                map_widget.set_path(
                    [(aero.latitud, aero.longitud), (lat_lebl, lon_lebl)],
                    color=color_ruta,
                    width=2
                )
        map_widget.set_marker(lat_lebl, lon_lebl, text="DESTINO: LEBL (BCN)")

    except Exception as e:
        messagebox.showerror("Error", f"Fallo al renderizar rutas en la interfaz: {e}")


def mostrar_mapa_vuelos_lejanos():
    if not vuelos:
        return

    vuelos_filtrados = LongDistanceArrivals(vuelos)
    if vuelos_filtrados:
        mostrar_mapa_rutas(vuelos_filtrados)
    else:
        messagebox.showinfo("Long Distance", "No hay vuelos a más de 2000 km para mapear.")

def mapa_puntos():
    mostrar_mapa_interactivo()
    MapAirports(mis_aeropuertos)

def mapa_rutas():
    mostrar_mapa_rutas(vuelos)
    crear_kml()

def mapa_lejano():
    mostrar_mapa_vuelos_lejanos()
    mapa_vuelos_lejanos()


def ejecutar_asignacion_nocturna():
    """Llama a la función de pernocta de LEBL y muestra el resultado."""
    global bcn_airport, vuelos
    if not bcn_airport:
        messagebox.showwarning("Aviso", "Falta cargar la estructura de LEBL.")
        return
    if not vuelos:
        messagebox.showwarning("Aviso", "No hay vuelos cargados para evaluar pernoctas.")
        return

    # Ejecutamos la función de LEBL.py
    resultado = AssignNightGates(bcn_airport, vuelos)

    if resultado == 0:
        messagebox.showinfo("Pernoctas", "Asignación de puertas nocturnas completada con éxito.")
        # Refrescamos el visor para ver cómo han quedado las puertas
        ver_ocupacion_puertas()
    else:
        messagebox.showerror("Error", "Hubo un problema al procesar las puertas nocturnas.")


def abrir_ventana_simulacion_hora():
    """Abre una ventana flotante para seleccionar una hora y simular ese instante."""
    global bcn_airport, vuelos
    if not bcn_airport:
        messagebox.showwarning("Aviso", "Primero debes cargar la estructura de LEBL.")
        return

    ventana_hora = tk.Toplevel(root)
    ventana_hora.title("Simular Franja Horaria")
    ventana_hora.geometry("300x150")
    ventana_hora.configure(bg=color_fondo)

    tk.Label(ventana_hora, text="Introduce la hora a simular (HH:00):", bg=color_fondo, font=("Helvetica", 10)).pack(
        pady=10)

    entrada_hora_sim = tk.Entry(ventana_hora, width=10, font=("Courier", 11), justify="center")
    entrada_hora_sim.insert(0, "08:00")  # Hora por defecto
    entrada_hora_sim.pack(pady=5)

    def procesar_hora():
        hora_texto = entrada_hora_sim.get().strip()
        # Validación básica de formato
        if not re.match(r"^\d{2}:\d{2}$", hora_texto):
            messagebox.showerror("Error", "Formato de hora inválido. Usa HH:MM (ej. 14:00)")
            return

        # Ejecuta la lógica de LEBL.py
        vuelos_rechazados = AssignGatesAtTime(bcn_airport, vuelos, hora_texto)

        # Actualizamos el visor de texto de la interfaz para mostrar el estado actual
        ver_ocupacion_puertas()
        messagebox.showinfo("Simulación Horaria", f"Simulación completada para las {hora_texto}.\n"
                                                  f"Aviones rechazados por falta de puerta: {vuelos_rechazados}")
        ventana_hora.destroy()

    tk.Button(ventana_hora, text="Simular", command=procesar_hora, bg=color_datos, font=("Helvetica", 9, "bold")).pack(
        pady=10)


def renderizar_ocupacion_24h():
    global bcn_airport, vuelos
    if not bcn_airport:
        messagebox.showwarning("Aviso", "Requiere tener la estructura de LEBL cargada.")
        return
    if not vuelos:
        messagebox.showwarning("Aviso", "No hay vuelos (Arrivals) para procesar la simulación de 24h.")
        return
    for widget in frame_grafico.winfo_children():
        widget.destroy()
    fig = PlotDayOccupancy(bcn_airport, vuelos)

    if fig is None:
        tk.Label(frame_grafico,
                 text="Error: La simulación no devolvió ningún gráfico.\nVerifica PlotDayOccupancy en LEBL.py",
                 bg=color_fondo, fg="red").pack(pady=20)
        return
    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


def cargar_salidas_archivo():
    """Carga los datos de vuelos de salida (Departures) para la simulación."""
    global vuelos
    if not vuelos:
        messagebox.showwarning("Aviso",
                               "Se recomienda cargar primero los Arrivals para complementar la lista de vuelos.")

    ruta_archivo = filedialog.askopenfilename(title="Seleccionar archivo de salidas (Departures)",
                                              filetypes=[("Text files", "*.txt")])
    if ruta_archivo:
        try:
            vuelos_salida = LoadDepartures(ruta_archivo)

            # Unimos los vuelos de salida a nuestra lista global de control
            vuelos.extend(vuelos_salida)
            messagebox.showinfo("Cargar",
                                f"Vuelos de salida cargados correctamente. Total de vuelos en memoria: {len(vuelos)}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo de salidas: {e}")

root = tk.Tk()
root.title("Panel de Control - Aeropuertos y Vuelos")
root.geometry("1300x650")
root.configure(bg=color_fondo)


root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=6)
for i in range(5):
    root.rowconfigure(i, weight=1)


frame_controles = tk.LabelFrame(root,text="Cargar Archivos", bg=color_fondo)
frame_controles.grid(row=0, column=0, padx=10, pady=1, sticky="nsew")
for i in range (2):
    frame_controles.columnconfigure(i, weight=1)
frame_controles.rowconfigure(0, weight=1)
tk.Button(frame_controles, text="Cargar Airports", command=cargar_archivo, bg=color_principal, fg="black", width=30, font=("Helvetica",8, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
tk.Button(frame_controles, text="Cargar Arrivals", command=cargar_vuelos_archivo, bg=color_principal, fg="black", width=30, font=("Helvetica", 8, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
tk.Button(frame_controles, text="Cargar Departures (Salidas)", command=cargar_salidas_archivo, bg=color_vuelos, fg="black", font=("Helvetica", 8, "bold")).grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

frame_5 = tk.LabelFrame(root,text="Gestionar", bg=color_fondo)
frame_5.grid(row=1, column=0, padx=10, pady=1, sticky="nsew")
for i in range (2):
    frame_5.columnconfigure(i, weight=1)
frame_5.rowconfigure(0, weight=1)

tk.Button(frame_5, text="Gestionar Aeropuertos", command=ventana_gestion_aeropuertos, bg=color_principal, fg="black", width=30, font=("Helvetica", 8, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
tk.Button(frame_5, text="Gestionar Arrivals", command=gestion_arrivals, bg=color_principal, fg="black", width=30, font=("Helvetica", 8, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky="nsew")


frame_2=tk.LabelFrame(root, text="Shengen", bg=color_fondo)
frame_2.grid(row=2, column=0, padx=10, pady=1, sticky="nsew")
for i in range(3):
    frame_2.columnconfigure(i, weight=1)
frame_2.rowconfigure(0, weight=1)
tk.Button(frame_2, text="Evaluar Schengen", command=marcar_schengen, bg=color_principal, fg="black", width=14, font=("Helvetica", 8, "bold")).grid(row=0, column=0, padx=1, pady=5, sticky="nsew")
tk.Button(frame_2, text="Ver Lista completa", command=ver_datos, bg=color_principal, fg="black", width=14, font=("Helvetica", 8, "bold")).grid(row=0, column=1, padx=1, pady=5, sticky="nsew")
tk.Button(frame_2, text="Guardar TXT", command=guardar_txt, bg=color_principal, fg="black", width=14, font=("Helvetica", 8, "bold")).grid(row=0, column=2, padx=1, pady=5, sticky="nsew")


# --- CONFIGURACIÓN DE FRAME_3 MODIFICADA ---
frame_3 = tk.LabelFrame(root, text=" Graficos ", bg=color_fondo)
frame_3.grid(row=3, column=0, padx=10, pady=1, sticky="nsew")

for i in range(2):
    frame_3.columnconfigure(i, weight=1)
for i in range(3):  # Expandido a 3 filas para dar cabida al nuevo gráfico
    frame_3.rowconfigure(i, weight=1)

# Botones originales
tk.Button(frame_3, text="Barras", command=lambda: renderizar_en_interfaz(PlotAirports, mis_aeropuertos), bg=color_principal, fg="black", font=("Helvetica", 8, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
tk.Button(frame_3, text="Hora", command=lambda: renderizar_en_interfaz(PlotArrivals, vuelos), bg=color_principal, fg="black", font=("Helvetica", 8, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
tk.Button(frame_3, text="Vuelos", command=lambda: renderizar_en_interfaz(PlotAirlines, vuelos), bg=color_principal, fg="black", font=("Helvetica", 8, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
tk.Button(frame_3, text="Schengen", command=lambda: renderizar_en_interfaz(PlotFlightsType, vuelos), bg=color_principal, fg="black", font=("Helvetica", 8, "bold")).grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

# NUEVO BOTÓN: Ocupación temporal LEBL
tk.Button(frame_3, text="Evolución Ocupación LEBL (24h)", command=renderizar_ocupacion_24h, bg=color_visual, fg="black", font=("Helvetica", 8, "bold")).grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

frame_4=tk.LabelFrame(root, text="Exportar mapas (Recomendado tener Win con Earth)", bg=color_fondo)
frame_4.grid(row=4, column=0, padx=10, pady=1, sticky="nsew")
for i in range(2):
    frame_4.columnconfigure(i, weight=1)
frame_4.rowconfigure(0, weight=1)
frame_4.rowconfigure(1, weight=1)
tk.Button(frame_4, text="Mapa aeropuertos", command=lambda: mapa_puntos(), bg=color_principal, fg="black", width=15, font=("Helvetica", 8, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
tk.Button(frame_4, text="Mapa rutas", command=lambda: mapa_rutas(), bg=color_principal, fg="black", width=15, font=("Helvetica", 8, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
tk.Button(frame_4, text="Mapa vuelos lejanos", command=lambda: mapa_lejano(), bg=color_principal, fg="black", width=32, font=("Helvetica", 8, "bold")).grid(row=1, column=0, columnspan=2, padx=5, pady=0, sticky="nsew")
tk.Button(frame_4, text="Pestaña de arrivals", command=mostrar_tabla_arribos, bg=color_principal, fg="black", width=22, font=("Helvetica", 10, "bold")).grid(row=6, column=0, padx=10, pady=8)


frame_grafico = tk.LabelFrame(root, text=" Visor de Gráficos ", bg=color_fondo)
frame_grafico.grid(row=0, column=1, rowspan=5,padx=15, pady=15, sticky="nsew")

frame_lebl = tk.LabelFrame(root, text=" Gestión Interna LEBL (Barcelona) ", bg=color_fondo)
frame_lebl.grid(row=5, column=0, padx=10, pady=1, sticky="nsew")

root.rowconfigure(5, weight=1)
frame_grafico.grid(row=0, column=1, rowspan=6, padx=15, pady=15, sticky="nsew")

for i in range(3):
    frame_lebl.columnconfigure(i, weight=1)
for i in range(2):
    frame_lebl.rowconfigure(i, weight=1)

tk.Button(frame_lebl, text="1. Cargar Estructura", command=cargar_estructura_lebl,bg=color_principal, fg="black", font=("Helvetica", 8, "bold")).grid(row=0, column=0, padx=2, pady=3, sticky="nsew")
tk.Button(frame_lebl, text="2. Cargar TxT T1", command=lambda: cargar_aerolineas_terminal("T1"),bg=color_principal, fg="black", font=("Helvetica", 8, "bold")).grid(row=0, column=1, padx=2, pady=3, sticky="nsew")
tk.Button(frame_lebl, text="3. Cargar TxT T2", command=lambda: cargar_aerolineas_terminal("T2"),bg=color_principal, fg="black", font=("Helvetica", 8, "bold")).grid(row=0, column=2, padx=2, pady=3, sticky="nsew")

tk.Button(frame_lebl, text="Asignar Puertas a Arrivals", command=asignar_puertas_vuelos,bg=color_principal, fg="black", font=("Helvetica", 8, "bold")).grid(row=1, column=0, columnspan=2, padx=2, pady=3, sticky="nsew")
tk.Button(frame_lebl, text="Ver Estado Puertas", command=ver_ocupacion_puertas,bg=color_principal, fg="black", font=("Helvetica", 8, "bold")).grid(row=1, column=2, padx=2, pady=3, sticky="nsew")

# --- CONFIGURACIÓN DE FRAME_LEBL MODIFICADA ---
frame_lebl = tk.LabelFrame(root, text=" Gestión Interna LEBL (Barcelona) ", bg=color_fondo)
frame_lebl.grid(row=5, column=0, padx=10, pady=1, sticky="nsew")

for i in range(3):
    frame_lebl.columnconfigure(i, weight=1)
for i in range(3):  # Aumentamos a 3 filas de capacidad
    frame_lebl.rowconfigure(i, weight=1)

# Fila 0: Cargas de archivos
tk.Button(frame_lebl, text="1. Cargar Estructura", command=cargar_estructura_lebl, bg=color_principal, fg="black", font=("Helvetica", 8, "bold")).grid(row=0, column=0, padx=2, pady=3, sticky="nsew")
tk.Button(frame_lebl, text="2. Cargar TxT T1", command=lambda: cargar_aerolineas_terminal("T1"), bg=color_principal, fg="black", font=("Helvetica", 8, "bold")).grid(row=0, column=1, padx=2, pady=3, sticky="nsew")
tk.Button(frame_lebl, text="3. Cargar TxT T2", command=lambda: cargar_aerolineas_terminal("T2"), bg=color_principal, fg="black", font=("Helvetica", 8, "bold")).grid(row=0, column=2, padx=2, pady=3, sticky="nsew")

# Fila 1: Operaciones inmediatas y visor
tk.Button(frame_lebl, text="Asignar Puertas a Arrivals", command=asignar_puertas_vuelos, bg=color_principal, fg="black", font=("Helvetica", 8, "bold")).grid(row=1, column=0, columnspan=2, padx=2, pady=3, sticky="nsew")
tk.Button(frame_lebl, text="Ver Estado Puertas", command=ver_ocupacion_puertas, bg=color_principal, fg="black", font=("Helvetica", 8, "bold")).grid(row=1, column=2, padx=2, pady=3, sticky="nsew")

# Fila 2: NUEVAS FUNCIONES DE LEBL
tk.Button(frame_lebl, text="Asignar Pernoctas (Nocturnos)", command=ejecutar_asignacion_nocturna, bg=color_anadir, fg="black", font=("Helvetica", 8, "bold")).grid(row=2, column=0, columnspan=1, padx=2, pady=3, sticky="nsew")
tk.Button(frame_lebl, text="Simular por Hora Específica", command=abrir_ventana_simulacion_hora, bg=color_anadir, fg="black", font=("Helvetica", 8, "bold")).grid(row=2, column=1, columnspan=2, padx=2, pady=3, sticky="nsew")

import pygame

pygame.mixer.init()
lista_musica=["musica1.mp3","musica2.mp3","musica3.mp3"]
indice_actual = 0
def reproducir_cancion():
    global indice_actual
    try:
        cancion = lista_musica[indice_actual]
        pygame.mixer.music.load(cancion)
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.8)
        texto_contador = f"{indice_actual + 1}/{len(lista_musica)}"
        lbl_contador.config(text=texto_contador)
    except Exception as e:
        messagebox.showerror("Algo salio mal",f"Error al cargar {lista_musica[indice_actual]}: {e}")

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

frame_musica = tk.LabelFrame(root, text=" 🎵 Reproductor de Fondo ", bg=color_fondo, fg="black")
frame_musica.grid(row=6, column=0, columnspan=2, padx=15, pady=10, sticky=tk.W+tk.E)

btn_anterior = tk.Button(frame_musica, text="⏮", command=anterior_cancion, bg="#D5F5E3", width=2)
btn_anterior.grid(row=0, column=0, padx=10, pady=5)

btn_play = tk.Button(frame_musica, text="▶", command=reproducir_cancion, bg="#FCF3CF", width=2)
btn_play.grid(row=0, column=1, padx=10, pady=5)
btn_siguiente = tk.Button(frame_musica, text="⏭", command=siguiente_cancion, bg="#D5F5E3", width=2)
btn_siguiente.grid(row=0, column=2, padx=10, pady=5)
btn_stop=tk.Button(frame_musica, text="⬜", command=parar_cancion, bg="#D5F5E3", width=2)
btn_stop.grid(row=0, column=3, padx=10, pady=5)
lbl_contador=tk.Button(frame_musica, text=f"0/{len(lista_musica)}", bg="#D5F5E3", width=3)
lbl_contador.grid(row=0, column=4, padx=10, pady=5)
root.mainloop()


