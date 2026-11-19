# Alzheimer's Lantern

The website at https://alzheimerslantern.com.

- `site/` is the live website. Netlify publishes this folder automatically on every change to `main`.
- `src/preview.html` is the single-page source. `src/build.py` turns it into the pages in `site/`.
- `src/hand-made/` holds files the build doesn't generate (site.js, logo, favicon, social card, robots.txt, _redirects). Copy them into `site/assets/` and `site/` after a rebuild.

Rebuild:

```
python3 src/build.py src/preview.html site
cp src/hand-made/{site.js,favicon.svg,logo.svg,social-card.png} site/assets/
cp src/hand-made/{robots.txt,_redirects} site/
```

Then regenerate `site/sitemap.xml` with every page.

Member PDFs are deliberately not in this repository. Anything in `site/` is public.
