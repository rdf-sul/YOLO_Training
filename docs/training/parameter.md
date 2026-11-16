# Parameter einstellen

Ultralytics hat über 100 Trainingsparameter – mit sinnvollen **Standardwerten**. Für den Anfang musst du nur eine
Handvoll kennen. Alle anderen lässt du erst einmal so, wie sie sind.

## Die wichtigsten Begriffe

| Begriff | Bedeutung | Bild dazu |
|---|---|---|
| **Epoche** (`epochs`) | Ein kompletter Durchlauf durch **alle** Trainingsbilder | 1 Epoche = das Lehrbuch einmal komplett durchgearbeitet |
| **Batch** (`batch`) | Anzahl Bilder, die **gleichzeitig** verarbeitet werden, bevor die Gewichte angepasst werden | Lernkarten-Stapel: nach jedem Stapel wird kurz nachgedacht |
| **Iteration** | ein Batch = ein Lernschritt | 1052 Bilder ÷ 16 pro Batch = **66 Iterationen pro Epoche** |
| **Bildgröße** (`imgsz`) | Auf diese Kantenlänge werden die Bilder skaliert | Lupe: größer = mehr Details, aber langsamer |

## Die Top-Parameter

| Parameter | Standard | Was bewirkt er? | Tipp |
|---|---|---|---|
| `model` | – | Startmodell, z. B. `yolo26n.pt` | mit `n` oder `s` beginnen |
| `data` | – | Pfad zur [data.yaml](../daten/data-yaml.md) | – |
| `epochs` | 100 | Anzahl Epochen | 30–100 für Transfer Learning; Early Stopping bremst rechtzeitig |
| `patience` | 100 | Abbruch, wenn sich die *mAP50-95* so viele Epochen lang nicht verbessert (**Early Stopping**) | 10–30 spart Zeit |
| `batch` | 16 | Bilder pro Batch | `-1` = automatisch passend zum GPU-Speicher; bei „out of memory“ halbieren |
| `imgsz` | 640 | Bildgröße in Pixeln | kleine Objekte → größer (z. B. 960), schnelle Tests → kleiner (320) |
| `device` | auto | `0` = 1. GPU, `cpu` = Prozessor | in Colab automatisch GPU |
| `name` | train | Name des Ergebnisordners in `runs/detect/` | sprechende Namen, z. B. `wildlife_n_30ep` |
| `fraction` | 1.0 | Anteil der Trainingsbilder, die verwendet werden | `0.25` für schnelle Experimente |
| `cache` | False | Bilder im Arbeitsspeicher halten | `True` beschleunigt, wenn genug RAM da ist |

