# inQRedible Website

Sitio estático de `inqredibleapp.com` para la app nativa iOS **Generador QR: inQRedible**.

## Estructura

```text
.
├── CNAME
├── index.html
├── privacy.html
├── terms.html
├── support.html
├── qr-code-with-logo.html
├── wifi-qr-code.html
├── barcode-generator-iphone.html
├── robots.txt
├── sitemap.xml
├── llms.txt
├── es/
│   ├── index.html
│   ├── privacy.html
│   ├── terms.html
│   ├── soporte.html
│   ├── codigo-qr-con-logo.html
│   ├── codigo-qr-wifi.html
│   └── generador-codigo-barras-iphone.html
├── styles.css
├── script.js
├── content/
│   ├── release-content.json
│   └── 2.5.0-content-matrix.md
├── scripts/check_content.py
├── tests/test_check_content.py
└── images/
    ├── app-icon.png
    ├── apple-touch-icon.png
    ├── favicon.png
    ├── og-image.png
    ├── og-image.svg
    ├── en/
    │   ├── screenshot-hero.png
    │   ├── screenshot1.png
    │   ├── screenshot2.png
    │   ├── screenshot3.png
    │   └── screenshot4.png
    ├── es/
    │   ├── screenshot-hero.png
    │   ├── screenshot1.png
    │   ├── screenshot2.png
    │   ├── screenshot3.png
    │   └── screenshot4.png
    └── app-store-badge.svg
```

## Assets sincronizados desde la app

- `images/app-icon.png`: copiado desde `~/projects/inQRedible/inQRedible/Assets.xcassets/AppIcon.appiconset/AppIcon.png`.
- `images/apple-touch-icon.png` y `images/favicon.png`: derivados del AppIcon.
- `images/en/screenshot-hero.png` y `images/en/screenshot1.png` a `images/en/screenshot4.png`: copiados desde `~/projects/inQRedible/screenshots/final/en-US/`.
- `images/es/screenshot-hero.png` y `images/es/screenshot1.png` a `images/es/screenshot4.png`: copiados desde `~/projects/inQRedible/screenshots/final/es-ES/`.
- `images/og-image.svg`: fuente editable de la imagen social.
- `images/og-image.png`: imagen social horizontal para Open Graph/Twitter.

## Verificación local

Al ser una web estática, se puede abrir `index.html` directamente. Para revisar rutas y assets como en producción:

```bash
python3 -m http.server 4173
```

Después abre `http://localhost:4173`.

Antes de publicar, ejecuta las comprobaciones deterministas de contenido, enlaces, paridad EN/ES, rutas canónicas y claims:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_content.py
```

La fuente canónica es `content/release-content.json`; la matriz Markdown es generada y el checker falla si queda desactualizada.

## Despliegue

El sitio está preparado para GitHub Pages con dominio personalizado definido en `CNAME`:

```text
inqredibleapp.com
```

No requiere build ni dependencias de Node.

## Idiomas

- `/` es la versión inglesa y funciona como `x-default` para cualquier idioma no español.
- `/es/` contiene la versión española.
- `script.js` redirige automáticamente desde las páginas raíz a `/es/` cuando el idioma preferido del navegador empieza por `es`.
- Para forzar la revisión de la versión inglesa desde un navegador en español, añade `?lang=en` a la URL.

## SEO y GEO

- `sitemap.xml` declara las rutas indexables y sus pares `hreflang`.
- `robots.txt` apunta al sitemap.
- `llms.txt` resume el producto, claims importantes, rutas principales y enlaces de App Store para crawlers de IA.
- `content/release-content.json` vincula el sitio con el handoff de inQRedible 2.5.0 y registra `legal-2.5.0-v1`, proveedores, catálogo, límites y checkpoints externos.
- Las home incluyen `SoftwareApplication`, `WebSite`, `Organization` y `FAQPage` en JSON-LD.
- Las guías long-tail cubren búsquedas de alta intención: QR con logo, QR Wi-Fi y generador de códigos de barras para iPhone.
