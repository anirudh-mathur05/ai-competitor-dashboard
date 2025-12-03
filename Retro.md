# 📘 Retrospective — AI Competitor Dashboard Project

This retro captures the major workflow issue we encountered and the corrective actions taken to permanently stabilize development.

---

## 🧩 Issue: Local–GitHub Drift + Broken File State

We spent a significant amount of time debugging issues caused by the local `app.py` diverging from the GitHub version. This created repeated cycles of:

- Syntax errors
- Indentation errors
- Duplicate/unwanted blocks of code
- Git refusing pulls due to uncommitted changes
- Confusion between local state vs GitHub state
- Streamlit continuously crashing with misleading error messages

The root cause was making code edits in **multiple locations**, often combined with unsafe multi-line terminal editing (sed) which corrupted Python indentation.

---

## 🔍 Root Causes

1. Editing code **both locally and in GitHub**, causing drift.
2. Use of `sed` for multi-line patches in Python (unsafe).
3. No CI pipeline to detect syntax errors early.
4. Repo structure separated backend + dashboard in different folders, increasing confusion.
5. No enforcement of Git pull before local runs.
6. No protections against accidental stray code blocks or indentation mismatch.

---

## 🎯 Impact

- Delivery slowed significantly.
- Multiple rework cycles.
- Increased cognitive load and frustration.
- Reduced confidence in local runs.
- Time spent on debugging instead of forward progress on AI features.

---

## ✔️ What We Are Changing Going Forward

### 1. **GitHub-only code edits (single source of truth)**
All code will be edited inside GitHub UI or via PRs.
Local environment is **read-only**: only `git pull` + `streamlit run`.

### 2. **No more multi-line edits in terminal**
`seds` and multi-line patches are banned.  
All changes go through GitHub to avoid indentation issues.

### 3. **Add CI Pipeline**
CI checks will enforce:
- Syntax correctness
- Linting
- Import errors
- Test execution (future)

Bad code will never merge again.

### 4. **Unified Repo Structure**
Move backend + dashboard into a single repo structure:

Cleaner imports, cleaner deployment, less confusion.

### 5. **Small, Sequenced Changes Only**
One patch → validate → pull → run.
No batch edits that risk breaking the environment.

### 6. **Better Error Observability**
We will add logging + clearer error responses to avoid misleading failure messages.

---

## 🚀 Expected Outcomes

- Zero drift between local + GitHub.
- No more indentation/syntax surprises.
- Predictable and stable development.
- Higher velocity with fewer interruptions.
- Better quality and portfolio polish.
- CI ensures production-grade reliability.

---

This retro will guide all future development steps.
