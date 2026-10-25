"""Clean and publish the Cademycode subscriber dataset."""
from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import sqlite3
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(filename=LOG_DIR / "error.log", level=logging.ERROR,
                    format="%(asctime)s %(levelname)s %(message)s")

OUTPUT_COLUMNS = [
    "uuid", "name", "dob", "sex", "mailing_address", "email", "job_category",
    "avg_salary", "career_path_name", "hours_to_complete", "num_course_taken",
    "time_spent_hrs",
]


def _number(value):
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def load_clean_rows(source: str | Path):
    con = sqlite3.connect(source)
    con.row_factory = sqlite3.Row
    try:
        students = con.execute("SELECT * FROM cademycode_students").fetchall()
        courses = {str(r["career_path_id"]): r for r in con.execute("SELECT * FROM cademycode_courses")}
        jobs = {str(r["job_id"]): r for r in con.execute("SELECT * FROM cademycode_student_jobs")}
    finally:
        con.close()

    rows = []
    for student in students:
        try:
            contact = json.loads(student["contact_info"] or "{}")
        except (TypeError, json.JSONDecodeError):
            logging.error("Invalid contact JSON for uuid=%s", student["uuid"])
            contact = {}
        course = courses.get(str(student["current_career_path_id"])) or {}
        job = jobs.get(str(student["job_id"])) or {}
        rows.append({
            "uuid": student["uuid"], "name": student["name"], "dob": student["dob"],
            "sex": student["sex"], "mailing_address": contact.get("mailing_address"),
            "email": contact.get("email"), "job_category": job.get("job_category"),
            "avg_salary": job.get("avg_salary"), "career_path_name": course.get("career_path_name"),
            "hours_to_complete": course.get("hours_to_complete"),
            "num_course_taken": _number(student["num_course_taken"]),
            "time_spent_hrs": _number(student["time_spent_hrs"]),
        })
    return rows


def publish(rows, output_db: str | Path, output_csv: str | Path):
    output_db, output_csv = Path(output_db), Path(output_csv)
    output_db.parent.mkdir(parents=True, exist_ok=True)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(output_db)
    try:
        con.execute("DROP TABLE IF EXISTS subscribers")
        con.execute("CREATE TABLE subscribers (" + ", ".join(f'"{c}" TEXT' for c in OUTPUT_COLUMNS) + ")")
        con.executemany("INSERT INTO subscribers VALUES (" + ",".join("?" for _ in OUTPUT_COLUMNS) + ")",
                        [[row[c] for c in OUTPUT_COLUMNS] for row in rows])
        con.commit()
    finally:
        con.close()
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader(); writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="dev/cademycode.db")
    parser.add_argument("--output", default="production/cademycode_clean.db")
    parser.add_argument("--csv", default="production/cademycode_clean.csv")
    args = parser.parse_args()
    try:
        rows = load_clean_rows(args.source)
        if not rows:
            raise ValueError("source database contains no students")
        publish(rows, args.output, args.csv)
        (LOG_DIR / "changelog.log").open("a", encoding="utf-8").write(
            f"published {len(rows)} cleaned subscriber rows\n")
        print(f"Published {len(rows)} rows")
    except Exception as exc:
        logging.exception("Pipeline failed: %s", exc)
        raise


if __name__ == "__main__":
    main()
