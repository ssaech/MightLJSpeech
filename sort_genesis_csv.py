#!/usr/bin/env python3

from __future__ import annotations

import re
from pathlib import Path


def find_dataset_root(start_dir: Path) -> Path:
    genesis_csv = start_dir / "genesis.csv"
    if genesis_csv.is_file():
        return start_dir

    candidates = [
        child for child in start_dir.iterdir() if child.is_dir() and (child / "genesis.csv").is_file()
    ]

    if len(candidates) == 1:
        return candidates[0]

    if not candidates:
        raise FileNotFoundError("Could not find genesis.csv in the current directory or its child directories.")

    candidate_names = ", ".join(sorted(child.name for child in candidates))
    raise RuntimeError(f"Found multiple directories containing genesis.csv: {candidate_names}")


def get_genesis_filenames(genesis_dir: Path) -> set[str]:
    if not genesis_dir.is_dir():
        raise FileNotFoundError(f"Could not find genesis directory: {genesis_dir}")

    return {path.stem for path in genesis_dir.glob("*.wav") if path.is_file()}


def finder_sort_key(value: str) -> list[int | str]:
    return [
        int(part) if part.isdigit() else part.casefold()
        for part in re.split(r"(\d+)", value)
    ]


def main() -> None:
    dataset_root = find_dataset_root(Path.cwd())
    genesis_csv = dataset_root / "genesis.csv"
    genesis_dir = dataset_root / "genesis"
    sorted_csv = dataset_root / "genesis_sorted.csv"
    genesis_filenames = get_genesis_filenames(genesis_dir)

    with genesis_csv.open("r", encoding="utf-8") as src:
        lines = [
            line
            for line in src
            if line.rstrip("\n").split("|", 1)[0] in genesis_filenames
        ]

    lines.sort(key=lambda line: finder_sort_key(line.split("|", 1)[0]))

    with sorted_csv.open("w", encoding="utf-8", newline="") as dst:
        dst.writelines(lines)

    print(f"Found {len(genesis_filenames)} wav files in {genesis_dir}")
    print(f"Kept {len(lines)} matching rows from {genesis_csv}")
    print(f"Wrote alphabetically sorted lines to {sorted_csv}")


if __name__ == "__main__":
    main()
