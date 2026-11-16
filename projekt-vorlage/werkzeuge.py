"""
werkzeuge.py – Hilfsfunktionen für das YOLO-Projekt (P1 und P2)

Die Notebooks P1 und P2 rufen diese Funktionen auf, damit die Notebooks
kurz und übersichtlich bleiben. Du musst hier nichts ändern – darfst aber
gerne hineinschauen, wie alles funktioniert.

Ordnerstruktur des Projekts (wird automatisch angelegt):

    1_rohbilder/              ← deine Fotos, so wie sie von Handy/Webcam kommen
    2_bilder/                 ← vorbereitete Bilder (gedreht, verkleinert, umbenannt)
    3_labelstudio_export/     ← JSON-Exporte aus Label Studio (eine Datei pro Person)
    4_datensatz/              ← fertiger YOLO-Datensatz + ZIP für Colab
    projekt.yaml              ← Projekt-Steckbrief (Klassen, Ziele …)
"""

from __future__ import annotations

import base64
import csv
import datetime as dt
import hashlib
import html
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

try:  # HEIC/HEIF-Fotos von iPhones lesen können
    from pillow_heif import register_heif_opener

    register_heif_opener()
    HEIC_OK = True
except Exception:  # pragma: no cover
    HEIC_OK = False

# ──────────────────────────────────────────────────────────────────────────────
# Ordner und Projektdatei
# ──────────────────────────────────────────────────────────────────────────────
ROH = Path("1_rohbilder")
BILDER = Path("2_bilder")
AUSSORTIERT = BILDER / "_aussortiert"
EXPORT = Path("3_labelstudio_export")
DATENSATZ = Path("4_datensatz")
PROJEKTDATEI = Path("projekt.yaml")
HERKUNFT = BILDER / "_herkunft.csv"
KATALOG = Path("katalog.csv")

BILD_ENDUNGEN = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff", ".heic", ".heif"}
FARBEN = ["#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4", "#42d4f4",
          "#f032e6", "#bfef45", "#469990", "#9a6324", "#800000", "#000075"]


def ordner_anlegen() -> None:
    """Legt die Projektordner an (falls sie noch fehlen)."""
    for o in (ROH, BILDER, EXPORT, DATENSATZ):
        o.mkdir(parents=True, exist_ok=True)


def projekt_speichern(projekt: dict) -> None:
    """Speichert den Projekt-Steckbrief als projekt.yaml."""
    import yaml

    klassen = [str(k).strip() for k in projekt.get("klassen", []) if str(k).strip()]
    if not klassen:
        raise ValueError("Bitte mindestens eine Klasse eintragen.")
    if len(set(k.lower() for k in klassen)) != len(klassen):
        raise ValueError("Jede Klasse darf nur einmal vorkommen.")
    for k in klassen:
        if not re.fullmatch(r"[A-Za-z0-9_\-]+", k):
            raise ValueError(f"Klassenname „{k}“: bitte nur Buchstaben a–z, Ziffern, _ und - "
                             "(keine Leerzeichen, keine Umlaute).")
    projekt = dict(projekt, klassen=klassen)
    PROJEKTDATEI.write_text(yaml.safe_dump(projekt, allow_unicode=True, sort_keys=False), encoding="utf-8")


def projekt_laden() -> dict:
    """Liest projekt.yaml (angelegt in P1)."""
    import yaml

    if not PROJEKTDATEI.exists():
        raise FileNotFoundError("projekt.yaml fehlt – bitte zuerst in P1 den Steckbrief ausfüllen und speichern.")
    return yaml.safe_load(PROJEKTDATEI.read_text(encoding="utf-8"))


def bilder_in(ordner: Path, mit_aussortierten: bool = False) -> list[Path]:
    """Alle Bilddateien in einem Ordner (inkl. Unterordner), sortiert."""
    ordner = Path(ordner)
    if not ordner.exists():
        return []
    dateien = [p for p in ordner.rglob("*") if p.is_file() and p.suffix.lower() in BILD_ENDUNGEN]
    if not mit_aussortierten:
        dateien = [p for p in dateien if "_aussortiert" not in p.parts]
    return sorted(dateien, key=lambda p: str(p).lower())


# ──────────────────────────────────────────────────────────────────────────────
# P1 · Bilder importieren (drehen, verkleinern, umbenennen)
# ──────────────────────────────────────────────────────────────────────────────
_UMLAUTE = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss"})


def _sauberer_name(text: str) -> str:
    text = text.translate(_UMLAUTE)
    text = re.sub(r"[^A-Za-z0-9_\-]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_") or "bild"


def zielname(rohdatei: Path, roh_ordner: Path = ROH) -> str:
    """Neuer Dateiname: Unterordner + Originalname, z. B. anna_handy/IMG_0042.HEIC → anna_handy_IMG_0042.jpg"""
    rel = Path(rohdatei).relative_to(roh_ordner)
    teile = [_sauberer_name(t) for t in rel.parent.parts] + [_sauberer_name(rel.stem)]
    return "_".join(teile) + ".jpg"


def _herkunft_laden() -> dict[str, str]:
    if not HERKUNFT.exists():
        return {}
    with HERKUNFT.open(encoding="utf-8", newline="") as f:
        return {zeile["bild"]: zeile["rohdatei"] for zeile in csv.DictReader(f, delimiter=";")}


def _herkunft_speichern(eintraege: dict[str, str]) -> None:
    HERKUNFT.parent.mkdir(parents=True, exist_ok=True)
    with HERKUNFT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["bild", "rohdatei"])
        for bild, roh in sorted(eintraege.items()):
            w.writerow([bild, roh])


def bild_oeffnen(pfad: Path) -> Image.Image:
    """Öffnet ein Bild und dreht es so, wie es auf dem Handy angezeigt wurde (EXIF)."""
    with Image.open(pfad) as im:  # „with“ schließt die Datei sofort wieder (wichtig unter Windows)
        im = ImageOps.exif_transpose(im)
        if im.mode in ("RGBA", "LA", "P"):  # transparente Bereiche weiß statt schwarz
            im = im.convert("RGBA")
            weiss = Image.new("RGBA", im.size, "white")
            im = Image.alpha_composite(weiss, im)
        return im.convert("RGB")


def schon_gelabelt() -> bool:
    """True, sobald Label-Studio-Exporte vorliegen. Dann dürfen Bilder nicht mehr gedreht werden."""
    return EXPORT.exists() and any(EXPORT.glob("*.json"))


