---
paths:
  - "frontend/src/**/*.jsx"
  - "frontend/src/**/*.css"
---

# Renk kuralı

Renk tokenleri `frontend/src/index.css` içinde `--color-*` değişkenleri
olarak tanımlı. Her ekran bu tokenlerden çekmeli, hex kodu hardcode
etmemeli (`bg-[#...]`, `style={{ color: '#...' }}` gibi kullanımlardan
kaçının — Tailwind'in token'a bağlı sınıflarını veya `var(--color-*)`
kullanın).
