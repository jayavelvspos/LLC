# Session 2 — Performance-Aware Querying (~45 min)

**Objective:** measure, not guess, the effect of an index on a real query;
implement server-side pagination instead of fetching everything; and apply
concrete practices for handling sensitive data safely in a query pipeline.

**Prerequisites:** Session 1 complete (`db.py`, seeded schema).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0 — re-answer
Session 1's Quick test.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–15 | Indexes; reading an execution plan |
| 15–20 | Pagination; the N+1 query problem |
| 20–35 | Build `code/query_perf.py` |
| 35–45 | Secure handling of sensitive data; notes |

---

## Concepts  <!-- step 2 -->

- **Index.** A separate, ordered structure (typically a B-tree) that lets
  the database find matching rows without scanning the whole table. Without
  one, `WHERE category = 'billing'` on a large `tickets` table means
  reading every row (a **full table scan**); with an index on `category`,
  it means a fast lookup.
- **Execution plan.** `EXPLAIN PLAN FOR <query>; SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);`
  shows *how* Oracle intends to run a query — full scan vs. index access,
  estimated cost, join order. Read the plan before assuming an index
  helped; sometimes the optimizer decides a full scan is actually cheaper
  (e.g. on a small table, or when most rows match anyway).
- **When an index doesn't help (or hurts).** Every index speeds up reads
  matching it but slows down writes (it must be updated on every
  insert/update/delete) and costs storage. Indexing every column
  "just in case" is a real anti-pattern, not a free win.
- **Pagination.** Never fetch an entire large table into memory to show a
  page of results. Oracle 12c+:
  `SELECT ... ORDER BY id OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY`.
  Always pair `OFFSET`/`FETCH` with an `ORDER BY` — without a defined order,
  which rows land on which page isn't guaranteed to be stable across calls.
- **The N+1 query problem.** Fetching a list of tickets, then running one
  more query *per ticket* to get its customer, is N+1 queries where one
  join (Session 1) would do. This is the single most common accidental
  performance bug in code that maps ORM-style objects onto relational data.
