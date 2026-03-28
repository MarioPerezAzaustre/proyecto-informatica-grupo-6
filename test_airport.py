#paso 2
from airport import *

aeropuerto1 = Airport("LEBL", 41.297445, 2.0832941)
SetSchengen(aeropuerto1)
PrintAirport(aeropuerto1)

aeropuerto_paris = Airport("LFPG", 49.009722, 2.547778)
SetSchengen(aeropuerto_paris)
PrintAirport(aeropuerto_paris)

aeropuerto_tokio = Airport("RJTT", 35.552258, 139.779694)
SetSchengen(aeropuerto_tokio)
PrintAirport(aeropuerto_tokio)

aeropuerto_baires = Airport("SAEZ", -34.822222, -58.535833)
SetSchengen(aeropuerto_baires)
PrintAirport(aeropuerto_baires)

#paso 4
lista_aeropuertos = LoadAirports("Airports.txt")
print(f"Se han cargado {len(lista_aeropuertos)} aeropuertos desde el archivo.")

if len(lista_aeropuertos) > 0:
    print("Datos del primer aeropuerto cargado:")
    PrintAirport(lista_aeropuertos[0])


nuevo_aeropuerto = Airport("LEMD", 40.471926, -3.56264)
SetSchengen(nuevo_aeropuerto)
AddAirport(lista_aeropuertos, nuevo_aeropuerto)
print(f"Ahora hay {len(lista_aeropuertos)} aeropuertos tras intentar añadir LEMD.")


resultado_borrar = RemoveAirport(lista_aeropuertos, "KJFK")
if resultado_borrar == 0:
    print("Aeropuerto KJFK borrado exitosamente de la lista.")
else:
    print("No se pudo borrar KJFK (correctamente detectado como no existente en la lista).")


for aeropuerto in lista_aeropuertos:
    SetSchengen(aeropuerto)

resultado_guardar = SaveSchengenAirports(lista_aeropuertos, "SchengenAirports.txt")
if resultado_guardar == 0:
    print("Archivo 'SchengenAirports.txt' creado y guardado exitosamente.")
else:
    print("Error al guardar el archivo o la lista estaba vacía.")