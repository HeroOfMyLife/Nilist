import json
import random
import os

# ── REALISTIC PR TITLE POOL ────────────────────────────────────────────────────
PR_TITLES = [
    "Fix auth token expiration bug",
    "Refactor user dashboard component",
    "Update dependencies to latest stable versions",
    "Add pagination to /api/orders endpoint",
    "Fix race condition in background job queue",
    "Implement OAuth2 login flow",
    "Remove deprecated payment gateway integration",
    "Add unit tests for UserService",
    "Fix null pointer exception in cart checkout",
    "Migrate database connection to connection pooling",
    "Add rate limiting to public API endpoints",
    "Refactor authentication middleware",
    "Fix broken redirect after password reset",
    "Optimise SQL queries in reporting module",
    "Add input validation to registration form",
    "Replace lodash with native ES2023 equivalents",
    "Fix memory leak in WebSocket handler",
    "Add dark mode support to settings page",
    "Implement soft-delete for user accounts",
    "Fix CSRF token mismatch on form submission",
    "Upgrade Node.js runtime to v20 LTS",
    "Add retry logic to external API client",
    "Fix timezone bug in scheduled notifications",
    "Refactor order status state machine",
    "Add caching layer for product catalogue",
    "Fix XSS vulnerability in comment renderer",
    "Implement file upload size validation",
    "Add audit logging for admin actions",
    "Fix broken image URLs after CDN migration",
    "Refactor config loading to use environment variables",
    "Add health check endpoint for load balancer",
    "Fix incorrect tax calculation for EU orders",
    "Implement two-factor authentication",
    "Resolve merge conflict in feature/checkout branch",
    "Add OpenAPI spec for internal services",
    "Fix stale cache bug in user profile page",
    "Refactor notification service to use event queue",
    "Add index to `created_at` column in events table",
    "Fix broken CI pipeline on Windows runners",
    "Implement password strength enforcement",
    "Add export to CSV feature in admin dashboard",
    "Fix session expiry not invalidating JWT",
    "Refactor frontend routing to React Router v6",
    "Add Sentry error tracking to API gateway",
    "Fix incorrect HTTP status codes in REST API",
    "Implement lazy loading for dashboard widgets",
    "Add GDPR data deletion endpoint",
    "Fix flaky integration test in checkout flow",
    "Refactor email template rendering engine",
    "Update Dockerfile to use multi-stage build",
    "Fix permissions check in document sharing feature",
]

# ── REALISTIC COMMENT POOLS ────────────────────────────────────────────────────
ROUND_1_COMMENTS = [
    ["Security flaw: user input is not sanitised before DB query", "Missing authentication check on this endpoint"],
    ["Null pointer exception if `user` is None — needs a guard clause", "Logic error: loop exits one iteration too early"],
    ["SQL injection risk in raw query string", "No error handling if the external API call times out"],
    ["Race condition possible when two threads update the same record", "Missing rollback on transaction failure"],
    ["Hardcoded secret key detected — must be moved to env vars", "No rate limiting on this public endpoint"],
    ["Business logic is incorrect: discount applies before tax, not after", "Missing index will cause full table scan at scale"],
    ["CSRF token not validated on this form action", "Session is not invalidated on logout"],
    ["XSS vulnerability: HTML is rendered from unescaped user input", "Sensitive data logged in plaintext"],
    ["Auth bypass possible via JWT algorithm confusion", "File path traversal vulnerability in upload handler"],
    ["Unhandled promise rejection will silently swallow errors", "Breaking change: this renames a public API field"],
]

ROUND_2_COMMENTS = [
    ["Rename `tmp` to `userPayload` for clarity", "Missing trailing comma in object literal"],
    ["LGTM — just a nit: extract this into a named constant"],
    ["Variable `x` should be `itemCount` per naming convention", "Unnecessary `else` after `return`"],
    ["Missing semicolon on line 42", "LGTM overall"],
    ["Whitespace nit: remove extra blank line", "Rename `cb` to `callback`"],
    ["LGTM — minor: this comment is outdated, please update it"],
    ["Prefer `const` over `let` here — value is never reassigned", "Typo in error message: 'occured' → 'occurred'"],
    ["Missing trailing newline at end of file", "LGTM"],
    ["Rename function `doIt` to `processPayment`", "Inline this single-use variable"],
    ["Nit: align ternary operator for readability", "LGTM from my side"],
]

ROUND_3_COMMENTS = [
    ["LGTM", "Approved — ready to merge"],
    ["Looks good to me 👍"],
    ["Approved"],
    ["LGTM — nice clean fix"],
    ["All previous comments addressed, good to go"],
    ["Approved after re-review"],
    ["LGTM, CI is green"],
    ["Ship it"],
    ["Looks good, no further comments"],
    ["Approved — well done"],
]

ROUND_4_COMMENTS = [
    ["LGTM"],
    ["Still approved"],
    ["No changes needed"],
    ["Merged"],
    ["Final LGTM"],
]


def _pick(pool: list) -> list:
    """Return a random entry from a comment pool (always a list)."""
    entry = random.choice(pool)
    return entry if isinstance(entry, list) else [entry]


def generate_mock_data():
    # Shuffle titles so each run produces a varied ordering
    titles = PR_TITLES.copy()
    random.shuffle(titles)

    prs = []

    for i in range(50):
        pr_id = f"PR-{1000 + i + 1}"
        title = titles[i % len(titles)]
        num_rounds = random.choices([2, 3, 4], weights=[40, 40, 20])[0]

        rounds = []
        for r in range(1, num_rounds + 1):
            if r == 1:
                value_type    = "high"
                comments      = _pick(ROUND_1_COMMENTS)
                lines_changed = random.randint(20, 100)
                time_spent    = random.randint(15, 45)
            elif r == 2:
                value_type    = "low"
                comments      = _pick(ROUND_2_COMMENTS)
                lines_changed = random.randint(1, 5)
                time_spent    = random.randint(5, 20)
            elif r == 3:
                value_type    = "low"
                comments      = _pick(ROUND_3_COMMENTS)
                lines_changed = random.randint(1, 3)
                time_spent    = random.randint(5, 15)
            else:  # round 4
                value_type    = "low"
                comments      = _pick(ROUND_4_COMMENTS)
                lines_changed = random.randint(1, 2)
                time_spent    = random.randint(5, 10)

            rounds.append({
                "round_number":          r,
                "reviewer_comments":     comments,
                "lines_of_code_changed": lines_changed,
                "time_spent_minutes":    time_spent,
                "value_assessment":      value_type,
            })

        prs.append({"pr_id": pr_id, "title": title, "rounds": rounds})

    # ── Write output ──────────────────────────────────────────────────────────
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir   = os.path.join(script_dir, '..', 'data')
    os.makedirs(data_dir, exist_ok=True)

    file_path = os.path.join(data_dir, 'sample_reviews.json')
    with open(file_path, 'w') as f:
        json.dump(prs, f, indent=4)

    print(f"Generated {len(prs)} PRs -> {file_path}")


if __name__ == "__main__":
    generate_mock_data()
