# Die data.yaml

Die **data.yaml** ist die „Landkarte“ deines Datensatzes. Ultralytics liest daraus:

1. **Wo** liegen die Bilder für Training, Validierung und Test?
2. **Welche Klassen** gibt es und welche Nummer hat welche Klasse?

Ohne `data.yaml` kein Training – der Dateiname wird beim Training übergeben: `model.train(data="data.yaml")`.

## Beispiel: African Wildlife

So sieht die mitgelieferte Datei unseres ersten Trainings aus (gekürzt):

```yaml title="african-wildlife.yaml"
path: african-wildlife     # Hauptordner des Datensatzes
train: images/train        # Trainingsbilder (relativ zu path)  – 1052 Bilder
val: images/val            # Validierungsbilder                 –  225 Bilder
test: images/test          # Testbilder                         –  227 Bilder

# Klassen: Nummer → Name
names:
  0: buffalo
  1: elephant
  2: rhino
  3: zebra

# Optional: Wo kann der Datensatz heruntergeladen werden?
download: https://github.com/ultralytics/assets/releases/download/v0.0.0/african-wildlife.zip
```

## Die Einträge im Detail

| Schlüssel | Pflicht? | Bedeutung |
|---|---|---|
| `path` | optional | Wurzelordner des Datensatzes. Absolut (`C:/daten/platinen` oder `/content/datensatz`) oder relativ zum Datensatz-Ordner von Ultralytics. **Fehlt `path`, gilt der Ordner, in dem die data.yaml liegt.** So macht es P2 im Projekt: Derselbe Datensatz läuft dann auf dem Laptop und in Colab. |
| `train` | ✅ | Ordner mit Trainingsbildern, relativ zu `path`. Die Labels werden automatisch im Parallelordner `labels/…` gesucht. |
| `val` | ✅ | Ordner mit Validierungsbildern. |
| `test` | optional | Ordner mit Testbildern für die Abschlussprüfung. |
| `names` | ✅ | Klassennummern und -namen. Die Nummern müssen **mit den Label-Dateien übereinstimmen**! |
| `download` | optional | URL oder Skript zum automatischen Herunterladen. |

!!! danger "Häufigster Fehler: Klassen-Reihenfolge vertauscht"
    In den Label-Dateien steht nur die **Nummer** (z. B. `2`). Welche Klasse das ist, steht **ausschließlich** in der `data.yaml`.
    Wenn Label Studio `classes.txt` mit `ic, kondensator, widerstand` exportiert, du in der `data.yaml` aber
    `0: widerstand, 1: kondensator, 2: ic` schreibst, lernt das Modell **falsche Namen** – ohne Fehlermeldung!
    → Die Reihenfolge in `names` muss **exakt** der Reihenfolge in `classes.txt` entsprechen. Im Projekt übernimmt P2 das automatisch: Die Reihenfolge steht nur an einer Stelle, im Steckbrief.

## Eigene data.yaml – Beispiel aus der Elektrotechnik

```yaml title="platinen.yaml"
path: C:/Users/max/yolo-lokal/datensatz_platinen
train: images/train
val: images/val
test: images/test

names:
  0: widerstand
  1: kondensator
  2: ic
  3: diode
  4: led
```

=== "In Google Colab"

    In Colab liegen Dateien unter `/content/…` oder auf Google Drive unter `/content/drive/MyDrive/…`:

    ```yaml
    path: /content/drive/MyDrive/YOLO/datensatz_platinen
    ```

=== "Lokal unter Windows"

    Verwende **Schrägstriche** `/` (oder doppelte Backslashes `\\`) – einfache Backslashes führen in YAML zu Fehlern:

    ```yaml
    path: C:/Users/max/yolo-lokal/datensatz_platinen
    ```

!!! example "🧪 Fehlersuche: Was ist hier falsch?"
    ```yaml
    path: C:\Users\max\daten
    train: images/training
    val: images/val
    names:
      1: widerstand
      2: kondensator
    ```

    ??? success "Lösung (3 Fehler)"
        1. **Backslashes** im Pfad → besser `C:/Users/max/daten`.
        2. Der Ordner heißt vermutlich `images/train` und nicht `images/training` – Pfade müssen **exakt** zum Ordner passen.
        3. Die Klassen beginnen bei **1** statt bei **0**. YOLO zählt ab 0 – Klasse 0 wäre unbenannt, und Labels mit `0` würden einer nicht existierenden Klasse zugeordnet.

<div class="quiz" data-titel="Kurz-Check: data.yaml" data-quiz='[
 {"q": "Welche Einträge braucht eine data.yaml mindestens?",
  "a": ["train, val und names", "nur names", "test und download", "epochs und batch"],
  "c": 0, "e": "Ohne Trainings- und Validierungsbilder und ohne Klassennamen kann nicht trainiert werden. epochs und batch sind Trainingsparameter, keine Datensatz-Angaben."},
 {"q": "Wo sucht Ultralytics die Labels zu den Bildern in images/train?",
  "a": ["In labels/train", "In der data.yaml", "In classes.txt", "In images/train/labels"],
  "c": 0, "e": "Ultralytics ersetzt im Pfad images durch labels und sucht dort die gleichnamigen .txt-Dateien."}
]'></div>
