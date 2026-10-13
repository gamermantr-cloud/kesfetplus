# Capacitor app icon & splash screen — TODO (needs user approval)

Capacitor native builds (`frontend/android`, `frontend/ios`) currently ship
with the **default Capacitor placeholder icon/splash** (the generic Capacitor
logo). This is fine for local testing but must be replaced before any real
App Store / Google Play submission — stores will accept a build with it, but
it looks unfinished.

## Why nothing was generated here

There is no real Keşfet Plus logo/brand mark yet. Making one up (a fake
"finished" logo) and committing it would misrepresent the brand, so this was
intentionally left undone. **Needs explicit user sign-off before a real
asset is committed.**

## Suggested placeholder direction (for approval, not implemented)

A minimal typographic mark using the existing "Editorial" theme tokens
already defined in `frontend/src/index.css` (`@theme` block — `--color-cream`,
`--color-tan`, `--color-espresso`, etc.) rather than inventing new brand
colors:

- Simple "K+" monogram (Fraunces, the app's existing serif display font),
  dark text (`--color-espresso` / `--color-tan-dark`) on the light background
  (`--color-cream` or `--color-sand`), or inverted for a dark splash variant.
- No illustration, no gradient logo — just a clean type mark until a real
  designer/brand asset exists.

This is a suggestion only. Do not generate/commit a real icon file without
the user explicitly approving a specific design.

## How to generate all sizes once a source image exists

Capacitor's official tool for this is `@capacitor/assets`. Workflow once
there's a single approved 1024×1024 PNG (icon, no transparency) and an
optional splash source image:

```bash
cd frontend
npm install -D @capacitor/assets
mkdir assets
# place icon.png (1024x1024) and splash.png (2732x2732 recommended) in assets/
npx capacitor-assets generate
```

This generates all required Android (`mipmap-*`, adaptive icon layers) and
iOS (`AppIcon.appiconset`, `Splash.imageset`) sizes automatically and wires
them into the native projects. Re-run after any source image change,
followed by `npx cap sync`.

Reference: https://github.com/ionic-team/capacitor-assets
