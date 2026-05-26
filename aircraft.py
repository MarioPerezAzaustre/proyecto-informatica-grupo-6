import math
import matplotlib.pyplot as plt
import airport
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from matplotlib.figure import Figure
import os

class Aircraft:
    def __init__(self, id, company, origin, time, destination, departure):
        self.id = id
        self.company = company
        self.origin = origin
        self.time = time
        self.destination = destination
        self.departure = departure

def time_to_mins(t_str):
    if not t_str:
        return -1
    partes = t_str.split(':')
    return int(partes[0]) * 60 + int(partes[1])

def LoadDepartures(filename):

    if not os.path.exists(filename):
        return [], -1

    departures_list = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lineas = f.readlines()

            for linea in lineas[1:]:
                linea = linea.strip()
                if linea:
                    partes = linea.split()
                    if len(partes) >= 4:
                        a_id = partes[0]
                        dest = partes[1]
                        dep_time = partes[2]
                        company = partes[3]

                        ac = Aircraft(aircraft_id=a_id, company=company, origin="",
                                      arrival_time="", destination=dest, departure_time=dep_time)
                        departures_list.append(ac)
        return departures_list, 0
    except Exception as e:
        print(f"Error leyendo salidas: {e}")
        return [], -1


def MergeMovements(arrivals, departures):

    if not arrivals or not departures:
        return -1

    merged_list = []
    used_departures = set()

    for arr in arrivals:
        mejor_indice_salida = -1
        mejor_tiempo_salida = 999999
        minutos_llegada = time_to_mins(arr.time)

        for i, dep in enumerate(departures):
            if i in used_departures:
                continue

            if arr.id == dep.id:
                minutos_salida = time_to_mins(dep.departure)

                if minutos_llegada < minutos_salida < mejor_tiempo_salida:
                    mejor_tiempo_salida = minutos_salida
                    mejor_indice_salida = i

        if mejor_indice_salida != -1:
            dep_elegida = departures[mejor_indice_salida]
            avion_fusionado = Aircraft(arr.id, arr.company, arr.origin, arr.time,
                                       dep_elegida.destination, dep_elegida.departure)
            merged_list.append(avion_fusionado)
            used_departures.add(mejor_indice_salida)
        else:
            merged_list.append(arr)

    for i, dep in enumerate(departures):
        if i not in used_departures:
            merged_list.append(dep)

    return merged_list

def NightAircraft(aircrafts):

    if not aircrafts:
        return -1

    night_list = []
    for ac in aircrafts:
        if ac.departure and not ac.time:
            night_list.append(ac)

    return night_list

def LoadArrivals(filename):
    arrivals = []
    try:
        archivo = open(filename, 'r')
        filas = archivo.readlines()
        archivo.close()

        if len(filas) > 1:
            for index in range(1, len(filas)):
                linea = filas[index]
                parts = linea.split()
                if len(parts) >= 4 and ':' in parts[2]:
                    new_avion = Aircraft(parts[0], parts[3], parts[1], parts[2])
                    arrivals.append(new_avion)
        return arrivals
    except:
        return []


def SaveFlights(aircrafts, filename):
    if len(aircrafts) == 0:
        return -1
    try:
        f = open(filename, 'w')
        f.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")
        for ac in aircrafts:
            id_v = ac.id if ac.id != "" else "''"
            orig = ac.origin if ac.origin != "" else "''"
            time = ac.time if ac.time != "" else "0"
            comp = ac.company if ac.company != "" else "''"

            f.write(id_v + " " + orig + " " + time + " " + comp + "\n")
        f.close()
        return 0
    except:
        return -1


def PlotArrivals(aircrafts):
    if len(aircrafts) == 0:
        messagebox.showwarning("Error en la lista","Estas seguro que es esta lista?")
        return
    horas = [0] * 24
    for ac in aircrafts:
        try:
            h = int(ac.time.split(':')[0])
            if 0 <= h < 24:
                horas[h] = horas[h] + 1
        except:
            continue
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)

    ax.bar(range(24), horas)
    ax.set_xlabel("Hora del día")
    ax.set_ylabel("Número de aterrizajes")
    ax.set_title("Frecuencia de aterrizajes en LEBL")
    return fig


