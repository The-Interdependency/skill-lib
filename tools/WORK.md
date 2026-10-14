# Repository-owned work launcher

`tools/work.sh` is the parent menu for the canonical `tools/ai.sh` and Google
Cloud CLI running inside Ubuntu. `tools/install_ai.sh` installs **symlinks**,
not independent copies, for both commands. Git is the update path. The earlier
chat-only `~/work.sh` / Downloads copy is superseded by this repository source;
it is not an update source and this installer does not delete personal files.

## Install and update

From the Termux environment that already owns the working `ai.sh` / SSH setup,
with your existing skill-lib checkout on its release branch (`main`):

```bash
git -C "$HOME/skill-lib" pull --ff-only &&
bash "$HOME/skill-lib/tools/install_ai.sh"
```

A failed pull prevents installation. Review local changes or branch divergence;
do not use a hard reset to discard them. The installer validates both source
files before modifying command links, rejects directory targets and self-links,
and never downloads or installs dependencies. Keep the checkout in place: the
installed links reference it. A later pull updates the commands through those
links; rerunning the installer is safe and repairs missing links.

On Termux, the existing writable `$PREFIX/bin` is preferred. Otherwise the
installer uses `~/.local/bin`, or the explicit `A0_AI_BIN_DIR` override, and adds
one marked line to `A0_AI_PROFILE` (default `~/.profile`) only when necessary.
An existing non-directory command at a target path is replaced by a symlink;
preserve a custom command before explicitly installing over it. Outside Termux,
follow the installer's printed PATH command for the current shell.

Open the new menu after installation:

```bash
work.sh
```

Direct commands:

```bash
work.sh ai status
work.sh ai codex
work.sh cloud
work.sh ubuntu
work.sh login
work.sh gcloud projects list
```

`ai.sh` remains independently callable, with its current SSH configuration,
remote tmux layout, provider-key handling, and command overrides unchanged.
The parent resolves `ai.sh` beside its own real repository source, even when
called through the installed symlink. Stale PATH or home-directory copies,
including the former download's `WORK_AI` override, are not fallback authorities.

## Ubuntu and Google access

Requires local Bash, `readlink`, and the existing Ubuntu installation. On Termux,
Google actions enter `proot-distro login ubuntu`; `WORK_DISTRO` may select an
existing differently named **Ubuntu** alias. Inside Ubuntu they do not create a
nested proot session. The child verifies `/etc/os-release` and includes
`$HOME/google-cloud-sdk/bin` in PATH before running the command. An already
installed system-wide `gcloud` can still be found on the remaining PATH.

`work.sh cloud` runs `gcloud cloud-shell ssh`: Google Cloud Shell is distinct
from the `a0` VM reached by `ai.sh`. This selects the active Google account's
Cloud Shell, not a guessed project, VM, zone, or SSH account. The Google command
owns session startup, key handling, and any interactive authorization prompts.
No SSH trust bypass, quiet flag, credential transfer flag, or forced key
replacement is added by the wrapper.

`work.sh login` runs `gcloud auth login --no-launch-browser`. Open the printed
Google authorization URL in a trusted browser and return the resulting code to
the terminal, never to a chat. `work.sh setup` explicitly runs
`gcloud init --console-only`; this may change the active account/project.
`work.sh status` prints the canonical AI path and configured Google account and
project. It does **not** prove network connectivity, permissions, or readiness.

An explicit `work.sh gcloud ...` retains the requested subcommand's normal
permissions and effects, including possible mutations or billable operations.
Arguments and stdin are forwarded, not evaluated as shell source. The wrapper
has no privileged shell, automatic login, retry loop, or background poller.
Opening or quitting its menu invokes no agent or cloud tool.

Official command contracts consulted for this change:

- https://docs.cloud.google.com/sdk/gcloud/reference/cloud-shell/ssh
- https://docs.cloud.google.com/sdk/gcloud/reference/auth/login
- https://docs.cloud.google.com/sdk/gcloud/reference/init
- https://github.com/termux/proot-distro

## Failure, recovery, and rollback

Direct commands return the child's failure status. The interactive menu reports
a failed action and remains open. Fix the named dependency or authentication
problem before retrying explicitly. Missing Ubuntu or a missing canonical AI
source returns 127; a selected non-Ubuntu environment returns 126; invalid
launcher arguments return 2. A missing AI source does not block the cloud menu.

The installer's two symlink changes are not one atomic transaction. Rerun the
installer after an interruption. It does not change credentials, SSH trust,
Google configuration, or agent processes. To remove only the parent menu, remove
the installed `work.sh` symlink after confirming it points into this checkout;
`ai.sh` remains usable. To roll back source behavior, use a reviewed Git revert
through the same repository/update path, not an untracked replacement download.
Remove the marked profile line only when neither installed command needs it.

## Validation and hmmm

```bash
bash -n tools/work.sh && bash -n tools/install_ai.sh
python -m unittest discover -s tests -p 'test_work_launcher.py' -v
python -m unittest discover -s tests -p 'test_ai_launcher.py' -v
```

The new tests are offline routing/install regressions. They cover both Ubuntu
routing branches with test doubles, SDK PATH resolution, literal arguments and
stdin, stale-copy rejection, canonical symlink resolution, source updates through
installed links, missing/invalid inputs, repeat installation, profile idempotency,
directory/self-link refusal, and child failure without menu termination.
They do not prove the phone's Ubuntu/gcloud installation, live Google access,
SSH host trust, current VM readiness, provider quota, or successful phone-side
installation. Those remain `hmmm` until observed on the actual client. Existing
`ai.sh` SSH behavior is preserved, not newly certified by these wrapper tests.
