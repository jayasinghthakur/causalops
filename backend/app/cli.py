"""Explicit local graph administration; never exposed to the browser."""

import argparse
import json
import sys

from pydantic import ValidationError

from app.config import Settings
from app.fixtures import load_fixture
from app.graph.repository import EntityNotFound, GraphRepository, GraphUnavailable


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("seed", help="Idempotently load the synthetic fixture")
    commands.add_parser("reset", help="Replace only the configured local/test graph")
    commands.add_parser("health", help="Check a real FalkorDB query")
    mutation = commands.add_parser("set-critical", help="Change a synthetic CALLS edge")
    mutation.add_argument("source")
    mutation.add_argument("target")
    mutation.add_argument("critical", choices=["true", "false"])
    args = parser.parse_args()
    repository = None
    try:
        repository = GraphRepository(Settings())
        if args.command == "seed":
            output = repository.seed(load_fixture())
        elif args.command == "reset":
            output = repository.reset(load_fixture())
        elif args.command == "health":
            if not repository.healthy():
                raise GraphUnavailable()
            output = {"status": "ok"}
        else:
            repository.set_critical(args.source, args.target, args.critical == "true")
            output = {"status": "updated", "synthetic": True}
        print(json.dumps(output, indent=2))
        return 0
    except (GraphUnavailable, EntityNotFound, ValidationError) as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        return 1
    finally:
        if repository:
            repository.close()


if __name__ == "__main__":
    raise SystemExit(main())
