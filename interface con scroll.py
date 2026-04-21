import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from airport import *
from aircraft import *

color_fondo = "#EBF5FB"
color_datos = "#A8E6CF"
color_visual = "#FFD3B6"
color_borrar = "#FFAAA5"
color_anadir = "#FFF0B3"
color_vuelos = "#ADD8E6"

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

    ventana_lista = tk.Toplevel(root)
    ventana_lista.title("Lista de Aeropuertos")
    ventana_lista.geometry("400x300")
    ventana_lista.configure(bg=color_fondo)

    barra_scroll = tk.Scrollbar(ventana_lista, bg=color_fondo)
    barra_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    lista_visual = tk.Listbox(ventana_lista, yscrollcommand=barra_scroll.set, font=("Courier", 10), bg="white", fg="black")
    for apt in mis_aeropuertos:
        if apt.schengen:
            estado = "Schengen"
        else:
            estado = "No Schengen"
        lista_visual.insert(tk.END, f"{apt.codigo}: {apt.latitud:.2f}, {apt.longitud:.2f} ({estado})")

    lista_visual.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    barra_scroll.config(command=lista_visual.yview)

def guardar_txt():
    resultado = SaveSchengenAirports(mis_aeropuertos, "SchengenAirports.txt")
    if resultado == 0:
        messagebox.showinfo("Guardar", "Archivo SchengenAirports.txt generado con exito.")
    else:
        messagebox.showerror("Error", "No se pudo guardar.")

def mostrar_grafica():
    PlotAirports(mis_aeropuertos)

def mostrar_mapa():
    MapAirports(mis_aeropuertos)
    messagebox.showinfo("KML", "Archivo KML generado. Abrelo en Google Earth.")

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


root = tk.Tk()
root.title("Panel de Control - Aeropuertos y Vuelos")
root.geometry("750x650")
root.configure(bg=color_fondo)

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

frame_inputs = tk.LabelFrame(root, text=" 1. Anadir / Borrar Aeropuertos ", bg=color_fondo, fg="black")
frame_inputs.grid(row=0, column=0, columnspan=2, padx=15, pady=15)

tk.Label(frame_inputs, text="Codigo:", bg=color_fondo, fg="black").grid(row=0, column=0, padx=5, pady=10)
entrada_codigo = tk.Entry(frame_inputs, width=12, bg="white", fg="black")
entrada_codigo.grid(row=0, column=1, padx=5, pady=10)

tk.Label(frame_inputs, text="Latitud:", bg=color_fondo, fg="black").grid(row=0, column=2, padx=5, pady=10)
entrada_lat = tk.Entry(frame_inputs, width=12, bg="white", fg="black")
entrada_lat.grid(row=0, column=3, padx=5, pady=10)

tk.Label(frame_inputs, text="Longitud:", bg=color_fondo, fg="black").grid(row=0, column=4, padx=5, pady=10)
entrada_lon = tk.Entry(frame_inputs, width=12, bg="white", fg="black")
entrada_lon.grid(row=0, column=5, padx=5, pady=10)

tk.Button(frame_inputs, text="Anadir a la Lista", command=agregar_nuevo, bg=color_anadir, fg="black", font=("Helvetica", 9, "bold")).grid(row=1, column=1, columnspan=2, padx=10, pady=10)
tk.Button(frame_inputs, text="Borrar por Codigo", command=eliminar_existente, bg=color_borrar, fg="black", font=("Helvetica", 9, "bold")).grid(row=1, column=3, columnspan=2, padx=10, pady=10)

frame_datos = tk.LabelFrame(root, text=" 2. Gestion de Datos ", bg=color_fondo, fg="black")
frame_datos.grid(row=1, column=0, padx=15, pady=5)

tk.Button(frame_datos, text="Cargar TXT", command=cargar_archivo, bg=color_datos, fg="black", width=22, font=("Helvetica", 10, "bold")).grid(row=0, column=0, padx=10, pady=8)
tk.Button(frame_datos, text="Evaluar Schengen", command=marcar_schengen, bg=color_datos, fg="black", width=22, font=("Helvetica", 10, "bold")).grid(row=1, column=0, padx=10, pady=8)
tk.Button(frame_datos, text="Ver Lista (Ventana)", command=ver_datos, bg=color_datos, fg="black", width=22, font=("Helvetica", 10, "bold")).grid(row=2, column=0, padx=10, pady=8)
tk.Button(frame_datos, text="Guardar Schengen", command=guardar_txt, bg=color_datos, fg="black", width=22, font=("Helvetica", 10, "bold")).grid(row=3, column=0, padx=10, pady=8)