def bilder_importieren(max_seite: int = 1280, qualitaet: int = 90) -> "pd.DataFrame":
    """
    Kopiert alle Fotos aus 1_rohbilder/ nach 2_bilder/ und
      1. dreht sie richtig herum (EXIF-Drehung wird fest ins Bild übernommen),
      2. verkleinert sie, sodass die längste Seite höchstens `max_seite` Pixel hat,
      3. speichert sie als JPG mit eindeutigem Namen (ohne Metadaten).
    Bereits importierte Bilder werden übersprungen – du kannst die Zelle also
    jederzeit erneut ausführen, wenn neue Fotos dazukommen.
    """
    import pandas as pd

    ordner_anlegen()
    herkunft = _herkunft_laden()
    bekannte_roh = set(herkunft.values())
    vorhandene_namen = {p.name for p in bilder_in(BILDER, mit_aussortierten=True)}
    zeilen = []
    for roh in bilder_in(ROH):
        roh_rel = roh.relative_to(ROH).as_posix()
        if roh_rel in bekannte_roh:
            zeilen.append({"rohdatei": roh_rel, "bild": "", "status": "schon importiert"})
            continue
        name = zielname(roh)
        basis, nr = name[:-4], 2
        while name in vorhandene_namen:  # gleicher Name aus anderer Quelle → Nummer anhängen
            name, nr = f"{basis}_{nr}.jpg", nr + 1
        try:
            with Image.open(roh) as original:
                exif_drehung = original.getexif().get(274, 1) not in (1, None)
            im = bild_oeffnen(roh)
            alt = im.size
            im.thumbnail((max_seite, max_seite), Image.Resampling.LANCZOS)
            im.save(BILDER / name, "JPEG", quality=qualitaet, optimize=True)
        except Exception as e:  # defekte Datei, unbekanntes Format …
            zeilen.append({"rohdatei": roh_rel, "bild": "", "status": f"FEHLER: {e}"})
            continue
        herkunft[name] = roh_rel
        vorhandene_namen.add(name)
        zeilen.append({
            "rohdatei": roh_rel, "bild": name, "status": "neu",
            "original": f"{alt[0]}×{alt[1]}", "neu": f"{im.size[0]}×{im.size[1]}",
            "exif_gedreht": "ja" if exif_drehung else "",
        })
    _herkunft_speichern(herkunft)
    df = pd.DataFrame(zeilen)
    if df.empty:
        print(f"⚠️  Keine Bilder in {ROH}/ gefunden. Lege deine Fotos dort ab (gern in Unterordnern).")
        return df
    z = df["status"].value_counts()
    print(f"✅ neu importiert: {z.get('neu', 0)}   ⏭️ schon vorhanden: {z.get('schon importiert', 0)}   "
          f"❌ Fehler: {sum(df['status'].str.startswith('FEHLER'))}")
    print(f"   Bilder in {BILDER}/ insgesamt: {len(bilder_in(BILDER))}")
    if not HEIC_OK and any(p.suffix.lower() in {'.heic', '.heif'} for p in bilder_in(ROH)):
        print("⚠️  HEIC-Fotos gefunden, aber pillow-heif fehlt: uv add pillow-heif")
    return df


# ──────────────────────────────────────────────────────────────────────────────
# P1 · Katalog und Qualitätsprüfung
# ──────────────────────────────────────────────────────────────────────────────
def _dhash(im: Image.Image, groesse: int = 16) -> int:
    """Differenz-Hash: 256-Bit-„Fingerabdruck“. Ähnliche Bilder → ähnliche Hashes."""
    g = np.asarray(im.convert("L").resize((groesse + 1, groesse), Image.Resampling.LANCZOS), dtype=np.int16)
    bits = (g[:, 1:] > g[:, :-1]).flatten()
    return int("".join("1" if b else "0" for b in bits), 2)


def _schaerfe(grau: np.ndarray) -> float:
    """Varianz des Laplace-Filters: klein = wenig Kanten = vermutlich unscharf."""
    import cv2

    return float(cv2.Laplacian(grau, cv2.CV_64F).var())


# Grenzwerte für die Qualitätsprüfung (bei Bedarf im Notebook anpassen: werkzeuge.GRENZEN["unscharf"] = 30)
#   aehnlich: Fingerabdrücke unterscheiden sich in höchstens so vielen von 256 Bits → „fast doppelt“
#   serie:    so ähnliche Bilder kommen bei der Aufteilung in dieselbe Teilmenge
GRENZEN = {"dunkel": 50, "hell": 210, "flau": 8, "unscharf": 20, "aehnlich": 20, "serie": 40}


def katalog_erstellen(speichern: bool = True) -> "pd.DataFrame":
    """
    Erstellt eine Tabelle mit allen Bildern in 2_bilder/:
    Quelle, Größe, Ausrichtung, Helligkeit, Kontrast, Schärfe – und markiert
    auffällige Bilder (zu dunkel, zu hell, kontrastarm, unscharf, fast doppelt).
    Wird als katalog.csv gespeichert (lässt sich in Excel öffnen).
    """
    import pandas as pd

    herkunft = _herkunft_laden()
    zeilen, hashes = [], []
    for p in bilder_in(BILDER):
        im = bild_oeffnen(p)
        klein = im.copy()
        klein.thumbnail((640, 640))
        grau = np.asarray(klein.convert("L"))
        roh = herkunft.get(p.name, "")
        quelle = roh.split("/")[0] if "/" in roh else "(ohne Unterordner)"
        h = _dhash(im)
        hashes.append(h)
        zeilen.append({
            "bild": p.name, "quelle": quelle, "breite": im.width, "hoehe": im.height,
            "format": "hoch" if im.height > im.width else ("quer" if im.width > im.height else "quadratisch"),
            "helligkeit": round(float(grau.mean()), 1), "kontrast": round(float(grau.std()), 1),
            "schaerfe": round(_schaerfe(grau), 1), "rohdatei": roh,
        })
    df = pd.DataFrame(zeilen)
    if df.empty:
        print("⚠️  Noch keine Bilder in 2_bilder/. Erst importieren!")
        return df
    # fast gleiche Bilder suchen (Hamming-Abstand der Fingerabdrücke)
    aehnlich = [""] * len(df)
    for i in range(len(hashes)):
        for j in range(i):
            if bin(hashes[i] ^ hashes[j]).count("1") <= GRENZEN["aehnlich"]:
                aehnlich[i] = df.loc[j, "bild"]
                break
    df["fast_gleich_wie"] = aehnlich
    hinweise = []
    for _, r in df.iterrows():
        h = []
        if r.helligkeit < GRENZEN["dunkel"]:
            h.append("zu dunkel")
        if r.helligkeit > GRENZEN["hell"]:
            h.append("zu hell")
        if r.kontrast < GRENZEN["flau"]:
            h.append("kontrastarm")
        if r.schaerfe < GRENZEN["unscharf"]:
            h.append("unscharf?")
        if r.fast_gleich_wie:
            h.append("fast doppelt")
        hinweise.append(", ".join(h))
    df["hinweis"] = hinweise
    if speichern:
        df.to_csv(KATALOG, sep=";", decimal=",", index=False, encoding="utf-8-sig")
    print(f"📋 {len(df)} Bilder im Katalog" + (f" → gespeichert als {KATALOG}" if speichern else ""))
    auff = df[df.hinweis != ""]
    print(f"   davon auffällig: {len(auff)}  " +
          "  ".join(f"{k}: {v}" for k, v in Counter(x for h in auff.hinweis for x in h.split(", ")).items()))
    return df


