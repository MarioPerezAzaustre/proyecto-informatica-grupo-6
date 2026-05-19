import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from airport import *
from aircraft import *
from LEBL import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

color_fondo = "#EBF5FB"
color_datos = "#A8E6CF"
color_visual = "#FFD3B6"
color_borrar = "#FFAAA5"
color_anadir = "#FFF0B3"
color_vuelos = "#ADD8E6"
color_principal = "#B0BEC5"
mis_aeropuertos = []
vuelos = []

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


def mostrar_mapa():
    MapAirports(mis_aeropuertos)


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


def renderizar_en_interfaz(funcion_grafica, *args):
    for widget in frame_grafico.winfo_children():
        widget.destroy()

    figura = funcion_grafica(*args)
    if figura is None:
        return

    canvas = FigureCanvasTkAgg(figura, master=frame_grafico)
    canvas.draw()
    canvas_widget = canvas.get_tk_widget()

    canvas_widget.pack(fill=tk.BOTH, expand=True)


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
            messagebox.showinfo("LEBL",
                                f"Estructura de {bcn_airport.code} cargada. Procede a cargar las aerolíneas (T1 y T2).")
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

    ruta = filedialog.askopenfilename(title=f"Seleccionar aerolíneas para {t_name}",
                                      filetypes=[("Text files", "*.txt")])
    if ruta:
        resultado = LoadAirlines(terminal_obj, t_name)
        if resultado == 0:
            messagebox.showinfo("Éxito", f"Fichero de aerolíneas asignado a la {t_name} correctamente.")
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


frame_3=tk.LabelFrame(root, text="Graficos", bg=color_fondo)
frame_3.grid(row=3, column=0, padx=10, pady=1, sticky="nsew")
for i in range(2):
    frame_3.columnconfigure(i, weight=1)
for i in range(2):
    frame_3.rowconfigure(i, weight=1)
tk.Button(frame_3, text="Barras", command=lambda: renderizar_en_interfaz(PlotAirports, mis_aeropuertos), bg=color_principal, fg="black", width=15, font=("Helvetica", 8, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
tk.Button(frame_3, text="Hora", command=lambda: renderizar_en_interfaz(PlotArrivals, vuelos), bg=color_principal, fg="black", width=15, font=("Helvetica", 8, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
tk.Button(frame_3, text="Vuelos", command=lambda: renderizar_en_interfaz(PlotAirlines, vuelos), bg=color_principal, fg="black", width=15, font=("Helvetica", 8, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
tk.Button(frame_3, text="Schengen", command=lambda: renderizar_en_interfaz(PlotFlightsType, vuelos), bg=color_principal, fg="black", width=15, font=("Helvetica", 8, "bold")).grid(row=1, column=1, padx=5, pady=5, sticky="nsew")


frame_4=tk.LabelFrame(root, text="Exportar mapas (Recomendado tener Win con Earth)", bg=color_fondo)
frame_4.grid(row=4, column=0, padx=10, pady=1, sticky="nsew")
for i in range(2):
    frame_4.columnconfigure(i, weight=1)
frame_4.rowconfigure(0, weight=1)
frame_4.rowconfigure(1, weight=1)
tk.Button(frame_4, text="Mapa aeropuertos", command=mostrar_mapa, bg=color_principal, fg="black", width=15, font=("Helvetica", 8, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
tk.Button(frame_4, text="Mapa rutas", command=crear_kml, bg=color_principal, fg="black", width=15, font=("Helvetica", 8, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
tk.Button(frame_4, text="Mapa vuelos lejanos", command=mapa_vuelos_lejanos, bg=color_principal, fg="black", width=32, font=("Helvetica", 8, "bold")).grid(row=1, column=0, columnspan=2, padx=5, pady=0, sticky="nsew")



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
root.mainloop()