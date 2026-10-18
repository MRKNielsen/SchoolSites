"""
The check-module contract. One module per exercise, consumed by BOTH runners:
the formative one inside the student's notebook, and the record runner the
teacher runs over collected submissions.

Two shapes of check, because the course has two shapes of artefact:

  QueryCheck  - the student supplies SQL. We run it and inspect the rows.
  SchemaCheck - the student supplies a .db file. We inspect its structure.

Every check returns Result(passed, feedback, detail). Feedback is written for
the student and must say what to do next, not merely that something failed.
"""
from dataclasses import dataclass, field
from typing import Any
import hashlib, os, re, sqlite3


_HERE = os.path.dirname(os.path.abspath(__file__))

# The same checks run from two layouts: the deployed site, where this file is
# at unit-1/workbooks/checks/ and the data at unit-1/data/, and the authoring
# spike, where data sits one level up. Resolve once, here, so no notebook and
# no bank ever carries a hand-written relative path.
_CANDIDATES = (
    os.path.join(_HERE, "..", "..", "data"),   # deployed
    os.path.join(_HERE, ".."),                 # authoring spike
    os.path.join(_HERE, "..", "data"),
)


def data_dir() -> str:
    for cand in _CANDIDATES:
        if os.path.exists(os.path.join(cand, "climate.db")):
            return os.path.abspath(cand)
    return os.path.abspath(_CANDIDATES[0])


def data_path(name: str) -> str:
    """Absolute path to a file in the unit dataset, from wherever we are run."""
    return os.path.join(data_dir(), name)


def digest(value) -> str:
    """Canonical sha256 of an expected answer.

    Expected values are stored as digests, never in clear, because these
    workbooks are published on a public site. A student reading the bank
    sees a hash; the check still works entirely client-side.
    """
    return hashlib.sha256(repr(value).encode("utf-8")).hexdigest()[:16]


def quantise(x, step):
    """Round to a tolerance grid so near-enough answers hash identically."""
    return 0.0 if step == 0 else round(float(x) / step)


@dataclass
class Result:
    passed: bool
    feedback: str
    detail: Any = None

    def __bool__(self):
        return self.passed


@dataclass
class QueryCheck:
    """Runs the student's SQL against a fixture and inspects the result."""
    exercise: str
    fixture: str
    expected_len: int
    expected_digest: str
    ordered: bool = False
    must_contain: list = field(default_factory=list)
    must_not_contain: list = field(default_factory=list)
    hint: str = ""

    def run(self, student_sql: str) -> Result:
        # A stub cell holds a comment, not a query. Strip comments before
        # deciding whether anything was submitted, or the feedback below
        # ends up describing a query that was never written.
        bare = re.sub(r"/\*.*?\*/", " ", student_sql or "", flags=re.S)
        bare = re.sub(r"--[^\n]*", " ", bare).strip()
        if not bare:
            return Result(False, "Nothing to check yet - write your query in the cell above.")

        low = " ".join(bare.lower().split())
        for kw in self.must_contain:
            if kw.lower() not in low:
                return Result(False, f"This exercise is about {kw.upper()}, and your query does not use it. {self.hint}".strip())
        for kw in self.must_not_contain:
            if kw.lower() in low:
                return Result(False, f"Try it without {kw.upper()} on this one. {self.hint}".strip())

        con = sqlite3.connect(self.fixture)
        con.execute("PRAGMA foreign_keys = ON")
        try:
            rows = con.execute(student_sql).fetchall()
        except sqlite3.Error as e:
            return Result(False, f"SQLite could not run that: {e}", detail=str(e))
        finally:
            con.close()

        got = list(rows) if self.ordered else sorted(map(repr, rows))
        if digest(got) == self.expected_digest:
            return Result(True, "Correct.", detail=rows)
        if len(rows) != self.expected_len:
            return Result(False, f"Expected {self.expected_len} row(s), got {len(rows)}. {self.hint}".strip(), detail=rows)
        return Result(False, f"Right number of rows, wrong values. {self.hint}".strip(), detail=rows)


