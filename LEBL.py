import os
import re
from tkinter import messagebox
from tkinter import filedialog
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from aircraft import *


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
        if resultado is True:
            return terminal.name
    return ""


def AssignGate(bcn, aircraft):
    nombre_t = SearchTerminal(bcn, aircraft.company)

    if not nombre_t:
        return f"Vuelo {aircraft.id}: La aerolínea '{aircraft.company}' no opera en ninguna terminal."

    terminal = next((t for t in bcn.terminals if t.name == nombre_t), None)
    if not terminal:
        return f"Vuelo {aircraft.id}: Error interno, no se encontró la terminal {nombre_t}."

    tipo_requerido = "Schengen" if getattr(aircraft, 'is_schengen', False) else "No Schengen"

    for area in terminal.boarding_areas:
        if area.type == tipo_requerido:
            for gate in area.gates:
                if not gate.occupied:
                    gate.occupied = True
                    gate.aircraft_id = aircraft.id
                    return f"Vuelo {aircraft.id} asignado a la puerta {gate.name} ({nombre_t} - Zona {area.name})."

    return f"Vuelo {aircraft.id}: No hay puertas libres en la zona {tipo_requerido} de la {nombre_t}."


def AssignNightGates(bcn, aircrafts):
    if not aircrafts:
        return -1

    for aircraft in aircrafts:
        origen_vacio = not getattr(aircraft, 'origin', None)

        if origen_vacio:
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

    for aircraft in aircrafts:
        hora_salida = getattr(aircraft, 'departure_time', None)
        if hora_salida and hora_salida <= hora:
            FreeGate(bcn, aircraft.id)

    for aircraft in aircrafts:
        hora_llegada = getattr(aircraft, 'arrival_time', None)
        if hora_llegada and hora_llegada.startswith(hora.split(':')[0]):
            resultado = AssignGate(bcn, aircraft)
            if "No hay puertas libres" in resultado:
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
