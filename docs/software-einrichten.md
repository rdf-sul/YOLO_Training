# Software einrichten

Diese Anleitung zeigt dir Schritt für Schritt, wie du die Software auf deinem Laptop installierst und wie du die
Notebooks in Google Colab startest. Erledige **Teil 1 und 2 zu Hause**: Die Downloads sind groß und das Schul-WLAN
wäre mit allen Laptops gleichzeitig überlastet.

| Teil | Was | Wo | Dauer |
|---|---|---|---|
| [1 · uv installieren](#1-uv-installieren) | das Werkzeug, das Python und alle Pakete verwaltet | dein Laptop | 2 min |
| [2 · Projektvorlage einrichten](#2-projektvorlage-einrichten) | Notebooks P1–P3, Ultralytics, JupyterLab, Label Studio | dein Laptop | 10–20 min |
| [3 · Lokal arbeiten](#3-lokal-arbeiten-p1-und-p2) | P1 und P2 starten | dein Laptop | jedes Mal 1 min |
| [4 · Google Colab](#4-in-google-colab-arbeiten) | Training mit kostenloser GPU | im Browser | jedes Mal 2 min |

!!! info "Was du brauchst"
    - einen **Windows-Laptop** mit Webcam und etwa **5 GB freiem Speicher** (macOS und Linux sollten auch funktionieren)
    - **keine Admin-Rechte**: uv installiert alles in deinem Benutzerordner
    - für Teil 4 ein **Google-Konto**

## 1 · uv installieren

1. Drücke ++win++, tippe `powershell` und öffne **Windows PowerShell**.
2. Kopiere diesen Befehl hinein und drücke ++enter++:

    ```bash
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

3. **Schließe die PowerShell und öffne sie neu.** Sonst findet Windows den Befehl `uv` noch nicht.
4. Prüfe die Installation:

    ```bash
    uv --version
    ```

    Es erscheint eine Versionsnummer, z. B. `uv 0.9.x`. Mehr zu uv: [Installation mit uv](grundlagen/installation-uv.md).

## 2 · Projektvorlage einrichten

### 2.1 Herunterladen und entpacken

[:material-download: Projektvorlage herunterladen (ZIP)](downloads/yolo-projekt-vorlage.zip){ .md-button .md-button--primary }

1. Lege den Ordner **`C:\YOLO\`** an.
2. Entpacke die ZIP-Datei dorthin (Rechtsklick → **Alle extrahieren…**). Es entsteht der Ordner **`C:\YOLO\yolo-projekt\`**.

!!! warning "Nicht in OneDrive, Teams oder auf dem Desktop arbeiten"
    Diese Ordner werden laufend synchronisiert. Bei Tausenden Bilddateien führt das zu gesperrten Dateien und
    seltsamen Fehlern. `C:\YOLO\` wird nicht synchronisiert.

### 2.2 Terminal im Projektordner öffnen

Öffne im Explorer den Ordner `C:\YOLO\yolo-projekt`, klicke in die **Adresszeile**, tippe `powershell` und drücke ++enter++.
Eine PowerShell öffnet sich, die schon im richtigen Ordner steht. Du erkennst es an `PS C:\YOLO\yolo-projekt>`.

Diesen Handgriff brauchst du ab jetzt **jedes Mal**.

### 2.3 Alles installieren

```bash
uv sync
```

uv lädt Python, Ultralytics, PyTorch, JupyterLab und alle weiteren Pakete in den Unterordner `.venv`.
Beim ersten Mal dauert das einige Minuten. Am Ende steht eine Zeile wie `Installed … packages`.

### 2.4 Label Studio vorbereiten

Label Studio ist das Programm zum Labeln. Es läuft in einer eigenen Umgebung, weil sich seine Pakete nicht mit Ultralytics
vertragen. Dieser Befehl lädt es einmal vorab herunter:

```bash
uvx --python 3.12 --from label-studio==1.23.2 python -c "import label_studio; print('Label Studio', label_studio.__version__, 'ist bereit')"
```

!!! success "Fertig, wenn …"
    … beide Befehle ohne rote Fehlermeldung durchgelaufen sind und am Ende **`Label Studio 1.23.2 ist bereit`** steht.
    Dann bist du startklar für das Projekt.

## 3 · Lokal arbeiten: P1 und P2

**P1** (Daten sammeln) und **P2** (Labeln und prüfen) laufen auf **deinem Laptop**, weil sie deine Webcam, deine
Bilderordner und Label Studio brauchen.

### Starten

1. Terminal im Projektordner öffnen (wie in [2.2](#22-terminal-im-projektordner-offnen)).
2. JupyterLab starten:

    ```bash
    uv run jupyter lab
    ```

3. Der Browser öffnet JupyterLab. Klicke links doppelt auf **`P1_daten_sammeln.ipynb`** bzw. **`P2_labeln_und_pruefen.ipynb`**.
4. Führe die Zellen **von oben nach unten** aus: Zelle anklicken und ++shift+enter++.

**Wichtig:** Das PowerShell-Fenster muss offen bleiben, solange du arbeitest. Wenn du es schließt, stoppt JupyterLab.

### Label Studio (in P2)

Label Studio wird **aus P2 heraus** gestartet, in Abschnitt 3. Es öffnet sich im Browser unter `http://localhost:8080`.

- **Windows-Firewall fragt nach:** **Zugriff zulassen**, nur für **private** Netzwerke.
- **Konto anlegen:** Die E-Mail-Adresse darf erfunden sein, z. B. `anna@projekt.local`. **Merke dir das Passwort.**
  Es gibt kein Zurücksetzen per E-Mail, denn das Konto existiert nur auf deinem Laptop.
- Wie du das Projekt in Label Studio einrichtest, steht auf der Seite [P2 · Labeln](projekt/p2-labeln.md#34-label-studio-mit-lokalem-ordner).

### Beenden

1. In P2 die Zelle **„Label Studio stoppen“** ausführen, falls Label Studio läuft.
2. In JupyterLab: **File → Save All**, dann **File → Shut Down**. Alternativ im Terminal ++ctrl+c++ drücken.

### Eigene Fotos auf den Laptop bringen

Kopiere deine Handyfotos in einen eigenen Unterordner, z. B. `C:\YOLO\yolo-projekt\1_rohbilder\anna_handy\`.
P1 importiert sie von dort, auch HEIC-Dateien vom iPhone. Webcam-Fotos nimmt P1 direkt auf.

## 4 · In Google Colab arbeiten

Das **Training** läuft in [Google Colab](https://colab.research.google.com/): im Browser, auf einem Rechner von Google mit
Grafikkarte (GPU). Dort musst du nichts installieren. Es gibt zwei Colab-Notebooks:

| Notebook | Wann | Öffnen |
|---|---|---|
| **Erstes Training** (African Wildlife) | Einheit 4 | [:simple-googlecolab: In Colab öffnen](https://colab.research.google.com/github/rdf-sul/YOLO_Training/blob/main/notebooks/01_erstes_training.ipynb){ .md-button } |
| **P3 · Training** (dein Projekt) | Einheit 5 | [:simple-googlecolab: In Colab öffnen](https://colab.research.google.com/github/rdf-sul/YOLO_Training/blob/main/projekt-vorlage/P3_training_colab.ipynb){ .md-button } |

### So startest du ein Colab-Notebook

1. Auf **In Colab öffnen** klicken und mit deinem **Google-Konto** anmelden.
2. **Datei → Kopie in Drive speichern.** Es öffnet sich ein neuer Tab mit „Kopie von …“.
   Arbeite **nur noch in dieser Kopie**: Nur sie behält deine Änderungen, und P3 braucht sie zum Fortsetzen.
3. **GPU einschalten:** **Laufzeit → Laufzeittyp ändern → T4 GPU → Speichern.**
4. Die Zellen der Reihe nach ausführen (▶ links neben der Zelle oder ++shift+enter++).
5. Warnung *„Dieses Notebook wurde nicht von Google erstellt“*: **Trotzdem ausführen**.
6. Bei P3: Colab fragt nach dem **Zugriff auf Google Drive**. Mit demselben Konto **zulassen**.

Deine Kopie findest du später in Google Drive im Ordner **Colab Notebooks**. Öffne sie von dort, nicht über den Link
oben. Sonst beginnst du wieder mit einer leeren Vorlage.

### Datensatz für P3 in Google Drive ablegen

P2 erzeugt die Datei `4_datensatz\datensatz_v1.zip`. Lade sie in Google Drive in diesen Ordner hoch:

```text
Meine Ablage/
└── YOLO_Projekt/
    └── datensaetze/
        └── datensatz_v1.zip
```

Lege die Ordner `YOLO_Projekt` und `datensaetze` vorher an (in Drive: **Neu → Ordner**). Achte auf die genaue
Schreibweise. P3 legt daneben selbst die Ordner `laeufe/` und `modelle/` an. Dort liegen danach deine Trainingsläufe
und Modelle.

!!! tip "In der Gruppe"
    Es trainiert **eine** Person mit **ihrem** Google-Konto (Rolle Training). Ein Ordner, der nur „Mit mir geteilt“ ist,
    liegt nicht in „Meine Ablage“ und wird von P3 nicht gefunden. Gib das ZIP deshalb per USB-Stick oder Teams weiter.

### Wenn Colab abbricht

Colab trennt die Verbindung nach längerer Inaktivität oder nach einigen Stunden. Bei P3 ist das kein Problem:
Kopie aus Drive öffnen, GPU einschalten und **alle Zellen erneut ausführen**. Das Training setzt beim letzten
gespeicherten Stand fort. Achte darauf, dass `LAUF` gleich bleibt.

## Wenn etwas nicht klappt

| Problem | Lösung |
|---|---|
| `uv` wird nicht gefunden | PowerShell schließen und neu öffnen. Hilft das nicht, Teil 1 wiederholen |
| `uv sync` bricht mit Netzwerkfehler ab | Befehl einfach noch einmal ausführen; er macht dort weiter, wo er aufgehört hat |
| `uv sync` meldet „No `pyproject.toml` found“ | Du bist im falschen Ordner. Terminal im Ordner `yolo-projekt` öffnen (Teil 2.2) |
| JupyterLab öffnet sich nicht im Browser | Im Terminal steht eine Adresse `http://localhost:8888/lab?token=…`. Diese mit ++ctrl++ + Klick öffnen |
| Webcam zeigt nichts | Teams, Zoom und die Kamera-App schließen. In P1 `KAMERA = 1` probieren |
| Label Studio startet nicht | Firewall-Abfrage zulassen. Ist Port 8080 belegt, in P2 `wz.labelstudio_starten(port=8081)` verwenden |
| Colab: „Backend konnte nicht zugewiesen werden“ | Die kostenlose GPU ist gerade nicht verfügbar oder dein Kontingent ist aufgebraucht. Später erneut versuchen oder ein anderes Konto der Gruppe nehmen. Siehe [Keine GPU verfügbar?](projekt/p3-training.md#keine-gpu-verfugbar) |
| P3 findet den Datensatz nicht | Ordner und Dateiname in Drive prüfen (siehe oben) und denselben Namen bei `DATENSATZ` eintragen |
