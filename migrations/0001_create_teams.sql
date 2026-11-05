CREATE TABLE teams (
    team_id text PRIMARY KEY
        CHECK (team_id ~ '^[0-9a-v]{19}[0g]$'),
    name text NOT NULL,
    league text NOT NULL,
    sport text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);