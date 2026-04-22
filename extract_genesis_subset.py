#!/usr/bin/env python3

from __future__ import annotations

import shutil
from pathlib import Path


PREFIX = "Genesis_"


def find_dataset_root(start_dir: Path) -> Path:
    metadata_path = start_dir / "metadata.csv"
    wavs_dir = start_dir / "wavs"
    if metadata_path.is_file() and wavs_dir.is_dir():
        return start_dir

    candidates = [
        child
        for child in start_dir.iterdir()
        if child.is_dir()
        and (child / "metadata.csv").is_file()
        and (child / "wavs").is_dir()
    ]

    if len(candidates) == 1:
        return candidates[0]

    if not candidates:
        raise FileNotFoundError(
            "Could not find a dataset directory with both metadata.csv and wavs/."
        )

    candidate_names = ", ".join(sorted(child.name for child in candidates))
    raise RuntimeError(
        f"Found multiple dataset directories with metadata.csv and wavs/: "
        f"{candidate_names}"
    )


def write_genesis_csv(metadata_path: Path, output_path: Path) -> int:
    match_count = 0

    with metadata_path.open("r", encoding="utf-8") as src, output_path.open(
        "w", encoding="utf-8", newline=""
    ) as dst:
        for line in src:
            if line.startswith(PREFIX):
                dst.write(line)
                match_count += 1

    return match_count


def copy_genesis_wavs(wavs_dir: Path, output_dir: Path) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)

    copied_count = 0
    for wav_path in sorted(wavs_dir.glob(f"{PREFIX}*.wav")):
        if wav_path.parent == output_dir:
            continue

        shutil.copy2(wav_path, output_dir / wav_path.name)
        copied_count += 1

    return copied_count


def main() -> None:
    start_dir = Path.cwd()
    dataset_root = find_dataset_root(start_dir)

    metadata_path = dataset_root / "metadata.csv"
    genesis_csv_path = dataset_root / "genesis.csv"
    wavs_dir = dataset_root / "wavs"
    genesis_wavs_dir = dataset_root / "genesis"

    matching_rows = write_genesis_csv(metadata_path, genesis_csv_path)
    copied_wavs = copy_genesis_wavs(wavs_dir, genesis_wavs_dir)

    print(f"Dataset directory: {dataset_root}")
    print(f"Wrote {matching_rows} Genesis rows to {genesis_csv_path}")
    print(f"Copied {copied_wavs} Genesis wav files to {genesis_wavs_dir}")


if __name__ == "__main__":
    main()
