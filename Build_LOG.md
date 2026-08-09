# Build Log 

## 2026-07-16


-Set up project foler, git repo, and Python virtual enviornment
-Installed FastAPU + Uvicorn, built a hello-world app with a single GET / route 
-Confirmed it runs locally and explored the auto-generated /docs (Swagger UI)
-Set up a .env file for secrets and confirmed it's properly gitignored


## 2026-07-18

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


## 2026-07-25

### Phase 3 — Authentication (DONE)

- Registration with bcrypt-hashed passwords, JWT login, token-gated expense endpoints, every query scoped to the logged-in owner, DEV_USER_ID retired, and two-user isolation proven.
- Framed the phase as an adversarial (GAN) gap analysis: for each way an attacker could break a naive build, closed the matching gap. The boss gap was #5 — user isolation (IDOR).

- What I built, step by step
    - Installed the auth toolkit: passlib[bcrypt] (hashing) + PyJWT (tokens) + python-multipart (form login) + python-dotenv; re-froze requirements after each install.
    - Added a hashed_password column (String, NOT NULL) to the User model; generated + reviewed the Alembic migration.
    - Rebuilt the local dev DB from scratch (alembic downgrade base -> upgrade head) so NOT NULL applied to empty tables (throwaway data, deliberately wiped).
    - UserCreate (input: name, email, plaintext password) and UserRead (output: id, name, email, created_at — no password/hash, ever).
    - security.py: hash_password / verify_password (CryptContext), create_access_token / decode_access_token (HS256, sub + 30-min exp), config loaded from .env.
    - POST /auth/register — hashes password, stores user, returns 201 UserRead, rejects duplicate email with 409.
    - Generated a strong SECRET_KEY (secrets.token_hex(32)) into .env; set ACCESS_TOKEN_EXPIRE_MINUTES=30.
    - POST /auth/login — OAuth2PasswordRequestForm, verifies password vs hash, returns a JWT (Token schema); generic 401 on failure.
    - get_current_user gatekeeper — pulls the bearer token, verifies signature + expiry, looks up the user by sub, hands the live User to any endpoint via Depends. Proved with GET /auth/me.
    - Protected all five expense endpoints: create stamps current_user.id; get-one / list / PATCH / DELETE filter by id AND owner.
    - Deleted the DEV_USER_ID line (grep-confirmed unused first).
    - Two-user isolation proof: Bob got [] on list and 404 on GET/PATCH/DELETE of User A's row id; A's data untouched.