- **Secure handling of sensitive data**, three concrete practices beyond
  Session 1's parameterization:
  - **Select only what you need** — never `SELECT *` in code that serves an
    API; a schema change silently changes your response shape, and you may
    expose a column (a customer's raw email, an internal note) you didn't
    mean to.
  - **Least-privilege DB users** — the middleware's DB user should have only
    the grants it needs (e.g. no `DROP TABLE`), so a bug or an injected
    query can't do more damage than the identity it runs as allows.
  - **Never log full sensitive values.** A query-timing log line that
    includes the raw bind parameters can leak PII into logs that get
    shipped, retained, and read by more people than the database itself is.
    Log a hash, a truncated value, or just the query shape.

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- Oracle docs — *Using EXPLAIN PLAN*:
  <https://docs.oracle.com/en/database/oracle/oracle-database/19/tgsql/generating-and-displaying-execution-plans.html>
  (skim for `DBMS_XPLAN.DISPLAY` usage).

**Video (pick one, ~15 min):**
- Search *"SQL index explain plan tutorial"* — any relational database's
  explanation transfers directly (the concepts are universal).

---

## Track_B link (step 3)

**None.** Query performance is a database-systems topic, not covered in
`Track_B/Math_stat`. If a curiosity about index big-O complexity comes up,
that's outside this workspace's current scope — note it and move on.

---

## Worked example — index effect, measured  <!-- step 4 -->

```python
from db import get_connection

conn = get_connection()
cur = conn.cursor()

def show_plan(query, **binds):
    cur.execute(f"EXPLAIN PLAN FOR {query}", **binds)
    cur.execute("SELECT plan_table_output FROM TABLE(DBMS_XPLAN.DISPLAY())")
    for row in cur.fetchall():
        print(row[0])

query = "SELECT * FROM tickets WHERE category = :cat"
print("--- before index ---")
show_plan(query, cat="billing")

cur.execute("CREATE INDEX idx_tickets_category ON tickets(category)")
conn.commit()

print("--- after index ---")
show_plan(query, cat="billing")
```

**Expected output** (shape matters more than exact numbers on a small seeded
table):

```
--- before index ---
...TABLE ACCESS FULL...tickets...Cost=3...

--- after index ---
...INDEX RANGE SCAN...idx_tickets_category...Cost=1...
```

Read it: on this session's tiny seeded table the *actual* speed difference
is imperceptible — the point is learning to read the plan, not to see a
dramatic number. On a real production-sized `tickets` table, `TABLE ACCESS
FULL` is the line that should make you look for a missing index.

---

## Build: `code/query_perf.py`  <!-- step 5 -->

Build the plan comparison above, then add a paginated ticket-listing
function: `list_tickets_page(offset: int, limit: int)` using
`OFFSET ... FETCH NEXT ... ROWS ONLY` with an explicit `ORDER BY id`.

Experiments:
1. **Reproduce N+1 on purpose.** Write a version that fetches all tickets,
   then loops and runs a separate `SELECT * FROM customers WHERE id = :id`
   per ticket. Count total queries executed for 10 tickets, then compare to
   Session 1's single-join version.
2. **Break pagination without `ORDER BY`.** Run the same `OFFSET`/`FETCH`
   query without an `ORDER BY` a few times and see the row order isn't
   guaranteed to stay stable — confirms why it's mandatory, not stylistic.
3. **Audit a query for sensitive-data exposure.** Take Session 1's joined
   query and rewrite it as `SELECT *` from a join including a hypothetical
   sensitive column (add a `notes` column to `tickets` with an internal-only
   comment). Confirm the explicit-column version doesn't leak it, and the
   `SELECT *` version does.

---

## Quick test (step 7 — answer from memory, then check)

1. What does an index actually speed up, and what does it cost in return?
2. Why should you check the execution plan instead of assuming an index
   helped?
3. What problem does `OFFSET`/`FETCH` solve, and what must always accompany
   it?
4. What is the N+1 query problem, concretely?
5. Name two ways sensitive data can leak out of a query pipeline besides SQL
   injection.

<details><summary>Answers</summary>

1. Speeds up reads that filter/sort on the indexed column(s); costs extra
   storage and slows down writes to that table (the index must update too).
2. The query optimizer might decide a full scan is actually cheaper (e.g. a
   small table, or a filter that matches most rows) — an index existing
   doesn't guarantee it's used.
3. Fetching a page of results instead of the whole table; it must be paired
   with `ORDER BY`, or row order (and therefore which rows land on which
   page) isn't guaranteed.
4. Running one query for a list, then one *additional* query per item in
   that list to fetch related data — N+1 queries where a single join would
   do.
5. Any two of: `SELECT *` exposing a column you didn't mean to return,
   logging raw sensitive bind-parameter values, an over-privileged DB user
   able to read more than the application needs.

</details>

---

## Done when  <!-- step 8 -->

- [ ] You've compared an execution plan before and after adding an index on
      the same query.
- [ ] `query_perf.py` implements stable, `ORDER BY`-backed pagination.
- [ ] You've reproduced the N+1 problem and counted the query difference
      against a single join.
- [ ] You can name two concrete sensitive-data leak paths beyond SQL
      injection.

## Pitfalls

- **Adding an index and declaring victory without checking the plan.** Read
  it — confirm the optimizer is actually using the new index for your
  actual query shape.
- **Paginating without `ORDER BY`.** Silent, intermittent bugs (duplicate or
  missing rows across pages) that are easy to miss in testing and painful
  in production.
- **`SELECT *` in anything that becomes an API response.** It couples your
  response shape to your schema and can leak columns you didn't intend to
  expose.

## Carries to next session

`db.py` and `query_perf.py`'s query functions are the data layer Session 3's
FastAPI service calls — this is where Oracle data starts flowing through an
actual HTTP endpoint.
