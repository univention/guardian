# AI-generated documentation

This directory contains AI-generated project documentation.

If you're here to *read* the documentation, head over to [../index.md](../index.md).

This file is about how to *maintain* it.

## Regenerating the documentation

### BMAD Installation

The documentation was created using a skill from the [BMAD](https://docs.bmad-method.org) project.
To access it, you have to add the skill and workflow to the repository.
To keep the Guardian repository clean, those are located in a Git submodule.

Run the following commands from the repository root.

```shell
git submodule init
git submodule update
```

There are now files in the `_bmad` directory.

To install the BMAD code (skills), run one of two scripts, depending on the agent you're using.

- For OpenCode (and other agents like GitHub Copilot using `.agent/skills`) run `_bmad/setup_opencode`.
- For Claude Code run `_bmad/setup_claude`.
- You can run both if you use both.

### Run bmad-document-project

Then, start your agent (`opencode` or `claude`) and load the documentation skill:

OpenCode:

```text
Start the bmad-document-project skill.
```

Claude Code:

```text
/bmad-document-project
```

It'll tell you something like:

```text
● Hello Nubus Core team! I've activated the Document Project workflow.

Status check:
- No in-progress state file found (docs/project-scan-report.json) — no resume needed
- Existing documentation found at docs/index.md, last generated 2026-03-29
- Loaded persistent fact: docs/project-context.md (127 AI-optimized rules, last updated 2026-03-28)

Existing documentation summary:
- Monorepo with 5 parts (Management API, Authorization API, Guardian Lib, Authorization Client, Management UI)
- 14 generated docs covering architecture, API contracts, data models, state management, UI components
- Scan level: Exhaustive

───────────────────────────────────────────────────────────────────────────────────────────────────────────────
☐ Workflow mode

Existing documentation was generated 2026-03-29 (~6 weeks old). What would you like to do?

❯ 1. Re-scan entire project
   Full rescan — refreshes all generated docs against the current codebase (most thorough; takes longest).
2. Deep-dive into specific area
   Generate detailed exhaustive documentation for one feature/module/folder you choose.
3. Cancel
   Keep existing documentation as-is and exit the workflow.
4. Type something.
```

Choose `Re-scan entire project`.

Then, it'll ask about the scan depth:

```text
Choose your scan depth level for the full rescan:

❯ 1. Quick (2-5 min)
Pattern-based only — reads configs/manifests/README, uses glob/grep for everything else. Fast but shallow.
2. Deep (10-30 min)
   Reads files in critical directories based on project type. Comprehensive without being exhaustive. Best for brownfield PRD prep.
3. Exhaustive (30-120 min)
   Reads ALL source files (excludes node_modules/dist/build). Matches the depth of the existing 2026-03-29 docs. Slowest and most thorough.
4. Type something.
   ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
5. Chat about this
```

Choose `Exhaustive` scan.

The documentation process is structured as a 12-step workflow.
The skill guides you through it.

### Cleanup

The process will create a file `docs/project-scan-report.json` which you can safely delete
to keep the repo clean of all too obvious BMAD references.

In the same spirit, I manually removed the "created with BMAD" footer from all generated files.
It's up to you whether to leave that or remove it (or let an agent remove it).
You can even customize BMAD to change the docs template so that it won't contain the footer in the future.

Check [docs/index.md](../index.md) for references to `_bmad/output`, and remove them.
Usage of the `_bmad` submodule is optional.
So, there shouldn't be references to it in the index.

Please note that `bmad-document-project` originally created the Markdown files directly in `docs/`,
and I moved them to `docs/generated`.
While testing the above commands, the skill adapted automatically to the new location.
If in your session it doesn't, you may have to move the files manually afterward.

### Remove BMAD installation

If you don't need the BMAD skills anymore, run:

```shell
rm -f .agents/skills/bmad
rm -f .claude/skills/bmad-*

git submodule deinit _bmad
```
