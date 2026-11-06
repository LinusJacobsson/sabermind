-- depends: 0001_create_teams 0002_create_players 0003_create_events 0006_create_mappings
-- Preserve migration 0006 for databases where it has already been applied.
-- Run with yoyo's default transactional behavior; deploy with the new repository.

LOCK TABLE mappings IN ACCESS EXCLUSIVE MODE;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM mappings
        WHERE object_type NOT IN ('player', 'team', 'event')
    ) THEN
        RAISE EXCEPTION 'Unsupported object_type in mappings; resolve before migrating';
    END IF;
END;
$$;

CREATE TABLE player_mappings (
    source text NOT NULL CHECK (source <> ''),
    external_id text NOT NULL CHECK (external_id <> ''),
    player_id text NOT NULL REFERENCES players(player_id),
    updated_at timestamptz NOT NULL DEFAULT now(),
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (source, external_id)
);

CREATE INDEX player_mappings_player_source_idx
    ON player_mappings (player_id, source);

CREATE TABLE team_mappings (
    source text NOT NULL CHECK (source <> ''),
    external_id text NOT NULL CHECK (external_id <> ''),
    team_id text NOT NULL REFERENCES teams(team_id),
    updated_at timestamptz NOT NULL DEFAULT now(),
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (source, external_id)
);

CREATE INDEX team_mappings_team_source_idx
    ON team_mappings (team_id, source);

CREATE TABLE event_mappings (
    source text NOT NULL CHECK (source <> ''),
    external_id text NOT NULL CHECK (external_id <> ''),
    event_id text NOT NULL REFERENCES events(event_id),
    updated_at timestamptz NOT NULL DEFAULT now(),
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (source, external_id)
);

CREATE INDEX event_mappings_event_source_idx
    ON event_mappings (event_id, source);

INSERT INTO player_mappings (source, external_id, player_id, updated_at, created_at)
SELECT source, external_id, object_id, updated_at, created_at
FROM mappings WHERE object_type = 'player';

INSERT INTO team_mappings (source, external_id, team_id, updated_at, created_at)
SELECT source, external_id, object_id, updated_at, created_at
FROM mappings WHERE object_type = 'team';

INSERT INTO event_mappings (source, external_id, event_id, updated_at, created_at)
SELECT source, external_id, object_id, updated_at, created_at
FROM mappings WHERE object_type = 'event';

-- All supported rows have been copied successfully within this transaction.
DROP TABLE mappings;
