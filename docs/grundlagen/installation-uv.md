# Installation mit uv

In diesem Kurs installieren wir Python-Pakete **nicht mit `pip`**, sondern mit **[uv](https://docs.astral.sh/uv/)**.

!!! abstract "Warum uv statt pip?"
    | | `pip` | **`uv`** |
    |---|---|---|
    | Geschwindigkeit | langsam | **10–100× schneller** |
    | Python selbst installieren | ❌ (separat nötig) | ✅ `uv` holt die passende Python-Version |
    | Virtuelle Umgebung | von Hand (`python -m venv …`) | ✅ automatisch pro Projekt |
    | Reproduzierbar | nur mit Zusatzaufwand | ✅ `uv.lock` hält exakte Versionen fest |
    | Ein Werkzeug für alles | ❌ pip + venv + pyenv + … | ✅ |

    Kurz: **Ein Projekt = ein Ordner mit eigener Umgebung.** Kein Durcheinander mehr mit globalen Paketen.

## Schritt 1 · uv installieren

=== ":fontawesome-brands-windows: Windows (PowerShell)"

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

=== ":fontawesome-brands-apple: macOS / :fontawesome-brands-linux: Linux"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

Danach das Terminal **schließen und neu öffnen** und prüfen:

```bash
uv --version
```

!!! tip "Keine Admin-Rechte nötig"
    uv installiert sich in dein Benutzerverzeichnis. Auch auf Rechnern ohne Administratorrechte funktioniert das in der Regel.

## Schritt 2 · Projekt anlegen und Ultralytics installieren

```bash
uv init yolo-lokal --python 3.12    # neuen Projektordner mit Python 3.12 anlegen
cd yolo-lokal
uv add ultralytics                  # Ultralytics (inkl. PyTorch) installieren
```

Der Ordner sieht danach so aus:

```text
yolo-lokal/
├── .venv/            ← virtuelle Umgebung (von uv verwaltet – nicht anfassen)
├── main.py           ← Beispielskript
├── pyproject.toml    ← Projektbeschreibung: welche Pakete werden gebraucht?
└── uv.lock           ← exakte Versionen aller Pakete
```

??? note "Vertiefung: Wie groß ist das? Und was ist mit Grafikkarten?"
    `uv add ultralytics` installiert auch **PyTorch** – das sind ca. 1–2 GB. Auf normalen Laptops wird die **CPU-Version**
    genutzt. Das reicht für Vorhersagen und kleine Experimente völlig aus. Für das **Training** nutzen wir später
    **Google Colab** mit kostenloser GPU, damit niemand stundenlang warten muss.

## Schritt 3 · Erste Vorhersage

Mit `uv run` führst du einen Befehl **in der Projektumgebung** aus – ohne sie vorher „aktivieren“ zu müssen.

=== "Kommandozeile (CLI)"

    ```bash
    uv run yolo predict model=yolo26n.pt source="https://ultralytics.com/images/bus.jpg"
    ```

    Das Ergebnisbild liegt danach in `runs/detect/predict/`.

=== "Python-Skript"

    Ersetze den Inhalt von `main.py`:

    ```python
    from ultralytics import YOLO

    model = YOLO("yolo26n.pt")                                   # lädt das Modell (beim 1. Mal Download)
    results = model("https://ultralytics.com/images/bus.jpg")    # Vorhersage

    for box in results[0].boxes:
        name = model.names[int(box.cls)]
        print(f"{name:10s}  Confidence: {float(box.conf):.2f}  Box: {box.xyxy[0].tolist()}")

    results[0].save("ergebnis.jpg")                              # Bild mit Boxen speichern
    ```

    ```bash
    uv run main.py
    ```

=== "Webcam live"

    ```bash
    uv run yolo predict model=yolo26n.pt source=0 show=True
    ```

    `source=0` ist die erste Webcam. Beenden mit ++q++ im Bildfenster oder ++ctrl+c++ im Terminal.

!!! example "🧪 Mini-Experiment"
    1. Führe die Vorhersage mit `yolo26n.pt` aus und notiere die **Zeit pro Bild** (steht in der Ausgabe, z. B. `86.3ms`).
    2. Wiederhole mit `yolo26s.pt` und `yolo26m.pt`.
    3. Vergleiche mit der Tabelle auf der Seite [Welches Modell?](modelle.md). Ist dein Laptop schneller oder langsamer als die Ultralytics-Messung?
    4. Probiere auch andere Tasks: `yolo26n-seg.pt`, `yolo26n-pose.pt` – was ändert sich am Ergebnisbild?

## Schritt 4 · Jupyter Notebooks lokal nutzen

`uv add ultralytics` installiert **kein Jupyter**. In Google Colab ist Jupyter schon eingebaut.
Auf deinem Laptop brauchst du es aber später, zum Beispiel für die **Projekt-Notebooks** P1 und P2
vor und nach dem [Labeln](../daten/labeln.md). In der [Projektvorlage](../projekt/index.md#projektvorlage-einrichten) ist JupyterLab schon enthalten, dort genügt `uv sync`.
In einem eigenen Projekt wie hier installierst du Jupyter **in dasselbe Projekt**:

```bash
uv add jupyterlab
```

=== "JupyterLab im Browser"

    ```bash
    uv run jupyter lab
    ```

    Im Browser öffnet sich JupyterLab. Dort kannst du `.ipynb`-Dateien öffnen und ausführen.
    Zum Beenden drückst du im Terminal ++ctrl+c++.

=== "VS Code"

    1. Öffne den Projektordner in VS Code und installiere die Erweiterung **Jupyter** (von Microsoft).
    2. Öffne eine `.ipynb`-Datei und klicke oben rechts auf **Select Kernel → Python Environments**.
    3. Wähle die Umgebung **`.venv`** aus deinem Projektordner.

!!! warning "Warum nicht einfach `uvx jupyter lab`?"
    `uvx` startet Jupyter in einer **eigenen, leeren Umgebung**. Dort fehlt Ultralytics, und
    `from ultralytics import YOLO` endet mit `ModuleNotFoundError`. Jupyter und deine Pakete müssen
    **in derselben Umgebung** liegen. Genau das erreichst du mit `uv add jupyterlab` und `uv run`.

## Die wichtigsten uv-Befehle

| Befehl | Was passiert? |
|---|---|
| `uv init name` | neues Projekt anlegen |
| `uv add paket` | Paket installieren und in `pyproject.toml` eintragen |
| `uv remove paket` | Paket entfernen |
| `uv run befehl` | Befehl in der Projektumgebung ausführen |
| `uv sync` | Umgebung genau nach `uv.lock` herstellen (z. B. nach dem Klonen eines Projekts) |
| `uvx paket` | Werkzeug einmalig ausführen, ohne es zu installieren (eigene Umgebung!) |
| `uv run jupyter lab` | JupyterLab in der Projektumgebung starten |
| `uv python list` | installierte/verfügbare Python-Versionen anzeigen |

<div class="quiz" data-titel="Kurz-Check: uv" data-quiz='[
 {"q": "Mit welchem Befehl installierst du Ultralytics in dein uv-Projekt?",
  "a": ["pip install ultralytics", "uv add ultralytics", "uv install ultralytics", "python get ultralytics"],
  "c": 1, "e": "uv add installiert das Paket und trägt es in pyproject.toml und uv.lock ein."},
 {"q": "Was macht uv run?",
  "a": ["Es startet den Rechner neu", "Es führt einen Befehl in der virtuellen Umgebung des Projekts aus", "Es trainiert ein Modell", "Es löscht die Umgebung"],
  "c": 1, "e": "uv run sorgt dafür, dass die richtige Python-Version und die Projektpakete genutzt werden."},
 {"q": "Ein Mitschüler gibt dir seinen Projektordner mit pyproject.toml und uv.lock. Wie bekommst du die exakt gleiche Umgebung?",
  "a": ["uv sync", "uv init", "Alle Pakete einzeln mit pip installieren", "Gar nicht"],
  "c": 0, "e": "uv sync stellt die Umgebung genau nach uv.lock her – gleiche Versionen wie beim Mitschüler."},
 {"q": "Du startest Jupyter mit uvx jupyter lab. Im Notebook meldet from ultralytics import YOLO einen ModuleNotFoundError. Warum?",
  "a": ["Ultralytics funktioniert nicht in Notebooks", "uvx nutzt eine eigene Umgebung ohne Ultralytics – besser: uv add jupyterlab und uv run jupyter lab", "Der Laptop hat keine GPU", "Man muss den Rechner neu starten"],
  "c": 1, "e": "Jupyter muss in derselben Umgebung laufen wie deine Pakete. uv run jupyter lab startet es im Projekt."}
]'></div>
