# Aufgabenstellung
„Wir sollen einen Routenfinder coden. Dabei soll der Fokus auf dem ÖPNV liegen. Wichtige Punkte hierbei wären:
Routing
Umstiege
Zeiten miteinander vergleichen und schnellste/optimale Route finden evt mit Suchfiltern nach Umstiegen, Zeit, Strecke oder so filtern
Zusatz (Pflicht):
MV und Rad + Fuß Router ebenso einbauen.

Bei dem Projekt haben wir auch noch die Einschränkung, dass wir nur eine Geocoder API für die Namen der Straßen, Haltestellen usw. benutzen dürfen. Keine weitere API (liegt daran dass wir 3 Leute sind)
Für den ÖPNV könnten wir die GTFs-Datenbank nutzen, mal schauen wie weit die uns bringt.
Für Rad, Fuß und MV sollten wir OSMNX nutzen (auch eine Datenbank)

Für das gesamte Projekt gilt, dass der Code modular aufgebaut werden muss.
Und wenn wir genügend Zeit haben (optional) wäre eine Visualisierung des ganzen (Wie bei Maps bspw.) ganz cool.“

## Voraussetzungen

Für die optionale Visualisierung werden die Pakete `osmnx` und `folium` benötigt:

```bash
pip install osmnx folium
```

Fehlen sie, läuft die Kommandozeile dennoch – es wird dann lediglich
keine HTML-Karte erzeugt.

Zusätzlich wird für das optionale Adressrouting das Paket `geopy`
benötigt.  Alle optionalen Abhängigkeiten können gemeinsam installiert
werden mit

```bash
pip install osmnx folium geopy
```

In `save_route_map` kann über den Parameter `network_type` das genutzte
OSM-Netz gewählt werden (z.B. `"drive"`, `"walk"`, `"bike"`, `"rail"`).

## Beispiele

### Adressrouting

```python
from geopy.geocoders import Nominatim
import osmnx as ox
import networkx as nx

geolocator = Nominatim(user_agent="routing-demo")
orig = geolocator.geocode("Hauptbahnhof München")
dest = geolocator.geocode("Marienplatz München")

# Straßennetz um den Startpunkt laden und Route berechnen
G = ox.graph_from_point((orig.latitude, orig.longitude), dist=3000,
                        network_type="walk")
start = ox.nearest_nodes(G, orig.longitude, orig.latitude)
goal = ox.nearest_nodes(G, dest.longitude, dest.latitude)
route = nx.shortest_path(G, start, goal, weight="length")
```

### Moduswahl bei der Visualisierung

```python
filename = save_route_map(graph, path, network_type="bike")
```
