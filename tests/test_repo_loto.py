#!/usr/bin/env python3
# === MODULE_BUILD ===
# id: repo_loto_evidence
#   module_name: test_repo_loto
#   module_kind: checks
#   summary: evidentiary procedures for repo_loto CONTRACTS; standalone or pytest; --audit reconciles the declared graph without execution
#   owner: Way Seer Erin
#   public_surface: test_* functions, main, --audit
#   internal_surface: _mk_repo, _run, _loto, _parse_block, _resolve_call, _requires_met
#   tests: self
#   unresolved: mutation-level verification that checks actually exercise their contracts
# === END MODULE_BUILD ===
# === CHECKS ===
# id: check_open_never_dirties
#   proves: loto_open_never_dirties
#   call: self::test_open_never_dirties
#   requires: git, python3, posix_shell
#   timeout: 20
#   mutates: filesystem
#   cleanup: tempdir_teardown
#
# id: check_close_deletes_tag
#   proves: loto_close_deletes_tag
#   call: self::test_close_deletes_tag
#   requires: git, python3, posix_shell
#   timeout: 20
#   mutates: filesystem
#   cleanup: tempdir_teardown
#
# id: check_latest_test_wins
#   proves: loto_latest_test_wins
#   call: self::test_latest_test_wins
#   requires: git, python3, posix_shell
#   timeout: 20
#   mutates: filesystem
#   cleanup: tempdir_teardown
#
# id: check_scope_enforced
#   proves: loto_scope_enforced
#   call: self::test_scope_enforced
#   requires: git, python3, posix_shell
#   timeout: 20
#   mutates: filesystem
#   cleanup: tempdir_teardown
#
# id: check_scar_blocks_work
#   proves: loto_scar_blocks_work
#   call: self::test_scar_blocks_work
#   requires: git, python3, posix_shell
#   timeout: 20
#   mutates: filesystem
#   cleanup: tempdir_teardown
#
# id: check_clear_is_empty_commit
#   proves: loto_clear_is_empty_commit
#   call: self::test_clear_is_empty_commit
#   requires: git, python3, posix_shell
#   timeout: 20
#   mutates: filesystem
#   cleanup: tempdir_teardown
#
# id: check_one_commit_per_session
#   proves: loto_one_commit_per_session
#   call: self::test_one_commit_per_session
#   requires: git, python3, posix_shell
#   timeout: 20
#   mutates: filesystem
#   cleanup: tempdir_teardown
# === END CHECKS ===
"""
Evidence for repo_loto. Contracts live in the source; this file only
claims to prove them. CHECKS fields enter the schema when a runner mode
consumes them; this module consumes requires and per-check timeout at
runtime, and mutates/cleanup are visible danger documentation.

Run:  python3 test_repo_loto.py            all checks, tempdir-isolated
      python3 test_repo_loto.py --audit    reconcile CONTRACTS<->CHECKS, no execution
      pytest test_repo_loto.py             same checks under pytest
"""

import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile

# locate the module under test: env override, then common layouts
_CANDIDATES = [
    os.environ.get("REPO_LOTO", ""),
    os.path.join(os.path.dirname(__file__), "repo_loto.py"),
    os.path.join(os.path.dirname(__file__), "..", "skill_lib", "safety", "repo_loto.py"),
    os.path.join(os.path.dirname(__file__), "..", "repo_loto.py"),
]
LOTO = next((os.path.abspath(p) for p in _CANDIDATES if p and os.path.exists(p)), None)


TIMEOUT = 20          # default bound; per-check CHECKS `timeout:` overrides
_ACTIVE_TIMEOUT = [TIMEOUT]   # consumed: set per check by main(), read by _run


# ---------- fixture ----------

def _run(cmd, cwd, check=False):
    """bounded subprocess that owns its whole process group: descendants
    inheriting captured pipes cannot outlive the timeout."""
    p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True,
                         start_new_session=True)
    try:
        out, err = p.communicate(timeout=_ACTIVE_TIMEOUT[0])
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        out, err = p.communicate()
        raise subprocess.TimeoutExpired(cmd, _ACTIVE_TIMEOUT[0],
                                        output=out, stderr=err)
    r = subprocess.CompletedProcess(cmd, p.returncode, out, err)
    if check and r.returncode != 0:
        raise subprocess.CalledProcessError(r.returncode, cmd,
                                            output=out, stderr=err)
    return r


def _mk_repo():
    d = tempfile.mkdtemp(prefix="loto-check-")
    def g(*a):
        _run(["git", *a], cwd=d, check=True)
    g("init", "-q")
    g("config", "user.email", "check@loto")
    g("config", "user.name", "loto-check")
    g("config", "gc.auto", "0")
    g("config", "maintenance.auto", "false")
    with open(os.path.join(d, "a.txt"), "w") as f:
        f.write("seed\n")
    g("add", ".")
    g("commit", "-qm", "init")
    return d


def _loto(repo, *args):
    return _run([sys.executable, LOTO, *args], cwd=repo)


def _git_out(repo, *args):
    return _run(["git", *args], cwd=repo, check=True).stdout


