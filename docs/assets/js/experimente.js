/*
 * Interaktive Experimente für die YOLO-Lernseite.
 * Einbinden im Markdown:  <div class="exp" data-exp="iou"></div>
 * Verfügbar: iou, pr, label, loss, imgsz
 */
(function () {
  "use strict";

  // ---------- Hilfsfunktionen ----------
  const css = (name) =>
    getComputedStyle(document.body).getPropertyValue(name).trim() || "#888";

  function el(tag, attrs = {}, kinder = []) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "text") e.textContent = v;
      else if (k === "html") e.innerHTML = v;
      else e.setAttribute(k, v);
    }
    kinder.forEach((k) => e.appendChild(k));
    return e;
  }

  function canvas(breite, hoehe) {
    const c = el("canvas");
    const dpr = window.devicePixelRatio || 1;
    c.width = breite * dpr;
    c.height = hoehe * dpr;
    c.style.width = breite + "px";
    c.style.aspectRatio = breite + " / " + hoehe;
    const ctx = c.getContext("2d");
    ctx.scale(dpr, dpr);
    c._b = breite;
    c._h = hoehe;
    return [c, ctx];
  }

  // Mausposition in logischen Canvas-Koordinaten
  function pos(c, ev) {
    const r = c.getBoundingClientRect();
    const p = ev.touches ? ev.touches[0] : ev;
    return [((p.clientX - r.left) / r.width) * c._b, ((p.clientY - r.top) / r.height) * c._h];
  }

  function regler(text, min, max, step, wert, format) {
    const inp = el("input", { type: "range", min, max, step, value: wert });
    const anz = el("b", { text: format(+wert) });
    const lab = el("label", {}, [el("span", { text: text }), inp, anz]);
    inp.addEventListener("input", () => (anz.textContent = format(+inp.value)));
    return [lab, inp];
  }

  function wertKachel(titel) {
    const b = el("b", { text: "–" });
    const k = el("div", { class: "wert" }, [b, el("small", { text: titel })]);
    return [k, b];
  }

  function titel(box, txt) {
    box.appendChild(el("div", { class: "exp-titel", text: box.dataset.titel || txt }));
  }

  function bildUrl(box, name) {
    return new URL(box.dataset.bild || "../../assets/img/" + name, location.href).href;
  }

  // ======================================================================
  // 1) IoU – Intersection over Union
  // ======================================================================
  function expIoU(box) {
    titel(box, "Experiment: Wie gut passt die Box? (IoU)");
    const [c, ctx] = canvas(560, 320);
    box.appendChild(c);

    let gt = { x: 150, y: 70, w: 200, h: 170 };
    let pr = { x: 220, y: 110, w: 190, h: 160 };
    let ziehen = null;
    let schaetzModus = false;

    const [lSchwelle, iSchwelle] = regler("IoU-Schwelle für „Treffer“", 0.3, 0.95, 0.05, 0.5, (v) => v.toFixed(2));
    const [lTipp, iTipp] = regler("Dein Tipp", 0, 1, 0.01, 0.5, (v) => v.toFixed(2));
    lTipp.style.display = "none";
    const bNeu = el("button", { text: "🎯 Schätzspiel starten" });
    const bAuf = el("button", { text: "Auflösen", class: "sek" });
    bAuf.style.display = "none";
    box.appendChild(el("div", { class: "regler" }, [lSchwelle, lTipp, bNeu, bAuf]));

    const [k1, vI] = wertKachel("Schnittfläche (px²)");
    const [k2, vU] = wertKachel("Vereinigung (px²)");
    const [k3, vIoU] = wertKachel("IoU");
    const [k4, vErg] = wertKachel("Bewertung");
    box.appendChild(el("div", { class: "werte" }, [k1, k2, k3, k4]));
    const hinweis = el("div", {
      class: "hinweis",
      text: "Grün = Label (Ground Truth), Orange = Vorhersage. Box verschieben: hineinklicken und ziehen. Größe ändern: an der rechten unteren Ecke ziehen.",
    });
    box.appendChild(hinweis);

    function iou() {
      const x1 = Math.max(gt.x, pr.x), y1 = Math.max(gt.y, pr.y);
      const x2 = Math.min(gt.x + gt.w, pr.x + pr.w), y2 = Math.min(gt.y + gt.h, pr.y + pr.h);
      const inter = Math.max(0, x2 - x1) * Math.max(0, y2 - y1);
      const uni = gt.w * gt.h + pr.w * pr.h - inter;
      return { inter, uni, iou: uni > 0 ? inter / uni : 0, x1, y1, x2, y2 };
    }

    function zeichne() {
      ctx.clearRect(0, 0, c._b, c._h);
      ctx.fillStyle = css("--md-default-bg-color");
      ctx.fillRect(0, 0, c._b, c._h);
      const r = iou();
      if (r.inter > 0) {
        ctx.fillStyle = "rgba(99,102,241,.45)";
        ctx.fillRect(r.x1, r.y1, r.x2 - r.x1, r.y2 - r.y1);
      }
      [[gt, "#16a34a", "Label"], [pr, "#f59e0b", "Vorhersage"]].forEach(([b, f, t]) => {
        ctx.strokeStyle = f;
        ctx.lineWidth = 3;
        ctx.strokeRect(b.x, b.y, b.w, b.h);
        ctx.fillStyle = f;
        ctx.fillRect(b.x + b.w - 9, b.y + b.h - 9, 9, 9);
        ctx.font = "bold 13px sans-serif";
        ctx.fillText(t, b.x + 4, b.y - 6);
      });
      if (schaetzModus) {
        [vI, vU, vIoU, vErg].forEach((v) => (v.textContent = "?"));
        return;
      }
      const s = +iSchwelle.value;
      vI.textContent = Math.round(r.inter);
      vU.textContent = Math.round(r.uni);
      vIoU.textContent = r.iou.toFixed(2);
      vErg.innerHTML = r.iou >= s ? '<span class="ok">TP ✔</span>' : '<span class="bad">FP ✘</span>';
    }

    function treffer(b, x, y) {
      if (Math.abs(x - (b.x + b.w)) < 14 && Math.abs(y - (b.y + b.h)) < 14) return "groesse";
      if (x > b.x && x < b.x + b.w && y > b.y && y < b.y + b.h) return "bewegen";
      return null;
    }

    function start(ev) {
      const [x, y] = pos(c, ev);
      for (const b of [pr, gt]) {
        const art = treffer(b, x, y);
        if (art) {
          ziehen = { b, art, dx: x - b.x, dy: y - b.y };
          ev.preventDefault();
          return;
        }
      }
    }
    function bewege(ev) {
      if (!ziehen) return;
      ev.preventDefault();
      const [x, y] = pos(c, ev);
      const b = ziehen.b;
      if (ziehen.art === "bewegen") {
        b.x = Math.min(Math.max(0, x - ziehen.dx), c._b - b.w);
        b.y = Math.min(Math.max(0, y - ziehen.dy), c._h - b.h);
      } else {
        b.w = Math.min(Math.max(20, x - b.x), c._b - b.x);
        b.h = Math.min(Math.max(20, y - b.y), c._h - b.y);
      }
      zeichne();
    }
    c.addEventListener("mousedown", start);
    c.addEventListener("touchstart", start, { passive: false });
    window.addEventListener("mousemove", bewege);
    c.addEventListener("touchmove", bewege, { passive: false });
    window.addEventListener("mouseup", () => (ziehen = null));
    c.addEventListener("touchend", () => (ziehen = null));
    iSchwelle.addEventListener("input", zeichne);

    const zufall = (a, b) => a + Math.random() * (b - a);
    bNeu.addEventListener("click", () => {
      gt = { x: zufall(40, 250), y: zufall(30, 120), w: zufall(110, 240), h: zufall(90, 170) };
      pr = { x: gt.x + zufall(-80, 80), y: gt.y + zufall(-60, 60), w: gt.w * zufall(0.6, 1.4), h: gt.h * zufall(0.6, 1.4) };
      pr.x = Math.max(0, Math.min(pr.x, c._b - pr.w));
      pr.y = Math.max(0, Math.min(pr.y, c._h - pr.h));
      schaetzModus = true;
      lTipp.style.display = "";
      bAuf.style.display = "";
      bNeu.textContent = "🎯 Neue Aufgabe";
      hinweis.textContent = "Schätze die IoU mit dem Regler „Dein Tipp“ und klicke auf „Auflösen“. Unter 0,05 Abweichung ist ein Profi-Wert!";
      zeichne();
    });
    bAuf.addEventListener("click", () => {
      schaetzModus = false;
      zeichne();
      const d = Math.abs(iou().iou - +iTipp.value);
      hinweis.innerHTML =
        `Echte IoU: <b>${iou().iou.toFixed(2)}</b> · Dein Tipp: <b>${(+iTipp.value).toFixed(2)}</b> · Abweichung: ` +
        (d < 0.05 ? `<span class="ok">${d.toFixed(2)} – super!</span>` : d < 0.15 ? `<b>${d.toFixed(2)}</b> – ganz gut` : `<span class="bad">${d.toFixed(2)}</span> – Boxen wirken oft ähnlicher, als die IoU ist.`);
    });

    zeichne();
  }

  // ======================================================================
  // 2) Precision / Recall / AP mit Confidence-Schwelle
  // ======================================================================
  function expPR(box) {
    titel(box, "Experiment: Confidence-Schwelle, Precision & Recall");
    // Szenario: Platine mit 10 Widerständen, Modell liefert 15 Boxen
    const GT = 10;
    const dets = [
      [0.97, 1], [0.95, 1], [0.91, 1], [0.88, 0], [0.85, 1],
      [0.80, 1], [0.74, 1], [0.69, 0], [0.62, 1], [0.55, 0],
      [0.48, 1], [0.40, 0], [0.33, 0], [0.27, 1], [0.15, 0],
    ];
    box.appendChild(el("p", {
      html: "Szenario: Auf einer Platine sind <b>10 Widerstände</b> gelabelt. Das Modell liefert 15 Boxen mit unterschiedlicher Confidence. Jede Box ist entweder ein Treffer (TP) oder ein Fehlalarm (FP). Verschiebe die Schwelle!",
    }));

    const grid = el("div", { class: "zweispaltig" });
    const links = el("div");
    const rechts = el("div");
    grid.append(links, rechts);
    box.appendChild(grid);

    const [c, ctx] = canvas(420, 300);
    links.appendChild(c);
    const [lS, iS] = regler("Confidence-Schwelle", 0, 1, 0.01, 0.5, (v) => v.toFixed(2));
    links.appendChild(el("div", { class: "regler" }, [lS]));

    const tab = el("table", { class: "dets" });
    tab.innerHTML = "<thead><tr><th>#</th><th>Confidence</th><th>Ergebnis</th></tr></thead>";
    const tb = el("tbody");
    dets.forEach(([cf, tp], i) => {
      const tr = el("tr", {
        html: `<td>${i + 1}</td><td>${cf.toFixed(2)}</td><td>${tp ? '<span class="ok">TP</span>' : '<span class="bad">FP</span>'}</td>`,
      });
      tb.appendChild(tr);
    });
    tab.appendChild(tb);
    rechts.appendChild(tab);

    const [k1, vTP] = wertKachel("TP (Treffer)");
    const [k2, vFP] = wertKachel("FP (Fehlalarme)");
    const [k3, vFN] = wertKachel("FN (übersehen)");
    const [k4, vP] = wertKachel("Precision");
    const [k5, vR] = wertKachel("Recall");
    const [k6, vF1] = wertKachel("F1");
    box.appendChild(el("div", { class: "werte" }, [k1, k2, k3, k4, k5, k6]));

    // PR-Kurve über alle Schwellen
    const kurve = [];
    let tp = 0, fp = 0;
    dets.forEach(([, t]) => {
      t ? tp++ : fp++;
      kurve.push([tp / GT, tp / (tp + fp)]);
    });
    // AP (all-point Interpolation wie in COCO/Ultralytics)
    const rec = [0, ...kurve.map((k) => k[0]), 1];
    const pre = [1, ...kurve.map((k) => k[1]), 0];
    for (let i = pre.length - 2; i >= 0; i--) pre[i] = Math.max(pre[i], pre[i + 1]);
    let ap = 0;
    for (let i = 1; i < rec.length; i++) ap += (rec[i] - rec[i - 1]) * pre[i];
    const apInfo = el("div", { class: "hinweis" });
    box.appendChild(apInfo);

    const M = { l: 44, r: 12, t: 14, b: 36 };
    const X = (r) => M.l + r * (c._b - M.l - M.r);
    const Y = (p) => c._h - M.b - p * (c._h - M.t - M.b);

    function zeichne() {
      const s = +iS.value;
      const fg = css("--md-default-fg-color");
      const leicht = css("--md-default-fg-color--lightest");
      ctx.clearRect(0, 0, c._b, c._h);
      ctx.fillStyle = css("--md-default-bg-color");
      ctx.fillRect(0, 0, c._b, c._h);

      // Achsen + Gitter
      ctx.strokeStyle = leicht;
      ctx.lineWidth = 1;
      ctx.fillStyle = fg;
      ctx.font = "11px sans-serif";
      for (let i = 0; i <= 5; i++) {
        const v = i / 5;
        ctx.beginPath(); ctx.moveTo(X(0), Y(v)); ctx.lineTo(X(1), Y(v)); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(X(v), Y(0)); ctx.lineTo(X(v), Y(1)); ctx.stroke();
        ctx.fillText(v.toFixed(1), X(v) - 8, c._h - M.b + 14);
        ctx.fillText(v.toFixed(1), 20, Y(v) + 4);
      }
      ctx.fillText("Recall →", X(0.5) - 22, c._h - 6);
      ctx.save(); ctx.translate(12, Y(0.5) + 30); ctx.rotate(-Math.PI / 2); ctx.fillText("Precision →", 0, 0); ctx.restore();

      // Fläche (AP) – interpolierte Kurve
      ctx.fillStyle = "rgba(99,102,241,.18)";
      ctx.beginPath(); ctx.moveTo(X(0), Y(0));
      for (let i = 1; i < rec.length; i++) { ctx.lineTo(X(rec[i - 1]), Y(pre[i])); ctx.lineTo(X(rec[i]), Y(pre[i])); }
      ctx.lineTo(X(1), Y(0)); ctx.closePath(); ctx.fill();

      // Rohkurve
      ctx.strokeStyle = "#6366f1"; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(X(0), Y(1));
      kurve.forEach(([r, p]) => ctx.lineTo(X(r), Y(p)));
      ctx.stroke();

      // aktueller Punkt
      let TP = 0, FP = 0;
      dets.forEach(([cf, t]) => { if (cf >= s) t ? TP++ : FP++; });
      const FN = GT - TP;
      const P = TP + FP ? TP / (TP + FP) : 1;
      const R = TP / GT;
      const F1 = P + R ? (2 * P * R) / (P + R) : 0;
      ctx.fillStyle = "#f59e0b";
      ctx.beginPath(); ctx.arc(X(R), Y(P), 7, 0, Math.PI * 2); ctx.fill();

      vTP.textContent = TP; vFP.textContent = FP; vFN.textContent = FN;
      vP.textContent = P.toFixed(2); vR.textContent = R.toFixed(2); vF1.textContent = F1.toFixed(2);
      [...tb.children].forEach((tr, i) => tr.classList.toggle("aus", dets[i][0] < s));
      apInfo.innerHTML = `Die blaue Fläche unter der Kurve ist die <b>Average Precision (AP) = ${ap.toFixed(3)}</b>. Sie hängt <i>nicht</i> von der Schwelle ab – sie bewertet das Modell über alle Schwellen hinweg. Der orange Punkt zeigt deine aktuelle Schwelle.`;
    }
    iS.addEventListener("input", zeichne);
    zeichne();
  }

  // ======================================================================
  // 3) Labeln: Box ziehen → YOLO-Zeile
  // ======================================================================
  function expLabel(box) {
    titel(box, "Experiment: Selbst labeln – so entsteht eine YOLO-Label-Datei");
    const klassen = (box.dataset.klassen || "person,bus").split(",");
    const img = new Image();
    img.src = bildUrl(box, "bus.jpg");
    const [c, ctx] = canvas(405, 540);
    const sel = el("select");
    klassen.forEach((k, i) => sel.appendChild(el("option", { value: i, text: `${i}: ${k}` })));
    const bLoesch = el("button", { text: "Letzte Box löschen", class: "sek" });
    const bAlle = el("button", { text: "Alle löschen", class: "sek" });

    const grid = el("div", { class: "zweispaltig" });
    const rechts = el("div");
    grid.append(el("div", {}, [c]), rechts);
    box.appendChild(el("div", { class: "regler" }, [el("label", {}, [el("span", { text: "Klasse:" }), sel]), bLoesch, bAlle]));
    box.appendChild(grid);
    rechts.appendChild(el("div", { html: "<b>Inhalt von <code>bus.txt</code></b>" }));
    const aus = el("div", { class: "ausgabe" });
    rechts.appendChild(aus);
    const pix = el("div", { class: "hinweis" });
    rechts.appendChild(pix);
    rechts.appendChild(el("div", {
      class: "hinweis",
      html: "Format pro Zeile:<br><code>klasse x_mitte y_mitte breite höhe</code><br>Alle Werte sind auf 0…1 normiert (geteilt durch Bildbreite bzw. -höhe).",
    }));

    const boxen = [];
    let neu = null;
    const farben = ["#f59e0b", "#16a34a", "#6366f1", "#dc2626", "#0891b2"];

    function zeichne() {
      ctx.clearRect(0, 0, c._b, c._h);
      if (img.complete && img.naturalWidth) ctx.drawImage(img, 0, 0, c._b, c._h);
      [...boxen, ...(neu ? [neu] : [])].forEach((b) => {
        const f = farben[b.k % farben.length];
        ctx.strokeStyle = f; ctx.lineWidth = 2.5;
        ctx.strokeRect(b.x, b.y, b.w, b.h);
        ctx.fillStyle = f; ctx.font = "bold 12px sans-serif";
        const t = klassen[b.k];
        ctx.fillRect(b.x, b.y - 16, ctx.measureText(t).width + 8, 16);
        ctx.fillStyle = "#000"; ctx.fillText(t, b.x + 4, b.y - 4);
      });
      const W = img.naturalWidth || 810, H = img.naturalHeight || 1080;
      const sx = W / c._b, sy = H / c._h;
      if (!boxen.length) {
        aus.textContent = "(noch leer – ziehe mit der Maus eine Box um ein Objekt)";
        pix.textContent = "";
        return;
      }
      aus.textContent = boxen
        .map((b) => {
          const xc = (b.x + b.w / 2) / c._b, yc = (b.y + b.h / 2) / c._h;
          return `${b.k} ${xc.toFixed(6)} ${yc.toFixed(6)} ${(b.w / c._b).toFixed(6)} ${(b.h / c._h).toFixed(6)}`;
        })
        .join("\n");
      const l = boxen[boxen.length - 1];
      pix.innerHTML = `Letzte Box in Pixeln (Bild ${W}×${H}): x1=${Math.round(l.x * sx)}, y1=${Math.round(l.y * sy)}, x2=${Math.round((l.x + l.w) * sx)}, y2=${Math.round((l.y + l.h) * sy)}`;
    }

    function start(ev) {
      const [x, y] = pos(c, ev);
      neu = { x0: x, y0: y, x, y, w: 0, h: 0, k: +sel.value };
      ev.preventDefault();
    }
    function bewege(ev) {
      if (!neu) return;
      ev.preventDefault();
      let [x, y] = pos(c, ev);
      x = Math.max(0, Math.min(c._b, x)); y = Math.max(0, Math.min(c._h, y));
      neu.x = Math.min(neu.x0, x); neu.y = Math.min(neu.y0, y);
      neu.w = Math.abs(x - neu.x0); neu.h = Math.abs(y - neu.y0);
      zeichne();
    }
    function ende() {
      if (neu && neu.w > 5 && neu.h > 5) boxen.push(neu);
      neu = null;
      zeichne();
    }
    c.addEventListener("mousedown", start);
    c.addEventListener("touchstart", start, { passive: false });
    window.addEventListener("mousemove", bewege);
    c.addEventListener("touchmove", bewege, { passive: false });
    window.addEventListener("mouseup", ende);
    c.addEventListener("touchend", ende);
    bLoesch.addEventListener("click", () => { boxen.pop(); zeichne(); });
    bAlle.addEventListener("click", () => { boxen.length = 0; zeichne(); });
    img.onload = zeichne;
    zeichne();
  }

  // ======================================================================
  // 4) Loss-Kurven: Overfitting & Early Stopping
  // ======================================================================
  function expLoss(box) {
    titel(box, "Experiment: Wann ist das Training fertig? (Overfitting & patience)");
    const [c, ctx] = canvas(560, 280);
    box.appendChild(c);
    const [lE, iE] = regler("Epochen", 5, 200, 1, 100, (v) => v);
    const [lP, iP] = regler("patience", 5, 100, 1, 20, (v) => v);
    const sel = el("select");
    [["klein", "Kleiner Datensatz (200 Bilder)"], ["gross", "Großer Datensatz (5000 Bilder)"]].forEach(([v, t]) =>
      sel.appendChild(el("option", { value: v, text: t })));
    box.appendChild(el("div", { class: "regler" }, [lE, lP, el("label", {}, [sel])]));
    const info = el("div", { class: "hinweis" });
    box.appendChild(info);

    // deterministisches Rauschen
    const rausch = (i, s) => Math.sin(i * 12.9898 + s * 78.233) * 43758.5453 % 1;

    function kurven(n, art) {
      const tr = [], va = [];
      const min = art === "klein" ? 45 : 140;   // Epoche, ab der Validierung schlechter wird
      const anstieg = art === "klein" ? 0.012 : 0.003;
      for (let e = 1; e <= n; e++) {
        const t = 0.35 + 2.2 * Math.exp(-e / 18) - (art === "klein" ? 0.0018 : 0.0008) * e;
        let v = 0.65 + 2.0 * Math.exp(-e / 16) + (e > min ? anstieg * (e - min) : 0);
        v += 0.04 * rausch(e, art === "klein" ? 1 : 2);
        tr.push(Math.max(0.05, t + 0.015 * rausch(e, 3)));
        va.push(v);
      }
      return [tr, va];
    }

    function zeichne() {
      const n = +iE.value, pat = +iP.value, art = sel.value;
      const [tr, va] = kurven(n, art);
      // Early Stopping simulieren
      let best = Infinity, bestE = 1, stopp = n;
      for (let e = 1; e <= n; e++) {
        if (va[e - 1] < best - 1e-6) { best = va[e - 1]; bestE = e; }
        else if (e - bestE >= pat) { stopp = e; break; }
      }
      const M = { l: 40, r: 10, t: 12, b: 28 };
      const maxY = 3;
      const X = (e) => M.l + ((e - 1) / Math.max(1, n - 1)) * (c._b - M.l - M.r);
      const Y = (v) => c._h - M.b - (Math.min(v, maxY) / maxY) * (c._h - M.t - M.b);
      const fg = css("--md-default-fg-color");
      ctx.clearRect(0, 0, c._b, c._h);
      ctx.fillStyle = css("--md-default-bg-color");
      ctx.fillRect(0, 0, c._b, c._h);
      ctx.font = "11px sans-serif"; ctx.fillStyle = fg;
      ctx.fillText("Loss", 4, 12); ctx.fillText("Epoche →", c._b - 60, c._h - 6);
      // Stopp-Bereich
      if (stopp < n) {
        ctx.fillStyle = "rgba(220,38,38,.10)";
        ctx.fillRect(X(stopp), M.t, X(n) - X(stopp), c._h - M.t - M.b);
      }
      const linie = (d, f, bis) => {
        ctx.strokeStyle = f; ctx.lineWidth = 2; ctx.beginPath();
        d.slice(0, bis).forEach((v, i) => (i ? ctx.lineTo(X(i + 1), Y(v)) : ctx.moveTo(X(1), Y(v))));
        ctx.stroke();
      };
      linie(tr, "#6366f1", n);
      linie(va, "#f59e0b", n);
      // beste Epoche
      ctx.strokeStyle = "#16a34a"; ctx.setLineDash([4, 4]);
      ctx.beginPath(); ctx.moveTo(X(bestE), M.t); ctx.lineTo(X(bestE), c._h - M.b); ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = "#6366f1"; ctx.fillText("■ train/loss", M.l + 8, M.t + 12);
      ctx.fillStyle = "#f59e0b"; ctx.fillText("■ val/loss", M.l + 90, M.t + 12);
      ctx.fillStyle = "#16a34a"; ctx.fillText("┆ best.pt", M.l + 160, M.t + 12);

      info.innerHTML =
        `Bestes Modell (<code>best.pt</code>) in Epoche <b>${bestE}</b>. ` +
        (stopp < n
          ? `Early Stopping bricht nach Epoche <b>${stopp}</b> ab (${pat} Epochen ohne Verbesserung) – das spart <b>${n - stopp}</b> Epochen Rechenzeit.`
          : `Kein Abbruch: Innerhalb von ${n} Epochen gab es nie ${pat} Epochen ohne Verbesserung.`) +
        (art === "klein" && n > 60 ? " Siehst du, wie <b>val/loss</b> wieder steigt, während train/loss weiter fällt? Das ist <b>Overfitting</b>: Das Modell lernt die Trainingsbilder auswendig." : "");
    }
    [iE, iP].forEach((i) => i.addEventListener("input", zeichne));
    sel.addEventListener("change", zeichne);
    zeichne();
  }

  // ======================================================================
  // 5) Bildgröße imgsz: Was sieht das Modell noch?
  // ======================================================================
  function expImgsz(box) {
    titel(box, "Experiment: Bildgröße (imgsz) – was sieht das Netz noch?");
    const img = new Image();
    img.src = bildUrl(box, "zidane.jpg");
    const [c, ctx] = canvas(560, 315);
    box.appendChild(c);
    const stufen = [64, 128, 160, 320, 480, 640, 1280];
    const [lS, iS] = regler("imgsz", 0, stufen.length - 1, 1, 5, (v) => stufen[v] + " px");
    box.appendChild(el("div", { class: "regler" }, [lS]));
    const info = el("div", { class: "hinweis" });
    box.appendChild(info);
    const off = document.createElement("canvas");

    function zeichne() {
      if (!img.complete || !img.naturalWidth) return;
      const s = stufen[+iS.value];
      const f = s / Math.max(img.naturalWidth, img.naturalHeight);
      off.width = Math.max(1, Math.round(img.naturalWidth * f));
      off.height = Math.max(1, Math.round(img.naturalHeight * f));
      off.getContext("2d").drawImage(img, 0, 0, off.width, off.height);
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(off, 0, 0, c._b, c._h);
      const px = off.width * off.height;
      info.innerHTML = `Das Netz bekommt ein Bild mit <b>${off.width} × ${off.height}</b> Pixeln (≈ ${(px / 1000).toFixed(0)}k Pixel). ` +
        `Rechenaufwand relativ zu 640: <b>×${((s / 640) ** 2).toFixed(2)}</b>. ` +
        (s <= 160 ? "Die Krawatte ist kaum noch zu erkennen – kleine Objekte gehen verloren!" : s >= 1280 ? "Sehr detailliert, aber das Training dauert etwa 4× so lang und braucht viel mehr GPU-Speicher." : "Guter Kompromiss zwischen Detail und Geschwindigkeit.");
    }
    iS.addEventListener("input", zeichne);
    img.onload = zeichne;
    zeichne();
  }

  const EXPERIMENTE = { iou: expIoU, pr: expPR, label: expLabel, loss: expLoss, imgsz: expImgsz };

  function init() {
    document.querySelectorAll(".exp[data-exp]").forEach((box) => {
      if (box.dataset.fertig) return;
      const f = EXPERIMENTE[box.dataset.exp];
      if (!f) return;
      box.dataset.fertig = "1";
      box.innerHTML = "";
      try { f(box); } catch (e) { box.textContent = "Experiment konnte nicht geladen werden: " + e.message; console.error(e); }
    });
  }

  if (typeof document$ !== "undefined") document$.subscribe(init);
  else document.addEventListener("DOMContentLoaded", init);

  // Beim Wechsel Hell/Dunkel die Canvas-Experimente neu aufbauen (Farben anpassen)
  new MutationObserver(() => {
    document.querySelectorAll(".exp[data-exp]").forEach((b) => delete b.dataset.fertig);
    init();
  }).observe(document.body, { attributes: true, attributeFilter: ["data-md-color-scheme"] });
})();