- Snags & Lessons
    - passlib vs modern bcrypt clash: first a KeyError, then "password cannot be longer than 72 bytes" on a 14-char password (passlib's internal self-test hit modern bcrypt's hard limit). Fix: pin bcrypt==4.0.1. (passlib is unmaintained; pwdlib is the modern alternative — noted for later.)
    - KeyError: unknown CryptContext keyword — was a misspelling of "deprecated". Read the traceback bottom-up; library file paths in the stack = not my code.
    - .env does nothing on its own: os.getenv only READS the environment; load_dotenv() is what LOADS .env into it. SECRET_KEY had no fallback (fail-fast), which is what exposed that .env wasn't being loaded. Added load_dotenv() to security.py and database.py (idempotent, safe to call twice).
    - "NameError: get_current_user is not defined" — an ordering bug, not a typo. Depends(...) in default args is evaluated at def time, so dependencies must be defined ABOVE the endpoints that use them.
    - Case-sensitivity typos: OAuth2PasswordBearer (both O and A uppercase — it's an acronym).

- Concepts locked in
    - Hashing is one-way (can't decrypt); bcrypt is deliberately slow + auto-salted, so identical passwords get different hashes. Even we can't read a user's password.
    - JWT = header.payload.signature. Payload is base64-encoded, NOT encrypted (readable by anyone) — the signature gives INTEGRITY, not secrecy. Never put secrets in a token.
    - Authentication (who are you?) != Authorization (are you allowed to touch THIS row?). Scoping every query by current_user.id is what enforces authz.
    - IDOR: the classic bug where a logged-in user reads someone else's data by guessing an id. Fix: bake the owner check INTO the query (id AND user_id) so a non-owner gets a clean 404.
    - 404 not 403 for a row you don't own — 403 would leak that the id exists.
    - Generic "Incorrect email or password" on login avoids user enumeration.
    - 204 No Content has no body by spec — the status code IS the message.
    - db.scalars(...) returns objects (not row-tuples); .first() = one-or-None, .all() = list, .one() = exactly-one-or-raise.
    - Python grammar: ":" describes (type annotations, dict pairs, block headers); "=" assigns (variables, keyword args). Same word can flip: subject: str (annotation) vs subject=... (keyword arg).

- Done when met: register + login work through /docs; all expense endpoints require a valid token; two different users cannot see or modify each other's data (verified); DEV_USER_ID gone.

- Notes
    - Never commit .env — SECRET_KEY stays local. Rotating the secret invalidates all existing tokens.
    - deprecated="auto" buys algorithm agility: old hashes keep verifying by their $-prefix; verify_and_update can silently upgrade them at login without a password reset.
    - "Know this exists" for later (NOT now): refresh tokens, EmailStr + password-strength rules, pwdlib migration, APIRouter split, rate-limiting /auth/login, try/except IntegrityError on register.
    - TODO Phase 4: (per roadmap — confirm exact tasks next session).

# Started phase 4 (React frontend); confirmed Node.js + npm are installed as the JS-side equivalents of Python + pip before scaffolding.


- Notes 
    - Vite is a scaffolding + dev-server tool for frontend apps.
    - Confirmed Node v22/ npm 11, then scaffolded a Vite + React(Javascript) app into frontend/ as a sibling of backend/. keeping monorepo layout.
    - Ran npm install(frontend equivalent of pip install, populates node_modules/) and npm run dev; Vite starter app loads at localhost:5173 with a working useState counter. 
    - Opened a second terminal so the dev server keeps running; verified via git status and git check-ignore that Vite's nested frontend/.gitignore alread excludes node_modeules before commiting the scafolld, as it is a huge file and we do not want to push that to github.
    - Commited the untouched React scaffold as a clean "frontend works" checkpoint (subject +why message) and pushed to GitHub; verified node_modules never entered the staging area.
    - Learned that a React component is a capitalized function returning JSX; replaced Vite's boilerplate App.jsx with my own minimal component and saw it hot-reload live in the browser.
    - We can add comment inside div in a .jsx file by doing this  { /* content */}
    - A Component Function runs every time it re-renders.
    - An async function is a special type of function in programming that runs tasks in the background, always returns a Promise, and lets you use the await keyword to pause code execution until a task finishes without freezing the main app.
    - A Promise is a programming object that acts as a temporary placeholder for a value that is not yet known because the operation delivering it is still incomplete.
    - #Gotcha fetch doesn not throw an error on a 404 or 500. It only rejectsif the network itself fails. So you must check response.ok yourself. [try/catch/finally]
    - A component can return different JSX depending on state. 
    - map() and key is used to turn an array of expense objects into a list of on-screen elements.
    - Ever element .map() produces needs a key prop.
    - The key is a table, unique ID that lets React track which row is which across re-renders.
    - Inline conditional rendering is the practice of emebedding conditional JavaScript logic directly within your UI layout. 
    - We use early return when the entire component is one state. Inline && is used when only part of UI Changes.
    - DELETE returns 204 No Content => we don't call response.json(), like we do for GET/POST. 
    - To delete a specific row, you need to tell the handler which id. The right way is to wrap it in an arrow function. Because, if we do not add an arrow, REACT will immediately call it during render. 
    - Found that login "did nothing until refresh" because React doens't watch localStorage and the list only fetched once on mount; fixed it by lifiting the token into App State(setToken on login) and conditionally rendering login vs. app, sp logging in re-renders instantly. 
    - Lifted the JWT into App React state(seeded from localStorage, set via setToken on login) and gated the UI on it - loggin in now re-renders into the app instantly instead of a manual refresh. [Same thing mentioned above]
    - Ternary Rendering and Fragments.
    - JSON.stringify() convers a JS object, array or primitive value into a JSON-formatted String.
    - Clicking Save makes my browser send a PATCH note describing the change to your backend; your backend validates who you are, updates the row, and the real save runs db.commit() to write it to SQLite; then the browser re-fetches so the screen matches the database.  

# Phase 4 [Wrapping Things up]

- Expired/invalid JWT now forces a clean re-login - any authed request returning 401 clears the token and drops the user back to the login screen, via an onAuthError callback passed from App into ExpenseList. 
- Refactored the UI into focused components; extracted <LoginForm> (owns its login state, reports the token up via onLoggedIn) and <AddExpenseForm> (owns its input state, reports successs via onAdded, and forwards onAuthError); App and Expense List are now thin Coordinators.
- Finished the Tailwind dashboard styling: adding a card-based expense list, styled add/edit forms and actions. responsive rows, accessible labels, clean UI states. and confirmed ESLint passes.
- Add an authenticated, owner-scoped monthly-total endpoint using SQL SUM, then manually verified the toal and confirmed previous-month expense are excluded.
- Notes
    - Logic that logs out the user lives in App.jsx , But the 401 happens  insides ExpenseList.jsx, to fix that, we will use a prop, that will be used to trigger the event in App.jsx upon receiving the information from ExpenseList.jsx.
    - The {} in function ExpenseList({ onAuthError }) is a destructuring pattern (unpacking a value on the left side), not an object literal(bulding a value on the right side). Same braces, opposite jobs -- one takes apart, one puts together. You'll see this exact pattern on  nearly every React component that takes props, so it's worth having it click now. 

# Phase 5


- Displayed the owner-scoper monthly total in the React dashboard and verified that it refreshes automatically after expense change.
- Added an owner-scoped month-over-month endpoint that compares databae-aggregated current and previous totals, returns amount and percentage changes, and safely handles a zero previous month.
- Added an automatically refreshing month-over-month dashboard card with plain-language increase or decrease messaging while preserving signed API.
- Fixed missing 401 handling in handleUpdate(): a PATCH with an expired/invalid token now forces a cleam re-login via onAuthError() instead of a silently failing, matching fetchExpenses() and handleDelete().
- Cleaned up fetchExpenses monthly-total block: fixed a broken template literal ($(...) -> ${...}) so the error message shows the real HTTP status, and switched the 401 check from == to === for consistency with the other status checks.
- Fixed silent Tailwind class typos.
- Removed the superseded commented-out ternary from the month-over-month card; buildComparisonText() is now the single, clear source of the comparison text.
- Notes:
    - Helper Function : Function that holds reusable logic.
    - _, convention implies that the value was returned, but we intentionally do not need it there. [unused]
    - Tuple :  ordered collection of values grouped together (unlike list, it is fixed)
    - We prefer to use SQL instead of python, as python would fetch every expense into itself and loop through them, which is inefficient. 
    - Add the month-over-month end point has 2 task
        - Ask the databbase for two totals
        - Compare those totals in Python
    

# Phase 6

- IMPORTANT: Any function parameter that isn't in the path and is a plain scalar type automatically becomes a query parameter. 
- Added authenticated, owner-scoped GET /reports/monthly: filters expenses by an explicit inclusive start/end date range, rejects reversed ranges with 400, and gets 422 on unparsable dates for free via date type hint. 
- Added GET /report/monthly.csv: streams a downloadable CSV of the date-range expenses using the csv module + io.StringIO + StreamingResponse with a Content-Disposition attachment header. (Bug  vaught: writer.writerow was initially outside the for loop, so only one row wrote.)
- Refactored both report endpoints onto a shared _expenses_in_range() helper (validation + owner-scoped date-range query), removing duplicated logic so the range rules live in one place.
- Added an Export CSV button to the React dashboard: fetches /reports/monthly.csv with the auth header, downloads the current month via a Blob + object URL + programmatic anchor click, and resues the 401 -> onAuthError logout path. 


# Phase 7 

- Added keyword-based categorize() and auto-fill on expense create, with user override respected; category now surfaced on ExpenseCreate(optional) and ExpenseRead.