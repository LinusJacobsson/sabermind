CREATE TABLE events (
    event_id text PRIMARY KEY
        CHECK (event_id ~ '^[0-9a-v]{19}[0g]$'),
    name text NOT NULL,
    sport text NOT NULL,
    start_time timestamptz NOT NULL,
    location text NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now(),
    created_at timestamptz NOT NULL DEFAULT now()
);