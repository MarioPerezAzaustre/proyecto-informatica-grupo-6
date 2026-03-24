#paso 1
class Airport:
   def __init__(self, code, lat, lon):
       self.code = code
       self.lat = lat
       self.lon = lon
       self.schengen = False

def IsSchengenAirport(code):
    schengen_prefixes = ['LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH', 'BI', 'LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE','ES', 'LS' ]
    if code[0:2] in schengen_prefixes:
        return True
    else:
        return False

def SetSchengen(airport):
   airport.schengen = IsSchengenAirport(airport.code)

def PrintAirport(airport):
   print(f"Código: {airport.code}")
   print(f"Coordenadas: {airport.lat}, {airport.lon}")
   print(f"Schengen: {airport.schengen}")
   print("-" * 20)

#paso 3
def convertir_a_decimal(coor):
   hemisferio = coor[0]
   segundos = float(coor[-2:])
   minutos = float(coor[-4:-2])
   grados = float(coor[1:-4])
   decimal = grados + (minutos / 60) + (segundos / 3600)
   if hemisferio == 'S' or hemisferio == 'W':
       decimal = -decimal
   return decimal

def SaveSchengenAirports(airports, filename):
   if not airports:
       return "error_lista_vacia"
   try:
       with open(filename, 'w') as f:
           f.write("CODE LAT LON\n")

           for airport in airports:
               if airport.schengen:
                   f.write(f"{airport.code} {airport.lat_org} {airport.lon_org}\n")
       return "exito"
   except Exception as e:
       return "error_escritura"

def LoadAirports(filename):
   lista_aeropuertos = []
   try:
       f = open(filename, 'r')
       lineas = f.readlines()
       f.close()
       for linea in lineas[1:]:
           partes = linea.split()
           if len(partes) > 0:
               codigo = partes[0]
               lat_org = partes[1]
               lon_org = partes[2]
               lat_dec = convertir_a_decimal(lat_org)
               lon_dec = convertir_a_decimal(lon_org)
               nuevo_aeropuerto = Airport(codigo, lat_dec, lon_dec)
               nuevo_aeropuerto.lat_org = lat_org
               nuevo_aeropuerto.lon_org = lon_org
               lista_aeropuertos.append(nuevo_aeropuerto)
       return lista_aeropuertos
   except:
       return []

def AddAirport(airports, airport):
   ya_existe = False
   i = 0
   while i < len(airports) and ya_existe == False: