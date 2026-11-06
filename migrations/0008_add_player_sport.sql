-- depends: 0002_create_players
-- Baseball is the only supported sport for existing player records.
ALTER TABLE players ADD COLUMN sport text NOT NULL DEFAULT 'baseball';
