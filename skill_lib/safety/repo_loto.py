#!/usr/bin/env python3
# === MODULE_BUILD ===
# id: repo_mutation_gate
#   module_name: repo_loto
#   module_kind: instrument
#   summary: delete-on-completion session gate for repo mutation; presence of state means open work, absence means clean
#   owner: Way Seer Erin
#   public_surface: loto open, loto run, loto test, loto close, loto fail, loto clear, loto status, loto guard, loto install-hook
#   internal_surface: _load, _save, _touched_files, _scope_violations, _trailers, _digest, _commit, _git, _ensure_gitignored
#   auth_boundary: none
#   storage_boundary: write
#   network_boundary: none
#   user_data_boundary: none
#   admin_only: false
#   tests: tests/test_repo_loto.py (CHECKS-declared, reconciled via --audit)
#   rollout: manual invocation; pre-push hook calls `loto guard`
#   rollback: rm -rf .loto/ and remove hook line
#   unresolved: credential-gate integration, RATIOS block
# === END MODULE_BUILD ===
# === CONTRACTS ===
# id: loto_open_never_dirties
#   given: clean working tree; `loto open` succeeds
#   then: working tree is still clean; exclusion went to .git/info/exclude, never .gitignore
#   class: doctrine
#
# id: loto_close_deletes_tag
#   given: one in-scope mutation commit and passing test evidence; `loto close`
#   then: .loto/ is empty and HEAD carries Loto-* trailers; git is the only archive
#   class: doctrine
#
# id: loto_latest_test_wins
#   given: a failing run of a test command followed by a passing run of the identical command
#   then: close proceeds; a distinct command whose latest run failed still blocks close
#   class: evidence
#
# id: loto_scope_enforced
#   given: files touched outside the declared --files globs
#   then: close refuses with the violating paths named
#   class: safety
#
# id: loto_scar_blocks_work
#   given: an unacknowledged SCAR-*.json in .loto/
#   then: `loto open` refuses and `loto guard` exits nonzero
#   class: safety
#
# id: loto_clear_is_empty_commit
#   given: `loto clear` on a scar
#   then: refused on dirty tree; on clean tree produces a commit touching zero files, carrying scar trailers, and deletes the scar
#   class: doctrine
#
# id: loto_one_commit_per_session
#   given: more than one commit between base and HEAD at close
#   then: close refuses (v0.1 invariant: one session, one mutation commit)
#   class: doctrine
# === END CONTRACTS ===
"""
repo_loto — lockout/tagout for repo mutation, delete-on-completion style.

Doctrine:
  The ledger is working memory, not archive. Git is the archive.
  PRESENCE of state in .loto/ means work is open or wounded.
  ABSENCE means clean. Steady state of a healthy repo: .loto/ empty.

  open  -> .loto/active.json exists (the hung tag)
  close -> evidence distilled into git commit trailers; tag deleted
  fail  -> tag becomes .loto/SCAR-<id>.json; blocks new work
  clear -> scar acknowledged via empty commit with trailers; scar deleted

Nothing here is ever appended forever. Success leaves only the commit.
"""

import fnmatch
import json
import os
import subprocess
import sys
import time
import uuid

LOTO_DIR = ".loto"
ACTIVE = os.path.join(LOTO_DIR, "active.json")


# ---------- git plumbing ----------

def _git(*args, check=True):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        _die(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout.strip()


def _die(msg, code=1):
    print(f"loto: {msg}", file=sys.stderr)
    sys.exit(code)


def _repo_root():
    return _git("rev-parse", "--show-toplevel")


def _head():
    return _git("rev-parse", "HEAD")


def _branch():
    return _git("rev-parse", "--abbrev-ref", "HEAD")


def _dirty():
    return bool(_git("status", "--porcelain"))


# ---------- state ----------

def _ensure_gitignored():
    """working memory must never enter the archive — and hanging the
    tag must never dirty the tree, so use .git/info/exclude, not .gitignore."""
    line = LOTO_DIR + "/"
    path = os.path.join(_git("rev-parse", "--git-dir"), "info", "exclude")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path) as f:
            if line in (l.strip() for l in f):
                return
    except FileNotFoundError:
        pass
    with open(path, "a") as f:
        f.write(line + "\n")


def _scars():
    if not os.path.isdir(LOTO_DIR):
        return []
    return sorted(f for f in os.listdir(LOTO_DIR) if f.startswith("SCAR-"))


def _load():
    if not os.path.exists(ACTIVE):
        _die("no active session. `loto open` first.")
    with open(ACTIVE) as f:
        return json.load(f)


def _save(tag):
    os.makedirs(LOTO_DIR, exist_ok=True)
    tmp = ACTIVE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(tag, f, indent=2)
    os.replace(tmp, ACTIVE)


# ---------- evidence ----------

def _touched_files(tag):
    committed = _git("diff", "--name-only", f"{tag['base']}..HEAD", check=False)
    dirty = _git("status", "--porcelain", check=False)
    files = set(filter(None, committed.splitlines()))
    for line in dirty.splitlines():
        files.add(line[3:].split(" -> ")[-1])
    return sorted(f for f in files if not f.startswith(LOTO_DIR + "/"))


