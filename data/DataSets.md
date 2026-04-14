# Benchmark Inputs

This repository no longer relies on language-specific random generation during collection. Shared deterministic input files are generated once and stored in `data/benchmark_inputs/`.

## Files

- `data/benchmark_inputs/manifest.csv` lists every input file
- `data/benchmark_inputs/<distribution>_n<N>.txt` stores whitespace-separated integers

Example entries:

- `ascending_n100.txt`
- `descending_n100.txt`
- `random_n100.txt`

## Design

- Values are unique integers so search hit cases are unambiguous.
- `ascending` uses `0..N-1`.
- `descending` uses `N-1..0`.
- `random` uses a deterministic shuffle of `0..N-1`.

## Regeneration

Run:

```powershell
python data/DataSetGenerator.py
```

That command rewrites the input files and the manifest from the current deterministic generator.