def _porcelain(repo):
    return _git_out(repo, "status", "--porcelain").strip()


def _append(repo, name, text):
    with open(os.path.join(repo, name), "a") as f:
        f.write(text + "\n")


def _commit_all(repo, msg):
    _run(["git", "add", "-A"], cwd=repo, check=True)
    _run(["git", "commit", "-qm", msg], cwd=repo, check=True)


# ---------- checks ----------

def test_open_never_dirties():
    repo = _mk_repo()
    try:
        r = _loto(repo, "open", "--intent", "check", "--files", "a.txt")
        assert r.returncode == 0, r.stderr
        assert _porcelain(repo) == "", "open dirtied the working tree"
        assert os.path.exists(os.path.join(repo, ".loto", "active.json"))
        gi = os.path.join(repo, ".gitignore")
        assert not os.path.exists(gi), ".gitignore was created by open"
        with open(os.path.join(repo, ".git", "info", "exclude")) as f:
            assert ".loto/" in f.read()
    finally:
        shutil.rmtree(repo)


def test_close_deletes_tag():
    repo = _mk_repo()
    try:
        _loto(repo, "open", "--intent", "check", "--files", "a.txt")
        _append(repo, "a.txt", "change")
        _loto(repo, "test", "true")
        _commit_all(repo, "edit")
        r = _loto(repo, "close")
        assert r.returncode == 0, r.stderr
        loto_dir = os.path.join(repo, ".loto")
        assert not os.path.exists(loto_dir) or not os.listdir(loto_dir), \
            ".loto not empty after close"
        body = _git_out(repo, "log", "-1", "--pretty=%B")
        for t in ("Loto-Session:", "Loto-Intent:", "Loto-Tests:",
                  "Loto-Command-Digest:"):
            assert t in body, f"missing trailer {t}"
    finally:
        shutil.rmtree(repo)


def test_latest_test_wins():
    repo = _mk_repo()
    try:
        # identical command: fail then pass -> close proceeds
        _loto(repo, "open", "--intent", "check", "--files", "a.txt")
        cmd = "grep -q PASS a.txt"
        _loto(repo, "test", cmd)            # fails, PASS absent
        _append(repo, "a.txt", "PASS")
        _loto(repo, "test", cmd)            # passes
        _commit_all(repo, "edit")
        r = _loto(repo, "close")
        assert r.returncode == 0, "passing rerun did not supersede: " + r.stderr
        assert "2 runs" in _git_out(repo, "log", "-1", "--pretty=%B")
        # distinct command whose latest run failed -> blocked
        _loto(repo, "open", "--intent", "check2", "--files", "a.txt")
        _append(repo, "a.txt", "more")
        _loto(repo, "test", "true")
        _loto(repo, "test", "false")
        _commit_all(repo, "edit2")
        r = _loto(repo, "close")
        assert r.returncode != 0, "distinct failing command did not block"
        assert "latest run failing" in r.stderr
    finally:
        shutil.rmtree(repo)


def test_scope_enforced():
    repo = _mk_repo()
    try:
        _loto(repo, "open", "--intent", "check", "--files", "a.txt")
        _append(repo, "b.txt", "outside scope")
        _loto(repo, "test", "true")
        _commit_all(repo, "sneaky")
        r = _loto(repo, "close")
        assert r.returncode != 0, "out-of-scope mutation closed"
        assert "scope violation" in r.stderr and "b.txt" in r.stderr
    finally:
        shutil.rmtree(repo)


def test_scar_blocks_work():
    repo = _mk_repo()
    try:
        _loto(repo, "open", "--intent", "doomed")
        r = _loto(repo, "fail", "--reason", "deliberate")
        assert r.returncode == 0, r.stderr
        scars = [f for f in os.listdir(os.path.join(repo, ".loto"))
                 if f.startswith("SCAR-")]
        assert len(scars) == 1
        assert _loto(repo, "open", "--intent", "blocked").returncode != 0
        assert _loto(repo, "guard").returncode != 0
    finally:
        shutil.rmtree(repo)


def test_clear_is_empty_commit():
    repo = _mk_repo()
    try:
        _loto(repo, "open", "--intent", "doomed")
        _loto(repo, "fail", "--reason", "deliberate")
        scar = next(f for f in os.listdir(os.path.join(repo, ".loto"))
                    if f.startswith("SCAR-"))
        _append(repo, "a.txt", "dirt")
        r = _loto(repo, "clear", scar, "--reason", "r")
        assert r.returncode != 0, "clear proceeded on dirty tree"
        _run(["git", "checkout", "--", "a.txt"], cwd=repo, check=True)
        r = _loto(repo, "clear", scar, "--reason", "acknowledged")
        assert r.returncode == 0, r.stderr
        touched = _git_out(repo, "diff-tree", "--no-commit-id",
                           "--name-only", "-r", "HEAD").strip()
        assert touched == "", "scar-clear commit touched files: " + touched
        body = _git_out(repo, "log", "-1", "--pretty=%B")
        assert "Loto-Scar-Reason:" in body and "Loto-Clear-Reason:" in body
        assert not os.listdir(os.path.join(repo, ".loto")), "scar not deleted"
        assert _loto(repo, "guard").returncode == 0
    finally:
        shutil.rmtree(repo)