def uebersicht(df) -> None:
    """Diagramme zum Katalog: Bilder pro Quelle, Hoch-/Querformat, Helligkeit, Schärfe."""
    import matplotlib.pyplot as plt

    if df is None or len(df) == 0:
        print("Keine Daten.")
        return
    fig, ax = plt.subplots(1, 4, figsize=(17, 3.6))
    df["quelle"].value_counts().plot.barh(ax=ax[0], color="#4363d8")
    ax[0].set_title("Bilder pro Quelle")
    ax[0].invert_yaxis()
    df["format"].value_counts().plot.bar(ax=ax[1], color="#3cb44b", rot=0)
    ax[1].set_title("Format")
    ax[2].hist(df["helligkeit"], bins=20, range=(0, 255), color="#f58231")
    ax[2].axvspan(0, GRENZEN["dunkel"], color="k", alpha=.12)
    ax[2].axvspan(GRENZEN["hell"], 255, color="k", alpha=.12)
    ax[2].set_title("Helligkeit (grau = auffällig)")
    ax[3].hist(np.log10(df["schaerfe"].clip(lower=1)), bins=20, color="#911eb4")
    ax[3].axvspan(0, np.log10(GRENZEN["unscharf"]), color="k", alpha=.12)
    ax[3].set_title("Schärfe (log, grau = unscharf?)")
    plt.tight_layout()
    plt.show()


# ──────────────────────────────────────────────────────────────────────────────
# Anzeige: Galerie (Kontaktabzug) und interaktiver Bildbrowser
# ──────────────────────────────────────────────────────────────────────────────
def _jpeg_bytes(im: Image.Image, max_seite: int, qualitaet: int = 80) -> bytes:
    im = im.copy()
    im.thumbnail((max_seite, max_seite))
    puffer = io.BytesIO()
    im.convert("RGB").save(puffer, "JPEG", quality=qualitaet)
    return puffer.getvalue()


def galerie(dateien, spalten: int = 6, breite: int = 170, texte: dict | None = None, max_bilder: int = 60) -> None:
    """Zeigt viele Bilder als kleine Vorschau (Kontaktabzug)."""
    from IPython.display import HTML, display

    dateien = [Path(d) for d in dateien][:max_bilder]
    if not dateien:
        print("Keine Bilder zum Anzeigen.")
        return
    kacheln = []
    for p in dateien:
        b64 = base64.b64encode(_jpeg_bytes(bild_oeffnen(p), breite * 2)).decode()
        text = html.escape((texte or {}).get(p.name, ""))
        kacheln.append(
            f'<figure style="margin:0;text-align:center;font:11px sans-serif">'
            f'<img src="data:image/jpeg;base64,{b64}" style="width:{breite}px;height:{breite}px;'
            f'object-fit:contain;background:#222;border-radius:4px">'
            f'<figcaption style="width:{breite}px;overflow-wrap:anywhere">{html.escape(p.name)}'
            f'{"<br><b style=color:#c00>" + text + "</b>" if text else ""}</figcaption></figure>')
    display(HTML(f'<div style="display:grid;grid-template-columns:repeat({spalten},{breite}px);gap:8px">'
                 + "".join(kacheln) + "</div>"))


def bild_drehen(name: str, grad: int) -> None:
    """Dreht ein Bild in 2_bilder/ dauerhaft (90 = gegen den Uhrzeigersinn, -90 = im Uhrzeigersinn)."""
    if schon_gelabelt():
        print("⛔ Es gibt schon Label-Studio-Exporte. Ein gedrehtes Bild würde nicht mehr zu seinen Boxen passen.\n"
              "   Bild stattdessen aussortieren oder in Label Studio löschen und neu labeln.")
        return
    p = next((b for b in bilder_in(BILDER) if b.name == name), None)
    if p is None:
        raise FileNotFoundError(name)
    bild_oeffnen(p).rotate(grad, expand=True).save(p, "JPEG", quality=92)


def bild_aussortieren(name: str) -> None:
    """Verschiebt ein Bild nach 2_bilder/_aussortiert/ (nicht gelöscht – kann zurückgeholt werden)."""
    p = next((b for b in bilder_in(BILDER) if b.name == name), None)
    if p is None:
        raise FileNotFoundError(name)
    AUSSORTIERT.mkdir(parents=True, exist_ok=True)
    shutil.move(str(p), AUSSORTIERT / p.name)


def bildbrowser(dateien=None, texte: dict | None = None, aendern: bool = True):
    """
    Interaktiver Bildbetrachter im Notebook:
    ◀ ▶ blättern · ⟲ ⟳ drehen · 🗑 aussortieren.
    `dateien`: Liste von Bildern (Standard: alle in 2_bilder/), `texte`: Hinweis pro Bildname.
    """
    import ipywidgets as w
    from IPython.display import display

    liste = [Path(d) for d in (dateien if dateien is not None else bilder_in(BILDER))]
    if not liste:
        print("Keine Bilder zum Anzeigen.")
        return
    zustand = {"i": 0}
    bild = w.Image(format="jpeg", layout=w.Layout(max_width="900px", max_height="620px", object_fit="contain"))
    info = w.HTML()
    knopf = lambda t, tip: w.Button(description=t, tooltip=tip, layout=w.Layout(width="auto"))
    zurueck, vor = knopf("◀ zurück", "vorheriges Bild"), knopf("weiter ▶", "nächstes Bild")
    links, rechts = knopf("⟲ 90°", "gegen den Uhrzeigersinn drehen"), knopf("⟳ 90°", "im Uhrzeigersinn drehen")
    weg = knopf("🗑 aussortieren", "nach 2_bilder/_aussortiert verschieben")
    weg.button_style = "warning"
    regler = w.IntSlider(min=1, max=len(liste), value=1, description="Bild", continuous_update=False)

    def zeigen():
        i = zustand["i"]
        p = liste[i]
        if p.exists():
            im = bild_oeffnen(p)
            bild.value = _jpeg_bytes(im, 1000)
            groesse = f"{im.width}×{im.height}"
        else:
            bild.value = b""
            groesse = "(aussortiert)"
        hinweis = (texte or {}).get(p.name, "")
        info.value = (f"<b>{i + 1} / {len(liste)}</b> · <code>{html.escape(p.name)}</code> · {groesse}"
                      + (f" · <b style='color:#c00'>{html.escape(hinweis)}</b>" if hinweis else ""))
        regler.value = i + 1

    def blaettern(d):
        zustand["i"] = (zustand["i"] + d) % len(liste)
        zeigen()

    def drehen(g):
        p = liste[zustand["i"]]
        if p.exists():
            bild_oeffnen(p).rotate(g, expand=True).save(p, "JPEG", quality=92)
            zeigen()

    def aussortieren(_):
        p = liste[zustand["i"]]
        if p.exists():
            AUSSORTIERT.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), AUSSORTIERT / p.name)
            zeigen()  # Eintrag bleibt in der Liste und zeigt „(aussortiert)“

    zurueck.on_click(lambda _: blaettern(-1))
    vor.on_click(lambda _: blaettern(+1))
    links.on_click(lambda _: drehen(90))
    rechts.on_click(lambda _: drehen(-90))
    weg.on_click(aussortieren)
    regler.observe(lambda c: (zustand.__setitem__("i", c["new"] - 1), zeigen()) if c["new"] - 1 != zustand["i"] else None,
                   names="value")
    if schon_gelabelt():  # nach dem Labeln nicht mehr drehen – die Boxen würden nicht mehr passen
        links.disabled = rechts.disabled = True
        links.tooltip = rechts.tooltip = "gesperrt: es gibt schon Label-Studio-Exporte"
    knoepfe = [zurueck, vor, regler] + ([links, rechts, weg] if aendern else [])
    zeigen()
    display(w.VBox([w.HBox(knoepfe), info, bild]))


