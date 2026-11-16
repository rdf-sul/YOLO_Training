# Glossar

AP – Average Precision
:   Fläche unter der Precision-Recall-Kurve **einer** Klasse. Wert zwischen 0 und 1. → [Ergebnisse verstehen](training/ergebnisse.md#map)

Augmentation (Datenvermehrung)
:   Zufällige Veränderung der Trainingsbilder (Spiegeln, Helligkeit, Mosaik …), damit das Modell robuster wird.

Batch
:   Anzahl Bilder, die gleichzeitig verarbeitet werden, bevor die Gewichte angepasst werden.

best.pt / last.pt
:   Gespeicherte Modelle nach dem Training: das **beste** (höchste mAP50-95 auf den Validierungsbildern) und das **letzte**.

Bounding Box
:   Rechteck, das ein Objekt umschließt. Bei YOLO als `x_mitte y_mitte breite höhe` (normiert) gespeichert.

Catastrophic Forgetting
:   Ein Modell „vergisst“ Gelerntes, wenn es nur noch mit neuen Bildern weitertrainiert wird. Gegenmittel: alte und neue Bilder gemeinsam trainieren. → [Nachtraining](projekt/nachtraining.md)

Checkpoint / resume
:   Zwischenstand eines Trainings (`last.pt`) mit Gewichten, Optimierer und Epochennummer. Mit `resume=True` geht ein unterbrochenes Training dort weiter. → [P3](projekt/p3-training.md)

COCO
:   Großer Standard-Datensatz (Common Objects in Context) mit 80 Alltagsklassen. Die vortrainierten YOLO-Modelle kennen diese Klassen.

Confidence
:   Wie sicher sich das Modell bei einer Vorhersage ist (0 bis 1).

Confusion Matrix
:   Tabelle, die zeigt, welche Klasse als welche erkannt wurde – inklusive Hintergrund (übersehen / Fehlalarm).

Data Leakage (Datenleck)
:   Informationen aus den Prüfbildern gelangen ins Training, z. B. fast gleiche Serienfotos in train und val. Die Kennzahlen werden dann zu gut. → [P2](projekt/p2-labeln.md#9-aufteilen-in-train-val-test)

Early Stopping / patience
:   Automatischer Abbruch des Trainings, wenn sich die Validierung eine bestimmte Anzahl Epochen lang nicht verbessert.

Epoche
:   Ein vollständiger Durchlauf durch alle Trainingsbilder.

EXIF
:   Metadaten in Fotos, u. a. die Ausrichtung („bitte um 90° drehen“). Wird nicht von jedem Programm beachtet. → [P1](projekt/p1-daten-sammeln.md)

F1-Score
:   Harmonisches Mittel aus Precision und Recall: \( F1 = 2 \cdot \frac{P \cdot R}{P + R} \).

Feintuning (Fine-Tuning)
:   Ein schon trainiertes Modell (z. B. `best.pt`) mit erweiterten Daten weitertrainieren. → [Nachtraining](projekt/nachtraining.md)

FN – False Negative
:   Ein vorhandenes Objekt wurde **übersehen**.

FP – False Positive
:   **Fehlalarm**: Das Modell meldet ein Objekt, wo keines (oder ein anderes) ist.

Ground Truth
:   Die „richtige Antwort“ – also die von Menschen erstellten Labels.

Hintergrundbild
:   Trainingsbild ohne Zielobjekte, aber mit typischen Störern. Senkt Fehlalarme.

imgsz
:   Bildgröße in Pixeln, auf die Bilder für Training und Vorhersage skaliert werden (Standard 640).

Inferenz
:   Anwenden eines fertigen Modells auf neue Bilder (Vorhersage).

IoU – Intersection over Union
:   Überlappung zweier Boxen: Schnittfläche ÷ Vereinigungsfläche. 1 = deckungsgleich, 0 = keine Überlappung.

Label / Labeln
:   Markierung von Objekten auf Trainingsbildern (Klasse + Box/Maske/Punkte).

Loss
:   Fehlermaß während des Trainings. Je kleiner, desto besser passen Vorhersagen und Labels zusammen.

mAP50 / mAP50-95
:   Mittelwert der AP über alle Klassen bei IoU-Schwelle 0,5 bzw. gemittelt über die Schwellen 0,5 bis 0,95. Wichtigstes Gütemaß für Detektion.

NMS – Non-Maximum Suppression
:   Entfernt doppelte, stark überlappende Boxen derselben Klasse und behält nur die sicherste.

OBB – Oriented Bounding Box
:   Gedrehte Box mit Winkel.

Overfitting (Überanpassung)
:   Das Modell lernt die Trainingsbilder „auswendig“ und wird auf neuen Bildern schlechter.

Precision
:   Anteil der Vorhersagen, die richtig sind: \( P = \frac{TP}{TP + FP} \). „Wenn das Modell etwas meldet – stimmt es?“

Recall
:   Anteil der vorhandenen Objekte, die gefunden wurden: \( R = \frac{TP}{TP + FN} \). „Findet das Modell alles?“

Segmentierung
:   Pixelgenaue Zuordnung: **Instanz** (jedes Objekt einzeln) oder **semantisch** (jeder Pixel bekommt eine Klasse).

TP – True Positive
:   Richtig erkanntes Objekt (richtige Klasse, IoU über der Schwelle).

Transfer Learning
:   Ein vortrainiertes Modell wird mit eigenen Daten auf neue Klassen angepasst.

uv
:   Sehr schneller Python-Paket- und Projektmanager; ersetzt pip, venv und mehr.

Validierung (val)
:   Prüfung des Modells auf Bildern, die nicht zum Lernen verwendet wurden.
