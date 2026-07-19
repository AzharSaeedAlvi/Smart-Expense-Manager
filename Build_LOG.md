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