import tkinter as tk
from tkinter import ttk
from datetime import datetime
import webbrowser

from cli import classify_query
from routing import (
    load_default_graph,
    find_route,
    parse_time_to_minutes,
    minutes_to_hhmm,
)
from osm_routing import find_osm_route, RouteNotFoundError
from visualization_osmnx import save_route_map, save_coords_map


class RoutingGUI:
    def __init__(self) -> None:
        self.graph = load_default_graph()
        self.stop_names = list(self.graph.nodes.keys())

        self.root = tk.Tk()
        self.root.title("Routing GUI")

        tk.Label(self.root, text="Start").grid(row=0, column=0, sticky="e")
        self.start_entry = tk.Entry(self.root, width=40)
        self.start_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(self.root, text="Ziel").grid(row=1, column=0, sticky="e")
        self.goal_entry = tk.Entry(self.root, width=40)
        self.goal_entry.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(self.root, text="Verkehrsmittel").grid(row=2, column=0, sticky="e")
        self.mode_combo = ttk.Combobox(self.root, values=["auto", "rad", "fuss", "bahn"], state="readonly")
        self.mode_combo.current(0)
        self.mode_combo.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        tk.Label(self.root, text="Zeitmodus").grid(row=3, column=0, sticky="e")
        self.time_mode = ttk.Combobox(
            self.root, values=["now", "abfahrt", "anreise"], state="readonly"
        )
        self.time_mode.current(0)
        self.time_mode.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        self.time_mode.bind("<<ComboboxSelected>>", self.on_time_mode_changed)

        self.time_label = tk.Label(self.root, text="Zeit (HH:MM)")
        self.time_label.grid(row=4, column=0, sticky="e")
        self.time_entry = tk.Entry(self.root, width=10)
        self.time_entry.grid(row=4, column=1, sticky="w", padx=5, pady=2)
        self.time_label.grid_remove()
        self.time_entry.grid_remove()

        tk.Label(self.root, text="Sortierung").grid(row=5, column=0, sticky="e")
        self.sort_combo = ttk.Combobox(
            self.root, values=["time", "transfers"], state="readonly"
        )
        self.sort_combo.current(0)
        self.sort_combo.grid(row=5, column=1, sticky="w", padx=5, pady=2)

        self.route_button = tk.Button(self.root, text="Route berechnen", command=self.compute_route)
        self.route_button.grid(row=6, column=0, columnspan=2, pady=5)

        self.output = tk.Text(self.root, width=60, height=15)
        self.output.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

    def log(self, text: str) -> None:
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    def on_time_mode_changed(self, event=None) -> None:
        mode = self.time_mode.get()
        if mode == "now":
            self.time_label.grid_remove()
            self.time_entry.grid_remove()
        else:
            self.time_label.grid()
            self.time_entry.grid()

    def compute_route(self) -> None:
        self.output.delete("1.0", tk.END)
        start_q = self.start_entry.get().strip()
        goal_q = self.goal_entry.get().strip()
        mode = self.mode_combo.get()

        if not start_q or not goal_q:
            self.log("Bitte Start und Ziel eingeben.")
            return

        if mode == "bahn":
            try:
                start_stop, start_coords = classify_query(start_q, self.stop_names)
            except Exception as exc:
                self.log(f"Fehler bei Start: {exc}")
                return
            try:
                goal_stop, goal_coords = classify_query(goal_q, self.stop_names)
            except Exception as exc:
                self.log(f"Fehler bei Ziel: {exc}")
                return
        else:
            try:
                start_coords = geocode_address(start_q)
            except Exception as exc:
                self.log(f"Fehler bei Start: {exc}")
                return
            try:
                goal_coords = geocode_address(goal_q)
            except Exception as exc:
                self.log(f"Fehler bei Ziel: {exc}")
                return
            start_stop = goal_stop = None

        if start_stop is not None:
            node = self.graph.nodes.get(start_stop)
            if not node or node.lat is None or node.lon is None:
                self.log(f"Keine Koordinaten f\u00fcr {start_stop}")
                return
            start_coords = (node.lat, node.lon)
        if goal_stop is not None:
            node = self.graph.nodes.get(goal_stop)
            if not node or node.lat is None or node.lon is None:
                self.log(f"Keine Koordinaten f\u00fcr {goal_stop}")
                return
            goal_coords = (node.lat, node.lon)

        if mode == "bahn":
            if start_stop is None or goal_stop is None:
                self.log("Bitte Haltestellennamen f\u00fcr den Bahnmodus eingeben.")
                return
            choice = self.time_mode.get()
            if choice == "now":
                now = datetime.now()
                start_minutes = now.hour * 60 + now.minute + now.second / 60.0
                reverse = False
            else:
                try:
                    start_minutes = parse_time_to_minutes(self.time_entry.get())
                except Exception as exc:
                    self.log(f"Ung\u00fcltige Zeitangabe: {exc}")
                    return
                reverse = choice == "anreise"
            sort_by = self.sort_combo.get()
            path = find_route(
                self.graph,
                start_stop,
                goal_stop,
                start_minutes,
                reverse=reverse,
                sort_by=sort_by,
            )
            if not path:
                self.log("Keine Route gefunden.")
                return
            self.log("Gefundene Route:")
            for stop, line, arr in path:
                line_str = line if line is not None else "start"
                self.log(f"{line_str} -> {stop} {minutes_to_hhmm(arr)}")
            filename = save_route_map(self.graph, path, network_type="walk")
            if filename:
                webbrowser.open(filename)
        else:
            nt_map = {"auto": "drive", "rad": "bike", "fuss": "walk"}
            nt = nt_map[mode]
            try:
                coords_path, travel_time = find_osm_route(
                    start_coords, goal_coords, network_type=nt
                )
            except RouteNotFoundError as exc:
                self.log(str(exc))
                return
            self.log("Koordinaten der Route:")
            for lat, lon in coords_path:
                self.log(f"  {lat:.5f}, {lon:.5f}")
            now = datetime.now()
            start_minutes = now.hour * 60 + now.minute + now.second / 60.0
            arrival = start_minutes + travel_time
            self.log(f"Ankunft gegen {minutes_to_hhmm(arrival)}")
            filename = save_coords_map(coords_path, network_type=nt)
            if filename:
                webbrowser.open(filename)

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    RoutingGUI().run()
