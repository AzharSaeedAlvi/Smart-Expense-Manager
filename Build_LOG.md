# Build Log 

## 2026-07-16

-Set up project foler, git repo, and Python virtual enviornment
-Installed FastAPU + Uvicorn, built a hello-world app with a single GET / route 
-Confirmed it runs locally and explored the auto-generated /docs (Swagger UI)
-Set up a .env file for secrets and confirmed it's properly gitignored


#2026-07-18

-Built users + expenses tables via SQLAlchemy models -> Alembic migration -> read/write.
-Best practices baked in: Decimal (not float) for money, created_at/updated_at. a metadata naming convention for stable constrain names, DB URL from an env var/ 
-Snags & Lessons
 -Installed packages in a throwaway folder first - venvs are per-project, so they were invisible to the real project initially. Reinstalled in the right venv.
 -My '-m' message said "expense" (singular), so the migration filename didn't match waht I searced for - the messsage is just a label, table names come from __tablename__. 
 -Gmail auto-lined 'uders.id' into a URL when I pasted the file - a display artifact, not real code. Always check code in the editor, not email. 
-Done when met: tables created via migration, row written and read back

-Notes
    -Migration Files must always be commited
    -git doesn't track empty folders
    =Never store money as float. Use Numeric/Decimal, and construct values from strings (Decimal("12/50"))
    -We keep models.py and database.py separate


    ## 2026-07-19

### Phase 2 — CRUD for expenses (DONE)

- Full CRUD for /expenses via /docs: POST (201), GET list, GET one, PATCH, DELETE (204). No auth yet.
- Separate Pydantic models: ExpenseCreate (input, no id/timestamps, validated), ExpenseRead (output, from_attributes=True), ExpenseUpdate (all fields optional for PATCH).
- get_db() session dependency (yield/try-finally) injected via Depends — one auto-closing session per request.
- Reads: db.scalars(select(...)).all() for list, db.get() for one; raise HTTPException(404) when missing.
- PATCH uses model_dump(exclude_unset=True) + setattr() so only sent fields change (chose PATCH over PUT).
- DELETE: db.delete()+commit() (permanent), returns 204.

- Key fixes / lessons
    - FK needs an owner but auth is deferred -> seeded a dev user, hardcoded DEV_USER_ID (Phase 3 swaps to current_user.id).
    - Every required (NOT NULL) DB column must exist in the input schema (hit this on users.name and expenses.spent_on).
    - Typos that cost time: payload.model.dump() vs payload.model_dump(); detail vs details in HTTPException; missing "/" in a route.
    - Status codes are semantic: 422 = malformed request (e.g. string id, function never runs), 404 = valid request but resource missing.
    - Swagger pre-fills placeholder body values -> blind Execute actually sends them (the "huge float" amount); edit the body down to test PATCH.
    - Slow /docs = browser fetching Swagger UI from a CDN on a proxied network; the local API is fast.

- Done when met: every CRUD op works through /docs; no auth added.

- Notes
    - Keep input vs output schemas separate; money stays Decimal (harden later with Field(max_digits, decimal_places)).
    - No new packages -> requirements.txt unchanged.
    - TODO Phase 3: retire DEV_USER_ID; add registration + hashed passwords + JWT login; protect endpoints; isolate users.
