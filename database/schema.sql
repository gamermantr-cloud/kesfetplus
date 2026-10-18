-- KesfetPlus PostgreSQL schema.
--
-- No PostGIS yet - deliberately. Seed venues only carry an approximate
-- district-center coordinate (see frontend/src/lib/districts.js and
-- database/checkins_store.py's _DISTRICT_LATLNG), not a real per-venue GPS
-- address. Adding PostGIS spatial columns/indexes now would mean either
-- leaving them unused or fabricating precise-looking coordinates that
-- don't exist - the second is forbidden by this project's "sahte veri
-- yasak" rule (see CLAUDE.md). PostGIS is a later phase, once real
-- per-venue coordinates exist - see
-- docs/research/turkiye-pazar-teknik-mimari.md Bölüm 2A.
--
-- Run this once against an empty database:
--   venv\Scripts\python.exe -c "import psycopg,os;psycopg.connect(os.environ['DATABASE_URL']).execute(open('database/schema.sql',encoding='utf-8').read())"
-- or simply, if you have the psql client:
--   psql "$DATABASE_URL" -f database/schema.sql
--
-- Idempotent: every statement uses IF NOT EXISTS, so re-running it against
-- a database that already has these tables is a safe no-op.

-- ---------------------------------------------------------------------------
-- Venues: the 243 real Istanbul places/restaurants/hotels that today live in
-- database/seed/{places,gurme,hotels}.json (see scripts/seed_venues.py).
--
-- Hybrid schema, per docs/research/turkiye-pazar-teknik-mimari.md Bölüm 2A's
-- recommendation: fixed columns for what every category shares and is
-- actually filtered/indexed on (id, category, name, district), JSONB for
-- everything else. places/gurme/hotels each carry a different and still-
-- evolving set of fields (tags/dish/priceLevel/michelinStars/...) - forcing
-- all of them into one wide fixed-column table would mean a lot of
-- always-NULL columns per category, which is exactly the kind of
-- over-engineering the research doc warns against for this project's scale.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS venues (
    id          TEXT PRIMARY KEY,
    category    TEXT NOT NULL CHECK (category IN ('places', 'gurme', 'hotels', 'sahne')),
    name        TEXT NOT NULL,
    district    TEXT,
    raw_data    JSONB NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_venues_district ON venues (district);
CREATE INDEX IF NOT EXISTS idx_venues_category ON venues (category);

-- ---------------------------------------------------------------------------
-- Users / sessions - see database/users_store.py.
--
-- member_number_seq backs the "founding member" feature (CLAUDE.md /
-- docs/research/buyume-ilk-100-kullanici-stratejisi.md Bölüm 1.4 & 2.4):
-- a real, monotonically increasing 1-indexed registration order. A DB
-- sequence gives this atomically for free, under concurrent registrations
-- from multiple API workers - the old JSON store could only approximate
-- this (len(users) + 1) *inside* a single-process threading.Lock, which
-- never worked across multiple workers to begin with.
-- ---------------------------------------------------------------------------
CREATE SEQUENCE IF NOT EXISTS member_number_seq START 1;

CREATE TABLE IF NOT EXISTS users (
    id                  TEXT PRIMARY KEY,
    email               TEXT NOT NULL UNIQUE,
    password_hash       TEXT NOT NULL,
    display_name        TEXT NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL,
    blocked_user_ids    TEXT[] NOT NULL DEFAULT '{}',
    is_moderator        BOOLEAN NOT NULL DEFAULT false,
    referral_code       TEXT NOT NULL UNIQUE,
    referred_by         TEXT REFERENCES users (id) ON DELETE SET NULL,
    member_number       INTEGER NOT NULL,
    is_founding_member  BOOLEAN NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_users_referred_by ON users (referred_by);

CREATE TABLE IF NOT EXISTS sessions (
    token       TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions (user_id);

-- ---------------------------------------------------------------------------
-- Comments - see database/comments_store.py. review_status/flagged_reason
-- are written by database/trust_scoring.py and database/content_filter.py,
-- same meaning as before (visible / pending_review / hidden).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS comments (
    id                      TEXT PRIMARY KEY,
    place_id                TEXT NOT NULL,
    author                  TEXT NOT NULL,
    author_user_id          TEXT REFERENCES users (id) ON DELETE SET NULL,
    text                    TEXT NOT NULL,
    lat                     DOUBLE PRECISION,
    lng                     DOUBLE PRECISION,
    accuracy                DOUBLE PRECISION,
    created_at              TIMESTAMPTZ NOT NULL,
    helpful_count           INTEGER NOT NULL DEFAULT 0,
    helpful_user_ids        TEXT[] NOT NULL DEFAULT '{}',
    computed_trust_score    DOUBLE PRECISION,
    flagged_reason          TEXT,
    review_status           TEXT NOT NULL DEFAULT 'visible',
    -- Yorumdan önceki kategoriye-özel puanlama (ör. {"hijyen": 4, "servis": 5}).
    -- Kriter seti venue.kind'e göre frontend'de belirleniyor (lib/ratingCriteria.js);
    -- burada serbest bırakıldı, backend hangi anahtarların "geçerli" olduğunu
    -- zorlamıyor - ortalamalar da frontend'de gerçek yorumlardan hesaplanıyor,
    -- hiçbir puan uydurulmuyor. NULL/boş = kullanıcı hiç puanlamadı.
    ratings                 JSONB
);
CREATE INDEX IF NOT EXISTS idx_comments_place_id ON comments (place_id);
CREATE INDEX IF NOT EXISTS idx_comments_author_user_id ON comments (author_user_id);
CREATE INDEX IF NOT EXISTS idx_comments_created_at ON comments (created_at);

-- ---------------------------------------------------------------------------
-- Check-ins + status updates ("anlık bilgi akışı") - see
-- database/checkins_store.py.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS checkins (
    id                  TEXT PRIMARY KEY,
    place_id            TEXT NOT NULL,
    author              TEXT NOT NULL,
    author_user_id      TEXT REFERENCES users (id) ON DELETE SET NULL,
    lat                 DOUBLE PRECISION,
    lng                 DOUBLE PRECISION,
    accuracy            DOUBLE PRECISION,
    location_verified   BOOLEAN NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_checkins_place_id ON checkins (place_id);
CREATE INDEX IF NOT EXISTS idx_checkins_author_user_id ON checkins (author_user_id);
CREATE INDEX IF NOT EXISTS idx_checkins_created_at ON checkins (created_at);

CREATE TABLE IF NOT EXISTS status_updates (
    id                  TEXT PRIMARY KEY,
    place_id            TEXT NOT NULL,
    author              TEXT NOT NULL,
    author_user_id      TEXT REFERENCES users (id) ON DELETE SET NULL,
    tag                 TEXT NOT NULL,
    text                TEXT NOT NULL DEFAULT '',
    created_at          TIMESTAMPTZ NOT NULL,
    review_status       TEXT NOT NULL DEFAULT 'visible',
    flagged_reason      TEXT,
    helpful_count       INTEGER NOT NULL DEFAULT 0,
    helpful_user_ids    TEXT[] NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_status_updates_place_id ON status_updates (place_id);
CREATE INDEX IF NOT EXISTS idx_status_updates_author_user_id ON status_updates (author_user_id);
CREATE INDEX IF NOT EXISTS idx_status_updates_created_at ON status_updates (created_at);

-- ---------------------------------------------------------------------------
-- Reports - see database/reports_store.py. Never auto-deletes the reported
-- content itself - this table only ever records that a report happened.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reports (
    id                  TEXT PRIMARY KEY,
    reporter_user_id    TEXT NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    target_type         TEXT NOT NULL,
    target_id           TEXT NOT NULL,
    place_id            TEXT NOT NULL,
    reason              TEXT NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL,
    status              TEXT NOT NULL DEFAULT 'open'
);
CREATE INDEX IF NOT EXISTS idx_reports_reporter_user_id ON reports (reporter_user_id);
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports (status);

-- ---------------------------------------------------------------------------
-- Web Push subscriptions - see database/push_subscriptions_store.py.
-- Composite PK matches the old store's dedup rule exactly: re-subscribing
-- with the same endpoint for the same user replaces that row (ON CONFLICT
-- DO UPDATE in the store) instead of duplicating it.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS push_subscriptions (
    user_id     TEXT NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    endpoint    TEXT NOT NULL,
    p256dh      TEXT NOT NULL,
    auth        TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (user_id, endpoint)
);
-- remove_subscription_by_endpoint() looks up by endpoint alone, regardless
-- of owning user (see database/push_notify.py - a dead-subscription cleanup
-- triggered by the push service itself returning 404/410).
CREATE INDEX IF NOT EXISTS idx_push_subscriptions_endpoint ON push_subscriptions (endpoint);