def test_one_commit_per_session():
    repo = _mk_repo()
    try:
        _loto(repo, "open", "--intent", "check", "--files", "a.txt")
        _append(repo, "a.txt", "c1")
        _commit_all(repo, "c1")
        _append(repo, "a.txt", "c2")
        _commit_all(repo, "c2")
        _loto(repo, "test", "true")
        r = _loto(repo, "close")
        assert r.returncode != 0, "multi-commit session closed"
        assert "commits since open" in r.stderr
    finally:
        shutil.rmtree(repo)


CHECK_FNS = [test_open_never_dirties, test_close_deletes_tag,
             test_latest_test_wins, test_scope_enforced,
             test_scar_blocks_work, test_clear_is_empty_commit,
             test_one_commit_per_session]


# ---------- audit: reconcile the declared graph, no execution ----------

def _parse_block(path, block):
    """return list of {field: value} dicts, one per id, inside block fences."""
    with open(path) as f:
        text = f.read()
    m = re.search(rf"# === {block} ===\n(.*?)# === END {block} ===",
                  text, re.S)
    if not m:
        return []
    out = []
    for line in m.group(1).splitlines():
        line = line.lstrip("# ").rstrip()
        if line.startswith("id:"):
            out.append({"id": line[3:].strip()})
        elif out and ":" in line:
            k, v = line.split(":", 1)
            out[-1][k.strip()] = v.strip()
    return out


def _resolve_call(spec):
    """resolve a call: target to a callable without executing anything.
    only form: self::fn — a callable in the file that declared it.
    dotted import paths are refused: python imports execute module top
    level, and an audit that executes is not an audit."""
    if not spec.startswith("self::"):
        raise LookupError(f"only self::fn resolves without execution: {spec}")
    fn = globals().get(spec[len("self::"):])
    if not callable(fn):
        raise LookupError(f"not callable: {spec}")
    return fn


def _proves_targets(check):
    return [target.strip() for target in check.get("proves", "").split(",")
            if target.strip()]


def audit():
    contracts = {c["id"] for c in _parse_block(LOTO, "CONTRACTS")}
    checks = _parse_block(__file__, "CHECKS")
    fn_names = {f.__name__ for f in CHECK_FNS}
    ok = True
    resolved_fns = set()
    for c in sorted(contracts):
        by = [ch["id"] for ch in checks if c in _proves_targets(ch)]
        if by:
            print(f"OK   {c}  <-  {', '.join(by)}")
        else:
            ok = False
            print(f"GAP  {c}  has no CHECKS entry claiming to prove it")
    for ch in checks:
        targets = _proves_targets(ch)
        if not targets:
            ok = False
            print(f"GAP  {ch['id']} has no proves target")
        for target in targets:
            if target not in contracts:
                ok = False
                print(f"GAP  {ch['id']} claims unknown contract: {target}")
        try:
            fn = _resolve_call(ch.get("call", ""))
            resolved_fns.add(fn.__name__)
        except Exception as e:
            ok = False
            print(f"GAP  {ch['id']} call does not resolve: {e}")
    for fn in sorted(fn_names - resolved_fns):
        ok = False
        print(f"GAP  executable check {fn} has no resolving CHECKS declaration")
    print(f"\naudit: {len(contracts)} contracts, {len(checks)} checks, "
          + ("graph closed." if ok else "gaps above."))
    return 0 if ok else 1


def _requires_met(checks):
    """consume the requires: field — refuse to run what the host can't host."""
    need = set()
    for ch in checks:
        need.update(r.strip() for r in ch.get("requires", "").split(",") if r.strip())
    missing = []
    for r in sorted(need):
        if r == "posix_shell":
            if not os.path.exists("/bin/sh"):
                missing.append(r)
        elif shutil.which(r.replace("python3", sys.executable)
                          if r == "python3" else r) is None:
            missing.append(r)
    return missing


def _timeout_for(checks, fn_name):
    for ch in checks:
        if ch.get("call", "").endswith("::" + fn_name):
            try:
                return int(ch.get("timeout", TIMEOUT))
            except ValueError:
                return TIMEOUT
    return TIMEOUT


def main():
    if LOTO is None:
        print("cannot find repo_loto.py (set REPO_LOTO)", file=sys.stderr)
        return 2
    if "--audit" in sys.argv:
        return audit()
    checks = _parse_block(__file__, "CHECKS")
    missing = _requires_met(checks)
    if missing:
        print(f"requires unmet, refusing to run: {', '.join(missing)}",
              file=sys.stderr)
        return 2
    failures = 0
    for fn in CHECK_FNS:
        _ACTIVE_TIMEOUT[0] = _timeout_for(checks, fn.__name__)
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"FAIL  {fn.__name__}: {e}")
        except Exception as e:
            failures += 1
            print(f"ERROR {fn.__name__}: {type(e).__name__}: {e}")
        finally:
            _ACTIVE_TIMEOUT[0] = TIMEOUT
    print(f"\n{len(CHECK_FNS) - failures}/{len(CHECK_FNS)} checks passed.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
