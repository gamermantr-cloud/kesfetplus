# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and Oxlint's TypeScript related rules in your project.

## Native apps (Capacitor)

This is still a normal Vite web app (`npm run dev` is unchanged). Capacitor
wraps the built `dist/` output in a native WebView shell for the App
Store / Google Play, as an *additional* build target — it doesn't change
how the web app itself runs.

- Native projects: `android/` (Android Studio project) and `ios/` (Xcode
  project). Both are committed to git (this is the normal/recommended
  Capacitor setup — only their build output, `.gradle/`, `Pods/`, etc. are
  gitignored inside each, via the `.gitignore` each platform generated).
- App id: `com.kesfetplus.app`. Config: `capacitor.config.json`.
- API base URL: in dev, `/api` still goes through the Vite proxy to
  `127.0.0.1:8000` (unchanged). In a production/native build there is no
  dev-server to proxy through, so `src/lib/api.js` uses an absolute URL
  from the `VITE_API_BASE_URL` env var instead — see `.env.example` (not a
  real backend domain yet; set the real one there once hosting exists).

### Rebuilding the native projects after a code change

```bash
npm run build && npx cap sync
# or, per platform:
npm run cap:android   # build + sync + open Android Studio
npm run cap:ios        # build + sync + open Xcode (Mac only, see below)
```

### Testing on Android locally

Requires [Android Studio](https://developer.android.com/studio) installed
(with an Android SDK + an emulator or a USB-connected device). Run
`npm run cap:android`, then build/run from Android Studio as usual.

### Testing on iOS locally

**Not possible on this (Windows) machine.** `npx cap add ios` can scaffold
the Xcode project here (it did — see `ios/`), but actually building/running
an iOS app requires Xcode, which only runs on macOS. There is no Windows
workaround for this step.

The plan is to build/sign iOS via **Codemagic** (a CI service that runs
macOS build agents in the cloud) instead of a local Mac. That still needs,
separately, an Apple Developer Program account, certificates and
provisioning profiles — none of that exists yet and has to be set up by the
project owner (it requires a paid account and identity verification).

### App icon / splash screen

Not done yet — see `docs/capacitor-icon-splash.md` for why and the plan
(`@capacitor/assets`, needs an approved source image first).
