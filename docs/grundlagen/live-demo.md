# Live-Demo: YOLO im Browser

Hier läuft ein **echtes YOLO26-Modell** (Größe *nano*, trainiert auf dem COCO-Datensatz mit 80 Alltagsklassen) direkt
in deinem Browser. Es wird nichts hochgeladen – die Berechnung passiert komplett auf deinem Rechner.

1. Klicke auf **▶ Modell laden** (einmalig ca. 10 MB).
2. Probiere die Beispielbilder, ein eigenes Foto oder deine **Webcam**.
3. Halte Gegenstände in die Kamera: Tasse, Handy, Schere, Buch, Flasche, Maus, Tastatur …

<div class="exp live-demo" data-modell="../../assets/models/yolo26n.onnx" data-bilder="../../assets/img/"></div>

## 🧪 Experimente mit der Demo

!!! example "Experiment 1 – Die Confidence-Schwelle"
    Jede erkannte Box hat einen **Confidence-Wert** zwischen 0 und 1: Wie sicher ist sich das Modell?

    - Stelle die Schwelle auf **0,05**. Was passiert?
    - Stelle sie auf **0,80**. Was verschwindet?
    - Welcher Wert ist für eine **Sicherheitsanwendung** (lieber einmal zu viel warnen) sinnvoll, welcher für eine **Zählung** (keine falschen Treffer)?

!!! example "Experiment 2 – Ohne NMS sieht das Modell doppelt"
    Das Netz liefert zunächst **8400 Kandidaten-Boxen** pro Bild. Viele davon liegen fast übereinander auf demselben Objekt.
    Die **Non-Maximum Suppression (NMS)** räumt auf: Von überlappenden Boxen derselben Klasse bleibt nur die sicherste.

    - Nimm das Häkchen bei **NMS aktiv** heraus. Wie viele Boxen siehst du jetzt am Bus?
    - Aktiviere NMS wieder und schiebe den Regler **NMS-IoU** auf **0,95**. Warum tauchen wieder Doppel-Boxen auf?

    ??? note "Vertiefung: YOLO26 kann auch ohne NMS"
        Das neue **YOLO26** hat zusätzlich einen *End-to-End-Kopf*, der direkt höchstens 300 fertige Boxen ausgibt –
        ganz ohne NMS. Das macht es auf CPUs und Kleinstrechnern schneller und einfacher einsetzbar. Für diese Demo
        verwenden wir bewusst den klassischen Kopf, damit du NMS sehen und ausprobieren kannst.

!!! example "Experiment 3 – Grenzen finden"
    - Was erkennt das Modell **nicht**? Probiere z. B. einen Widerstand, einen Schraubendreher oder ein Multimeter.
    - Warum klappt das nicht? *(Tipp: Schau dir die Liste der 80 COCO-Klassen an – unten aufklappen.)*

    ??? info "Die 80 Klassen des COCO-Datensatzes"
        person, bicycle, car, motorcycle, airplane, bus, train, truck, boat, traffic light, fire hydrant, stop sign,
        parking meter, bench, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack, umbrella,
        handbag, tie, suitcase, frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard,
        surfboard, tennis racket, bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple, sandwich, orange,
        broccoli, carrot, hot dog, pizza, donut, cake, chair, couch, potted plant, bed, dining table, toilet, tv, laptop,
        mouse, remote, keyboard, cell phone, microwave, oven, toaster, sink, refrigerator, book, clock, vase, scissors,
        teddy bear, hair drier, toothbrush

!!! success "Merke"
    Ein vortrainiertes Modell erkennt nur die Klassen, die es im Training gesehen hat. Für **eigene Objekte**
    (Bauteile, Werkzeuge, Fehlerbilder …) musst du das Modell **mit eigenen Bildern nachtrainieren**.
    Genau das lernst du in diesem Kurs.

<div class="quiz" data-titel="Kurz-Check: Live-Demo" data-quiz='[
 {"q": "Du senkst die Confidence-Schwelle von 0,5 auf 0,1. Was passiert typischerweise?",
  "a": ["Es werden weniger Boxen angezeigt", "Es werden mehr Boxen angezeigt – auch mehr Fehlalarme", "Das Modell wird genauer", "Die Rechenzeit sinkt stark"],
  "c": 1, "e": "Eine niedrige Schwelle lässt auch unsichere Vorhersagen durch: mehr Treffer, aber auch mehr Fehlalarme."},
 {"q": "Wofür ist die Non-Maximum Suppression (NMS) da?",
  "a": ["Sie entfernt doppelte Boxen für dasselbe Objekt", "Sie macht das Bild schärfer", "Sie trainiert das Modell nach", "Sie übersetzt die Klassennamen"],
  "c": 0, "e": "NMS behält von stark überlappenden Boxen derselben Klasse nur die mit der höchsten Confidence."},
 {"q": "Warum erkennt das Demo-Modell keinen Widerstand?",
  "a": ["Die Webcam ist zu schlecht", "Widerstände sind zu klein für KI", "Die Klasse kam im Trainingsdatensatz (COCO) nicht vor", "Das Modell ist kaputt"],
  "c": 2, "e": "Ein Modell kann nur Klassen ausgeben, die es gelernt hat. Für Widerstände braucht man eigene, gelabelte Trainingsbilder."}
]'></div>
