#Paso 2
from Airport import *

airport = Airport("LEBL", 41.297445, 2.0832941)
SetSchengen(airport)
PrintAirport(airport)
print("-" * 20)

airport2 = Airport("KJFK", 40.639722, -73.778889)
SetSchengen(airport2)
PrintAirport(airport2)
