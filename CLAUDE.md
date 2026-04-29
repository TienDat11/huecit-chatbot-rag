# CLAUDE.md — Git Workflow Rules for HueCIT Chatbot RAG

> **MANDATORY**: This file defines Git workflow rules that MUST be followed by ANY Claude Code session, ANY model, ANY conversation. These rules are non-negotiable and apply to all development work.

---

## Git Branching Strategy

This project follows a **modified GitFlow** branching strategy optimized for enterprise reliability and clean commit history.

### Branch Structure

```
main (production)
  ↑
  └── develop (integration)
        ↑
        ├── feature/A-* (Epic A features)
        ├── feature/B-* (Epic B features)
        ├── feature/C-* (Epic C features)
        ├── feature/D-* (Epic D features)
        ├── feature/E-* (Epic E features)
        └── feature/F-* (Epic F features)
```

### Branch Types

| Branch | Purpose | Lifetime | Naming |
|--------|---------|----------|--------|
| `main` | Production-ready code | Permanent | `main` |
| `develop` | Integration branch | Permanent | `develop` |
| `feature/*` | Single feature/issue | Short (1-3 days) | `feature/<epic>-<issue>-<desc>` |
| `hotfix/*` | Urgent production fix | Very short | `hotfix/<issue>-<desc>` |

---

## ⛔ Mandatory Git Rules

### Rule 1: NEVER Commit Directly to `main`

```
❌ WRONG: git checkout main && git commit -m "..."
✅ RIGHT: git checkout develop && git checkout -b feature/...
```

**Rationale**: `main` is sacred. It only receives code from `develop` during EPIC releases.

### Rule 2: Feature Branches Come FROM `develop`, Return TO `develop`

```
# Start a feature
git checkout develop
git pull origin develop
git checkout -b feature/A1-repo-structure

# Work on the feature (max 2 meaningful commits)
git add <files>
git commit -m "feat(A1): add repository structure"

# Finish feature - merge back to develop
git checkout develop
git pull origin develop
git merge --no-ff feature/A1-repo-structure
# If conflicts occur, resolve them, then:
git merge --continue  # This creates 1 merge commit
```

### Rule 3: Maximum 3 Commits Per Branch (Including Merge)

**Strict limit**: A feature branch must have at most **3 commits**:
- Commit 1: Primary work commit
- Commit 2: Secondary/fixup commit (if needed)
- Commit 3: Merge commit (from `git merge --continue`)

**Before merging to `develop`**, if you have more commits:
```bash
# Squash commits down to 1-2 meaningful commits
git checkout feature/A1-repo-structure
git rebase -i HEAD~N  # Interactive rebase to squash
# OR use reset and re-commit:
git reset --soft HEAD~N
git commit -m "feat(A1): comprehensive change description"
```

### Rule 4: No Rebase on Shared Branches

```
❌ NEVER: git rebase develop (when develop is shared)
❌ NEVER: git rebase main
✅ SAFE: git rebase -i HEAD~N (on your local feature branch only)
```

**Rationale**: Rebase rewrites history. On shared branches, this causes chaos. Use merge instead.

### Rule 5: Merge to `develop` Only After Squashing

When merging to `develop`:

```bash
# Step 1: Ensure your branch has clean commits (max 2 non-merge commits)
git checkout feature/A1-repo-structure
git log --oneline -5  # Review your commits

# Step 2: If commits are messy, squash first
# Option A: Interactive rebase (local cleanup)
git rebase -i HEAD~N

# Option B: Soft reset and re-commit
git reset --soft HEAD~N
git commit -m "feat(A1): complete description of all changes"

# Step 3: Merge to develop
git checkout develop
git pull origin develop
git merge --no-ff feature/A1-repo-structure

# Step 4: Resolve conflicts if any
# ... resolve conflicts ...
git add <resolved-files>
git merge --continue  # Creates merge commit (commit #3)

# Step 5: Push
git push origin develop
```

### Rule 6: Linear Branching Only

```
✅ ALLOWED: develop → feature/A1-xxx (linear, one level)
❌ FORBIDDEN: feature/A1-xxx → feature/A1-yyy (branch from branch)
❌ FORBIDDEN: feature/A1-xxx → feature/sub-xxx (nested branches)
```

**Rationale**: Nested branches create merge hell. Always branch from `develop`, always merge back to `develop`.

### Rule 7: Merge to `main` Only at EPIC Release

```bash
# When an EPIC is complete and tested on develop:
git checkout main
git pull origin main
git merge --no-ff develop -m "release: EPIC A complete"
git tag -a v0.1.0 -m "EPIC A - Setup & Governance"
git push origin main --tags
```

---

## Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | When to use |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code refactoring |
| `docs` | Documentation |
| `test` | Adding/updating tests |
| `chore` | Build/tooling changes |
| `perf` | Performance improvement |
| `style` | Code style (formatting) |

### Scopes

Use Epic identifier: `A`, `B`, `C`, `D`, `E`, `F` or module name.

### Examples

```bash
git commit -m "feat(A1): add repository structure"
git commit -m "fix(C3): resolve token overlap in chunker"
git commit -m "docs(setup): update REPO_STRUCTURE.md"
git commit -m "test(D2): add OCR preprocessing tests"
```

---

## Complete Workflow Example

### Starting a New Feature

```bash
# 1. Ensure develop is up-to-date
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/A1-repo-structure

# 3. Work on the feature
# ... make changes ...
git add <files>
git commit -m "feat(A1): add directory structure"

# 4. If more changes needed, add second commit
# ... more changes ...
git add <files>
git commit -m "feat(A1): add configuration files"

# 5. Ready to merge - review commits
git log --oneline -3
# Should see max 2 commits

# 6. If too many commits, squash:
git rebase -i HEAD~N  # Squash into meaningful commits

# 7. Merge to develop
git checkout develop
git pull origin develop
git merge --no-ff feature/A1-repo-structure

# 8. Resolve conflicts if any
# ... resolve ...
git add <resolved-files>
git merge --continue

# 9. Push
git push origin develop

# 10. Delete feature branch
git branch -d feature/A1-repo-structure
```

### Releasing an EPIC

```bash
# 1. Ensure all features merged to develop
git checkout develop
git pull origin develop

# 2. Run full test suite
make check
make test

# 3. Merge to main
git checkout main
git pull origin main
git merge --no-ff develop -m "release: EPIC A - Setup & Governance"

# 4. Tag the release
git tag -a v0.1.0 -m "EPIC A - Setup & Governance complete"

# 5. Push
git push origin main --tags

# 6. Announce release
gh release create v0.1.0 --title "EPIC A Release" --notes "..."
```

---

## Hotfix Workflow

For urgent production fixes:

```bash
# 1. Branch from main (NOT develop)
git checkout main
git pull origin main
git checkout -b hotfix/A1-critical-fix

# 2. Fix and commit
git add <files>
git commit -m "fix(A1): critical security patch"

# 3. Merge to main
git checkout main
git merge --no-ff hotfix/A1-critical-fix

# 4. Back-merge to develop
git checkout develop
git merge --no-ff main

# 5. Push both
git push origin main
git push origin develop

# 6. Tag hotfix
git tag -a v0.1.1 -m "Hotfix: critical fix"
git push origin --tags
```

---

## Branch Protection Rules

### `main` Branch
- ✅ Required: Pull request reviews
- ✅ Required: Status checks pass
- ✅ Required: Branch is up-to-date
- ❌ Forbidden: Force push
- ❌ Forbidden: Direct commits

### `develop` Branch
- ✅ Required: No rebase
- ✅ Required: Squashed commits before merge
- ⚠️ Caution: Merge commits allowed (from `git merge --continue`)

---

## Quick Reference

| Action | Command |
|--------|---------|
| Start feature | `git checkout develop && git checkout -b feature/X-y` |
| Check commits | `git log --oneline -5` |
| Squash N commits | `git rebase -i HEAD~N` or `git reset --soft HEAD~N` |
| Merge to develop | `git checkout develop && git merge --no-ff feature/X-y` |
| Merge to main | `git checkout main && git merge --no-ff develop` |
| Tag release | `git tag -a v0.X.0 -m "Release message"` |

---

## Why These Rules Exist

1. **Never commit to `main`**: Protects production from accidental breaks
2. **Branch from `develop` only**: Prevents merge conflicts from nested branches
3. **Max 3 commits**: Keeps history clean and understandable
4. **No rebase on shared branches**: Prevents history conflicts for teammates
5. **Squash before merge**: Clean history on `develop` for easy bisect/revert
6. **Linear branching**: Simpler mental model, easier debugging
7. **EPIC releases only to `main`**: Stable production at all times

---

## Enforcement

These rules are enforced through:
1. **Pre-commit hooks**: Format and lint checks
2. **GitHub Actions**: CI/CD pipeline validation
3. **Branch protection**: GitHub settings prevent direct commits to `main`
4. **Code review**: PR templates enforce workflow compliance
5. **This CLAUDE.md file**: All AI sessions must follow these rules

---

## References

- [GitFlow Original Paper](https://nvie.com/posts/a-successful-git-branching-model/)
- [Atlassian GitFlow Tutorial](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)
- [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow)
- [Trunk-Based Development](https://trunkbaseddevelopment.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)