# Session 1 — Oracle SQL for AI Pipelines (~45 min)

**Objective:** stand up a local Oracle instance, create a small
support-ticket schema, and pull joined, real data into Python via
`python-oracledb` — the data source the rest of this stage's middleware
serves.

**Prerequisites:** Stage 6 complete. Docker installed. `pip install
python-oracledb` (pure-Python "thin mode" — no separate Oracle client
install needed).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0 — re-answer
Stage 6's last Quick test.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Stand up Oracle XE via Docker; connect from Python |
| 10–20 | SQL recap: `SELECT`/`WHERE`/`JOIN`; parameterized queries |
| 20–40 | Build `code/db.py` |
| 40–45 | Notes |

---

## Concepts  <!-- step 2 -->

- **Getting an Oracle instance without a license headache.** The
  `gvenzl/oracle-xe` Docker image gives you a real, free Oracle Database XE
  in one command:
  ```
  docker run -d --name oracle-xe -p 1521:1521 -e ORACLE_PASSWORD=devpass gvenzl/oracle-xe
  ```
  (Oracle Cloud's Always Free tier is the alternative if you'd rather not
  run it locally — same SQL either way.)
- **`python-oracledb` "thin mode".** Unlike the older `cx_Oracle`, this
  driver talks Oracle's network protocol directly in pure Python — no
  separate Oracle Instant Client install. `oracledb.connect(user=...,
  password=..., dsn="localhost:1521/XEPDB1")`.
- **Schema for this stage:** two tables mirroring Stage 1B/4B's
  support-ticket theme — `CUSTOMERS(id, name, email)` and
  `TICKETS(id, customer_id, subject, body, category, status,
  created_at)`, `customer_id` a foreign key into `CUSTOMERS`.
- **`JOIN`** combines rows from two tables on a matching column. An **inner
  join** (`JOIN`) returns only rows with a match in both tables; a **left
  join** (`LEFT JOIN`) keeps every row from the left table even without a
  match (nulls fill the right side) — the right choice when a ticket might
  not yet have, say, an assigned agent.
- **Parameterized queries — the security-critical habit.** Never format a
  query string with `f"...{user_input}..."`. Always pass values as bind
  parameters: `cursor.execute("SELECT * FROM tickets WHERE id = :id", id=42)`.
  String formatting into SQL is exactly how SQL injection happens — this
  matters even more once Stage 6B session 3-4 exposes queries behind a
  public API.
- **Fetching results into Python.** A cursor yields tuples by default;
  `cursor.description` gives you column names if you want dicts instead of
  positional tuples — you'll want dicts once this data crosses into a JSON
  API response (session 3).

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- `python-oracledb` docs — *Quick Start*:
  <https://python-oracledb.readthedocs.io/en/latest/user_guide/introduction.html>
  (the thin-mode connection example specifically).

**Video (pick one, ~15 min):**
- Search *"SQL joins explained inner left join"* — a visual refresher if
  joins feel rusty.

---

## Track_B link (step 3)

**None.** This stage is pure applied engineering — Oracle SQL and Python
driver mechanics. Note "no Track_B link" and continue.

---

## Worked example — schema, seed data, a joined query  <!-- step 4 -->

```python
import oracledb

connection = oracledb.connect(
    user="system", password="devpass", dsn="localhost:1521/XEPDB1"
)
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE customers (
        id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        name VARCHAR2(100), email VARCHAR2(100)
    )
""")
cursor.execute("""
    CREATE TABLE tickets (
        id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        customer_id NUMBER REFERENCES customers(id),
        subject VARCHAR2(200), body CLOB,
        category VARCHAR2(20), status VARCHAR2(20) DEFAULT 'open',
        created_at TIMESTAMP DEFAULT SYSTIMESTAMP
    )
""")
connection.commit()

cursor.execute(
    "INSERT INTO customers (name, email) VALUES (:1, :2)",
    ["Jane Doe", "jane@example.com"],
)
cursor.execute(
    """INSERT INTO tickets (customer_id, subject, body, category)
       VALUES (:1, :2, :3, :4)""",
    [1, "Double charge", "I was charged twice this month, $49.99 both times", "billing"],
)
connection.commit()

cursor.execute("""
    SELECT t.id, t.subject, t.category, c.name, c.email
    FROM tickets t
    JOIN customers c ON t.customer_id = c.id
    WHERE t.status = :status
""", status="open")

columns = [d[0].lower() for d in cursor.description]
rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
print(rows)
```

