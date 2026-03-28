#paso 1
class Airport:
    def __init__(self, codigo, latitud, longitud):
        self.codigo = codigo
        self.latitud = latitud
        self.longitud = longitud
        self.schengen = False


def IsSchengenAirport(codigo):
    if not codigo:
        return False

    prefijos_schengen = ['LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH', 'BI', 'LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS']

    if codigo[0:2] in prefijos_schengen:
        return True
    else:
        return False

def SetSchengen(aeropuerto):
    aeropuerto.schengen = IsSchengenAirport(aeropuerto.codigo)


def PrintAirport(aeropuerto):
    print(f"Código: {aeropuerto.codigo}")
    print(f"Coordenadas: {aeropuerto.latitud}, {aeropuerto.longitud}")
    print(f"Schengen: {aeropuerto.schengen}")
    print("-" * 20)

#paso 3
def LoadAirports(nombre_archivo):
    lista_aeropuertos = []
    try:
        f = open(nombre_archivo, "r")
        lineas = f.readlines()
        f.close()

        for i in range(1, len(lineas)):
            linea = lineas[i]
            partes = linea.split()

            if len(partes) == 3:
                codigo = partes[0]
                lat_texto = partes[1]
                lon_texto = partes[2]

                lat_dir = lat_texto[0]
                lat_grados = float(lat_texto[1:3])
                lat_minutos = float(lat_texto[3:5])
                lat_segundos = float(lat_texto[5:7])

                latitud = lat_grados + (lat_minutos / 60) + (lat_segundos / 3600)
                if lat_dir == 'S':
                    latitud = -latitud

                lon_dir = lon_texto[0]
                lon_grados = float(lon_texto[1:4])
                lon_minutos = float(lon_texto[4:6])
                lon_segundos = float(lon_texto[6:8])

                longitud = lon_grados + (lon_minutos / 60) + (lon_segundos / 3600)
                if lon_dir == 'W':
                    longitud = -longitud

                nuevo_aeropuerto = Airport(codigo, latitud, longitud)
                lista_aeropuertos.append(nuevo_aeropuerto)

        return lista_aeropuertos
    except:
        return []

def FormatCoord(valor, es_latitud):
    if valor < 0:
        valor_positivo = -valor
        if es_latitud:
            direccion = 'S'
        else:
            direccion = 'W'
    else:
        valor_positivo = valor
        if es_latitud:
            direccion = 'N'
        else:
            direccion = 'E'

    grados = int(valor_positivo)
    resto_minutos = (valor_positivo - grados) * 60
    minutos = int(resto_minutos)
    segundos = int((resto_minutos - minutos) * 60)

    if segundos == 60:
        minutos = minutos + 1
        segundos = 0
    if minutos == 60:
        grados = grados + 1
        minutos = 0

    if es_latitud:
        return f"{direccion}{grados:02d}{minutos:02d}{segundos:02d}"
    else:
        return f"{direccion}{grados:03d}{minutos:02d}{segundos:02d}"

def SaveSchengenAirports(lista_aeropuertos, nombre_archivo):
    if len(lista_aeropuertos) == 0:
        return -1

    try:
        f = open(nombre_archivo, "w")
        f.write("CODE LAT LON\n")

        for aeropuerto in lista_aeropuertos:
            if aeropuerto.schengen == True:
                lat_texto = FormatCoord(aeropuerto.latitud, True)
                lon_texto = FormatCoord(aeropuerto.longitud, False)
                f.write(aeropuerto.codigo + " " + lat_texto + " " + lon_texto + "\n")

        f.close()
        return 0
    except:
        return -1

def AddAirport(lista_aeropuertos, nuevo_aeropuerto):
    encontrado = False
    for a in lista_aeropuertos:
        if a.codigo == nuevo_aeropuerto.codigo:
            encontrado = True

    if not encontrado:
        lista_aeropuertos.append(nuevo_aeropuerto)


def RemoveAirport(lista_aeropuertos, codigo_aeropuerto):
    lista_temporal = []
    resultado = -1

    for a in lista_aeropuertos:
        if a.codigo == codigo_aeropuerto:
            resultado = 0
        else:
            lista_temporal.append(a)

    if resultado == 0:
        lista_aeropuertos.clear()
        for a in lista_temporal:
            lista_aeropuertos.append(a)

    return resultado
#paso 5
import matplotlib.pyplot as plt

def PlotAirports(lista_aeropuertos):
    if len(lista_aeropuertos) == 0:
        return

    schengen_count = 0
    no_schengen_count = 0

    for aeropuerto in lista_aeropuertos:
        if aeropuerto.schengen:
            schengen_count = schengen_count + 1
        else:
            no_schengen_count = no_schengen_count + 1

    total_aeropuertos = schengen_count + no_schengen_count

    plt.bar([1], [total_aeropuertos], color='red', label='No Schengen')

    plt.bar([1], [schengen_count], color='blue', label='Schengen')

    plt.ylabel("Airports")
    plt.title("Schengen airports")
    plt.legend()
    plt.show()


def MapAirports(lista_aeropuertos):
    if len(lista_aeropuertos) == 0:
        print("La lista de aeropuertos está vacía.")
        return

    try:
        f = open("mapa_aeropuertos.kml", "w")
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write('<Document>\n')

        f.write('<Style id="schengenStyle">\n<IconStyle>\n<color>ffff0000</color>\n</IconStyle>\n</Style>\n')
        f.write('<Style id="noSchengenStyle">\n<IconStyle>\n<color>ff0000ff</color>\n</IconStyle>\n</Style>\n')

        for aeropuerto in lista_aeropuertos:
            if aeropuerto.schengen:
                estilo = "#schengenStyle"
            else:
                estilo = "#noSchengenStyle"

            f.write('<Placemark>\n')
            f.write(f'<name>{aeropuerto.codigo}</name>\n')
            f.write(f'<styleUrl>{estilo}</styleUrl>\n')
            f.write('<Point>\n')
            f.write(f'<coordinates>{aeropuerto.longitud},{aeropuerto.latitud}</coordinates>\n')
            f.write('</Point>\n')
            f.write('</Placemark>\n')

        f.write('</Document>\n')
        f.write('</kml>\n')
        f.close()
        print("Archivo 'mapa_aeropuertos.kml' generado con éxito.")
    except:
        print("Error al generar el mapa KML.")