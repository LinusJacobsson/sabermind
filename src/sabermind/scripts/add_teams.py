import argparse
import json
from pathlib import Path

from sabermind.database.database import Database
from sabermind.database.teams import TeamRepository
from sabermind.schemas.schemas import Sport, Team
from sabermind.schemas.xid import TeamId


def main() -> None:
    parser = argparse.ArgumentParser(description="Import KBO teams into the database.")
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate teams without database writes."
    )
    args = parser.parse_args()
    data_path = Path(__file__).resolve().parent / "raw_entities" / "kbo_teams.json"
    with data_path.open(encoding="utf-8") as f:
        teams_data = json.load(f)

    teams = [
        Team(
            team_id=TeamId.new(),
            name=team["name"],
            league=team["league"],
            sport=Sport(team["sport"].lower()),
        )
        for team in teams_data["teams"]
    ]
    if args.dry_run:
        print(f"Validated {len(teams)} teams; no database writes.")
        return

    db = Database()
    db.connect()
    try:
        team_repository = TeamRepository(db)
        with db.transaction():
            for team in teams:
                team_repository.create_team(team)
        for team in teams:
            print(f"Added team: {team.name} (ID: {team.team_id})")
    finally:
        db.disconnect()


if __name__ == "__main__":
    main()