**Expected output:**

```
[{'id': 1, 'subject': 'Double charge', 'category': 'billing', 'name': 'Jane Doe', 'email': 'jane@example.com'}]
```

Read it: the join pulled customer identity alongside ticket data in one
round trip — exactly the shape a real API endpoint needs, and exactly the
kind of query you'd otherwise hand-write twice (once for tickets, once for
customers) and join in Python, wastefully.

---

## Build: `code/db.py`  <!-- step 5 -->

Build the schema + seed data above, then write a small module with:
`get_connection()`, `list_open_tickets_with_customer()` (the join above,
returning a list of dicts), and `get_ticket_by_id(ticket_id)` (a
parameterized single-row lookup). Seed at least 8-10 tickets across 3-4
customers, with a mix of categories.

Experiments:
1. **Try a left join.** Insert a ticket with no matching customer row
   deliberately impossible under the current foreign key — instead,
   demonstrate the *other* direction: a customer with no tickets, and
   confirm an inner join excludes them while a `LEFT JOIN customers c ON
   ... ` from the customers side would not.
2. **Break parameterization on purpose, safely.** Build the same query with
   an f-string instead of a bind parameter, using a "malicious-looking"
   ticket ID like `"1 OR 1=1"` as input. Watch it either error or return
   every row — then fix it with a bind parameter and confirm it's inert.
3. **Fetch as tuples vs. dicts.** Time both approaches over the full ticket
   list — dict conversion has a small cost; note it, but note it's usually
   worth it for API code.

---

## Quick test (step 7 — answer from memory, then check)

1. What's the difference between an inner join and a left join?
2. Why must query values be passed as bind parameters instead of formatted
   into the SQL string?
3. What does `cursor.description` give you, and why is it useful here?
4. What does "thin mode" mean for `python-oracledb`, and why does it matter
   for setup?
5. Name the two tables in this session's schema and the column that links
   them.

<details><summary>Answers</summary>

1. An inner join returns only rows with a match in both tables; a left join
   keeps every row from the left table even without a match, filling the
   right side with nulls.
2. To prevent SQL injection — a formatted string lets malicious input change
   the query's structure; a bind parameter is always treated as a value,
   never as SQL.
3. Column names for the result set, letting you convert tuple rows into
   dicts (`{column_name: value}`) instead of relying on position.
4. It means the driver speaks Oracle's network protocol directly in pure
   Python, with no separate Oracle Instant Client library to install —
   simpler setup.
5. `customers` and `tickets`, linked by `tickets.customer_id` referencing
   `customers.id`.

</details>

---

## Done when  <!-- step 8 -->

- [ ] A local Oracle instance is running and reachable from Python.
- [ ] `db.py` creates the schema, seeds real sample data, and exposes a
      working joined query and a parameterized single-row lookup.
- [ ] You've demonstrated an unparameterized query being exploitable and
      the parameterized version being safe, on the same malicious input.
- [ ] You can explain, from memory, why bind parameters matter.

## Pitfalls

- **String-formatting any part of a query with request-controlled data.**
  Always a bind parameter, no exceptions — this habit has to be automatic
  before session 3 puts a query behind a public endpoint.
- **Forgetting `connection.commit()`.** DML (`INSERT`/`UPDATE`/`DELETE`)
  without a commit is invisible to other connections and lost on
  disconnect.
- **Fetching a `CLOB` column and getting a LOB object, not a string.** Read
  it explicitly (`.read()`) or cast in SQL if you need the text immediately.

## Carries to next session

`db.py`'s connection and query functions are what Session 2 profiles and
optimizes — the same schema, now under a performance lens.
