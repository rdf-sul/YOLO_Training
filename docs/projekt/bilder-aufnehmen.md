# Gute Trainingsbilder

> **Ein Modell kann nur lernen, was in den Trainingsbildern vorkommt.**
> Die Welt deines Modells ist dein Datensatz, nicht mehr und nicht weniger.

Diese Seite erklärt die **Regeln** für das Fotografieren. In Notebook P1 findest du sie als Kurzfassung wieder,
zusammen mit einem automatisch berechneten **Aufnahmeplan**.

## Regel 1 · Training = Einsatz

Das Modell vergleicht ein neues Bild mit allem, was es im Training gesehen hat. Je **ähnlicher** die Trainingsbilder
der späteren Einsatzsituation sind, desto besser funktioniert es.

| Merkmal | Frage an dein Projekt |
|---|---|
| **Kamera** | Läuft das Modell später auf der Webcam, dem Handy oder einer Industriekamera? |
| **Perspektive** | Von oben? Schräg? Aus welcher Entfernung? |
| **Umgebung** | Welcher Tisch, welche Unterlage, was liegt sonst noch herum? |
| **Licht** | Tageslicht, Werkstattbeleuchtung, Schatten, Reflexionen? |

!!! example "Beispiel"
    Ein Modell, das nur mit scharfen 12-MP-Handyfotos auf weißem Papier trainiert wurde, erkennt Bauteile auf der
    grünen Schneidematte unter der rauschenden Laptop-Webcam oft **gar nicht**, obwohl es auf val super Werte hatte.
    Die Validierungsbilder stammten ja aus derselben „Handy-auf-Papier-Welt“.

## Regel 2 · Vielfalt schlägt Menge

100 **verschiedene** Situationen sind wertvoller als 1.000 fast gleiche Fotos.
Das Modell soll das **Objekt** lernen, nicht die Situation.

| Was variieren? | Beispiele |
|---|---|
| Hintergrund | Papier, Holz, Matte, Platine, Hand |
| Licht | hell/dunkel, warm/kalt, Schatten, seitlich |
| Abstand und Größe | nah, mittel, weit |
| Lage | gedreht, schräg, liegend, gestapelt |
| Anzahl | ein Objekt bis viele, gemischte Klassen |
| Verdeckung | sich berührend, halb verdeckt, am Bildrand angeschnitten |
| Exemplare | verschiedene Farben, Größen, Hersteller |

### Die „Kluger-Hans“-Falle

Um 1900 konnte das Pferd **„Kluger Hans“** angeblich rechnen. Es klopfte die richtige Antwort mit dem Huf.
In Wahrheit las es an winzigen Bewegungen des Fragestellers ab, wann es aufhören sollte.
Es hatte eine **Abkürzung** gelernt, nicht das Rechnen.

KI-Modelle machen genau dasselbe: Sie lernen die **einfachste** Regel, die zu den Trainingsdaten passt.

| Datensatz | Was das Modell lernt | Folge im Einsatz |
|---|---|---|
| alle LEDs auf weißem Papier, alle Widerstände auf grüner Matte | „weißer Hintergrund → LED“ | Widerstand auf Papier wird zur „LED“ |
| alle Taster mit Blitz fotografiert | „heller Lichtreflex → Taster“ | ohne Blitz werden Taster übersehen |
| Kondensatoren immer in der Bildmitte | „Mitte → Kondensator“ | am Bildrand übersehen |

**Gegenmittel:** Jede Klasse kommt auf **jedem** Hintergrund und in **jeder** Lichtsituation vor.
Der Aufnahmeplan in P1 hilft dir dabei.

## Regel 3 · Genug Beispiele pro Klasse

Gezählt werden **Objekte** (Boxen), nicht Bilder.

| Stufe | Objekte pro Klasse | Wofür |
|---|---|---|
| 🟡 Prototyp | ab ca. 100 | einfache, gut unterscheidbare Objekte, feste Umgebung |
| 🟢 **Solides Projekt** | **200–300** | mehrere Hintergründe und Lichtsituationen |
| 🔵 Profi (Ultralytics-Empfehlung) | ≥ 1.500 Bilder und ≥ 10.000 Objekte | wechselnde, unkontrollierte Bedingungen |

Dass für Schulprojekte schon wenige hundert Beispiele reichen, liegt am **Transfer Learning**: Das Startmodell
`yolo26n.pt` hat an über 100.000 COCO-Bildern bereits gelernt, Kanten, Formen und Objekte zu sehen.
Es muss nur noch **deine** Klassen dazulernen.

!!! info "Ausgewogenheit"
    Alle Klassen sollten **ungefähr gleich oft** vorkommen. Hat eine Klasse 400 Objekte und eine andere 40,
    „lohnt“ es sich für das Modell kaum, die seltene Klasse zu lernen.

## Regel 4 · Hintergrundbilder

**5–10 %** deiner Bilder sollten **keine** Zielobjekte zeigen, aber typische **Störer**: Kabel, Schrauben,
andere Bauteile, Werkzeug. Beim Labeln schickst du sie einfach **ohne Box** ab.
Sie zeigen dem Modell, was es **nicht** melden soll, und senken die Zahl der Fehlalarme.

## Regel 5 · Objekte nicht zu klein

