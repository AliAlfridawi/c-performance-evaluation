import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import collect_benchmarks as cb
import plot_benchmarks as pb


def _bench_case() -> cb.BenchCase:
    input_spec = cb.InputSpec(
        input_id="random_n10",
        distribution="random",
        n=10,
        path=REPO_ROOT / "data" / "benchmark_inputs" / "random_n10.txt",
    )
    return cb.BenchCase("quicksort", "random", 10, input_spec, "sort")


def _rows_for_case(
    language: str,
    case: cb.BenchCase,
    *,
    trials: int,
    warmup: int,
    comparisons: list[int] | None = None,
) -> list[dict[str, str]]:
    total = trials + warmup
    comparison_values = comparisons or [34] * total
    rows: list[dict[str, str]] = []
    for trial_no in range(1, total + 1):
        rows.append(
            {
                "language": language,
                "algorithm": case.algorithm,
                "distribution": case.distribution,
                "input_id": case.input_spec.input_id,
                "N": str(case.n),
                "search_case": case.search_case,
                "trial": str(trial_no),
                "warmup": "1" if trial_no <= warmup else "0",
                "comparisons": str(comparison_values[trial_no - 1]),
                "elapsed_ns": "500000",
                "batch_loops": "10",
            }
        )
    return rows


class CollectorValidationTests(unittest.TestCase):
    def test_validate_case_rows_rejects_inconsistent_comparisons(self) -> None:
        case = _bench_case()
        rows = _rows_for_case("python", case, trials=1, warmup=1, comparisons=[34, 35])

        errors = cb.validate_case_rows(rows, case, "python", trials=1, warmup=1)

        self.assertTrue(any("inconsistent comparison counts" in error for error in errors))

    def test_validate_collection_rows_rejects_missing_groups(self) -> None:
        case = _bench_case()
        rows = _rows_for_case("python", case, trials=1, warmup=1)
        rows.extend(_rows_for_case("c", case, trials=1, warmup=1))

        errors = cb.validate_collection_rows(rows, [case], ["python", "c", "java"], trials=1, warmup=1)

        self.assertTrue(any("missing benchmark groups" in error for error in errors))

    @unittest.skipUnless(
        cb.find_c_benchmark() and cb.find_java_executable() and cb.find_java_classes_dir(),
        "requires built C and Java benchmark targets",
    )
    def test_collect_and_plot_smoke_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            raw_csv = tmp / "smoke_runs.csv"
            summary_csv = tmp / "summary.csv"
            graph_dir = tmp / "graphs"

            cb.collect(raw_csv, [10], trials=1, warmup=1, languages=["python", "c", "java"], strict=True)
            rows = cb.parse_rows(raw_csv.read_text(encoding="utf-8"))
            cases = cb.build_cases(cb.load_inputs(cb.ensure_input_manifest(), [10]), [10])

            self.assertEqual(66, len(rows))
            self.assertEqual([], cb.validate_collection_rows(rows, cases, ["python", "c", "java"], 1, 1))

            pb.run_all(raw_csv, summary_csv, graph_dir, strict=True)

            self.assertTrue(summary_csv.is_file())
            self.assertTrue((graph_dir / "quicksort_median_time.png").is_file())
            self.assertTrue((graph_dir / "linear_search_median_time.png").is_file())
            self.assertTrue((graph_dir / "binary_search_median_time.png").is_file())
            self.assertTrue((graph_dir / "comparison_counts.png").is_file())


class PlotValidationTests(unittest.TestCase):
    def test_validate_trials_rejects_partial_matrix(self) -> None:
        case = _bench_case()
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "partial.csv"
            cb.write_rows(csv_path, _rows_for_case("python", case, trials=1, warmup=1))

            trials = pb.load_trials(csv_path)

            with self.assertRaises(pb.SummaryValidationError):
                pb.validate_trials(trials, strict=True)


if __name__ == "__main__":
    unittest.main()
