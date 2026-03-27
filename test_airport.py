#paso 2
from airport import *

airport = Airport("LEBL", 41.297445, 2.0832941)
SetSchengen(airport)
PrintAirport(airport)
print("-" * 20)

airport2 = Airport("KJFK", 40.639722, -73.778889)
SetSchengen(airport2)
PrintAirport(airport2)
print("-" * 20)


#paso 4
lista_aeropuertos = LoadAirports("Airports.txt")
print("Se han cargado", len(lista_aeropuertos), "aeropuertos.")

if len(lista_aeropuertos) > 0:
    print("Datos del primer aeropuerto cargado:")
    PrintAirport(lista_aeropuertos[0])


nuevo_aeropuerto = Airport("LEMD", 40.471926, -3.56264)
SetSchengen(nuevo_aeropuerto)
AddAirport(lista_aeropuertos, nuevo_aeropuerto)
print("Ahora hay", len(lista_aeropuertos), "aeropuertos tras añadir LEMD.")


resultado_borrar = RemoveAirport(lista_aeropuertos, "KJFK")
if resultado_borrar == 0:
    print("Aeropuerto KJFK borrado exitosamente de la lista.")
else:
    print("No se pudo borrar KJFK (probablemente no estaba en el archivo).")


for apt in lista_aeropuertos:
    SetSchengen(apt)

resultado_guardar = SaveSchengenAirports(lista_aeropuertos, "SchengenAirports.txt")
if resultado_guardar == 0:
    print("Archivo SchengenAirports.txt creado y guardado exitosamente.")
else:
    print("Error al guardar el archivo.")