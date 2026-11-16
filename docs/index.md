---
title: Start
hide:
  - navigation
---

# Bilder-KI verstehen und selbst trainieren

**Willkommen!** Auf dieser Seite lernst du, wie eine Bilder-KI Objekte erkennt – und wie du selbst eine trainierst.
Wir arbeiten mit **Ultralytics YOLO**, einem der bekanntesten Werkzeuge für Objekterkennung in Echtzeit.
Es wird in der Industrie z. B. für Qualitätsprüfung, Zählen von Bauteilen und Arbeitssicherheit eingesetzt.

!!! tip "Starte mit einem Aha-Erlebnis"
    Bevor es um Theorie geht: Öffne die **[Live-Demo](grundlagen/live-demo.md)** und lass ein fertiges YOLO-Modell
    direkt in deinem Browser deine Webcam analysieren. Danach verstehst du Schritt für Schritt, was da passiert.

## Was dich erwartet

<div class="kacheln" markdown>
<a class="kachel" href="grundlagen/"><span class="nr">Einheit 1</span><strong>:material-lightbulb-on-outline: Grundlagen</strong><span class="txt">Was ist YOLO? Detektion, Segmentierung, Pose, OBB … Welches Modell wofür? Installation mit uv.</span></a>
<a class="kachel" href="daten/"><span class="nr">Einheit 2</span><strong>:material-database-outline: Daten</strong><span class="txt">Woher bekomme ich Bilder? Wie labelt man? Was steht in der data.yaml?</span></a>
<a class="kachel" href="training/"><span class="nr">Einheit 3</span><strong>:material-chart-bell-curve-cumulative: Training</strong><span class="txt">Ablauf, Parameter wie Epochen und Batch – und wie man Confusion Matrix & mAP liest.</span></a>
<a class="kachel" href="praxis/"><span class="nr">Einheit 4</span><strong>:material-rocket-launch-outline: Praxis</strong><span class="txt">Dein erstes eigenes Training in Google Colab und Live-Test mit Ultralytics Solutions.</span></a>
<a class="kachel" href="projekt/"><span class="nr">Einheit 5</span><strong>:material-hammer-wrench: Projekt</strong><span class="txt">Eigene Bilder, eigene Labels, eigenes Modell: mit drei Projekt-Notebooks und gezieltem Nachtraining.</span></a>
</div>

## So arbeitest du mit dieser Seite

| Symbol | Bedeutung |
|---|---|
| 🧪 **Experiment** | Interaktive Elemente direkt auf der Seite. Probier aus, verschiebe Regler, beobachte! |
| ❓ **Kurz-Check** | Kleine Quizze am Ende der Seiten. Ergebnisse werden nicht gespeichert – sie sind nur für dich. |
| :material-google-colab: **Colab** | Aufgaben, die du im Jupyter Notebook in Google Colab ausführst (kostenlose GPU). |
| :material-chevron-down-box-outline: **Vertiefung** | Aufklappbare Kästen mit Zusatzwissen. Für den Kurs nicht nötig – aber spannend. |

!!! info "Was du brauchst"
    - einen Laptop mit aktuellem Browser (Chrome, Edge oder Firefox) und am besten einer Webcam
    - ein Google-Konto für **Google Colab**
    - für den lokalen Teil: [**uv**](grundlagen/installation-uv.md) (Python-Paketmanager, Installation dauert 1 Minute)

??? note "Über diese Seite"
    Diese Seite ist Unterrichtsmaterial für angehende Elektrotechniker:innen.
    Sie orientiert sich am Aufbau der offiziellen [Ultralytics-Dokumentation](https://docs.ultralytics.com/de/), ist aber
    didaktisch reduziert. Grafiken und Beispiel-Datensätze von Ultralytics werden mit Quellenangabe verlinkt.
    Ultralytics-Software und -Modelle stehen unter der Lizenz [AGPL-3.0](https://www.ultralytics.com/license).

    **Lizenz dieses Materials:** Texte und eigene Grafiken stehen unter
    [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.de), der Code (Notebooks, Projektvorlage,
    JavaScript) und das Browser-Modell unter der [AGPL-3.0](https://github.com/rdf-sul/YOLO_Training/blob/main/LICENSE).
    Du darfst alles nutzen, verändern und weitergeben, wenn du die Quelle nennst und Veränderungen unter derselben
    Lizenz teilst.
