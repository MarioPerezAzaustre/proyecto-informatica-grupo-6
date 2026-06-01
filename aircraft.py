import math
import os
from matplotlib.figure import Figure
import airport

class Aircraft:
    def __init__(self, id, company, origin="", time="", destination="", departure=""):
        self.id = id
        self.company = company
        self.origin = origin
        self.time = time
        self.destination = destination
        self.departure = departure

def tiempo_a_minutos(t_str):
    if not t_str:
        return -1
    partes = t_str.split(':')
    return int(partes[0]) * 60 + int(partes[1])

def LoadDepartures(nombre_archivo):
    if not os.path.exists(nombre_archivo):
        return [], -1

    lista_salidas = []
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as f:
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

                        ac = Aircraft(id=a_id, company=company, destination=dest, departure=dep_time)
                        lista_salidas.append(ac)
        return lista_salidas, 0
    except Exception:
        return [], -1

def MergeMovements(llegadas, salidas):
    if not llegadas or not salidas:
        return -1

    lista_fusionada = []
    salidas_usadas = set()

    for arr in llegadas:
        mejor_indice_salida = -1
        mejor_tiempo_salida = 999999
        minutos_llegada = tiempo_a_minutos(arr.time)

        for i, dep in enumerate(salidas):
            if i in salidas_usadas:
                continue

            if arr.id == dep.id:
                minutos_salida = tiempo_a_minutos(dep.departure)

                if minutos_llegada < minutos_salida < mejor_tiempo_salida:
                    mejor_tiempo_salida = minutos_salida
                    mejor_indice_salida = i

        if mejor_indice_salida != -1:
            dep_elegida = salidas[mejor_indice_salida]
            avion_fusionado = Aircraft(id=arr.id, company=arr.company, origin=arr.origin, time=arr.time,
                                       destination=dep_elegida.destination, departure=dep_elegida.departure)
            lista_fusionada.append(avion_fusionado)
            salidas_usadas.add(mejor_indice_salida)
        else:
            lista_fusionada.append(arr)

    for i, dep in enumerate(salidas):
        if i not in salidas_usadas:
            lista_fusionada.append(dep)

    return lista_fusionada

def NightAircraft(vuelos):
    if not vuelos:
        return -1

    lista_nocturnos = []
    for ac in vuelos:
        if ac.departure and not ac.time:
            lista_nocturnos.append(ac)

    return lista_nocturnos

def LoadArrivals(nombre_archivo):
    llegadas = []
    try:
        archivo = open(nombre_archivo, 'r')
        filas = archivo.readlines()
        archivo.close()

        if len(filas) > 1:
            for index in range(1, len(filas)):
                linea = filas[index]
                partes = linea.split()
                if len(partes) >= 4 and ':' in partes[2]:
                    nuevo_avion = Aircraft(id=partes[0], company=partes[3], origin=partes[1], time=partes[2])
                    llegadas.append(nuevo_avion)
        return llegadas
    except:
        return []

def SaveFlights(vuelos, nombre_archivo):
    if len(vuelos) == 0:
        return -1
    try:
        f = open(nombre_archivo, 'w')
        f.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")
        for ac in vuelos:
            id_v = ac.id if ac.id != "" else "''"
            orig = ac.origin if ac.origin != "" else "''"
            time = ac.time if ac.time != "" else "0"
            comp = ac.company if ac.company != "" else "''"

            f.write(id_v + " " + orig + " " + time + " " + comp + "\n")
        f.close()
        return 0
    except:
        return -1

def PlotArrivals(vuelos):
    if len(vuelos) == 0:
        return None
    horas = [0] * 24
    for ac in vuelos:
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

def PlotAirlines(vuelos):
    if not vuelos:
        return None

    conteo = {}
    for ac in vuelos:
        cia = ac.company
        conteo[cia] = conteo.get(cia, 0) + 1
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.bar(conteo.keys(), conteo.values(), color='orange', edgecolor='black')
    ax.set_title("Vuelos por Aerolínea")
    ax.tick_params(axis='x', rotation=45, labelsize=8)
    fig.tight_layout()
    return fig

def PlotFlightsType(vuelos):
    if len(vuelos) == 0:
        return None
    schengen_count = 0
    no_schengen_count = 0
    for flight in vuelos:
        if airport.IsSchengenAirport(flight.origin):
            schengen_count += 1
        else:
            no_schengen_count += 1
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.bar(["Arrivals"], [schengen_count], color='#4682B4', label='Schengen', width=0.5)
    ax.bar(["Arrivals"], [no_schengen_count], bottom=[schengen_count], color='#F08080', label='No Schengen', width=0.5)
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

def LongDistanceArrivals(vuelos):
    if len(vuelos) == 0:
        return []

    lista_aeropuertos = airport.LoadAirports("Airports.txt")

    vuelos_lejanos = []
    lat_lebl = 41.297445
    lon_lebl = 2.0832941

    for flight in vuelos:
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

def MapFlights(vuelos):
    if len(vuelos) == 0:
        return -1

    lista_aeropuertos = airport.LoadAirports("Airports.txt")

    try:
        f = open("Rutas_Barcelona.kml", "w", encoding="utf-8")
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n')
        f.write('<Style id="rutaSchengen"><LineStyle><color>ff0000ff</color><width>2</width></LineStyle></Style>\n')
        f.write('<Style id="rutaNoSchengen"><LineStyle><color>ffff0000</color><width>2</width></LineStyle></Style>\n')

        for flight in vuelos:
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
        return 0

    except Exception:
        return -1

if __name__ == "__main__":
    vuelos = LoadArrivals("arrivals.txt")
    if len(vuelos) > 0:
        PlotArrivals(vuelos)
        PlotAirlines(vuelos)
        PlotFlightsType(vuelos)
        MapFlights(vuelos)
        lejanos = LongDistanceArrivals(vuelos)
        print("Vuelos lejanos para inspección especial:", len(lejanos))