def _scope_violations(tag, touched):
    allowed = tag["files_allowed"]
    if not allowed:
        return []
    return [f for f in touched
            if not any(fnmatch.fnmatch(f, pat) for pat in allowed)]


def _latest_tests(tag):
    """latest-run-wins, per command: a rerun supersedes its predecessor.
    the full record stays in working memory (and in the digest);
    only the standing evidence is the last run of each command."""
    latest = {}
    for t in tag["tests"]:
        latest[t["cmd"]] = t
    return list(latest.values())


def _digest(tag):
    """sha256 shadow of the working memory that close will delete.
    verifiable against scrollback/shell history if ever disputed."""
    import hashlib
    blob = json.dumps({"commands": tag["commands"], "tests": tag["tests"]},
                      sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def _trailers(tag, touched, kind="close"):
    attempts = {}
    for t in tag["tests"]:
        attempts[t["cmd"]] = attempts.get(t["cmd"], 0) + 1
    tests = "; ".join(
        f"{t['cmd']} (exit {t['exit']}"
        + (f", {attempts[t['cmd']]} runs" if attempts[t["cmd"]] > 1 else "")
        + ")"
        for t in _latest_tests(tag)
    ) or "none recorded"
    lines = [
        f"Loto-Session: {tag['id']}",
        f"Loto-Kind: {kind}",
        f"Loto-Actor: {tag.get('actor', 'unknown')}",
        f"Loto-Intent: {tag['intent']}",
        f"Loto-Base: {tag['base']}",
        f"Loto-Branch: {tag['branch']}",
        f"Loto-Scope: {','.join(tag['files_allowed']) or 'unrestricted'}",
        f"Loto-Touched: {len(touched)} file(s)",
        f"Loto-Tests: {tests}",
        f"Loto-Commands: {len(tag['commands'])} recorded",
        f"Loto-Command-Digest: {_digest(tag)}",
    ]
    if kind == "scar-clear":
        lines.append(f"Loto-Scar-Reason: {tag.get('fail_reason', 'unknown')}")
        lines.append(f"Loto-Clear-Reason: {tag.get('clear_reason', 'unstated')}")
    return "\n".join(lines)


# ---------- verbs ----------

def cmd_open(args):
    if os.path.exists(ACTIVE):
        _die("a tag is already hung (active session exists). close or fail it.")
    scars = _scars()
    if scars:
        _die(f"unacknowledged scar(s) block new work: {', '.join(scars)}. "
             f"`loto clear <scar> --reason ...` first.")
    intent = _req(args, "--intent")
    files = _opt(args, "--files", "")
    if _dirty() and "--allow-dirty" not in args:
        _die("working tree dirty. commit/stash first, or pass --allow-dirty "
             "(the dirt becomes part of your declared pre-state).")
    tag = {
        "id": f"{time.strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:6]}",
        "opened": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "actor": (_opt(args, "--actor", None)
                  or os.environ.get("LOTO_ACTOR")
                  or os.environ.get("USER") or "unknown"),
        "repo": _repo_root(),
        "branch": _branch(),
        "base": _head(),
        "dirty_at_open": _dirty(),
        "intent": intent,
        "files_allowed": [p.strip() for p in files.split(",") if p.strip()],
        "commands": [],
        "tests": [],
    }
    _ensure_gitignored()
    _save(tag)
    print(f"tag hung: {tag['id']}")
    print(f"  base {tag['base'][:12]} on {tag['branch']}")
    print(f"  scope: {files or 'unrestricted'}")


def _record(tag_list_key, args):
    tag = _load()
    cmd = " ".join(args)
    if not cmd:
        _die("no command given.")
    r = subprocess.run(cmd, shell=True)
    tag[tag_list_key].append({
        "cmd": cmd,
        "shell": True,
        "exit": r.returncode,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    })
    _save(tag)
    return r.returncode


def cmd_run(args):
    sys.exit(_record("commands", args))


def cmd_test(args):
    code = _record("tests", args)
    print(f"test recorded (exit {code}).")
    sys.exit(code)


def cmd_close(args):
    tag = _load()
    touched = _touched_files(tag)
    violations = _scope_violations(tag, touched)
    if violations:
        _die("scope violation — touched outside declared files:\n  "
             + "\n  ".join(violations)
             + "\nrevert them, or `loto fail` honestly and reopen wider.")
    if _dirty():
        _die("working tree dirty. commit your changes, then close "
             "(close distills evidence into that commit).")
    if _head() == tag["base"]:
        # nothing happened; the tag comes off, nothing to archive
        os.remove(ACTIVE)
        print("no mutation occurred. tag removed, nothing archived.")
        return
    n_commits = int(_git("rev-list", "--count", f"{tag['base']}..HEAD"))
    if n_commits > 1:
        _die(f"{n_commits} commits since open; trailers on one commit would "
             "misdescribe the session. squash to one, or fail and reopen. "
             "(v0.1 invariant: one session, one mutation commit.)")
    failed = [t for t in _latest_tests(tag) if t["exit"] != 0]
    if failed and "--allow-failing-tests" not in args:
        _die("latest run failing for:\n  "
             + "\n  ".join(t["cmd"] for t in failed)
             + "\nfix and re-run `loto test` (latest run wins), or close "
             "with --allow-failing-tests (the failure goes into the trailers).")
    if not tag["tests"]:
        if "--no-test" not in args:
            _die("no test evidence recorded. run `loto test <cmd>`, "
                 "or close with --no-test to record that honestly.")
        tag["tests"].append({"cmd": "NONE (waived at close)", "shell": False,
                             "exit": -1,
                             "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z")})
    elif "--no-test" in args:
        print("note: --no-test ignored; test evidence exists and stands.")
    body = _git("log", "-1", "--pretty=%B")
    msg = body.rstrip() + "\n\n" + _trailers(tag, touched, "close") + "\n"
    _commit(msg, amend=True)
    os.remove(ACTIVE)
    print(f"session {tag['id']} closed. evidence lives in HEAD trailers.")
    print(f"  touched {len(touched)} file(s); .loto/ is clean.")