# ──────────────────────────────────────────────────────────────────────────────
# P1 · Fotos mit der Webcam aufnehmen
# ──────────────────────────────────────────────────────────────────────────────
def webcam_aufnahme(name: str = "webcam", kamera: int = 0, breite: int = 1280, hoehe: int = 720,
                    serie_sekunden: float = 1.0, max_bilder: int | None = None, automatisch: bool = False) -> int:
    """
    Öffnet ein Kamerafenster und speichert Fotos in 1_rohbilder/<name>/.
      Leertaste  = ein Foto
      S          = Serienaufnahme an/aus (alle `serie_sekunden` ein Foto)
      Q oder Esc = beenden
    Gibt die Anzahl gespeicherter Fotos zurück.
    """
    import cv2

    ziel = ROH / _sauberer_name(name)
    ziel.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(kamera, cv2.CAP_DSHOW) if sys.platform == "win32" else cv2.VideoCapture(kamera)
    if not cap.isOpened():
        cap = cv2.VideoCapture(kamera)
    if not cap.isOpened():
        print(f"❌ Kamera {kamera} lässt sich nicht öffnen. Andere Nummer probieren (0, 1, 2) "
              "oder prüfen, ob eine andere App die Kamera benutzt.")
        return 0
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, breite)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, hoehe)
    fenster = "Webcam  |  Leertaste = Foto  |  S = Serie an/aus  |  Q = Ende"
    anzahl, serie, letzte = 0, automatisch, 0.0
    blitz = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("❌ Kein Bild von der Kamera.")
                break
            jetzt = time.time()
            taste = -1
            if not automatisch:
                anzeige = frame.copy()
                text = f"Fotos: {anzahl}" + ("   SERIE AN" if serie else "")
                cv2.putText(anzeige, text, (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4)
                cv2.putText(anzeige, text, (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                if blitz > 0:
                    cv2.rectangle(anzeige, (0, 0), (anzeige.shape[1] - 1, anzeige.shape[0] - 1), (255, 255, 255), 12)
                    blitz -= 1
                cv2.imshow(fenster, anzeige)
                taste = cv2.waitKey(1) & 0xFF
                if taste in (ord("q"), ord("Q"), 27):
                    break
                if taste in (ord("s"), ord("S")):
                    serie = not serie
                try:
                    if cv2.getWindowProperty(fenster, cv2.WND_PROP_VISIBLE) < 1:
                        break
                except cv2.error:
                    break
            if taste == 32 or (serie and jetzt - letzte >= serie_sekunden):
                datei = ziel / f"{dt.datetime.now():%Y%m%d_%H%M%S_%f}"[:-3]
                cv2.imwrite(str(datei) + ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 92])
                anzahl, letzte, blitz = anzahl + 1, jetzt, 3
                if max_bilder and anzahl >= max_bilder:
                    break
    finally:
        cap.release()
        if not automatisch:
            cv2.destroyAllWindows()
            cv2.waitKey(1)
    print(f"📷 {anzahl} Fotos gespeichert in {ziel}/  → jetzt „Bilder importieren“ erneut ausführen.")
    return anzahl


# ──────────────────────────────────────────────────────────────────────────────
# P2 · Arbeit in der Gruppe aufteilen
# ──────────────────────────────────────────────────────────────────────────────
def pakete_aufteilen(namen: list[str]) -> None:
    """
    Verteilt alle Bilder, die direkt in 2_bilder/ liegen, gleichmäßig auf Unterordner
    2_bilder/<name>/ – ein Paket pro Person. Bilder, die schon in einem Paket liegen,
    bleiben, wo sie sind. Wichtig: VOR dem Einrichten von Label Studio ausführen!
    """
    namen = [_sauberer_name(n) for n in namen if n.strip()]
    if not namen:
        raise ValueError("Bitte mindestens einen Namen angeben.")
    lose = sorted(p for p in BILDER.glob("*") if p.is_file() and p.suffix.lower() in BILD_ENDUNGEN)
    if not lose:
        print("Keine unverteilten Bilder direkt in 2_bilder/ gefunden.")
    for i, p in enumerate(lose):
        ziel = BILDER / namen[i % len(namen)]
        ziel.mkdir(exist_ok=True)
        shutil.move(str(p), ziel / p.name)
    for n in namen:
        print(f"📦 2_bilder/{n}/: {len(bilder_in(BILDER / n))} Bilder")


# ──────────────────────────────────────────────────────────────────────────────
# P2 · Label Studio starten, Konfiguration erzeugen
# ──────────────────────────────────────────────────────────────────────────────
LABEL_STUDIO_VERSION = "1.23.2"
_PID_DATEI = Path(".labelstudio.pid")


def _labelstudio_laeuft(port: int) -> bool:
    import urllib.request

    try:
        with urllib.request.urlopen(f"http://localhost:{port}/health", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def labelstudio_starten(port: int = 8080, browser_oeffnen: bool = True, warten_s: int = 600) -> None:
    """
    Startet Label Studio im Hintergrund – mit Zugriff auf deinen Projektordner
    („Local Files“). Beim allerersten Start wird Label Studio heruntergeladen (1–3 min).
    """
    if _labelstudio_laeuft(port):
        print(f"✅ Label Studio läuft bereits: http://localhost:{port}")
        return
    uvx = shutil.which("uvx")
    if uvx is None:
        raise RuntimeError("uvx nicht gefunden – ist uv installiert? (siehe Seite „Installation mit uv“)")
    env = dict(os.environ,
               LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED="true",
               LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=str(Path.cwd().resolve()),
               PYTHONIOENCODING="utf-8")
    befehl = [uvx, "--python", "3.12", f"label-studio=={LABEL_STUDIO_VERSION}", "start",
              "--port", str(port), "--no-browser"]
    flags = 0
    if sys.platform == "win32":
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
    log = open("labelstudio.log", "w", encoding="utf-8")
    proz = subprocess.Popen(befehl, env=env, stdout=log, stderr=subprocess.STDOUT, creationflags=flags,
                            start_new_session=(sys.platform != "win32"))
    _PID_DATEI.write_text(str(proz.pid))
    print("⏳ Label Studio startet … (beim ersten Mal wird es heruntergeladen, bitte warten)")
    start = time.time()
    while not _labelstudio_laeuft(port):
        if proz.poll() is not None:
            print("❌ Label Studio wurde beendet. Die letzten Zeilen aus labelstudio.log:")
            print("".join(Path("labelstudio.log").read_text(encoding="utf-8", errors="replace").splitlines(True)[-15:]))
            return
        if time.time() - start > warten_s:
            print("⚠️  Das dauert ungewöhnlich lange – schau in labelstudio.log nach.")
            return
        time.sleep(3)
    print(f"✅ Label Studio läuft: http://localhost:{port}   (gestartet in {time.time() - start:.0f} s)")
    if browser_oeffnen:
        import webbrowser

        webbrowser.open(f"http://localhost:{port}")


def labelstudio_stoppen() -> None:
    """Beendet das im Hintergrund laufende Label Studio."""
    if not _PID_DATEI.exists():
        print("Kein von hier gestartetes Label Studio gefunden.")
        return
    pid = int(_PID_DATEI.read_text())
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)
    else:
        import signal

        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
        except Exception:
            try:
                os.kill(pid, signal.SIGTERM)
            except Exception:
                pass
    _PID_DATEI.unlink(missing_ok=True)
    print("🛑 Label Studio beendet.")


def labelstudio_konfiguration(klassen: list[str]) -> str:
    """Erzeugt die Label-Konfiguration (XML) für Label Studio: Rechtecke, nicht drehbar, Tasten 1, 2, 3 …"""
    zeilen = ['<View>',
              '  <Image name="image" value="$image" zoom="true" zoomControl="true" rotateControl="false"/>',
              '  <RectangleLabels name="label" toName="image" canRotate="false">']
    for i, k in enumerate(klassen):
        taste = f' hotkey="{i + 1}"' if i < 9 else ""
        zeilen.append(f'    <Label value="{html.escape(k)}" background="{FARBEN[i % len(FARBEN)]}"{taste}/>')
    zeilen += ['  </RectangleLabels>', '</View>']
    return "\n".join(zeilen)


def ordner_fuer_labelstudio() -> list[str]:
    """Absolute Pfade der Bildordner, die in Label Studio als „Local Files“ eingetragen werden."""
    if not BILDER.exists():
        return []
    unterordner = sorted(p for p in BILDER.iterdir() if p.is_dir() and not p.name.startswith("_"))
    lose = [p for p in BILDER.glob("*") if p.is_file() and p.suffix.lower() in BILD_ENDUNGEN]
    ordner = ([BILDER] if lose else []) + unterordner
    return [str(o.resolve()) for o in ordner]


# ──────────────────────────────────────────────────────────────────────────────
# P2 · Exporte einlesen
# ──────────────────────────────────────────────────────────────────────────────
def bildname_aus_labelstudio(pfad: str) -> str:
    """'/data/local-files/?d=projekt%5C2_bilder%5Canna%5Cbild_01.jpg' → 'bild_01.jpg'"""
    from urllib.parse import unquote

    pfad = unquote(unquote(pfad))
    name = re.split(r"[\\/]", pfad)[-1]
    # Label Studio setzt bei hochgeladenen Dateien eine Kennung davor: '1a2b3c4d-bild_01.jpg'
    return re.sub(r"^[0-9a-f]{8}-", "", name)


def bildindex() -> dict[str, Path]:
    """Bildname → Pfad für alle Bilder in 2_bilder/ (auch in Unterordnern)."""
    return {p.name: p for p in bilder_in(BILDER)}


def exporte_einlesen(klassen: list[str]) -> tuple[dict, "pd.DataFrame"]:
    """
    Liest ALLE JSON-Exporte aus 3_labelstudio_export/ ein und führt sie zusammen.
    Ergebnis:
      annotationen: {bildname: [ {"klasse": "LED", "x":…, "y":…, "width":…, "height":… (in %), …}, … ]}
      protokoll:    Tabelle mit Hinweisen und Problemen
    Wird ein Bild mehrfach gelabelt (z. B. von zwei Personen), gewinnt die NEUESTE Version.
    """
    import pandas as pd

    dateien = sorted(EXPORT.glob("*.json"))
    if not dateien:
        print(f"⚠️  Keine .json-Dateien in {EXPORT}/ – bitte aus Label Studio als „JSON“ exportieren.")
        return {}, pd.DataFrame(columns=["bild", "export", "problem"])
    index = bildindex()
    beste: dict[str, tuple[str, list, str]] = {}  # name → (zeitstempel, boxen, quelle)
    probleme = []
    for datei in dateien:
        try:
            aufgaben = json.loads(datei.read_text(encoding="utf-8"))
        except Exception as e:
            probleme.append({"bild": "", "export": datei.name, "problem": f"Datei nicht lesbar: {e}"})
            continue
        if not isinstance(aufgaben, list) or (aufgaben and "annotations" not in aufgaben[0]):
            probleme.append({"bild": "", "export": datei.name,
                             "problem": "Falsches Format – bitte als „JSON“ (nicht JSON-MIN/YOLO) exportieren"})
            continue
        for a in aufgaben:
            bildpfad = a.get("data", {}).get("image") or next(iter(a.get("data", {}).values()), "")
            name = bildname_aus_labelstudio(str(bildpfad))
            gueltig = [x for x in a.get("annotations", []) if not x.get("was_cancelled")]
            if not gueltig:
                continue  # nicht gelabelt oder übersprungen
            anno = max(gueltig, key=lambda x: x.get("updated_at") or x.get("created_at") or "")
            zeit = anno.get("updated_at") or anno.get("created_at") or ""
            boxen = []
            for r in anno.get("result", []):
                if r.get("type") != "rectanglelabels":
                    continue
                v = r["value"]
                k = v["rectanglelabels"][0]
                if k not in klassen:
                    probleme.append({"bild": name, "export": datei.name,
                                     "problem": f"Unbekannte Klasse „{k}“ – Schreibweise in Label Studio prüfen"})
                    continue
                boxen.append({"klasse": k, "x": v["x"], "y": v["y"], "width": v["width"], "height": v["height"],
                              "rotation": v.get("rotation", 0) or 0,
                              "bild_breite": r.get("original_width"), "bild_hoehe": r.get("original_height")})
            if name in beste:
                alt_zeit, alt_boxen, alt_quelle = beste[name]
                gewinner = datei.name if zeit > alt_zeit else alt_quelle
                art = ("doppelt gelabelt" if len(alt_boxen) == len(boxen)
                       else f"KONFLIKT: doppelt gelabelt ({len(alt_boxen)} vs. {len(boxen)} Boxen)")
                probleme.append({"bild": name, "export": f"{alt_quelle} + {datei.name}",
                                 "problem": f"{art} – neuere Version aus {gewinner} verwendet"})
                if zeit <= alt_zeit:
                    continue
            beste[name] = (zeit, boxen, datei.name)

    annotationen = {}
    for name, (_, boxen, quelle) in sorted(beste.items()):
        if name not in index:
            probleme.append({"bild": name, "export": quelle,
                             "problem": "Bild fehlt in 2_bilder/ (gelöscht, umbenannt oder aussortiert?)"})
            continue
        if boxen and boxen[0]["bild_breite"]:
            with Image.open(index[name]) as im:
                b, h = im.size
            lb, lh = boxen[0]["bild_breite"], boxen[0]["bild_hoehe"]
            if (b, h) != (lb, lh):
                probleme.append({"bild": name, "export": quelle, "problem":
                                 f"Bildgröße passt nicht: gelabelt {lb}×{lh}, jetzt {b}×{h}"
                                 + (" → Bild wurde NACH dem Labeln gedreht! Neu labeln."
                                    if (b, h) == (lh, lb) else "")})
                continue
        if any(abs(bx["rotation"]) > 0.5 for bx in boxen):
            probleme.append({"bild": name, "export": quelle,
                             "problem": "gedrehte Box gefunden – wird als umschließendes Rechteck übernommen"})
        annotationen[name] = boxen
    protokoll = pd.DataFrame(probleme, columns=["bild", "export", "problem"])
    leer = sum(1 for b in annotationen.values() if not b)
    print(f"📥 {len(dateien)} Export-Datei(en) gelesen: {', '.join(d.name for d in dateien)}")
    print(f"   gelabelte Bilder: {len(annotationen)}   davon ohne Objekt (Hintergrund): {leer}   "
          f"Boxen: {sum(len(b) for b in annotationen.values())}")
    offen = sorted(set(index) - set(annotationen))
    print(f"   noch NICHT gelabelt: {len(offen)} von {len(index)} Bildern")
    print(f"   Hinweise/Probleme: {len(protokoll)}" + ("  ✅" if protokoll.empty else "  ⚠️ siehe Tabelle"))
    return annotationen, protokoll


def _gedrehte_box_umschliessen(b: dict) -> tuple[float, float, float, float]:
    """Label Studio dreht um die linke obere Ecke. Gibt das umschließende achsparallele Rechteck (in %) zurück."""
    import math

    if abs(b.get("rotation", 0)) <= 0.5:
        return b["x"], b["y"], b["width"], b["height"]
    W, H = b.get("bild_breite") or 100, b.get("bild_hoehe") or 100  # Drehung in Pixeln rechnen
    x0, y0, w, h = b["x"] * W / 100, b["y"] * H / 100, b["width"] * W / 100, b["height"] * H / 100
    a = math.radians(b["rotation"])
    ecken = [(x0 + dx * math.cos(a) - dy * math.sin(a), y0 + dx * math.sin(a) + dy * math.cos(a))
             for dx, dy in ((0, 0), (w, 0), (w, h), (0, h))]
    xs, ys = [e[0] for e in ecken], [e[1] for e in ecken]
    return min(xs) / W * 100, min(ys) / H * 100, (max(xs) - min(xs)) / W * 100, (max(ys) - min(ys)) / H * 100


def labels_schreiben(annotationen: dict, klassen: list[str], umrechnen) -> Path:
    """
    Schreibt für jedes gelabelte Bild eine YOLO-Textdatei nach 4_datensatz/labels/.
    `umrechnen` ist deine Funktion aus dem Notebook: Label-Studio-Box → (x_mitte, y_mitte, breite, hoehe).
    Der Ordner wird jedes Mal komplett neu erzeugt – die Exporte sind die „Quelle der Wahrheit“.
    """
    ziel = DATENSATZ / "labels"
    if ziel.exists():
        shutil.rmtree(ziel)
    ziel.mkdir(parents=True)
    for name, boxen in annotationen.items():
        zeilen = []
        for b in boxen:
            x, y, w, h = _gedrehte_box_umschliessen(b)
            xc, yc, bw, bh = umrechnen({"x": x, "y": y, "width": w, "height": h})
            # auf das Bild begrenzen (Boxen dürfen nicht über den Rand ragen)
            x1, y1 = max(0.0, xc - bw / 2), max(0.0, yc - bh / 2)
            x2, y2 = min(1.0, xc + bw / 2), min(1.0, yc + bh / 2)
            if x2 - x1 <= 0.001 or y2 - y1 <= 0.001:
                continue
            zeilen.append(f"{klassen.index(b['klasse'])} {(x1 + x2) / 2:.6f} {(y1 + y2) / 2:.6f} "
                          f"{x2 - x1:.6f} {y2 - y1:.6f}")
        (ziel / (Path(name).stem + ".txt")).write_text("".join(z + "\n" for z in zeilen), encoding="utf-8")
    print(f"✅ {len(annotationen)} Label-Dateien geschrieben nach {ziel}/")
    return ziel


def labels_lesen(label_ordner: Path = DATENSATZ / "labels") -> dict[str, list[tuple]]:
    """Liest die YOLO-Labels: {bildname: [(klasse_nr, xc, yc, w, h), …]}"""
    index = {p.stem: p.name for p in bilder_in(BILDER)}
    daten = {}
    for t in sorted(Path(label_ordner).glob("*.txt")):
        if t.stem not in index:
            continue
        zeilen = [z.split() for z in t.read_text(encoding="utf-8").splitlines() if z.strip()]
        daten[index[t.stem]] = [(int(z[0]), *map(float, z[1:5])) for z in zeilen]
    return daten


# ──────────────────────────────────────────────────────────────────────────────
# P2 · Statistik und Kontrolle
# ──────────────────────────────────────────────────────────────────────────────
def statistik(labels: dict, klassen: list[str], ziel_pro_klasse: int | None = None) -> "pd.DataFrame":
    """Zählt Objekte und Bilder pro Klasse und zeigt Diagramme (inkl. Zielwert)."""
    import matplotlib.pyplot as plt
    import pandas as pd

    objekte, bilder_mit = Counter(), Counter()
    groessen = defaultdict(list)
    for name, boxen in labels.items():
        for k, xc, yc, w, h in boxen:
            objekte[k] += 1
            groessen[k].append(np.sqrt(w * h) * 100)
        for k in {b[0] for b in boxen}:
            bilder_mit[k] += 1
    tab = pd.DataFrame({
        "klasse": klassen,
        "objekte": [objekte[i] for i in range(len(klassen))],
        "bilder_mit_klasse": [bilder_mit[i] for i in range(len(klassen))],
        "typische_groesse_%": [round(float(np.median(groessen[i])), 1) if groessen[i] else 0
                               for i in range(len(klassen))],
    })
    if ziel_pro_klasse:
        tab["ziel"] = ziel_pro_klasse
        tab["erreicht"] = [f"{o / ziel_pro_klasse:.0%}" for o in tab.objekte]
    fig, ax = plt.subplots(1, 3, figsize=(17, 3.8))
    farben = [FARBEN[i % len(FARBEN)] for i in range(len(klassen))]
    ax[0].barh(klassen, tab.objekte, color=farben)
    if ziel_pro_klasse:
        ax[0].axvline(ziel_pro_klasse, color="k", ls="--", label=f"Ziel {ziel_pro_klasse}")
        ax[0].legend(loc="lower right")
    ax[0].set_title("Objekte pro Klasse")
    ax[0].invert_yaxis()
    anz = [len(b) for b in labels.values()]
    ax[1].hist(anz, bins=range(0, max(anz + [1]) + 2), color="#469990", align="left", rwidth=.85)
    ax[1].set_title("Objekte pro Bild (0 = Hintergrundbild)")
    ax[1].set_xlabel("Anzahl Boxen")
    for i, k in enumerate(klassen):
        if groessen[i]:
            ax[2].hist(groessen[i], bins=25, range=(0, 100), alpha=.6, color=farben[i], label=k)
    ax[2].axvspan(0, 5, color="k", alpha=.1)
    ax[2].set_title("Objektgröße in % der Bildseite (grau = sehr klein)")
    ax[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()
    print(f"Bilder: {len(labels)}  ·  Hintergrundbilder (ohne Objekt): {sum(1 for a in anz if a == 0)}  ·  "
          f"Objekte gesamt: {sum(anz)}")
    if tab.objekte.min() == 0:
        print("⚠️  Mindestens eine Klasse hat noch KEIN Objekt.")
    elif tab.objekte.max() / tab.objekte.min() > 3:
        print(f"⚠️  Ungleich verteilt: Die häufigste Klasse hat {tab.objekte.max() / tab.objekte.min():.1f}× "
              "so viele Objekte wie die seltenste.")
    return tab


def bild_mit_boxen(pfad: Path, boxen: list[tuple], klassen: list[str], max_seite: int = 1000,
                   farben_boxen: list[str] | None = None, texte: list[str] | None = None) -> Image.Image:
    """Zeichnet YOLO-Boxen (klasse, xc, yc, w, h) in ein Bild."""
    im = bild_oeffnen(pfad)
    im.thumbnail((max_seite, max_seite))
    d = ImageDraw.Draw(im)
    W, H = im.size
    dicke = max(2, round(max(W, H) / 300))
    from matplotlib import font_manager

    schrift = ImageFont.truetype(font_manager.findfont("DejaVu Sans"), max(12, round(max(W, H) / 55)))
    for n, (k, xc, yc, w, h) in enumerate(boxen):
        farbe = (farben_boxen[n] if farben_boxen else None) or FARBEN[k % len(FARBEN)]
        x1, y1, x2, y2 = (xc - w / 2) * W, (yc - h / 2) * H, (xc + w / 2) * W, (yc + h / 2) * H
        d.rectangle([x1, y1, x2, y2], outline=farbe, width=dicke)
        text = texte[n] if texte else (klassen[k] if k < len(klassen) else str(k))
        if text:
            tb = d.textbbox((0, 0), text, font=schrift)
            th = tb[3] - tb[1] + 6
            ty = y1 - th if y1 > th else y1
            d.rectangle([x1, ty, x1 + tb[2] - tb[0] + 8, ty + th], fill=farbe)
            d.text((x1 + 4, ty + 1), text, fill="white", font=schrift)
    return im


def labelbrowser(labels: dict, klassen: list[str], namen: list[str] | None = None) -> None:
    """
    Interaktiver Betrachter: Bilder MIT eingezeichneten Boxen.
    Filter nach Klasse; ◀ ▶ blättern. Fehler findest du so am schnellsten.
    """
    import ipywidgets as w
    from IPython.display import display

    index = bildindex()
    alle = [n for n in (namen if namen is not None else sorted(labels)) if n in index]
    if not alle:
        print("Keine gelabelten Bilder zum Anzeigen.")
        return
    filt = w.Dropdown(options=["alle Bilder", "nur Hintergrundbilder (0 Boxen)"] + [f"enthält: {k}" for k in klassen],
                      description="Filter")
    zustand = {"liste": alle, "i": 0}
    bild, info = w.Image(format="jpeg", layout=w.Layout(max_width="950px")), w.HTML()
    zurueck = w.Button(description="◀ zurück", layout=w.Layout(width="auto"))
    vor = w.Button(description="weiter ▶", layout=w.Layout(width="auto"))

    def zeigen():
        liste = zustand["liste"]
        if not liste:
            bild.value, info.value = b"", "<b>Keine Bilder für diesen Filter.</b>"
            return
        n = liste[zustand["i"]]
        boxen = labels.get(n, [])
        puffer = io.BytesIO()
        bild_mit_boxen(index[n], boxen, klassen).save(puffer, "JPEG", quality=85)
        bild.value = puffer.getvalue()
        z = Counter(klassen[b[0]] for b in boxen)
        info.value = (f"<b>{zustand['i'] + 1} / {len(liste)}</b> · <code>{html.escape(n)}</code> · "
                      + (", ".join(f"{k}: {v}" for k, v in z.items()) or "<i>keine Objekte (Hintergrund)</i>"))

    def filtern(_=None):
        f = filt.value
        if f == "alle Bilder":
            zustand["liste"] = alle
        elif f.startswith("nur Hintergrund"):
            zustand["liste"] = [n for n in alle if not labels.get(n)]
        else:
            k = klassen.index(f.split(": ", 1)[1])
            zustand["liste"] = [n for n in alle if any(b[0] == k for b in labels.get(n, []))]
        zustand["i"] = 0
        zeigen()

    def blaettern(d):
        if zustand["liste"]:
            zustand["i"] = (zustand["i"] + d) % len(zustand["liste"])
            zeigen()

    zurueck.on_click(lambda _: blaettern(-1))
    vor.on_click(lambda _: blaettern(+1))
    filt.observe(filtern, names="value")
    zeigen()
    display(w.VBox([w.HBox([filt, zurueck, vor]), info, bild]))


def ausschnitte(labels: dict, klassen: list[str], klasse: str, max_anzahl: int = 48, groesse: int = 110) -> None:
    """
    Zeigt alle Objekte EINER Klasse als Ausschnitte nebeneinander.
    Ein falsch gelabeltes Objekt fällt zwischen lauter richtigen sofort auf.
    """
    from IPython.display import HTML, display

    index = bildindex()
    k = klassen.index(klasse)
    kacheln = []
    for n, boxen in sorted(labels.items()):
        if len(kacheln) >= max_anzahl:
            break
        treffer = [b for b in boxen if b[0] == k]
        if not treffer or n not in index:
            continue
        im = bild_oeffnen(index[n])
        W, H = im.size
        for _, xc, yc, w, h in treffer:
            x1, y1 = max(0, (xc - w * .55) * W), max(0, (yc - h * .55) * H)
            x2, y2 = min(W, (xc + w * .55) * W), min(H, (yc + h * .55) * H)
            b64 = base64.b64encode(_jpeg_bytes(im.crop((int(x1), int(y1), int(x2), int(y2))), groesse * 2)).decode()
            kacheln.append(f'<div title="{html.escape(n)}" style="text-align:center;font:9px sans-serif">'
                           f'<img src="data:image/jpeg;base64,{b64}" style="width:{groesse}px;height:{groesse}px;'
                           f'object-fit:contain;background:#ddd;border-radius:3px"><br>{html.escape(n[-24:])}</div>')
            if len(kacheln) >= max_anzahl:
                break
    print(f"Klasse „{klasse}“: {len(kacheln)} Ausschnitte (höchstens {max_anzahl}). Darunter steht der Bildname.")
    display(HTML('<div style="display:flex;flex-wrap:wrap;gap:6px">' + "".join(kacheln) + "</div>"))


# ──────────────────────────────────────────────────────────────────────────────
# P2 · Datensatz bauen: Aufteilung, data.yaml, ZIP
# ──────────────────────────────────────────────────────────────────────────────
AUFTEILUNG = DATENSATZ / "aufteilung.csv"


TEILMENGEN = ("train", "val", "test")


def _reihenfolge(name: str) -> str:
    """Fester „Zufall“: Die Prüfsumme des Dateinamens bestimmt die Reihenfolge – jedes Mal gleich."""
    return hashlib.md5(name.encode("utf-8")).hexdigest()


def aufteilen(labels: dict, anteile: tuple[float, float, float] = (0.7, 0.2, 0.1)) -> dict[str, str]:
    """
    Teilt die gelabelten Bilder in train / val / test auf und merkt sich das in 4_datensatz/aufteilung.csv.
      • Einmal zugeteilte Bilder bleiben IMMER in ihrer Teilmenge (wichtig fürs Nachtraining!).
      • Fast gleiche Bilder (Serienfotos) kommen gemeinsam in eine Teilmenge – sonst „schummelt“ die Validierung.
      • Neue Bilder gehen dorthin, wo gemessen an `anteile` am meisten fehlt – bei Bildern UND bei den
        Klassen. So kommt jede Klasse möglichst auch in val und test vor (bei sehr seltenen Klassen nicht garantiert).
    """
    assert abs(sum(anteile) - 1) < 1e-6, "Die Anteile müssen zusammen 1.0 ergeben."
    ziel = dict(zip(TEILMENGEN, anteile))
    bisher = {}
    if AUFTEILUNG.exists():
        with AUFTEILUNG.open(encoding="utf-8") as f:
            bisher = {z["bild"]: z["teilmenge"] for z in csv.DictReader(f, delimiter=";")}
    index = bildindex()
    namen = sorted((n for n in labels if n in index), key=_reihenfolge)
    hashes = {n: _dhash(bild_oeffnen(index[n])) for n in namen}

    # 1. Serien finden: fast gleiche Bilder werden zu einer Gruppe verbunden
    eltern = {n: n for n in namen}

    def wurzel(n):
        while eltern[n] != n:
            eltern[n] = eltern[eltern[n]]
            n = eltern[n]
        return n

    for i, n in enumerate(namen):
        for m in namen[:i]:
            if bin(hashes[n] ^ hashes[m]).count("1") <= GRENZEN["serie"]:
                eltern[wurzel(n)] = wurzel(m)
    gruppen = defaultdict(list)
    for n in namen:
        gruppen[wurzel(n)].append(n)

    # 2. Zuteilen: alte Bilder behalten ihre Teilmenge, neue Gruppen füllen die größte Lücke
    klassen_gesamt = Counter(b[0] for n in namen for b in labels[n])
    bilder_in_teil = Counter()
    klassen_in_teil = {t: Counter() for t in TEILMENGEN}
    zuteilung = {}

    def eintragen(n, t):
        zuteilung[n] = t
        bilder_in_teil[t] += 1
        klassen_in_teil[t].update(b[0] for b in labels[n])

    for n in namen:
        if n in bisher:
            eintragen(n, bisher[n])
    neu = 0
    def seltenheit(g):  # Gruppen mit seltenen Klassen zuerst verteilen, damit diese überall landen
        k = [klassen_gesamt[b[0]] for n in g for b in labels[n]]
        return (min(k) if k else 10 ** 9, _reihenfolge(g[0]))

    for g in sorted(gruppen.values(), key=seltenheit):
        offen = [n for n in g if n not in zuteilung]
        if not offen:
            continue
        schon = Counter(zuteilung[n] for n in g if n in zuteilung)
        if schon:  # Serie hat schon eine Teilmenge → dazu
            t = schon.most_common(1)[0][0]
        else:
            k_g = Counter(b[0] for n in offen for b in labels[n])

            def luecke(t):  # Wie viel vom Soll fehlt der Teilmenge noch? (1 = leer, 0 = voll, < 0 = übervoll)
                bild = 1 - bilder_in_teil[t] / (ziel[t] * len(namen))
                klass = sum(1 - klassen_in_teil[t][k] / (ziel[t] * klassen_gesamt[k]) for k in k_g)
                return bild + klass

            t = max((t for t in TEILMENGEN if ziel[t] > 0), key=luecke)
        for n in offen:
            eintragen(n, t)
            neu += 1

    alle = {**bisher, **zuteilung}
    AUFTEILUNG.parent.mkdir(parents=True, exist_ok=True)
    with AUFTEILUNG.open("w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f, delimiter=";")
        wr.writerow(["bild", "teilmenge"])
        for n in sorted(alle):
            wr.writerow([n, alle[n]])
    z = Counter(zuteilung.values())
    serien = sum(1 for g in gruppen.values() if len(g) > 1)
    print(f"✂️  train: {z['train']}   val: {z['val']}   test: {z['test']}   "
          f"(neu zugeteilt: {neu} · unverändert aus früheren Versionen: {len(zuteilung) - neu} · "
          f"Serien mit fast gleichen Bildern: {serien})")
    return zuteilung


def datensatz_bauen(labels: dict, klassen: list[str], zuteilung: dict[str, str], version: str,
                    notiz: str = "") -> Path:
    """
    Baut den fertigen YOLO-Datensatz 4_datensatz/datensatz_<version>/ und packt ihn als ZIP:
        images/train|val|test, labels/train|val|test, data.yaml, info.json, projekt.yaml
    """
    import pandas as pd
    import yaml
    from IPython.display import display

    version = _sauberer_name(str(version))
    index = bildindex()
    name = f"datensatz_{version}"
    ziel = DATENSATZ / name
    if ziel.exists():
        print(f"⚠️  {name} gibt es schon und wird ersetzt. Hast du diese Version schon in Colab trainiert, "
              "dann lieber VERSION hochzählen!")
        shutil.rmtree(ziel)
    zaehler = defaultdict(Counter)
    for n, boxen in labels.items():
        t = zuteilung.get(n)
        if t is None or n not in index:
            continue
        for unter in ("images", "labels"):
            (ziel / unter / t).mkdir(parents=True, exist_ok=True)
        shutil.copy2(index[n], ziel / "images" / t / n)
        (ziel / "labels" / t / (Path(n).stem + ".txt")).write_text(
            "".join(f"{k} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}\n" for k, xc, yc, w, h in boxen), encoding="utf-8")
        zaehler[t]["bilder"] += 1
        for b in boxen:
            zaehler[t][klassen[b[0]]] += 1
    teilmengen = [t for t in ("train", "val", "test") if zaehler[t]["bilder"]]
    if "train" not in teilmengen or "val" not in teilmengen:
        raise RuntimeError("Zu wenige Bilder: train und val brauchen jeweils mindestens ein Bild.")
    data = {"train": "images/train", "val": "images/val"}
    if "test" in teilmengen:
        data["test"] = "images/test"
    data["names"] = {i: k for i, k in enumerate(klassen)}
    kopf = (f"# YOLO-Datensatz {name} – erzeugt mit P2 am {dt.datetime.now():%d.%m.%Y %H:%M}\n"
            "# Ohne 'path:' gelten alle Pfade relativ zu dem Ordner, in dem diese Datei liegt.\n")
    (ziel / "data.yaml").write_text(kopf + yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    info = {"datensatz": name, "version": version, "erstellt": dt.datetime.now().isoformat(timespec="seconds"),
            "klassen": klassen, "notiz": notiz, "anzahl": {t: dict(zaehler[t]) for t in teilmengen}}
    (ziel / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    if PROJEKTDATEI.exists():
        shutil.copy2(PROJEKTDATEI, ziel / "projekt.yaml")
    zip_pfad = DATENSATZ / f"{name}.zip"
    with zipfile.ZipFile(zip_pfad, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ziel.rglob("*")):
            if p.is_file():
                z.write(p, (Path(name) / p.relative_to(ziel)).as_posix())
    tab = pd.DataFrame({t: zaehler[t] for t in teilmengen}).fillna(0).astype(int)
    tab = tab.reindex(["bilder"] + klassen).fillna(0).astype(int)
    print(f"📦 Datensatz: {ziel}/")
    print(f"🗜️  ZIP für Colab: {zip_pfad}  ({zip_pfad.stat().st_size / 1e6:.1f} MB)")
    display(tab)
    for teil in ("val", "test"):
        fehlt = [k for k in klassen if teil in tab.columns and tab.loc[k, teil] == 0]
        if fehlt:
            print(f"⚠️  Diese Klassen kommen in {teil} nicht vor: {fehlt} → Sie können dort nicht bewertet werden. "
                  "Mehr Bilder dieser Klassen labeln!")
    return ziel
