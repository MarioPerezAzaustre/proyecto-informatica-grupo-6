import tkinter as tk
from tkinter import messagebox
from airport import *

color_fondo = "#EBF5FB"
color_datos = "#A8E6CF"
color_visual = "#FFD3B6"
color_borrar = "#FFAAA5"
color_anadir = "#FFF0B3"

mis_aeropuertos = []


def cargar_archivo():
    datos_temporales = LoadAirports("Airports.txt")

    mis_aeropuertos.clear()

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

    texto_total = ""
    for apt in mis_aeropuertos:
        if apt.schengen:
            estado = "Schengen"
        else:
            estado = "No Schengen"
        texto_total += f"{apt.codigo}: {apt.latitud:.2f}, {apt.longitud:.2f} ({estado})\n"

    messagebox.showinfo("Lista de Aeropuertos", texto_total)


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


root = tk.Tk()
root.title("Panel de Control - Aeropuertos")
root.geometry("650x450")
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

tk.Button(frame_inputs, text="Anadir a la Lista", command=agregar_nuevo, bg=color_anadir, fg="black",  font=("Helvetica", 9, "bold")).grid(row=1, column=1, columnspan=2, padx=10, pady=10)
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

root.mainloop()