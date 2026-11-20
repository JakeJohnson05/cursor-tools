# cursor-tools

Utility scripts for maintaining Cursor editor state.

---

## clean-cursor-diffs.py

Removes stale pending inline diff rows from Cursor's global database (`state.vscdb`) where the referenced file no longer exists on disk.

### Background

Cursor persists pending "Keep / Reject" diffs in a SQLite database. When files are deleted (e.g. after removing a git worktree), those rows become unresolvable — the "Keep all changes" button silently no-ops and the ghost tab reappears on every launch.

This script finds and deletes those stale rows, leaving any diffs that reference files still on disk untouched.

### Requirements

- Python 3.6+
- Cursor installed on macOS (default path assumed)

### Usage

**Always quit Cursor fully before running (`Cmd+Q`).**

Preview what would be deleted without making any changes:

```sh
python3 clean-cursor-diffs.py --dry-run
```

Delete all stale rows:

```sh
python3 clean-cursor-diffs.py
```

### Database location

```
~/Library/Application Support/Cursor/User/globalStorage/state.vscdb
```

Table: `cursorDiskKV`, keys matching `inlineDiff:<workspaceHash>:<diffId>`
