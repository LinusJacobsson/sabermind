CREATE TABLE odds (
    odds_id text PRIMARY KEY
        CHECK (odds_id ~ '^[0-9a-v]{19}[0g]$'),
    event_id text NOT NULL REFERENCES events(event_id) ON DELETE CASCADE,
    bookmaker text NOT NULL,
    market_type text NOT NULL,
    outcome text NOT NULL,
    odds_value numeric NOT NULL CHECK (odds_value > 0),
    updated_at timestamptz NOT NULL DEFAULT now(),
    created_at timestamptz NOT NULL DEFAULT now()
);