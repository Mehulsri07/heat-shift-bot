"""Load hand-verified cooling points into DynamoDB.

Usage: COOLING_TABLE=<CoolingTable from the stack outputs> python scripts/seed_cooling_points.py
Reads data/cooling_points_jaipur.json: a JSON list of objects with exactly the keys in REQUIRED.
"""
import json
import os
import sys
from decimal import Decimal
from pathlib import Path

import boto3

DATA_FILE = Path(__file__).parent.parent / "data" / "cooling_points_jaipur.json"
REQUIRED = {"city", "point_id", "name", "lat", "lon", "type", "verified_by"}
TYPES = {"water", "shade", "clinic"}


def load_points(path: Path) -> list[dict]:
    # DynamoDB rejects Python floats, so parse lat/lon as Decimal.
    points = json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal)
    for p in points:
        if set(p) != REQUIRED:
            sys.exit(f"{p.get('point_id', '?')}: keys must be exactly {sorted(REQUIRED)}")
        if p["type"] not in TYPES:
            sys.exit(f"{p['point_id']}: type must be one of {sorted(TYPES)}")
        if not p["verified_by"]:
            sys.exit(f"{p['point_id']}: verified_by is empty; only hand-verified points go in")
    return points


def main() -> None:
    points = load_points(DATA_FILE)
    table = boto3.resource("dynamodb").Table(os.environ["COOLING_TABLE"])
    with table.batch_writer() as batch:
        for p in points:
            batch.put_item(Item=p)
    print(f"Seeded {len(points)} cooling points")


if __name__ == "__main__":
    main()