Für das Training werden alle Bilder auf **640 Pixel** (längste Seite) verkleinert. Ein Objekt, das auf deinem
1280-px-Foto 30 Pixel breit ist, hat beim Training nur noch

$$
30\,\text{px} \cdot \frac{640}{1280} = 15\,\text{px}.
$$

Das ist an der Grenze dessen, was YOLO noch erkennen kann. Faustregel: Ein Objekt sollte mindestens etwa
**1/20 der Bildbreite** groß sein. Probiere es aus: Bei kleiner Bildgröße verschwinden Details.

<div class="exp" data-exp="imgsz" data-bild="../../assets/img/zidane.jpg"></div>

Sind deine Objekte zwangsläufig klein (Lötstellen, SMD-Bauteile), gibt es zwei Auswege:
**näher heran** fotografieren oder in P3 mit `BILDGROESSE = 1280` trainieren. Das dauert etwa 4× länger.

## Regel 6 · Technische Sauberkeit

| ✅ | ❌ |
|---|---|
| scharf, ruhig gehalten, Autofokus abwarten | verwackelt, Bewegungsunschärfe |
| normaler Fotomodus | Porträtmodus, Beauty-Filter, Digitalzoom, Blitz |
| Originaldatei per Kabel/Cloud übertragen | per Messenger verschickt (wird komprimiert) |
| zwischen zwei Fotos etwas verändern (auch bei der Serienaufnahme) | 30 Serienfotos derselben Szene |
| nur Objekte im Bild | Gesichter, Namen, Bildschirme mit privaten Daten |

??? note "Vertiefung: Warum schaden fast gleiche Fotos?"
    Fast gleiche Fotos bringen dem Modell kaum neue Information. Sie haben aber noch einen zweiten, versteckten
    Nachteil: Landet ein Foto im **Training** und sein „Zwilling“ in der **Validierung**, kennt das Modell die
    Prüfungsaufgabe schon. Die Kennzahlen werden **zu gut** und täuschen dich. Fachleute nennen das
    **Data Leakage** (Datenleck). P2 erkennt fast gleiche Bilder deshalb automatisch und steckt sie in dieselbe Teilmenge.
    Am besten vermeidest du Serienfotos aber schon beim Fotografieren.

## Handy oder Webcam?

| | 📱 Handy | 💻 Webcam |
|---|---|---|
| Bildqualität | sehr gut | mittel, rauschig, Weitwinkel |
| Tempo | viele Fotos schnell, überall | Serienaufnahme direkt am Rechner (P1, Abschnitt 4b) |
| Typische Falle | **EXIF-Drehung**, HEIC-Format | Autofokus, Bewegungsunschärfe |

**Empfehlung:** Mindestens die **Hälfte** der Fotos mit der **Einsatzkamera**, den Rest gern mit anderen Kameras.
Ein Mix macht das Modell robuster.

<div class="quiz" data-titel="Kurz-Check: Gute Trainingsbilder" data-quiz='[
 {"q": "Dein Modell soll später mit der Laptop-Webcam am Laborplatz laufen. Womit fotografierst du die Trainingsbilder?",
  "a": ["Nur mit dem Handy, denn bessere Bilder ergeben ein besseres Modell", "Überwiegend mit der Webcam am Laborplatz, ergänzt durch andere Kameras", "Nur mit der Webcam, andere Kameras verwirren das Modell", "Mit dem Handy, die Bilder werden ja ohnehin verkleinert"],
  "c": 1, "e": "Trainingsbilder sollen dem Einsatz ähneln. Ein Mix mit anderen Kameras macht das Modell zusätzlich robuster."},
 {"q": "Alle Widerstände wurden auf der grünen Matte fotografiert, alle LEDs auf weißem Papier. Was ist das Problem?",
  "a": ["Zu wenig Kontrast zwischen Objekt und Hintergrund", "Das Modell lernt womöglich den Hintergrund statt der Form („Kluger Hans“)", "Das Modell wird dadurch nur etwas ungenauer, das ist unkritisch", "Zu wenige Bilder pro Klasse"],
  "c": 1, "e": "Jede Klasse muss auf jedem Hintergrund vorkommen, sonst lernt das Modell eine Abkürzung."},
 {"q": "Du hast 60 Fotos mit je 5 Widerständen. Wie viele Widerstands-Beispiele sind das?",
  "a": ["60", "5", "300", "12"],
  "c": 2, "e": "Gezählt werden Objekte: 60 × 5 = 300."},
 {"q": "Wozu dienen Hintergrundbilder ohne Zielobjekte?",
  "a": ["Sie sparen Labelzeit", "Sie zeigen dem Modell, was es nicht melden soll, und verringern Fehlalarme", "Sie erhöhen vor allem den Recall", "Sie stören das Training und sollten gelöscht werden"],
  "c": 1, "e": "Hintergrundbilder mit typischen Störern sind ein wirksames Mittel gegen Fehlalarme."},
 {"q": "Ein Bauteil ist auf deinem 1280-px-Foto 24 px breit. Wie breit ist es beim Training mit imgsz = 640?",
  "a": ["48 px", "24 px", "12 px", "6 px"],
  "c": 2, "e": "24 · 640 / 1280 = 12 px, das ist sehr klein. Näher heran fotografieren!"}
]'></div>