frame_visual = tk.LabelFrame(root, text=" 3. Graficos y Mapas ", bg=color_fondo, fg="black")
frame_visual.grid(row=1, column=1, padx=15, pady=5, sticky=tk.N)

tk.Button(frame_visual, text="Ver Grafica de Barras", command=mostrar_grafica, bg=color_visual, fg="black", width=22, font=("Helvetica", 10, "bold")).grid(row=0, column=0, padx=10, pady=8)
tk.Button(frame_visual, text="Generar Mapa KML", command=mostrar_mapa, bg=color_visual, fg="black", width=22, font=("Helvetica", 10, "bold")).grid(row=1, column=0, padx=10, pady=8)

frame_vuelos = tk.LabelFrame(root, text=" 4. Vuelos planeados ", bg=color_fondo, fg="black")
frame_vuelos.grid(row=2, column=0, padx=15, pady=15, sticky=tk.N)

tk.Button(frame_vuelos, text="Cargar Archivo Vuelos", command=cargar_vuelos_archivo, bg=color_vuelos, fg="black", width=22, font=("Helvetica", 10, "bold")).grid(row=0, column=0, padx=10, pady=8)
tk.Button(frame_vuelos, text="Ver Gráfica de Horas", command=lambda: PlotArrivals(vuelos), bg=color_vuelos, fg="black", width=22, font=("Helvetica", 10, "bold")).grid(row=1, column=0, padx=10, pady=8)
tk.Button(frame_vuelos, text="Ver Vuelos por Aerolínea", command=lambda: PlotAirlines(vuelos), bg=color_vuelos, fg="black", width=22, font=("Helvetica", 10, "bold")).grid(row=2, column=0, padx=10, pady=8)
tk.Button(frame_vuelos, text="Distribución Schengen", command=lambda: PlotFlightsType(vuelos), bg=color_vuelos, fg="black", width=22, font=("Helvetica", 10, "bold")).grid(row=3, column=0, padx=10, pady=8)
tk.Button(frame_vuelos, text="Generar Mapa KML", command=crear_kml, bg=color_vuelos, fg="black", width=22, font=("Helvetica", 10, "bold")).grid(row=4, column=0, padx=10, pady=8)
tk.Button(frame_vuelos, text="Mapa Vuelos Lejanos", command=mapa_vuelos_lejanos, bg=color_vuelos, fg="black", width=22, font=("Helvetica", 10, "bold")).grid(row=5, column=0, padx=10, pady=8)

frame_guardado = tk.LabelFrame(root, text=" 5. Guardar vuelos ", bg=color_fondo, fg="black")
frame_guardado.grid(row=2, column=1, columnspan=2, padx=15, pady=15, sticky=tk.N)

tk.Label(frame_guardado, text="ID Vuelo:", bg=color_fondo, fg="black").grid(row=0, column=0, padx=5, pady=5)
entrada_id = tk.Entry(frame_guardado, width=10)
entrada_id.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_guardado, text="Origen:", bg=color_fondo, fg="black").grid(row=0, column=2, padx=5, pady=5)
entrada_orig = tk.Entry(frame_guardado, width=10)
entrada_orig.grid(row=0, column=3, padx=5, pady=5)

tk.Label(frame_guardado, text="Hora (H:M):", bg=color_fondo, fg="black").grid(row=1, column=0, padx=5, pady=5)
entrada_time = tk.Entry(frame_guardado, width=10)
entrada_time.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_guardado, text="Compañía:", bg=color_fondo, fg="black").grid(row=1, column=2, padx=5, pady=5)
entrada_comp = tk.Entry(frame_guardado, width=10)
entrada_comp.grid(row=1, column=3, padx=5, pady=5)

tk.Button(frame_guardado, text="Añadir Vuelo", command=agregar_vuelo_manual, bg=color_anadir, fg="black", font=("Helvetica", 9, "bold")).grid(row=2, column=1, columnspan=2, pady=10)
tk.Button(frame_guardado, text="Guardar Vuelos a TXT", command=guardar_vuelos_archivo, bg=color_datos, fg="black", font=("Helvetica", 9, "bold")).grid(row=3, column=1, columnspan=2, pady=10)

root.mainloop()

#Las funciones "Toplevel", "Listbox" y "Scrollbar" son de fuentes externas para crear la ventana emergente ya que si no los aeropuertos no cabian en la pantalla