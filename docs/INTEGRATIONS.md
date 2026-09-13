# Integrations & Automation Plugins

Full list of tools/APIs researched by the "EURO MİLYONERLERİ" agent team for
Keşfet Plus. Status legend:

- **Kodlandı** - wired into the codebase, works today (may need an API key to do real work)
- **Key bekliyor** - code-ready placeholder in `.env.example`, needs a real API key/account
- **Manuel kurulum** - needs a human to install/connect (GitHub App, Slack app, hosting account)

## Otomasyon (agent takımı mekanizmaları)

### Koordinator - PR review & merge
| Araç | Durum | Not |
|---|---|---|
| GitHub Actions | Kodlandı | `.github/workflows/ci.yml` |
| Dependabot | Kodlandı | `.github/dependabot.yml` |
| CodeRabbit | Manuel kurulum | GitHub App olarak repoya eklenmeli |
| Graphite | Manuel kurulum | Stacked-PR workflow'u için |
| Mergify | Manuel kurulum | Kural tabanlı otomatik merge |
| claude-code-action | Manuel kurulum | Resmi Anthropic GitHub Action |

### Ataturk - CI monitoring
| Araç | Durum | Not |
|---|---|---|
| GitHub Actions status | Kodlandı | Aynı CI workflow'u kullanılır |
| Sentry | Key bekliyor | `.env.example` -> `SENTRY_DSN` |
| Better Stack (Uptime) | Manuel kurulum | `/health` endpoint'ine bağlanacak |

### Baglayici - backlog grooming
| Araç | Durum | Not |
|---|---|---|
| Zapier | Manuel kurulum | Linear/Notion/Trello <-> Slack |
| Linear native entegrasyonu | Manuel kurulum | |

### Hafiza - code quality
| Araç | Durum | Not |
|---|---|---|
| Ruff | Kodlandı | `pyproject.toml`, `.pre-commit-config.yaml`, proje hook'u |
| mypy | Kodlandı | `pyproject.toml` |
| Bandit | Kodlandı | `pyproject.toml`, `.pre-commit-config.yaml` |
| pip-audit | Kodlandı | CI'da çalışıyor |
| pre-commit framework | Kodlandı | `.pre-commit-config.yaml` (kurulum: `pre-commit install`) |
| Claude Code PostToolUse hook | Kodlandı | `.claude/settings.json` - .py dosyaları düzenlenince otomatik ruff |

## Ürün (Keşfet Plus'ın kendisi)

### Anlık bilgi akışı / gerçek zamanlı veri
| Araç | Durum | Not |
|---|---|---|
| Google Places API (New) | Kodlandı | `agents/scout_agent.py` - `GOOGLE_PLACES_API_KEY` |
| Foursquare Places API | Key bekliyor | `.env.example` -> `FOURSQUARE_API_KEY` |
| Ably (WebSocket pub/sub) | Key bekliyor | `.env.example` -> `ABLY_API_KEY` |
| Firebase Realtime DB / Firestore | Manuel kurulum | Postgres gelene kadar hızlı prototip seçeneği |

### Mekan / restoran / otel veri kaynakları
| Araç | Durum | Not |
|---|---|---|
| TripAdvisor Content API | Key bekliyor | `.env.example` -> `TRIPADVISOR_API_KEY` |
| Amadeus API (otel) | Key bekliyor | `.env.example` -> `AMADEUS_API_KEY` / `AMADEUS_API_SECRET` |
| Booking.com Affiliate API | Manuel kurulum | Affiliate başvurusu gerekiyor |

### Trust-scoring / doğrulama (README hedefi)
| Araç | Durum | Not |
|---|---|---|
| OpenAI Moderation API | Key bekliyor | `.env.example` -> `OPENAI_API_KEY` (zaten vardı) |
| Sift Score API | Key bekliyor | `.env.example` -> `SIFT_API_KEY` |
| Hive AI Moderation | Key bekliyor | `.env.example` -> `HIVE_API_KEY` |

### Deploy
| Araç | Durum | Not |
|---|---|---|
| Railway | Manuel kurulum | MVP için önerilen ilk deploy hedefi |
| Render | Manuel kurulum | Production'a geçişte |
| Fly.io | Manuel kurulum | Global ölçek gerekirse |

## Öncelik sırası (MVP)

1. Google Places API key al -> Scout Agent gerçek veri döndürsün
2. Ably key al -> anlık bilgi akışı prototipi
3. `pre-commit install` çalıştır -> Hafiza mekanizması commit'lerde de aktif olsun
4. GitHub'a push et -> CI + Dependabot devreye girsin
5. Railway'e ilk deploy
