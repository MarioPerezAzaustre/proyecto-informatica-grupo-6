import os
import re
from tkinter import messagebox
from tkinter import filedialog
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from aircraft import *
from airport import *

class Gate:
    def __init__(self, name):
        self.name = name
        self.occupied = False
        self.aircraft_id = None
class BoardingArea:
    def __init__(self, name, area_type):
        self.name = name
        self.type = area_type
        self.gates = []
class Terminal:
    def __init__(self, name):
        self.name = name
        self.boarding_areas = []
        self.airlines = []
class BarcelonaAP:
    def __init__(self, code):
        self.code = code
        self.terminals = []

def SetGates(area, init_gate, end_gate, prefix):
    if end_gate <= init_gate:
        return -1
    area.gates = []
    for i in range(init_gate, end_gate + 1):
        area.gates.append(Gate(f"{prefix}{i}"))
    return 0

def LoadAirlines(terminal, t_name):
    filename = f"{t_name}_Airlines.txt"
    if not os.path.exists(filename):
        return -1
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            terminal.airlines = []
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        terminal.airlines.append(parts[1].strip())
        return 0
    except IOError:
        return -1

def LoadAirportStructure(filename):
    if not os.path.exists(filename):
        return -1
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file if line.strip()]

            if not lines:
                return -1

            first_line = lines[0].split()
            bcn = BarcelonaAP(first_line[0])
            num_terminals = int(first_line[1])

            idx = 1
            for _ in range(num_terminals):
                t_line = lines[idx].split()
                t_name = t_line[1]
                num_areas = int(t_line[2])

                terminal = Terminal(t_name)
                bcn.terminals.append(terminal)
                LoadAirlines(terminal, t_name)

                idx += 1
                for _ in range(num_areas):
                    a_line = lines[idx].split()
                    a_name = a_line[1]
                    a_type = a_line[2]

                    nums = re.findall(r'\d+', ' '.join(a_line[3:]))
                    init_gate = int(nums[0]) if len(nums) >= 1 else 0
                    end_gate = int(nums[1]) if len(nums) >= 2 else 0

                    area = BoardingArea(a_name, a_type)
                    terminal.boarding_areas.append(area)

                    prefix = f"{t_name}BA{a_name}G"
                    SetGates(area, init_gate, end_gate, prefix)

                    idx += 1

            return bcn
    except Exception:
        return -1

def GateOccupancy(bcn):
    occupancy_list = []
    for terminal in bcn.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                occupancy_list.append([gate.name, gate.occupied, gate.aircraft_id])
    return occupancy_list

def IsAirlineInTerminal(terminal, name):

   if not name:
       return False, -1
   if not terminal.airlines:
       return False
   if name in terminal.airlines:
       return True
   else:
       return False

def SearchTerminal(bcn, name):
    for terminal in bcn.terminals:
       resultado = IsAirlineInTerminal(terminal, name)
       if resultado is True:
           return terminal.name
    return ""


def AssignGate(bcn, aircraft):
    t_name = SearchTerminal(bcn, aircraft.company)

    if not t_name:
        return f"Vuelo {aircraft.id}: La aerolínea '{aircraft.company}' no opera en ninguna terminal."
    terminal = next((t for t in bcn.terminals if t.name == t_name), None)
    if not terminal:
        return f"Vuelo {aircraft.id}: Error interno, no se encontró la terminal {t_name}."
    tipo_requerido = "Schengen" if getattr(aircraft, 'is_schengen', False) else "No Schengen"
    for area in terminal.boarding_areas:
        if area.type == tipo_requerido:
            for gate in area.gates:
                if not gate.occupied:
                    gate.occupied = True
                    gate.aircraft_id = aircraft.id  # Guardamos el ID del avión
                    return f"Vuelo {aircraft.id} asignado a la puerta {gate.name} ({t_name} - Zona {area.name})."
    return f"Vuelo {aircraft.id}: No hay puertas libres en la zona {tipo_requerido} de la {t_name}."
    Guardado=False
    for gate in boarding_area.gates:
        if not gate.occupied:
            gate.occupied = True
            Guardado=True
            gate.aircraft = aircraft
    if Guardado:
        messagebox.showinfo("Guardado","Avion asignado corectamente")
        return
    else:
        messagebox.showerror("Error","Avion no guardado, gates llenas")
        return
