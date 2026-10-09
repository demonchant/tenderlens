# TenderLens live desk UI

This is a multi-page live TED source interface. It is not a static fixture demo and does not run when opened directly from `file://`; serve it through `tenderlens.web` so `/api/versions` reaches the live TED Search API.

## Pages

- `index.html` — enter an actual TED publication ID; show live source records, hashes, explicit amendment edges, and fetch status.
- `compare.html` — inspect one TED BT-758-linked notice pair and structurally compare fields TED returned.
- `mechanism.html` — inspect the task roles and testnet implementation status.
- `scoring.html` — inspect the scoring contract and evidence limits; it does not calculate or display a pretend miner score.

All pages link directly to all other pages. User actions have visible state feedback; source/API interactions have loading/success/error transitions. Keyboard focus and reduced-motion support are defined in `styles.css`. The layout uses a field notebook / orbital map / procurement gazette visual grammar, not a generic card dashboard. It loads no external font, image, analytics or UI library.

The captured `8-2026` TED record exists only as a documented test/evidence artifact. The frontend requires a publication input and always queries TED live. It never substitutes that captured evidence if a request fails.

Run from repository root:

```powershell
python -m pip install -e .
tenderlens-web
```

Then open `http://127.0.0.1:8787`. The page-structure check is `node web/check-pages.mjs`.
