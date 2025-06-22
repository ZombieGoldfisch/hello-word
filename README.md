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
keine HTML-Karte erzeugt. In `save_route_map` kann über den Parameter
`network_type` das genutzte OSM-Netz gewählt werden (z.B. `"drive"`,
`"walk"`, `"bike"`, `"rail"`).
