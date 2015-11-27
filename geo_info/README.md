## geo_info - Geografische Zuordnung der Knoten
### Beschreibung
Dieses Script wertet eine gegebene nodes.json Datei aus und ordnet die Knoten nach Abfrage der Nominatim-Geocoder-API Administrativen Relationen zu. Das geschieht hierarchisch, soweit ausreichend Daten über Nominatim/OSM zur Verfügung stehen.

### Requirements
Das Script wurde unter Python 2.7 getestet, wie es unter Python 3 läuft, kann ich nicht sagen.
Folgende Python Pakete sind erforderlich und sollten via `pip install` installiert werden. Von einer Installation über `apt-get` o. Ä. ist abzuraten, da hier z. B. das Geocoding-Modul so weit veraltet ist, dass benötigte Features noch nicht enthalten sind.
- [geopy]{https://geopy.readthedocs.org/en/1.10.0/}
- [blitzdb]{https://blitzdb.readthedocs.org/en/latest/}

### Bedienung
Im einfachsten Fall muss einfach nur die `geo.py` ausgeführt werden.
In eben dieser Datei lassen sich auch noch einige Anpassungen vornehmen:
- Mit der Variablen `nodefile` kann die Quelle einer nodes.json Datei angegeben werden, dabei kann es sich entweder um eine URI handeln oder um eine Referenz auf eine Datei auf dem lokalen Dateisystem.
- Um Info-Ausgaben zu deaktivieren, kann bei den Klassen `NodesParser` sowie `Domaene` das Attribut `printStatus` auf ```False``` gesetzt werden.
- By default wird auf der Konsole eine (hierarchische) Liste im Doku-Wiki Style ausgegeben, alternativ kann die Liste auch mit simpler Einrückung ausgegeben werden. Dazu muss der Funktionsaufruf zur Ausgabe von `domaene.results_as_dokuwiki_list()` auf `domaene.results_as_indent()` geändert werden.

### Anmerkungen
Der Nominatim-Geocoder hat die Reglementierung, dass maximal ein Request pro Sekunde gestellt werden darf. Daher kann das Auswerten einer großen Domäne einige Zeit in Anspruch nehmen. Es wurde jedoch ein Cache implementiert, der einmal abgerufene Geo-Informationen speichert, sodass bei einem erneuten Aufrufen nur die in der Zwischenzeit hinzugekommenen Knoten beim Geocoder abgefragt werden müssen.

### ToDos
- Ausgabe in Datei vernünftig realisieren.
- Konfiguration über Aufruf-Argumente realisieren
- Weitere Ausgabeformate

---- 
2015 - Simon Wüllhorst - CC-BY-SA 3.0