??? note "Vertiefung: Lernrate, Optimierer & Augmentation"
    - **Lernrate** (`lr0`): Wie groß ist jeder Verbesserungsschritt? Zu groß → das Training „springt“ und wird instabil;
      zu klein → es dauert ewig. Mit `optimizer="auto"` (Standard) wählt Ultralytics Optimierer und Lernrate selbst –
      für YOLO26 z. B. den neuen **MuSGD**-Optimierer.
    - **Augmentation** (Datenvermehrung): Während des Trainings werden die Bilder zufällig verändert, damit das Modell
      robuster wird. Standardmäßig aktiv sind u. a.:

        | Parameter | Standard | Wirkung |
        |---|---|---|
        | `fliplr` | 0.5 | 50 % der Bilder werden horizontal gespiegelt |
        | `hsv_h`, `hsv_s`, `hsv_v` | 0.015 / 0.7 / 0.4 | Farbton, Sättigung, Helligkeit variieren |
        | `scale` | 0.5 | Bilder zufällig größer/kleiner skalieren |
        | `mosaic` | 1.0 | 4 Bilder werden zu einem Mosaik zusammengesetzt |
        | `degrees` | 0.0 | Drehung (aus) – bei Bauteilen von oben sinnvoll, z. B. `degrees=180` |
        | `flipud` | 0.0 | vertikal spiegeln (aus) – bei Draufsicht-Bildern sinnvoll |

      In Colab siehst du die Augmentation in den Bildern `train_batch0.jpg`, `train_batch1.jpg` … im Ergebnisordner.

    Die vollständige Liste: [Ultralytics – Training Settings](https://docs.ultralytics.com/modes/train/#train-settings)

## 🧪 Experiment: Overfitting und Early Stopping

Während des Trainings werden zwei Fehlerkurven gemessen:

- **train/loss** – der Fehler auf den **Trainingsbildern**, aus denen das Modell lernt.
- **val/loss** – der Fehler auf den **Validierungsbildern**, die das Modell nie zum Lernen benutzt.

Spiele mit den Reglern: Wann lohnt es sich nicht mehr weiterzutrainieren?
*(Simulierte Kurven. Vereinfacht wird hier am val/loss gemessen – Ultralytics selbst bewertet für best.pt und patience die mAP50-95 auf den Validierungsbildern.)*

<div class="exp" data-exp="loss"></div>

!!! example "Aufgaben zum Experiment"
    1. Wähle den **kleinen Datensatz** und 200 Epochen. Ab welcher Epoche steigt `val/loss` wieder an?
    2. Was bedeutet es, wenn `train/loss` weiter fällt, `val/loss` aber steigt? *(Stichwort: Auswendiglernen)*
    3. Stelle `patience` auf 10 und dann auf 50. Wie viele Epochen spart Early Stopping jeweils?
    4. Wechsle zum **großen Datensatz**. Was ändert sich – und warum?

    ??? success "Lösungshinweise"
        1. Etwa ab Epoche 45 – danach wird das Modell auf neuen Bildern wieder schlechter.
        2. Das ist **Overfitting** (Überanpassung): Das Modell merkt sich Details der Trainingsbilder, statt allgemeine Merkmale zu lernen.
        3. Kleine patience bricht früh ab und spart viel Zeit, kann aber bei „Wellen“ in der Kurve zu früh stoppen.
        4. Mit mehr (vielfältigen) Daten tritt Overfitting viel später und schwächer auf. **Mehr Daten sind das beste Mittel gegen Overfitting.**

!!! info "In echt: Was macht Ultralytics?"
    Ultralytics speichert automatisch das **beste** Modell (`best.pt`, gemessen an den Validierungsbildern)
    und das **letzte** (`last.pt`). Selbst wenn du zu lange trainierst, hast du also immer den besten Stand.
    Mit `patience` stoppt das Training automatisch, wenn sich nichts mehr verbessert.

## 🧪 Experiment: Bildgröße

<div class="exp" data-exp="imgsz" data-bild="../../assets/img/zidane.jpg"></div>

!!! question "Überlege"
    Du sollst winzige SMD-Bauteile (1 × 0,5 mm) auf einem 10 × 10 cm großen Platinenfoto erkennen.
    Ein Bauteil ist auf dem Originalfoto ca. 40 Pixel groß, das Foto hat 4000 Pixel Breite.
    Wie groß ist das Bauteil noch bei `imgsz=640`? Ist das ein Problem?

    ??? success "Lösung"
        Skalierungsfaktor 640 / 4000 = 0,16 → 40 px × 0,16 ≈ **6 Pixel**. Das ist für das Netz sehr klein!
        Abhilfe: größeres `imgsz` (z. B. 1280), Bild in **Kacheln** zerlegen, oder näher heranfotografieren.

## Typische Fehlermeldungen

| Meldung | Ursache | Lösung |
|---|---|---|
| `CUDA out of memory` | Batch oder Bildgröße zu groß für die GPU | `batch` halbieren oder `batch=-1` |
| `Dataset images not found` | Pfad in der data.yaml stimmt nicht | `path`/`train`/`val` prüfen |
| `labels ... not found` / 0 Labels | Label-Ordner fehlt oder Dateinamen passen nicht | Struktur `images/…` ↔ `labels/…` prüfen |
| Training extrem langsam | läuft auf der CPU | in Colab: *Laufzeit → Laufzeittyp ändern → T4 GPU* |

<div class="quiz" data-titel="Kurz-Check: Parameter" data-quiz='[
 {"q": "Dein Datensatz hat 800 Trainingsbilder, batch=16. Wie viele Iterationen hat eine Epoche?",
  "a": ["16", "50", "800", "12.800"],
  "c": 1, "e": "800 ÷ 16 = 50 Lernschritte pro Epoche."},
 {"q": "train/loss sinkt weiter, val/loss steigt seit 20 Epochen. Was liegt vor?",
  "a": ["Underfitting", "Overfitting", "Ein Fehler in der data.yaml", "Alles in Ordnung, weitertrainieren"],
  "c": 1, "e": "Das Modell lernt die Trainingsbilder auswendig und wird auf neuen Bildern schlechter."},
 {"q": "Was bewirkt patience=15?",
  "a": ["Das Training wartet 15 Sekunden vor dem Start", "Das Training stoppt, wenn sich 15 Epochen lang nichts verbessert", "Es werden 15 Bilder pro Batch verwendet", "Das Modell wird 15-mal gespeichert"],
  "c": 1, "e": "Early Stopping: spart Zeit und verhindert unnötig langes Training."},
 {"q": "Beim Training erscheint CUDA out of memory. Was hilft?",
  "a": ["batch verkleinern", "imgsz verkleinern", "epochs erhöhen", "batch=-1 (AutoBatch) verwenden"],
  "c": [0, 1, 3], "e": "Weniger Bilder pro Batch oder kleinere Bilder brauchen weniger GPU-Speicher. Die Anzahl der Epochen ändert den Speicherbedarf nicht."}
]'></div>