def PlotAirlines(aircrafts):
    if not aircrafts:
        return None

    conteo = {}
    for ac in aircrafts:
        cia = ac.company
        conteo[cia] = conteo.get(cia, 0) + 1
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.bar(conteo.keys(), conteo.values(), color='orange', edgecolor='black')
    ax.set_title("Vuelos por Aerolínea")
    ax.tick_params(axis='x', rotation=45, labelsize=8)
    fig.tight_layout()
    return fig

def PlotFlightsType(aircrafts):
    if len(aircrafts) == 0:
        messagebox.showwarning("Error en la lista","Estas seguro que es esta lista?")
        return
    schengen_count = 0
    no_schengen_count = 0
    for flight in aircrafts:
        if airport.IsSchengenAirport(flight.origin):
            schengen_count += 1
        else:
            no_schengen_count += 1
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.bar(["Arrivals"], [schengen_count], color='blue', label='Schengen', width=0.5)
    ax.bar(["Arrivals"], [no_schengen_count], bottom=[schengen_count], color='red', label='No Schengen', width=0.5)
    ax.set_title("Distribución Schengen / No Schengen")
    return fig


def Haversine(lat1, lon1, lat2, lon2):
    r = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def LongDistanceArrivals(aircrafts):
    if len(aircrafts) == 0:
        return []

    lista_aeropuertos = airport.LoadAirports("Airports.txt")

    vuelos_lejanos = []
    lat_lebl = 41.297445
    lon_lebl = 2.0832941

    for flight in aircrafts:
        aero_origen = None
        for a in lista_aeropuertos:
            if a.codigo == flight.origin:
                aero_origen = a
                break
        if aero_origen:
            distancia = Haversine(aero_origen.latitud, aero_origen.longitud, lat_lebl, lon_lebl)
            if distancia > 2000:
                vuelos_lejanos.append(flight)
    return vuelos_lejanos


def MapFlights(aircrafts):
    if len(aircrafts) == 0:
        messagebox.showerror("Error: La lista de vuelos está vacía. No se generará el mapa.")
        return

    lista_aeropuertos = airport.LoadAirports("Airports.txt")

    try:
        f = open("Rutas_Barcelona.kml", "w", encoding="utf-8")
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n')
        f.write(
            '<Style id="rutaSchengen"><LineStyle><color>ff0000ff</color><width>2</width></LineStyle></Style>\n')  # Rojo
        f.write(
            '<Style id="rutaNoSchengen"><LineStyle><color>ffff0000</color><width>2</width></LineStyle></Style>\n')  # Azul

        for flight in aircrafts:
            aero = None
            for a in lista_aeropuertos:
                if a.codigo == flight.origin:
                    aero = a
                    break
            if aero:
                estilo = "#rutaSchengen" if airport.IsSchengenAirport(flight.origin) else "#rutaNoSchengen"
                f.write('<Placemark>\n<name>' + str(flight.id) + '</name>\n')
                f.write('<styleUrl>' + estilo + '</styleUrl>\n')
                f.write('<LineString><tessellate>1</tessellate><coordinates>\n')
                f.write(str(aero.longitud) + ',' + str(aero.latitud) + '\n')
                f.write('2.0832941,41.297445\n')
                f.write('</coordinates></LineString>\n</Placemark>\n')
        f.write('</Document>\n</kml>\n')
        f.close()
        os.startfile('Rutas_Barcelona.kml')

    except Exception as e:
        messagebox.showerror("Error", f"no se ha podido crear, error: {e}")


if __name__ == "__main__":
    plt.style.use('default')
    vuelos = LoadArrivals("arrivals.txt")
    if len(vuelos) > 0:
        PlotArrivals(vuelos)
        PlotAirlines(vuelos)
        PlotFlightsType(vuelos)
        MapFlights(vuelos)
        lejanos = LongDistanceArrivals(vuelos)
        print("Vuelos lejanos para inspección especial:", len(lejanos))

