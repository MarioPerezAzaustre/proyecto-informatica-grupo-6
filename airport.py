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
def LoadAirports(filename):
    lista_aeropuertos = []
    try:
        f = open(filename, "r")
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
        minutos += 1
        segundos = 0
    if minutos == 60:
        grados += 1
        minutos = 0

    if es_latitud:
        return f"{direccion}{grados:02d}{minutos:02d}{segundos:02d}"
    else:
        return f"{direccion}{grados:03d}{minutos:02d}{segundos:02d}"


def SaveSchengenAirports(airports, filename):
    if len(airports) == 0:
        return -1

    try:
        f = open(filename, "w")
        f.write("CODE LAT LON\n")

        for apt in airports:
            if apt.schengen == True:
                lat_texto = FormatCoord(apt.lat, True)
                lon_texto = FormatCoord(apt.lon, False)
                f.write(apt.code + " " + lat_texto + " " + lon_texto + "\n")

        f.close()
        return 0
    except:
        return -1


def AddAirport(airports, airport):
    encontrado = False
    for a in airports:
        if a.code == airport.code:
            encontrado = True

    if not encontrado:
        airports.append(airport)


def RemoveAirport(airports, code):
    for i in range(len(airports)):
        if airports[i].code == code:
            del airports[i]
            return 0
    return -1