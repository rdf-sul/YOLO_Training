# Modell testen mit Ultralytics Solutions

Ein trainiertes Modell allein ist noch keine Anwendung. **[Ultralytics Solutions](https://docs.ultralytics.com/solutions/)**
sind fertige Bausteine, mit denen du dein Modell sofort **praktisch einsetzen** kannst – ohne selbst viel zu programmieren.

[![Ultralytics Solutions](https://cdn.ul.run/i/af2a06dd04b546ae345e818580d16e7e.avif){ loading=lazy width=640 }](https://docs.ultralytics.com/solutions/)
<small>Grafik: © Ultralytics, [docs.ultralytics.com/solutions](https://docs.ultralytics.com/solutions/) (AGPL-3.0)</small>

## Eine Auswahl

| Solution | CLI-Name | Was macht sie? | Idee für die Praxis |
|---|---|---|---|
| **Live-Inferenz (Streamlit)** | `inference` | Web-App im Browser: Modell wählen, Webcam/Video, Regler für Confidence | schneller Test jedes Modells |
| **Objekte zählen** | `count` | zählt Objekte, die eine Linie oder Fläche überqueren (rein/raus) | Bauteile auf dem Förderband zählen |
| **Zählen in Regionen** | `region` | zählt Objekte in festgelegten Bereichen | Belegung von Lagerfächern |
| **Heatmap** | `heatmap` | zeigt, wo sich Objekte häufig aufhalten | Laufwege in der Werkstatt |
| **Geschwindigkeit** | `speed` | schätzt die Geschwindigkeit bewegter Objekte | Förderbandgeschwindigkeit |
| **Warteschlange** | `queue` | zählt Objekte in einer Warteschlangen-Zone | Kassen, Ladestationen |
| **Unkenntlich machen** | `blur` | verwischt erkannte Objekte | Datenschutz: Gesichter/Personen verpixeln |
| **Ausschneiden** | `crop` | speichert jedes erkannte Objekt als eigenes Bild | Datensammlung für neue Trainingsbilder |
| **Sicherheitsalarm** | `security` | Alarm, wenn Objekte erkannt werden | Person im Gefahrenbereich |
| **Workout** | `workout` | zählt Wiederholungen mit Pose-Modell | Ergonomie-Analyse |

!!! info "Warum lokal und nicht in Colab?"
    Die Solutions zeigen ihre Ergebnisse in einem **Fenster** oder einer **Web-App** und nutzen gerne die **Webcam** –
    beides funktioniert in Colab nicht gut. Deshalb arbeiten wir hier **auf dem eigenen Laptop** mit **uv**.
    Für Vorhersagen reicht die CPU völlig aus.

## Vorbereitung

1. [uv installieren](../grundlagen/installation-uv.md) (falls noch nicht geschehen).
2. Projekt anlegen und Pakete installieren:

    ```bash
    uv init yolo-lokal --python 3.12
    cd yolo-lokal
    uv add ultralytics streamlit
    ```

3. Dein trainiertes Modell aus Colab (z. B. `wildlife_n_30ep_best.pt`) in den Ordner `yolo-lokal` kopieren.

!!! tip "Kein eigenes Modell zur Hand?"
    Verwende einfach `yolo26n.pt` (COCO, 80 Klassen). Es wird automatisch heruntergeladen und erkennt z. B. Personen,
    Handys, Tassen und Flaschen – ideal zum Testen mit der Webcam.

## 1 · Live-Inferenz im Browser (Streamlit)

```bash
uv run yolo solutions inference model=wildlife_n_30ep_best.pt
```

Im Terminal erscheint eine Adresse wie `http://localhost:8501` – öffne sie im Browser. In der App kannst du
links die **Quelle** (Webcam oder Video), die **Klassen** und die **Confidence** wählen.

!!! example "🧪 Experiment"
    1. Öffne auf dem Handy ein **Bild eines Zebras oder Nashorns** und halte es in die Webcam. Wird es erkannt?
    2. Was passiert bei einem **Spielzeugtier** oder einer **Zeichnung**?
    3. Ab welcher **Entfernung** und welchem **Winkel** versagt das Modell?
    4. Vergleiche mit `model=yolo26n.pt`: Welches Modell erkennt Zebras besser – und warum?

## 2 · Objekte zählen

Mit der Webcam (`source=0`) und einer Zähllinie:

```bash
uv run yolo solutions count source=0 model=yolo26n.pt show=True region="[(320, 0), (320, 480)]"
```

- `region` ist eine **Linie** (2 Punkte) oder eine **Fläche** (4+ Punkte) in Pixel-Koordinaten.
- Gezählt wird, wenn ein Objekt die Linie **überquert** – getrennt nach rein (*IN*) und raus (*OUT*).
- Beenden mit ++q++ im Fenster. Das Ergebnisvideo liegt in `runs/solutions/exp/`.

??? note "Dasselbe als Python-Skript – zum Anpassen"
    ```python title="zaehlen.py"
    import cv2
    from ultralytics import solutions

    cap = cv2.VideoCapture(0)                        # 0 = Webcam, oder "video.mp4"
    zaehler = solutions.ObjectCounter(
        model="yolo26n.pt",                          # oder dein eigenes Modell
        region=[(320, 0), (320, 480)],               # senkrechte Zähllinie in der Bildmitte
        classes=[39, 41, 67],                        # nur Flasche, Tasse, Handy (COCO-Nummern)
        show=True,
    )

    while cap.isOpened():
        ok, bild = cap.read()
        if not ok:
            break
        ergebnis = zaehler(bild)
        print("rein:", ergebnis.in_count, "raus:", ergebnis.out_count, end="\r")
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    ```

    ```bash
    uv run zaehlen.py
    ```

## 3 · Heatmap

```bash
uv run yolo solutions heatmap source=0 model=yolo26n.pt show=True
```

Bewege dich (oder einen Gegenstand) vor der Kamera. Bereiche, in denen sich Objekte oft aufhalten, werden „wärmer“ eingefärbt.

## 4 · Weitere Solutions ausprobieren

```bash
uv run yolo solutions help                                     # Übersicht aller Solutions
uv run yolo solutions blur source=0 model=yolo26n.pt show=True classes=0   # Personen verpixeln
uv run yolo solutions workout source=0 model=yolo26n-pose.pt show=True     # Übungen zählen (Pose)
```

!!! example "🧪 Mini-Challenge (15 min)"
    Überlege dir eine kleine Anwendung für die Werkstatt oder das Labor und setze sie mit einer Solution um.
    Beispiele:

    - **„Handy-Detektor“**: Zähle, wie oft ein Handy in den Arbeitsbereich gelegt wird (`count`, Klasse 67).
    - **„Datenschutz-Kamera“**: Alle Personen werden automatisch verpixelt (`blur`, Klasse 0).
    - **„Werkzeug-Ablage“**: Ist eine Schere in der Ablagefläche? (`region`, Klasse 76)

    Präsentiert eure Lösung in 1 Minute: Welche Solution, welche Parameter, wo sind die Grenzen?

!!! success "Ausblick auf das Projekt"
    Damit hast du alle Bausteine zusammen: **Daten → Labeln → Trainieren → Bewerten → Anwenden.**
    Im [Projekt](../projekt/index.md) baust du das alles für **deine eigene Problemstellung** – mit eigenen Fotos.

<div class="quiz" data-titel="Kurz-Check: Solutions" data-quiz='[
 {"q": "Mit welchem Befehl startest du die Streamlit-Web-App mit deinem eigenen Modell?",
  "a": ["uv run yolo solutions inference model=best.pt", "uv run yolo train model=best.pt", "pip install streamlit", "uv run yolo solutions count"],
  "c": 0, "e": "Die Solution inference startet eine Streamlit-App im Browser."},
 {"q": "Was bedeutet source=0?",
  "a": ["Kein Video", "Die erste Webcam", "Das erste Bild im Ordner", "Klasse 0"],
  "c": 1, "e": "source=0 ist die Standard-Webcam des Rechners."},
 {"q": "Du willst Bauteile zählen, die auf einem Förderband eine Lichtschranken-Position passieren. Welche Solution passt?",
  "a": ["heatmap", "blur", "count mit einer Linie als region", "workout"],
  "c": 2, "e": "ObjectCounter zählt Objekte, die eine definierte Linie überqueren – wie eine virtuelle Lichtschranke."}
]'></div>
