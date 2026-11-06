Repository and mapping integration tests require a disposable PostgreSQL database. They create
and remove isolated schemas and one uniquely named test table. The database role
must be able to create schemas and tables. Never point these tests at production.

```bash
SABERMIND_TEST_DATABASE_URL=postgresql://USER:PASSWORD@localhost:5433/TEST_DATABASE \
    uv run --locked pytest -m integration
```

Tests skip when `SABERMIND_TEST_DATABASE_URL` is unset. CI provisions PostgreSQL 17
and runs them with the rest of the suite. Coverage includes legacy-data migration,
atomic migration failure, foreign keys, identity conflicts, aliases, multiple
providers, typed ID round trips, persistent writes, and transaction rollback.
Repository tests also exercise player and team CRUD, odds and prediction round
trips, event deletion cascades, probability constraints, player sport backfills,
and atomic creation of players and their mappings.
