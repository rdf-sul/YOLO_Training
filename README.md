# YOLO Training – Bilder-KI verstehen und trainieren

Unterrichtsmaterial zur Objekterkennung mit **Ultralytics YOLO26** für angehende Elektrotechniker:innen.

**📖 Lernseite:** https://rdf-sul.github.io/YOLO_Training/

| Einheit | Inhalt |
|---|---|
| 1 · Grundlagen | Live-Demo im Browser, YOLO & Ultralytics, Aufgabenarten, Modellwahl, Installation mit uv |
| 2 · Daten | Datensätze finden, Labeln (Label Studio), data.yaml |
| 3 · Training | Ablauf, Parameter, Ergebnisse verstehen (Loss, Precision/Recall, mAP, Confusion Matrix) |
| 4 · Praxis | Erstes Training in Google Colab, Test mit Ultralytics Solutions |
| 5 · Projekt | Gute Trainingsbilder, P1 Daten sammeln, P2 Labeln und prüfen, P3 Training in Colab, Nachtraining |

**🚀 Erstes Training in Colab:**
[![In Colab öffnen](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rdf-sul/YOLO_Training/blob/main/notebooks/01_erstes_training.ipynb)

## Aufbau

```text
docs/                 Inhalte der Lernseite (Markdown, MkDocs Material)
  assets/js/          Quiz, interaktive Experimente, Live-Demo (ONNX Runtime Web)
  assets/models/      YOLO26n als ONNX für die Browser-Demo
notebooks/            Jupyter Notebooks für Google Colab
projekt-vorlage/      Vorlage für das eigene Projekt (P1–P3, werkzeuge.py)
hooks/                MkDocs-Hook: packt die Projektvorlage als ZIP
mkdocs.yml            Konfiguration der Lernseite
pyproject.toml        Python-Abhängigkeiten (uv)
```

## Lernseite lokal starten

```bash
uv sync
uv run mkdocs serve
```

Dann http://127.0.0.1:8000/YOLO_Training/ öffnen. Bei jedem Push auf `main` wird die Seite automatisch
über GitHub Actions auf GitHub Pages veröffentlicht.

Die optionale Gruppe `ml` (`uv sync --group ml`) enthält Ultralytics und ONNX – nur nötig, um Beispielbilder
oder das Browser-Modell neu zu erzeugen.

## Lizenz

| Teil | Lizenz |
|---|---|
| **Code**: Notebooks (`notebooks/`, `projekt-vorlage/`), `werkzeuge.py`, JavaScript in `docs/assets/js/`, Hooks, Workflow sowie das Modell `docs/assets/models/yolo26n.onnx` | [GNU AGPL-3.0](LICENSE) |
| **Texte und eigene Grafiken** der Lernseite (`docs/`, sofern nicht anders gekennzeichnet) | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.de) |

Du darfst das Material nutzen, verändern und weitergeben. Bedingungen: Nenne die Quelle
(„YOLO Training – Bilder-KI verstehen und trainieren, https://rdf-sul.github.io/YOLO_Training/“) und gib Veränderungen
unter derselben Lizenz weiter.

**Fremdmaterial:** Ultralytics-Software, -Modelle (YOLO26n, auch als ONNX-Export) und die Beispielbilder
`bus.jpg`/`zidane.jpg` stammen von [Ultralytics](https://github.com/ultralytics/ultralytics) und stehen unter der
[AGPL-3.0](https://www.ultralytics.com/license). Grafiken aus der Ultralytics-Dokumentation werden nur verlinkt.
Die Screenshots zeigen die Oberfläche von [Label Studio](https://labelstud.io/) (HumanSignal, Apache-2.0).