def _commit(msg, amend=False, allow_empty=False):
    """multiline messages via -F tempfile, inspectable and quote-safe."""
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".loto-msg",
                                     delete=False) as f:
        f.write(msg)
        path = f.name
    try:
        args = ["commit", "-F", path]
        if amend:
            args.insert(1, "--amend")
        if allow_empty:
            args.insert(1, "--allow-empty")
        _git(*args)
    finally:
        os.unlink(path)


def cmd_fail(args):
    tag = _load()
    tag["fail_reason"] = _req(args, "--reason")
    tag["failed"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    scar = os.path.join(LOTO_DIR, f"SCAR-{tag['id']}.json")
    with open(scar, "w") as f:
        json.dump(tag, f, indent=2)
    os.remove(ACTIVE)
    print(f"scar written: {scar}")
    print("new sessions are blocked until it is cleared with a reason.")


def cmd_clear(args):
    names = [a for a in args if a.startswith("SCAR-")]
    if not names:
        _die(f"name the scar: {', '.join(_scars()) or '(none found)'}")
    reason = _req(args, "--reason")
    path = os.path.join(LOTO_DIR, names[0])
    if not os.path.exists(path):
        _die(f"no such scar: {names[0]}")
    with open(path) as f:
        tag = json.load(f)
    if _dirty():
        _die("working tree dirty. commit/stash first — a scar acknowledgment "
             "must be an empty commit, not a mixed one.")
    tag["clear_reason"] = reason
    msg = (f"loto: acknowledge scar {tag['id']}\n\n"
           + _trailers(tag, [], "scar-clear") + "\n")
    _commit(msg, allow_empty=True)
    os.remove(path)
    print(f"scar {tag['id']} acknowledged into an empty commit and removed.")


def cmd_status(_args):
    active = os.path.exists(ACTIVE)
    scars = _scars()
    if not active and not scars:
        print("clean. no tag hung, no scars. (.loto/ empty is the goal state)")
        return
    if active:
        with open(ACTIVE) as f:
            tag = json.load(f)
        print(f"ACTIVE  {tag['id']}  intent: {tag['intent']}")
        print(f"        base {tag['base'][:12]}  "
              f"cmds {len(tag['commands'])}  tests {len(tag['tests'])}")
    for s in scars:
        print(f"SCAR    {s}")


def cmd_guard(_args):
    """pre-push hook body: refuse push unless .loto/ is clean."""
    if os.path.exists(ACTIVE):
        _die("push refused: session still open. `loto close` or `loto fail`.")
    if _scars():
        _die("push refused: unacknowledged scar(s). `loto clear` first.")
    sys.exit(0)


def cmd_install_hook(_args):
    """write the pre-push hook so rollout is a command, not a memory."""
    hook = os.path.join(_git("rev-parse", "--git-dir"), "hooks", "pre-push")
    me = os.path.abspath(__file__)
    body = f"#!/bin/sh\nexec python3 {me} guard\n"
    if os.path.exists(hook):
        with open(hook) as f:
            existing = f.read()
        if "guard" in existing:
            print("hook already installed.")
            return
        _die(f"a pre-push hook already exists at {hook}; merge manually.")
    with open(hook, "w") as f:
        f.write(body)
    os.chmod(hook, 0o755)
    print(f"pre-push guard installed: {hook}")


# ---------- arg helpers ----------

def _req(args, flag):
    v = _opt(args, flag, None)
    if v is None:
        _die(f"{flag} is required.")
    return v


def _opt(args, flag, default):
    if flag in args:
        i = args.index(flag)
        if i + 1 < len(args):
            return args[i + 1]
    return default


VERBS = {
    "open": cmd_open, "run": cmd_run, "test": cmd_test,
    "close": cmd_close, "fail": cmd_fail, "clear": cmd_clear,
    "status": cmd_status, "guard": cmd_guard,
    "install-hook": cmd_install_hook,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in VERBS:
        print(__doc__)
        print("verbs: " + ", ".join(VERBS))
        sys.exit(2)
    os.chdir(_repo_root())
    VERBS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    main()
