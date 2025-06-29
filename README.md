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

Alle benötigten Abhängigkeiten sind in `requirements.txt` aufgelistet und
können gemeinsam installiert werden mit

```bash
pip install -r requirements.txt
```

Alternativ kann das Skript `setup.sh` verwendet werden, das die Installation
automatisch durchführt:

```bash
./setup.sh
```

Mit dem Zusatz `--with-optional` werden auch die optionalen Pakete
installiert.

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

Die Funktion `find_osm_route` besitzt zudem die Parameter `box_margin` und
`fallback_dist`, mit denen sich die Größe des geladenen OSM-Ausschnitts
steuern lässt. `box_margin` legt den Puffer in Grad um Start- und Zielpunkt
fest (Standard: `0.02`), `fallback_dist` bestimmt den Radius in Metern, der
verwendet wird, wenn das Laden der Bounding Box fehlschlägt.

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

## Grafische Oberfläche


Eine einfache GUI auf Basis von ``tkinter`` kann direkt 
mit dem Hauptskript gestartet werden:

```bash
python main.py gui
```

Dort lassen sich Start und Ziel eingeben, das

Verkehrsmittel wählen sowie optional eine Abfahrts- oder Ankunftszeit
angeben. Zudem kann die Route nach Reisezeit oder der Anzahl der
Umstiege sortiert werden. Nach dem Klick auf "Route berechnen" wird der berechnete Weg
im Textfeld ausgegeben und – sofern ``osmnx`` und ``folium`` verfügbar
 sind – eine HTML-Karte automatisch im Browser geöffnet.
