/*
 * Live-Demo: YOLO26n (COCO, 80 Klassen) läuft direkt im Browser mit ONNX Runtime Web.
 * Keine Daten verlassen den Rechner – alles wird lokal im Browser berechnet.
 * Einbinden: <div class="exp live-demo" data-modell="../../assets/models/yolo26n.onnx"></div>
 */
(function () {
  "use strict";
  const ORT_VERSION = "1.20.1";
  const ORT_URL = `https://cdn.jsdelivr.net/npm/onnxruntime-web@${ORT_VERSION}/dist/`;
  const GROESSE = 640;
  const COCO = ["person","bicycle","car","motorcycle","airplane","bus","train","truck","boat","traffic light","fire hydrant","stop sign","parking meter","bench","bird","cat","dog","horse","sheep","cow","elephant","bear","zebra","giraffe","backpack","umbrella","handbag","tie","suitcase","frisbee","skis","snowboard","sports ball","kite","baseball bat","baseball glove","skateboard","surfboard","tennis racket","bottle","wine glass","cup","fork","knife","spoon","bowl","banana","apple","sandwich","orange","broccoli","carrot","hot dog","pizza","donut","cake","chair","couch","potted plant","bed","dining table","toilet","tv","laptop","mouse","remote","keyboard","cell phone","microwave","oven","toaster","sink","refrigerator","book","clock","vase","scissors","teddy bear","hair drier","toothbrush"];
  const DE = {person:"Person",bicycle:"Fahrrad",car:"Auto",bus:"Bus",truck:"Lkw",tie:"Krawatte",bottle:"Flasche",cup:"Tasse",chair:"Stuhl",laptop:"Laptop",mouse:"Maus",keyboard:"Tastatur","cell phone":"Handy",book:"Buch",scissors:"Schere",clock:"Uhr",backpack:"Rucksack",tv:"Bildschirm",remote:"Fernbedienung","potted plant":"Pflanze","dining table":"Tisch",elephant:"Elefant",zebra:"Zebra",dog:"Hund",cat:"Katze"};

  let ortLaden = null;
  function ladeOrt() {
    if (window.ort) return Promise.resolve(window.ort);
    if (!ortLaden) {
      ortLaden = new Promise((ok, fehler) => {
        const s = document.createElement("script");
        s.src = ORT_URL + "ort.min.js";
        s.onload = () => ok(window.ort);
        s.onerror = () => fehler(new Error("ONNX Runtime konnte nicht geladen werden (Internet?)"));
        document.head.appendChild(s);
      });
    }
    return ortLaden;
  }

  const farbe = (k) => `hsl(${(k * 47) % 360} 85% 50%)`;

  function iou(a, b) {
    const x1 = Math.max(a[0], b[0]), y1 = Math.max(a[1], b[1]);
    const x2 = Math.min(a[2], b[2]), y2 = Math.min(a[3], b[3]);
    const i = Math.max(0, x2 - x1) * Math.max(0, y2 - y1);
    const u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i;
    return u > 0 ? i / u : 0;
  }

  // Non-Maximum Suppression pro Klasse
  function nms(boxen, schwelle) {
    boxen.sort((a, b) => b.conf - a.conf);
    const behalten = [];
    for (const b of boxen) {
      if (behalten.every((k) => k.k !== b.k || iou(k.box, b.box) < schwelle)) behalten.push(b);
    }
    return behalten;
  }

  function baueDemo(wurzel) {
    if (wurzel.dataset.fertig) return;
    wurzel.dataset.fertig = "1";
    wurzel.innerHTML = "";
    const modellUrl = new URL(wurzel.dataset.modell || "../../assets/models/yolo26n.onnx", location.href).href;
    const bildBasis = new URL(wurzel.dataset.bilder || "../../assets/img/", location.href).href;

    const h = (tag, attrs = {}, txt) => {
      const e = document.createElement(tag);
      Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v));
      if (txt) e.textContent = txt;
      return e;
    };

    wurzel.appendChild(h("div", { class: "exp-titel" }, "Live-Demo: YOLO26n erkennt 80 Alltagsobjekte – direkt in deinem Browser"));
    const leiste = h("div", { class: "live-leiste" });
    const bStart = h("button", {}, "▶ Modell laden");
    const bBus = h("button", { class: "sek" }, "Bild: Bus");
    const bZidane = h("button", { class: "sek" }, "Bild: Fußball");
    const bUpload = h("button", { class: "sek" }, "📁 Eigenes Bild");
    const bCam = h("button", { class: "sek" }, "📷 Webcam");
    const datei = h("input", { type: "file", accept: "image/*" });
    datei.style.display = "none";
    const status = h("span", { class: "live-status" }, "Noch nicht geladen (ca. 10 MB).");
    [bBus, bZidane, bUpload, bCam].forEach((b) => (b.disabled = true));
    leiste.append(bStart, bBus, bZidane, bUpload, bCam, datei, status);
    wurzel.appendChild(leiste);

    const regl = h("div", { class: "regler" });
    const mkRegler = (txt, min, max, step, wert) => {
      const inp = h("input", { type: "range", min, max, step, value: wert });
      const anz = h("b", {}, (+wert).toFixed(2));
      inp.addEventListener("input", () => { anz.textContent = (+inp.value).toFixed(2); neuZeichnen(); });
      const lab = h("label");
      lab.append(h("span", {}, txt), inp, anz);
      regl.appendChild(lab);
      return inp;
    };
    const iConf = mkRegler("Confidence ≥", 0.01, 0.95, 0.01, 0.25);
    const iIou = mkRegler("NMS-IoU", 0.1, 0.95, 0.05, 0.5);
    const cbNms = h("input", { type: "checkbox" });
    cbNms.checked = true;
    cbNms.addEventListener("change", neuZeichnen);
    const labNms = h("label");
    labNms.append(cbNms, h("span", {}, "NMS aktiv"));
    regl.appendChild(labNms);
    wurzel.appendChild(regl);

    const cv = h("canvas", { width: GROESSE, height: GROESSE });
    cv.style.width = "100%";
    cv.style.maxWidth = "640px";
    wurzel.appendChild(cv);
    const ctx = cv.getContext("2d");
    const info = h("div", { class: "werte" });
    wurzel.appendChild(info);
    const liste = h("div", { class: "hinweis" });
    wurzel.appendChild(liste);
    const video = h("video", { playsinline: "", muted: "" });
    video.muted = true;

    let sitzung = null;
    let rohdaten = null;   // Kandidaten vor Filter
    let quelle = null;     // Bild oder Video
    let skala = null;      // Letterbox-Parameter
    let camAn = false, stream = null, laeuft = false, msLetzte = 0;

    function kachel(titel, wert) {
      const d = h("div", { class: "wert" });
      d.append(h("b", {}, String(wert)), h("small", {}, titel));
      return d;
    }

    async function ladeModell() {
      bStart.disabled = true;
      status.textContent = "Lade ONNX Runtime …";
      try {
        const ort = await ladeOrt();
        ort.env.wasm.wasmPaths = ORT_URL;
        ort.env.wasm.numThreads = 1;
        status.textContent = "Lade Modell (10 MB) …";
        sitzung = await ort.InferenceSession.create(modellUrl, { executionProviders: ["wasm"] });
        status.textContent = "✔ Modell bereit. Wähle ein Bild oder die Webcam.";
        [bBus, bZidane, bUpload, bCam].forEach((b) => (b.disabled = false));
        bStart.style.display = "none";
        ladeBild(bildBasis + "bus.jpg");
      } catch (e) {
        status.textContent = "Fehler: " + e.message;
        bStart.disabled = false;
        console.error(e);
      }
    }

    // Bild/Video → Letterbox 640×640 → Tensor [1,3,640,640]
    function vorverarbeiten(q, w, hh) {
      const r = Math.min(GROESSE / w, GROESSE / hh);
      const nw = Math.round(w * r), nh = Math.round(hh * r);
      const dx = (GROESSE - nw) / 2, dy = (GROESSE - nh) / 2;
      const off = document.createElement("canvas");
      off.width = GROESSE; off.height = GROESSE;
      const o = off.getContext("2d");
      o.fillStyle = "rgb(114,114,114)";
      o.fillRect(0, 0, GROESSE, GROESSE);
      o.drawImage(q, dx, dy, nw, nh);
      const px = o.getImageData(0, 0, GROESSE, GROESSE).data;
      const n = GROESSE * GROESSE;
      const t = new Float32Array(3 * n);
      for (let i = 0; i < n; i++) {
        t[i] = px[i * 4] / 255;
        t[n + i] = px[i * 4 + 1] / 255;
        t[2 * n + i] = px[i * 4 + 2] / 255;
      }
      return { t, r, dx, dy, w, h: hh };
    }

    async function analysiere(q, w, hh) {
      const p = vorverarbeiten(q, w, hh);
      const t0 = performance.now();
      const ein = new window.ort.Tensor("float32", p.t, [1, 3, GROESSE, GROESSE]);
      const aus = await sitzung.run({ [sitzung.inputNames[0]]: ein });
      msLetzte = performance.now() - t0;
      const d = aus[sitzung.outputNames[0]].data; // [1, 84, 8400]
      const N = 8400, K = 80;
      const kand = [];
      for (let i = 0; i < N; i++) {
        let best = 0, bk = 0;
        for (let k = 0; k < K; k++) {
          const s = d[(4 + k) * N + i];
          if (s > best) { best = s; bk = k; }
        }
        if (best < 0.01) continue;
        const cx = d[i], cy = d[N + i], bw = d[2 * N + i], bh = d[3 * N + i];
        // zurück in Originalkoordinaten
        const x1 = (cx - bw / 2 - p.dx) / p.r, y1 = (cy - bh / 2 - p.dy) / p.r;
        const x2 = (cx + bw / 2 - p.dx) / p.r, y2 = (cy + bh / 2 - p.dy) / p.r;
        kand.push({ box: [x1, y1, x2, y2], conf: best, k: bk });
      }
      rohdaten = kand;
      skala = p;
      quelle = q;
      neuZeichnen();
    }

    function neuZeichnen() {
      if (!quelle || !skala) return;
      const w = skala.w, hh = skala.h;
      cv.width = w; cv.height = hh;
      ctx.drawImage(quelle, 0, 0, w, hh);
      const conf = +iConf.value;
      let boxen = rohdaten.filter((b) => b.conf >= conf);
      const vorNms = boxen.length;
      if (cbNms.checked) boxen = nms(boxen.map((b) => ({ ...b })), +iIou.value);
      const lw = Math.max(2, Math.round(Math.max(w, hh) / 300));
      ctx.lineWidth = lw;
      ctx.font = `bold ${Math.max(12, lw * 6)}px sans-serif`;
      boxen.forEach((b) => {
        const [x1, y1, x2, y2] = b.box;
        const f = farbe(b.k);
        ctx.strokeStyle = f;
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
        const name = COCO[b.k];
        const t = `${DE[name] || name} ${b.conf.toFixed(2)}`;
        const tw = ctx.measureText(t).width + 8, th = Math.max(16, lw * 8);
        ctx.fillStyle = f;
        ctx.fillRect(x1, Math.max(0, y1 - th), tw, th);
        ctx.fillStyle = "#000";
        ctx.fillText(t, x1 + 4, Math.max(th - 4, y1 - 4));
      });
      info.innerHTML = "";
      info.append(
        kachel("Kandidaten (Rohausgabe)", 8400),
        kachel("nach Confidence-Filter", vorNms),
        kachel(cbNms.checked ? "nach NMS (Ergebnis)" : "ohne NMS (Ergebnis)", boxen.length),
        kachel("Rechenzeit", Math.round(msLetzte) + " ms")
      );
      const zaehl = {};
      boxen.forEach((b) => { const n = DE[COCO[b.k]] || COCO[b.k]; zaehl[n] = (zaehl[n] || 0) + 1; });
      liste.textContent = Object.keys(zaehl).length
        ? "Gefunden: " + Object.entries(zaehl).map(([n, z]) => `${z}× ${n}`).join(", ")
        : "Nichts gefunden – senke die Confidence-Schwelle oder probiere ein anderes Bild.";
    }

    function ladeBild(src) {
      stoppeCam();
      const img = new Image();
      img.crossOrigin = "anonymous";
      img.onload = () => analysiere(img, img.naturalWidth, img.naturalHeight);
      img.src = src;
    }

    async function schleife() {
      if (!camAn) return;
      if (!laeuft && video.readyState >= 2) {
        laeuft = true;
        // Standbild kopieren, damit Bild und Boxen zusammenpassen
        const f = document.createElement("canvas");
        f.width = video.videoWidth; f.height = video.videoHeight;
        f.getContext("2d").drawImage(video, 0, 0);
        try { await analysiere(f, f.width, f.height); } finally { laeuft = false; }
      }
      requestAnimationFrame(schleife);
    }

    async function starteCam() {
      if (camAn) { stoppeCam(); return; }
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 }, audio: false });
        video.srcObject = stream;
        await video.play();
        camAn = true;
        bCam.textContent = "⏹ Webcam stoppen";
        status.textContent = "Webcam läuft – alles wird lokal berechnet, nichts wird hochgeladen.";
        schleife();
      } catch (e) {
        status.textContent = "Webcam nicht verfügbar: " + e.message;
      }
    }
    function stoppeCam() {
      camAn = false;
      if (stream) stream.getTracks().forEach((t) => t.stop());
      stream = null;
      bCam.textContent = "📷 Webcam";
    }

    bStart.addEventListener("click", ladeModell);
    bBus.addEventListener("click", () => ladeBild(bildBasis + "bus.jpg"));
    bZidane.addEventListener("click", () => ladeBild(bildBasis + "zidane.jpg"));
    bUpload.addEventListener("click", () => datei.click());
    datei.addEventListener("change", () => {
      if (datei.files[0]) ladeBild(URL.createObjectURL(datei.files[0]));
    });
    bCam.addEventListener("click", starteCam);

    // Webcam beim Seitenwechsel (instant navigation) beenden
    if (typeof location$ !== "undefined") location$.subscribe(() => { if (!document.body.contains(wurzel)) stoppeCam(); });
  }

  function init() {
    document.querySelectorAll(".live-demo").forEach(baueDemo);
  }
  if (typeof document$ !== "undefined") document$.subscribe(init);
  else document.addEventListener("DOMContentLoaded", init);
})();
