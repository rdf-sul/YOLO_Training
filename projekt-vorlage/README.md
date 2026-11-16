# YOLO-Projektvorlage

Vorlage für das eigene Projekt aus dem Kurs **[YOLO Training – Bilder-KI verstehen und trainieren](https://rdf-sul.github.io/YOLO_Training/projekt/)**.

| Notebook | Wo? | Aufgabe |
|---|---|---|
| `P1_daten_sammeln.ipynb` | Laptop | Steckbrief, Regeln, Fotos (Handy/Webcam), Import, Sichten, Katalog |
| `P2_labeln_und_pruefen.ipynb` | Laptop | Label Studio (lokaler Ordner), JSON-Export zusammenführen, YOLO-Format, Kontrolle, Datensatz-ZIP |
| `P3_training_colab.ipynb` | Google Colab | Training mit automatischem Fortsetzen, Auswertung, Fehleranalyse, Nachtraining |

## Einrichten

Voraussetzung: [uv](https://docs.astral.sh/uv/) ist installiert.

```bash
uv sync               # Umgebung herstellen (einmalig, ein paar Minuten)
uv run jupyter lab    # JupyterLab starten → P1 öffnen
```

Label Studio wird nicht ins Projekt installiert. P2 startet es mit `uvx` in einer eigenen Umgebung.

## Ordner

Die Ordner legt P1 beim ersten Start an:

```text
1_rohbilder/            Originalfotos, ein Unterordner pro Person/Kamera
2_bilder/               vorbereitete Bilder (P1), ggf. in Paketen pro Person (P2)
3_labelstudio_export/   JSON-Exporte aus Label Studio
4_datensatz/            YOLO-Labels, Aufteilung, Datensätze v1, v2 … und ZIPs für Colab
```

`werkzeuge.py` enthält die Hilfsfunktionen für P1 und P2.

Lizenz: Diese Vorlage steht unter der [GNU AGPL-3.0](https://github.com/rdf-sul/YOLO_Training/blob/main/LICENSE), wie Ultralytics YOLO selbst.
