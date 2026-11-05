CREATE TABLE players (
    player_id text PRIMARY KEY
        CHECK (player_id ~ '^[0-9a-v]{19}[0g]$'),
    name text NOT NULL,
    date_of_birth date NOT NULL,
    position text NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now(),
    created_at timestamptz NOT NULL DEFAULT now()
);