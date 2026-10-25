import sqlite3
import shutil
import unittest
from pathlib import Path

from src.pipeline import load_clean_rows, publish


ROOT = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):
    def test_source_is_cleaned_and_joined(self):
        rows = load_clean_rows(ROOT / "dev" / "cademycode.db")
        self.assertEqual(len(rows), 5000)
        self.assertTrue(rows[0]["email"])
        self.assertIn("career_path_name", rows[0])

    def test_publish_creates_database_and_csv(self):
        rows = load_clean_rows(ROOT / "dev" / "cademycode.db")[:3]
        temp = ROOT / ".test-output"
        temp.mkdir(exist_ok=True)
        try:
            db, csv_path = temp / "out.db", temp / "out.csv"
            publish(rows, db, csv_path)
            con = sqlite3.connect(db)
            self.assertEqual(con.execute("SELECT count(*) FROM subscribers").fetchone()[0], 3)
            con.close()
            self.assertEqual(len(csv_path.read_text(encoding="utf-8").splitlines()), 4)
        finally:
            shutil.rmtree(temp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
