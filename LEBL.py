import os
import re
from matplotlib.figure import Figure
import airport


class Gate:
    def __init__(self, nombre):
        self.name = nombre
        self.occupied = False
        self.aircraft_id = None


class BoardingArea:
    def __init__(self, nombre, tipo_area):
        self.name = nombre
        self.type = tipo_area
        self.gates = []


class Terminal:
    def __init__(self, nombre):
        self.name = nombre
        self.boarding_areas = []
        self.airlines = []


class BarcelonaAP:
    def __init__(self, codigo):
        self.code = codigo
        self.terminals = []


def SetGates(area, puerta_inicio, puerta_fin, prefijo):
    if puerta_fin <= puerta_inicio:
        return -1
    area.gates = []
    for i in range(puerta_inicio, puerta_fin + 1):
        area.gates.append(Gate(f"{prefijo}{i}"))
    return 0


def LoadAirlines(terminal, nombre_t):
    archivo_nombre = f"{nombre_t}_Airlines.txt"
    if not os.path.exists(archivo_nombre):
        return -1
    try:
        with open(archivo_nombre, 'r', encoding='utf-8') as archivo:
            terminal.airlines = []
            for linea in archivo:
                linea = linea.strip()
                if linea:
                    partes = linea.split('\t')
                    if len(partes) >= 2:
                        terminal.airlines.append(partes[1].strip())
        return 0
    except IOError:
        return -1


def LoadAirportStructure(filename):
    if not os.path.exists(filename):
        return -1
    try:
        with open(filename, 'r', encoding='utf-8') as archivo:
            lineas = [linea.strip() for linea in archivo if linea.strip()]

            if not lineas:
                return -1

            primera_linea = lineas[0].split()
            bcn = BarcelonaAP(primera_linea[0])
            num_terminales = int(primera_linea[1])

            indice = 1
            for _ in range(num_terminales):
                linea_t = lineas[indice].split()
                nombre_t = linea_t[1]
                num_areas = int(linea_t[2])

                terminal = Terminal(nombre_t)
                bcn.terminals.append(terminal)
                LoadAirlines(terminal, nombre_t)

                indice += 1
                for _ in range(num_areas):
                    linea_a = lineas[indice].split()
                    nombre_a = linea_a[1]
                    tipo_a = linea_a[2]

                    numeros = re.findall(r'\d+', ' '.join(linea_a[3:]))
                    puerta_inicio = int(numeros[0]) if len(numeros) >= 1 else 0
                    puerta_fin = int(numeros[1]) if len(numeros) >= 2 else 0

                    area = BoardingArea(nombre_a, tipo_a)
                    terminal.boarding_areas.append(area)

                    prefijo = f"{nombre_t}BA{nombre_a}G"
                    SetGates(area, puerta_inicio, puerta_fin, prefijo)

                    indice += 1

            return bcn
    except Exception:
        return -1


def GateOccupancy(bcn):
    lista_ocupacion = []
    for terminal in bcn.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                lista_ocupacion.append([gate.name, gate.occupied, gate.aircraft_id])
    return lista_ocupacion


def IsAirlineInTerminal(terminal, nombre):
    if not nombre:
        return False, -1
    if not terminal.airlines:
        return False
    if nombre in terminal.airlines:
        return True
    else:
        return False


def SearchTerminal(bcn, nombre):
    for terminal in bcn.terminals:
        resultado = IsAirlineInTerminal(terminal, nombre)
        if isinstance(resultado, tuple):
            if resultado[0]:
                return terminal.name
        else:
            if resultado:
                return terminal.name
    return ""


def AssignGate(bcn, aircraft):
    nombre_t = SearchTerminal(bcn, aircraft.company)

    if not nombre_t:
        return -1

    terminal = next((t for t in bcn.terminals if t.name == nombre_t), None)
    if not terminal:
        return -1

    es_schengen = airport.IsSchengenAirport(aircraft.origin)
    tipo_requerido = "Schengen" if es_schengen else "non-Schengen"

    for area in terminal.boarding_areas:
        if area.type == tipo_requerido:
            for gate in area.gates:
                if not gate.occupied:
                    gate.occupied = True
                    gate.aircraft_id = aircraft.id
                    return 0

    return -1


def AssignNightGates(bcn, aircrafts):
    if not aircrafts:
        return -1

    for aircraft in aircrafts:
        if not aircraft.time and aircraft.departure:
            AssignGate(bcn, aircraft)

    return 0


def FreeGate(bcn, id):
    for terminal in bcn.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                if gate.occupied and gate.aircraft_id == id:
                    gate.occupied = False
                    gate.aircraft_id = None
                    return 0

    return -1


def AssignGatesAtTime(bcn, aircrafts, hora):
    no_asignados = 0
    hora_prefijo = hora.split(':')[0]

    for aircraft in aircrafts:
        if aircraft.departure:
            if aircraft.departure.split(':')[0] <= hora_prefijo:
                FreeGate(bcn, aircraft.id)

    for aircraft in aircrafts:
        if aircraft.time:
            if aircraft.time.split(':')[0] == hora_prefijo:
                resultado = AssignGate(bcn, aircraft)
                if SearchTerminal(bcn, aircraft.company) != "" and resultado == -1:
                    no_asignados += 1

    return no_asignados


def PlotDayOccupancy(bcn, aircrafts):
    horas_del_dia = [f"{str(h).zfill(2)}:00" for h in range(24)]
    ocupacion_por_terminal = {t.name: [] for t in bcn.terminals}
    aviones_no_asignados = []

    for hora in horas_del_dia:
        fallos_asignacion = AssignGatesAtTime(bcn, aircrafts, hora)
        aviones_no_asignados.append(fallos_asignacion)

        for terminal in bcn.terminals:
            puertas_ocupadas = 0
            for area in terminal.boarding_areas:
                for gate in area.gates:
                    if gate.occupied:
                        puertas_ocupadas += 1
            ocupacion_por_terminal[terminal.name].append(puertas_ocupadas)

    fig = Figure(figsize=(8, 5), dpi=100)
    ax = fig.add_subplot(111)

    bottom = [0] * 24
    colores = ['#4682B4', '#F08080', '#3CB371']

    for i, (term_name, counts) in enumerate(ocupacion_por_terminal.items()):
        color = colores[i % len(colores)]
        ax.bar(horas_del_dia, counts, bottom=bottom, label=f"Terminal {term_name}", color=color)
        bottom = [b + c for b, c in zip(bottom, counts)]

    ax.plot(horas_del_dia, aviones_no_asignados, color='black', marker='o', linestyle='-', linewidth=2,
            label="No asignados")

    ax.set_xlabel("Hora del día")
    ax.set_ylabel("Cantidad")
    ax.set_title("Ocupación de Puertas por Terminal y Aviones No Asignados")
    ax.tick_params(axis='x', rotation=45, labelsize=8)
    ax.legend()
    fig.tight_layout()

    return fig


if __name__ == "__main__":
    from aircraft import LoadArrivals, LoadDepartures, MergeMovements

    bcn_ap = LoadAirportStructure("LEBL.txt")
    if bcn_ap != -1:
        arr = LoadArrivals("arrivals.txt")
        dep, status = LoadDepartures("departures.txt")
        if status == 0 and arr:
            vuelos = MergeMovements(arr, dep)
            fig_ocupacion = PlotDayOccupancy(bcn_ap, vuelos)
