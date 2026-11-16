/*
 * Mini-Quiz für MkDocs Material
 * Verwendung im Markdown:
 *   <div class="quiz" data-titel="Check: Aufgabenarten" data-quiz='[
 *     {"q": "Frage?", "a": ["Antwort A", "Antwort B"], "c": 1, "e": "Erklärung"}
 *   ]'></div>
 * "c" = Index der richtigen Antwort (0-basiert) oder Liste bei Mehrfachauswahl.
 */
(function () {
  function baueQuiz(box, nr) {
    if (box.dataset.fertig) return;
    let fragen;
    try {
      fragen = JSON.parse(box.dataset.quiz);
    } catch (e) {
      box.textContent = "Quiz konnte nicht geladen werden (JSON-Fehler).";
      return;
    }
    box.dataset.fertig = "1";
    box.innerHTML = "";

    const kopf = document.createElement("div");
    kopf.className = "quiz-kopf";
    kopf.textContent = box.dataset.titel || "Kurz-Check";
    box.appendChild(kopf);

    fragen.forEach((f, i) => {
      const mehrfach = Array.isArray(f.c);
      const richtige = mehrfach ? f.c : [f.c];

      const frage = document.createElement("div");
      frage.className = "quiz-frage";
      frage.textContent = (i + 1) + ". " + f.q + (mehrfach ? " (mehrere richtig)" : "");
      box.appendChild(frage);

      const optionen = document.createElement("div");
      optionen.className = "quiz-optionen";
      // Antworten zufällig mischen (Original-Index bleibt in input.value erhalten)
      const reihenfolge = f.a.map((_, j) => j);
      for (let k = reihenfolge.length - 1; k > 0; k--) {
        const r = Math.floor(Math.random() * (k + 1));
        [reihenfolge[k], reihenfolge[r]] = [reihenfolge[r], reihenfolge[k]];
      }
      reihenfolge.forEach((j) => {
        const txt = f.a[j];
        const label = document.createElement("label");
        const inp = document.createElement("input");
        inp.type = mehrfach ? "checkbox" : "radio";
        inp.name = "quiz-" + nr + "-" + i;
        inp.value = j;
        const span = document.createElement("span");
        span.textContent = txt;
        label.append(inp, span);
        optionen.appendChild(label);
      });
      box.appendChild(optionen);

      const erkl = document.createElement("div");
      erkl.className = "quiz-erklaerung";
      erkl.textContent = f.e || "";
      box.appendChild(erkl);

      f._optionen = optionen;
      f._erkl = erkl;
      f._richtige = richtige;
    });

    const fuss = document.createElement("div");
    fuss.className = "quiz-fuss";
    const pruefen = document.createElement("button");
    pruefen.textContent = "Auswerten";
    const neu = document.createElement("button");
    neu.textContent = "Nochmal";
    neu.style.display = "none";
    const ergebnis = document.createElement("span");
    fuss.append(pruefen, neu, ergebnis);
    box.appendChild(fuss);

    pruefen.addEventListener("click", () => {
      let punkte = 0;
      fragen.forEach((f) => {
        const labels = [...f._optionen.querySelectorAll("label")];
        const gewaehlt = labels
          .filter((l) => l.querySelector("input").checked)
          .map((l) => +l.querySelector("input").value);
        labels.forEach((l) => {
          const j = +l.querySelector("input").value;
          l.classList.remove("richtig", "falsch");
          if (f._richtige.includes(j)) l.classList.add("richtig");
          else if (gewaehlt.includes(j)) l.classList.add("falsch");
          l.querySelector("input").disabled = true;
        });
        const korrekt =
          gewaehlt.length === f._richtige.length &&
          gewaehlt.every((j) => f._richtige.includes(j));
        if (korrekt) punkte++;
        f._erkl.classList.add("sichtbar");
      });
      const anteil = punkte / fragen.length;
      const smiley = anteil === 1 ? "🏆" : anteil >= 0.6 ? "👍" : "📖";
      ergebnis.textContent = `${smiley} ${punkte} von ${fragen.length} richtig`;
      pruefen.style.display = "none";
      neu.style.display = "";
    });

    neu.addEventListener("click", () => {
      delete box.dataset.fertig;
      baueQuiz(box, nr);
    });
  }

  function init() {
    document.querySelectorAll(".quiz[data-quiz]").forEach((b, i) => baueQuiz(b, i));
  }

  if (typeof document$ !== "undefined") document$.subscribe(init);
  else document.addEventListener("DOMContentLoaded", init);
})();
