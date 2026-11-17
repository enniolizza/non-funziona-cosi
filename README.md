# Non Funziona Così

Sito editoriale statico, compilato con Eleventy e pubblicato da GitHub Pages
dal branch `main`, cartella root. Le pagine generate sono sincronizzate e
versionate ai percorsi pubblici correnti.

## Struttura

| Percorso | Responsabilità |
| --- | --- |
| `src/index.njk` | Ingresso con redirect HTML e link di riserva |
| `src/pagine/` | Template della prima pagina e del manifesto |
| `src/articoli/` | Template, fonti e immagini degli articoli |
| `src/_includes/` | Parziali condivisi per testata, navigazione e footer |
| `src/assets/css/shared.css` | Token semantici, font locali, testata, footer, accessibilità |
| `src/assets/fonts/` | Cinzel, Playfair Display, Inter in WOFF2, licenze OFL e provenienza |
| `src/assets/css/` | Fogli di stile condivisi e specifici delle pagine |
| `src/assets/js/carousel.js` | Navigazione manuale e accessibile dei banner |
| `.eleventy.js` | Build statico da `src/` a `_site/`; permalink espliciti |
| `scripts/sync_pages.py` | Sincronizza o verifica l'output versionato in root rispetto a `_site/` |
| `scripts/check_site.py` | Verifiche offline senza dipendenze esterne |
| `scripts/check_history.py` | Blocca gli asset rimossi in `HEAD` e nei commit entranti rispetto alla base |
| `tests/content-baseline.json` | Impronte del contenuto originale e collegamenti preservati |
| `tests/browser-smoke.cjs` | Smoke test Playwright su quattro viewport |
| `docs/revisione-sicurezza-2026-10-22.md` | Analisi, fonti, limiti e interventi amministrativi |

## Anteprima locale

Dalla cartella del repository, con Node.js 24:

```bash
npm ci
npm run build
npm run sync:pages
python -m http.server 8000 --bind 127.0.0.1
```

Aprire `http://127.0.0.1:8000/`. Il server è solo per l'anteprima locale.
Gli URL pubblici, inclusi i nomi `.html` degli articoli, sono conservati da
permalink espliciti. La sorgente Pages è il branch `main`, cartella `/`.

## Verifiche prima di pubblicare

```bash
npm ci
npm run build
python scripts/sync_pages.py --check
python scripts/check_site.py --root _site
python scripts/check_history.py
python -m unittest discover -s tests
node --check src/assets/js/carousel.js
npm run test:browser
git diff --check
git diff --check origin/main...HEAD
```

Il primo controllo del diff riguarda le modifiche non ancora in stage; il
secondo confronta i commit del ramo con `origin/main` (aggiornare prima i ref).
La pipeline `Site checks` compila e controlla `_site`, verifica che gli output
versionati in root coincidano con il build, installa Chromium ed esegue i test
browser su ogni PR e sui push a `main`. Dopo una modifica a template o asset,
eseguire `npm run build` e `npm run sync:pages`, quindi includere gli output
root nella modifica. Il test browser avvia e chiude un server locale, verifica
quattro larghezze da 320 a 1440 px, assenza di overflow orizzontale, adattamento
della copertina Superbonus, navigazione da tastiera, redirect anche senza
JavaScript, caricamento delle nove varianti dei font locali, newsletter in
arrivo e blocco reale degli script inline e dei font esterni dalla CSP.
Per usare Chromium già presente, impostare `CHROME_PATH`; per screenshot,
`QA_OUTPUT`. Le Actions sono fissate a commit; non esiste un workflow di deploy.
In CI il controllo della cronologia riceve la base e la testa del cambiamento:
permette copie storiche già presenti prima della base, ma blocca la loro
reintroduzione nei commit entranti o nell'albero finale. Senza `BASE_SHA`,
l'esecuzione locale controlla solo l'albero corrente.

## Modifiche editoriali

I testi di articoli e manifesto sono protetti da impronte del testo nel `main`
e dal confronto dei collegamenti esterni. Non rigenerare le impronte per
nascondere una regressione: aggiornarle solo dopo una modifica editoriale
intenzionale, controllando il diff rispetto alla versione precedente.
I dati degli articoli risalgono ad aprile 2026; il refactoring non costituisce
una verifica o un aggiornamento delle notizie.

Per una nuova pagina, creare un template in `src/` con un `permalink` esplicito,
mantenere la CSP all'inizio di `head`, utilizzare CSS e
JavaScript locali e registrare gli URL nella sitemap. Evitare stili e gestori
JavaScript inline. Non inserire chiavi, token, file privati o credenziali nel
repository: tutti i file del repository pubblico sono consultabili.
`lastmod` nella sitemap indica l'ultima modifica significativa della pagina,
non la data di pubblicazione. Per i due articoli d'archivio il campo facoltativo
è omesso: il refactoring non aggiorna prezzi, dati o notizie. Le date originali
restano nel testo; una nota esterna al corpo dell'articolo chiarisce il contesto
storico. Home e ticker presentano esplicitamente l'archivio di aprile 2026.

I font si caricano esclusivamente dal sito con `font-src 'self'`. Provenienza,
licenze e impronte sono descritte in `src/assets/fonts/README.md`; il controllo
offline rifiuta font esterni e rileva modifiche ai file acquisiti.

La newsletter è esplicitamente inattiva e non raccoglie indirizzi. Attivarla
richiede una scelta separata del servizio, una verifica dei dati trattati e
una modifica mirata di `form-action` / `connect-src`; non allargare la CSP
con `*` o `unsafe-inline` per aggirare un blocco.

## Refactoring applicato

- **Extract Method**: selezione dei banner in `showSlide`, eventi registrati
  con `addEventListener`, stato confinato nel modulo.
- **Duplicate Code**: testata, navigazione e footer riutilizzati da parziali
  Eleventy; palette semantica condivisa dai fogli di stile.
- **Separazione delle responsabilità**: contenuto in HTML, presentazione in CSS,
  interazione in JavaScript. Classi descrittive sostituiscono gli stili inline.
- **Semplificazione**: rimosso il redirect JavaScript ridondante e il finto
  invio newsletter; navigazione dei banner senza timer automatico.
- **Conservazione del comportamento utile**: stessi URL degli articoli,
  immagini e fonti, lettura e collegamenti disponibili senza JavaScript.

Riferimenti: [tecniche](https://refactoring.guru/refactoring/techniques),
[code smells](https://refactoring.guru/refactoring/smells),
[Duplicate Code](https://refactoring.guru/smells/duplicate-code),
[Extract Method](https://refactoring.guru/extract-method).

## Rilascio e ripristino

Esaminare la pull request e i controlli prima di integrare in `main`.
GitHub Pages serve direttamente i file versionati in root dal branch `main`;
`Site checks` impedisce che gli output pubblici divergano dai template.
Dopo il rilascio verificare home, manifesto, dossier e header HTTP dal sito
pubblico; le prove locali non attestano la configurazione remota.
Per annullare, creare una PR che esegua il revert del commit integrato:
non cancellare la cronologia e non eseguire un force push su `main`.
