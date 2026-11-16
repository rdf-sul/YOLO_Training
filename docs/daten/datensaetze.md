# Datensätze finden

## Woher bekomme ich Trainingsdaten?

| Quelle | Was gibt es dort? | Gut für |
|---|---|---|
| **[Ultralytics Datasets](https://docs.ultralytics.com/datasets/)** | Dutzende fertig aufbereitete Datensätze, die beim Training **automatisch heruntergeladen** werden | Einstieg, Übungen, Benchmarks |
| **[Roboflow Universe](https://universe.roboflow.com/)** | über 500.000 Datensätze von Nutzern, direkt im YOLO-Format exportierbar | spezielle Themen (z. B. Platinen, Werkzeuge, Bauteile) |
| **[Kaggle Datasets](https://www.kaggle.com/datasets)** | Datensätze aus Wettbewerben und Forschung | Vergleich mit anderen, große Datensätze |
| **[Open Images V7](https://storage.googleapis.com/openimages/web/index.html)** (Google) | ~9 Mio. Bilder, 600 Klassen | einzelne Klassen herausfiltern |
| **[Hugging Face Datasets](https://huggingface.co/datasets?task_categories=task_categories:object-detection)** | Forschungsdatensätze, oft mit Lizenzangabe | aktuelle Forschung |
| **Eigene Fotos** | genau dein Problem, deine Kamera, dein Licht | **echte Projekte** (→ Einheit 5) |

!!! warning "Lizenz und Datenschutz beachten"
    - Nicht jeder Datensatz darf für jeden Zweck genutzt werden. Achte auf die **Lizenz** (z. B. CC BY 4.0 = Nutzung mit Namensnennung erlaubt).
    - Bilder mit **erkennbaren Personen** sind personenbezogene Daten (DSGVO). Bei eigenen Fotos im Betrieb vorher klären, was erlaubt ist.

## Beispiele von Ultralytics zum Erkunden

Alle Datensätze lassen sich mit einer einzigen Zeile trainieren – der Name der `.yaml`-Datei genügt, den Rest erledigt Ultralytics.

| Datensatz | Task | Klassen | Bilder / Größe | Idee |
|---|---|---|---|---|
| [**COCO8**](https://docs.ultralytics.com/datasets/detect/coco8/) | Detektion | 80 | 8 Bilder | Mini-Test: Funktioniert mein Setup? |
| [**African Wildlife**](https://docs.ultralytics.com/datasets/detect/african-wildlife/) | Detektion | 4 (Büffel, Elefant, Nashorn, Zebra) | ~1.500 / 100 MB | **unser erstes Training** 🦓 |
| [**Medical Pills**](https://docs.ultralytics.com/datasets/detect/medical-pills/) | Detektion | 1 (Tablette) | 8 MB | Zählen wie in der Fertigung |
| [**Signature**](https://docs.ultralytics.com/datasets/detect/signature/) | Detektion | 1 (Unterschrift) | 11 MB | Dokumentenprüfung |
| [**Construction-PPE**](https://docs.ultralytics.com/datasets/detect/construction-ppe/) | Detektion | 12 (Helm, Weste, *kein* Helm …) | mittel | Arbeitssicherheit |
| [**Brain Tumor**](https://docs.ultralytics.com/datasets/detect/brain-tumor/) | Detektion | 2 | 4 MB | Medizintechnik |
| [**Crack Segmentation**](https://docs.ultralytics.com/datasets/segment/crack-seg/) | Segmentierung | 1 (Riss) | mittel | Materialprüfung |
| [**Package Segmentation**](https://docs.ultralytics.com/datasets/segment/package-seg/) | Segmentierung | 1 (Paket) | 103 MB | Logistik |
| [**Hand Keypoints**](https://docs.ultralytics.com/datasets/pose/hand-keypoints/) | Pose | 21 Punkte | mittel | Gestensteuerung |
| [**DOTA8**](https://docs.ultralytics.com/datasets/obb/dota8/) | OBB | 15 | 8 Bilder | Luftbilder ausprobieren |

!!! example "🧪 Erkundungsauftrag (10 min)"
    Wähle **zwei** Datensätze aus der Tabelle und öffne ihre Ultralytics-Seite. Notiere für jeden:

    1. Wie viele Bilder gibt es in **train**, **val** und **test**?
    2. Wie sehen die Beispielbilder aus – sind die Objekte groß oder klein, einzeln oder dicht gedrängt?
    3. Welche **Schwierigkeiten** erwartest du beim Training (z. B. ähnliche Klassen, wenig Bilder, kleine Objekte)?
    4. **Bonus:** Suche auf [Roboflow Universe](https://universe.roboflow.com/) nach „pcb components“ oder „resistor“. Was findest du?

## Wie ist ein YOLO-Datensatz aufgebaut?

Jeder Datensatz im YOLO-Format hat dieselbe Struktur: **Zu jedem Bild gibt es eine Textdatei mit gleichem Namen**, in der die Labels stehen.

```text
african-wildlife/
├── images/
│   ├── train/          ← Trainingsbilder  (~70 %)  → daraus lernt das Modell
│   │   ├── 1 (1).jpg
│   │   └── …
│   ├── val/            ← Validierungsbilder (~15 %) → Kontrolle während des Trainings
│   └── test/           ← Testbilder (~15 %)         → Abschlussprüfung, nie im Training gesehen
└── labels/
    ├── train/
    │   ├── 1 (1).txt   ← Labels zu „1 (1).jpg“
    │   └── …
    ├── val/
    └── test/
```

!!! abstract "Warum drei Teile? – Ein Vergleich aus der Schule"
    - **train** = die Übungsaufgaben, mit denen du lernst.
    - **val** = die Probe-Klausur: Du prüfst zwischendurch, ob du wirklich verstanden hast – oder nur auswendig gelernt.
    - **test** = die echte Abschlussprüfung mit **neuen** Aufgaben. Erst hier zeigt sich, wie gut du wirklich bist.

    Würde man mit den Prüfungsaufgaben üben, wäre die Note geschönt. Genauso darf ein Modell die Val- und Testbilder **nie** zum Lernen benutzen.

<div class="quiz" data-titel="Kurz-Check: Datensätze" data-quiz='[
 {"q": "Wozu dienen die Validierungsbilder (val)?",
  "a": ["Das Modell lernt hauptsächlich aus ihnen", "Sie kontrollieren während des Trainings, wie gut das Modell auf ungesehenen Bildern ist", "Sie werden gelöscht", "Sie enthalten keine Labels"],
  "c": 1, "e": "Val-Bilder werden nach jeder Epoche geprüft, aber nie zum Lernen der Gewichte verwendet."},
 {"q": "Zum Bild images/train/platine_07.jpg gehört die Label-Datei …",
  "a": ["labels/train/platine_07.txt", "images/train/platine_07.txt", "labels/platine.txt", "classes.txt"],
  "c": 0, "e": "Gleicher Dateiname, Ordner images wird durch labels ersetzt, Endung .txt."},
 {"q": "Du findest auf Roboflow Universe einen passenden Datensatz. Was prüfst du vor der Nutzung in einem Firmenprojekt?",
  "a": ["Nur die Anzahl der Bilder", "Die Lizenz und ob die Bilder zu meiner Anwendung passen", "Ob der Datensatz bunt ist", "Nichts, alles im Internet ist frei"],
  "c": 1, "e": "Lizenz und Passung (Kamera, Licht, Objekte) entscheiden, ob ein Datensatz brauchbar ist."}
]'></div>
