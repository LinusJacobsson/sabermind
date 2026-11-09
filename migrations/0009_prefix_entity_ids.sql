-- depends: 0004_create_odds 0005_create_model_predictions 0007_split_mappings 0008_add_player_sport
-- Run transactionally with the application stopped for the ID format change.
-- Keep the existing XID suffix; change internal IDs and all their references.

LOCK TABLE teams, players, events, odds, model_predictions,
    team_mappings, player_mappings, event_mappings IN ACCESS EXCLUSIVE MODE;

-- Temporarily remove foreign keys so both sides can be updated together.
ALTER TABLE team_mappings DROP CONSTRAINT team_mappings_team_id_fkey;
ALTER TABLE player_mappings DROP CONSTRAINT player_mappings_player_id_fkey;
ALTER TABLE event_mappings DROP CONSTRAINT event_mappings_event_id_fkey;
ALTER TABLE odds DROP CONSTRAINT odds_event_id_fkey;
ALTER TABLE model_predictions DROP CONSTRAINT model_predictions_event_id_fkey;

-- PostgreSQL assigned these names to the original inline CHECK constraints.
ALTER TABLE teams DROP CONSTRAINT teams_team_id_check;
ALTER TABLE players DROP CONSTRAINT players_player_id_check;
ALTER TABLE events DROP CONSTRAINT events_event_id_check;
ALTER TABLE odds DROP CONSTRAINT odds_odds_id_check;
ALTER TABLE model_predictions DROP CONSTRAINT model_predictions_prediction_id_check;

UPDATE teams SET team_id = 'team_' || team_id;
UPDATE players SET player_id = 'player_' || player_id;
UPDATE events SET event_id = 'event_' || event_id;
UPDATE odds SET odds_id = 'odds_' || odds_id, event_id = 'event_' || event_id;
UPDATE model_predictions
SET prediction_id = 'sim_' || prediction_id, event_id = 'event_' || event_id;

UPDATE team_mappings SET team_id = 'team_' || team_id;
UPDATE player_mappings SET player_id = 'player_' || player_id;
UPDATE event_mappings SET event_id = 'event_' || event_id;

ALTER TABLE teams ADD CONSTRAINT teams_team_id_check
    CHECK (team_id ~ '^team_[0-9a-v]{19}[0g]$');
ALTER TABLE players ADD CONSTRAINT players_player_id_check
    CHECK (player_id ~ '^player_[0-9a-v]{19}[0g]$');
ALTER TABLE events ADD CONSTRAINT events_event_id_check
    CHECK (event_id ~ '^event_[0-9a-v]{19}[0g]$');
ALTER TABLE odds ADD CONSTRAINT odds_odds_id_check
    CHECK (odds_id ~ '^odds_[0-9a-v]{19}[0g]$');
ALTER TABLE model_predictions ADD CONSTRAINT model_predictions_prediction_id_check
    CHECK (prediction_id ~ '^sim_[0-9a-v]{19}[0g]$');

-- Restore foreign keys and their original deletion behavior.
-- Adding them also validates every migrated reference before commit.
ALTER TABLE team_mappings ADD CONSTRAINT team_mappings_team_id_fkey
    FOREIGN KEY (team_id) REFERENCES teams(team_id);
ALTER TABLE player_mappings ADD CONSTRAINT player_mappings_player_id_fkey
    FOREIGN KEY (player_id) REFERENCES players(player_id);
ALTER TABLE event_mappings ADD CONSTRAINT event_mappings_event_id_fkey
    FOREIGN KEY (event_id) REFERENCES events(event_id);
ALTER TABLE odds ADD CONSTRAINT odds_event_id_fkey
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE;
ALTER TABLE model_predictions ADD CONSTRAINT model_predictions_event_id_fkey
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE;
