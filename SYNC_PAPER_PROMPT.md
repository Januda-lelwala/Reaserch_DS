# Auto-Update Paper Workflow

> **Copy-paste this prompt to Claude Code** after pulling the latest repo changes.
> Each team member should run this after committing their work.

---

## Prompt for Claude Code

```
You are working on the research paper "Analysing the Economic Drivers of Underemployment in Sri Lanka".

The `current_latest_paper/` directory contains the latest LaTeX source and compiled PDF.

**Task:** Scan the repository for any new or modified analysis scripts, visualization outputs (Visualizations/*.png), and LaTeX tables (output/tables/*.tex) that are NOT yet reflected in `current_latest_paper/main.tex`. For each new contribution found:

1. Copy any new .png figures and .tex table files into `current_latest_paper/`
2. Add the appropriate \subsection, \input{}, and \includegraphics{} blocks into `main.tex` at the correct location (match the paper's section structure)
3. Update the abstract and conclusion if the new results change key statistics
4. Regenerate the `overleaf_source.zip` with all current files
5. List what was added/changed

Do NOT:
- Remove or modify existing sections written by other members
- Change citation keys or references.bib without confirmation
- Modify scripts or data files — only update the paper source

After updating, show a summary of changes made.
```

---

## Quick Usage

```bash
# 1. Pull latest
git pull origin main

# 2. Open Claude Code in the repo root
claude

# 3. Paste the prompt above (or save it and run):
#    cat SYNC_PAPER_PROMPT.md | claude
```

## Structure Convention

| Directory | Purpose |
|-----------|---------|
| `current_latest_paper/` | LaTeX source + compiled PDF + Overleaf ZIP |
| `current_latest_paper/overleaf_source.zip` | Ready to upload to Overleaf |
| `Visualizations/` | All figure .png files |
| `output/tables/` | All LaTeX table .tex files |
| `Kusal/` | Member 4 contribution summary |

## Member Workflow

1. Write your analysis script in repo root
2. Save figures to `Visualizations/`, tables to `output/tables/`
3. Commit and push your work
4. Run the Claude Code prompt above to sync the paper
5. Commit the updated `current_latest_paper/` directory
