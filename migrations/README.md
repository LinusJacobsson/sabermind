# Database migrations and external identities

Migration `0006_create_mappings` has already been applied. Keep it unchanged and
apply `0007_split_mappings` as a forward migration:

```bash
uv run --env-file .env.dev yoyo list
uv run --env-file .env.dev yoyo apply --batch
```

These commands use `yoyo.ini` and `MIGRATION_DATABASE_URL` from the environment
file. Review the pending migration list before applying it. The database must
already exist. Do not run migration SQL outside a transaction.

`0008_add_player_sport` adds the `sport` column expected by `PlayerRepository`.
Existing players receive `baseball`, the only currently supported sport. Apply
this migration before using the updated player repository. The Python
`Player.date_of_birth` field now uses `date` to match the PostgreSQL `date` column.

`0007` creates `player_mappings`, `team_mappings`, and `event_mappings`, copies any
existing rows including timestamps, then drops `mappings`. An empty old table
needs no special handling. Existing rows must use the exact object types `player`,
`team`, or `event`, have existing internal targets, and have unique external
identities per entity type. Invalid rows abort the whole migration; fix them and
retry. The migration takes an exclusive lock on the old table, so deploy it with
the updated application while old mapping writers are stopped.

Each new table has:

- A primary key on `(source, external_id)` identifying one external identity.
- A non-null foreign key to its specific domain table.
- An index on `(internal_entity_id, source)` for listing provider identities.
- Creation and update timestamps. Repeated identical mapping inserts preserve
  both timestamps; future explicit remapping must maintain `updated_at`.

`source` identifies an ID namespace. If IDs are only unique within a sport or
league, use a namespace that includes that scope. External IDs are exact strings;
leading zeros are preserved. One internal entity may have several provider IDs,
including aliases from the same source. Deleting an entity with mappings is
blocked by its foreign key until the mappings are explicitly removed.

Python schemas use `external_id` consistently. `MappingRepository` provides typed
create, resolve, and list methods, plus `create_mapping` for the mapping union.
Repeating an identical insert succeeds. Linking an existing external identity to
a different entity raises `MappingConflictError` without changing its target.

The database connection uses autocommit outside explicit transactions. To create
an entity and its mappings atomically, wrap their writes in
`with db.transaction():`. Nested mapping writes participate through savepoints.
Use `execute_command` for statements without results and `execute_query` for
queries or writes with `RETURNING`. Mapping IDs are serialized to strings before
binding and parsed back into typed IDs on reads.

This migration is forward-only. The old schema cannot represent multiple
provider identities for one internal entity, so an automatic rollback would be
lossy. Use a reviewed corrective migration if a later change is needed; do not
use `yoyo rollback` for this migration.
