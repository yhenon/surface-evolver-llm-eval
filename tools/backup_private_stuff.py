from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path


PRIVATE_DIRS = ("runs", "tasks_private", "ground_truth_fe")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def backup_name() -> str:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"surface-evolver-private-backup-{stamp}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy ignored private project directories into a timestamped backup directory."
    )
    parser.add_argument(
        "target_dir",
        type=Path,
        help="Directory where the timestamped backup directory should be created.",
    )
    parser.add_argument(
        "--name",
        default=backup_name(),
        help="Backup directory name to create inside target_dir.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be copied without changing files.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if any expected private directory is missing.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = repo_root()
    target_dir = args.target_dir.expanduser().resolve()
    backup_dir = target_dir / args.name

    sources = [root / name for name in PRIVATE_DIRS]
    existing_sources = [source for source in sources if source.exists()]
    missing_sources = [source for source in sources if not source.exists()]

    if args.strict and missing_sources:
        missing = ", ".join(str(source.relative_to(root)) for source in missing_sources)
        raise SystemExit(f"Missing expected private directories: {missing}")

    if not existing_sources:
        raise SystemExit("No private directories found to back up.")

    for source in existing_sources:
        if is_relative_to(target_dir, source.resolve()):
            raise SystemExit(f"Refusing to back up into a source directory: {target_dir}")

    if backup_dir.exists():
        raise SystemExit(f"Backup directory already exists: {backup_dir}")

    for source in existing_sources:
        destination = backup_dir / source.name
        print(f"{source.relative_to(root)} -> {destination}")

    if missing_sources:
        missing = ", ".join(str(source.relative_to(root)) for source in missing_sources)
        print(f"Skipping missing directories: {missing}")

    if args.dry_run:
        print("Dry run only; no files copied.")
        return

    backup_dir.mkdir(parents=True)
    for source in existing_sources:
        shutil.copytree(source, backup_dir / source.name)

    print(f"Backed up {len(existing_sources)} directories in {backup_dir}")


if __name__ == "__main__":
    main()
