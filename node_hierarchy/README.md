# Knoten Migrationstool
Dieses Tool dient zur Generierung von nginx-Konfigurationsdateien für die Migration von Knoten von einer Domäne in eine andere Domäne. Dabei wird berücksichtigt, welche Knoten von anderen Knoten abhängen um ins Internet zu kommen.

## Konfiguration
In der ``targets``-Datei werden Domänen (oder ähnliche Ziele) definiert. Hierbei handelt es sich um eine JSON-Datei. Dabei werden dort Gebietsrelationen für den Nominatik-Geocoder eingetragen.

## Aufruf
Es muss eine Datei mit den ``targets`` existieren.

Im einfachsten Fall wird das Programm dann wie folgt aufgerufen:
```
./node_hierarcy.py --all
```

Sollen spezielle ``nodes.json`` und ``graph.json`` Dateien verwendet werden, so kann der Datenpfad wie folgt angegeben werden (dabei kann es sich um einen lokalen Dateipfad als auch um eine http oder https URL handel):

```
./node_hierarcy.py --all --json-path https://service.freifunk-muensterland.de/maps/data/
```

Eine Ausgabe des Fortschritts erhält man mit dem Schalter ``-p`` oder ``--print-status``:

```
./node_hierarcy.py --all -p
```

Eine Limitierung auf eine Auswahl an Targets aus der Targets-Datei kann mit dem Schalter ``-t`` oder ``--targets`` vorgenommen werden:
```
./node_hierarcy.py -t domaene_01 domaene_02 --print-status
```

Weitere Hilfestellungen erhält mann mit ``-h`` oder ``--help``:
```
./node_hierarcy.py
```

### Ein- und Ausgabe
Standardmäßig wird eine Datei ``targets.json`` erwartet. Soll diese Datei von einer anderen Stelle aufgerufen werden kann das ``--targets-file``-Argument verwendet werden:
```
./node_hierarcy.py --targets-file /root/targets.json
```

Standardmäßig erfolgt die Ausgabe der generierten nginx-Konfigurationsdateien in das Verzeichnis ``./webserver-configuration/``. Das kann mit dem Schalter ``--out-path`` geändert werden:
```
./node_hierarcy.py --out-path /root/config/
```