def query_check(exercise, fixture, solution, ordered=False, must_contain=(), must_not_contain=(), hint=""):
    """Builds a QueryCheck by running the reference solution and storing only
    its row count and a digest - never the rows themselves."""
    con = sqlite3.connect(fixture)
    rows = con.execute(solution).fetchall()
    con.close()
    canon = list(rows) if ordered else sorted(map(repr, rows))
    return QueryCheck(exercise, fixture, len(rows), digest(canon), ordered,
                      list(must_contain), list(must_not_contain), hint)


@dataclass
class SchemaCheck:
    """Inspects a database the student built. Structure IS the key knowledge."""
    exercise: str
    tables: list
    primary_keys: dict = field(default_factory=dict)
    foreign_keys: list = field(default_factory=list)
    naming: bool = True
    hint: str = ""

    def run(self, db_path: str) -> Result:
        # sqlite3.connect() happily CREATES a missing file, which would report
        # "tables missing" for what is really a typo in the filename.
        if not db_path or not str(db_path).strip():
            return Result(False, "Nothing to check yet - type the name of your database file.")
        if not os.path.isfile(db_path):
            return Result(False, f"No file called {os.path.basename(str(db_path))} next to this workbook. "
                                 "Save your database in the same folder as this notebook, then check the spelling.")
        con = sqlite3.connect(db_path)
        try:
            found = {r[0] for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
            missing = [t for t in self.tables if t not in found]
            if missing:
                return Result(False, f"These tables are missing: {', '.join(missing)}. {self.hint}".strip())

            for t, pk in self.primary_keys.items():
                cols = list(con.execute(f"PRAGMA table_info({t})"))
                pks = [c[1] for c in cols if c[5]]
                if pks != [pk]:
                    return Result(False, f"Table {t} should have {pk} as its primary key; found {pks or 'none'}.")

            for t, col, ref in self.foreign_keys:
                fks = [(r[3], r[2]) for r in con.execute(f"PRAGMA foreign_key_list({t})")]
                if (col, ref) not in fks:
                    return Result(False, f"Table {t} needs a foreign key on {col} referencing {ref}. Found: {fks or 'none'}.")

            if self.naming:
                bad = []
                for t in self.tables:
                    if t != t.lower():
                        bad.append(t)
                    for c in con.execute(f"PRAGMA table_info({t})"):
                        name = c[1]
                        if name != name.lower() or " " in name or "-" in name:
                            bad.append(f"{t}.{name}")
                if bad:
                    return Result(False, "Naming convention: use lower_snake_case throughout. Fix: " + ", ".join(bad[:5]))

            orphans = 0
            for t, col, ref in self.foreign_keys:
                pk = self.primary_keys.get(ref, ref + "_id")
                orphans += con.execute(
                    f"SELECT COUNT(*) FROM {t} WHERE {col} NOT IN (SELECT {pk} FROM {ref})").fetchone()[0]
            if orphans:
                return Result(False, f"{orphans} row(s) reference a record that does not exist. Turn on PRAGMA foreign_keys and clean the orphans before loading.")

            return Result(True, "Schema correct.", detail=sorted(found))
        finally:
            con.close()


@dataclass
class NumericCheck:
    """The student computes a number. Compared with a tolerance, because
    rounding and float arithmetic should not fail an otherwise correct answer."""
    exercise: str
    expected_digest: str
    step: float = 0.1
    unit: str = ""
    hint: str = ""

    def run(self, value) -> Result:
        if value is None or value == "":
            return Result(False, "Nothing to check yet - compute your answer first.")
        try:
            got = float(value)
        except (TypeError, ValueError):
            return Result(False, f"That is not a number: {value!r}. {self.hint}".strip())
        if digest(quantise(got, self.step)) == self.expected_digest:
            return Result(True, f"Correct - {got:g}{self.unit}.", detail=got)
        return Result(False, f"Not right yet. {self.hint}".strip(), detail=got)


def numeric_check(exercise, expected, step=0.1, unit="", hint=""):
    """Builds a NumericCheck storing only a digest of the quantised answer."""
    return NumericCheck(exercise, digest(quantise(expected, step)), step, unit, hint)
