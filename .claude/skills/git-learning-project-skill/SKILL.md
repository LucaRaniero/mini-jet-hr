# Git Learning Project Skill

## Purpose
This skill enables Claude to manage Git versioning for learning projects with semantic commits, automatic learning tracking, and professional workflow management.

## When to Use This Skill
Trigger this skill when:
- User asks to "commit changes" or "push to git"
- User says "version this" or "save progress"
- User completes a User Story or feature
- User wants to "update learning journal"
- User mentions "git", "commit", "push", "branch"
- End of a coding session that should be saved

## Core Capabilities

### 1. Semantic Commit Creation
Generate commits following Conventional Commits specification with learning annotations:

```
<type>(<scope>): <subject> (US-XXX)

<body explaining what and why>

Learning notes:
- Key concept understood
- Pattern discovered
- Resource used

Tests: X passed, Coverage: Y%
```

**Types**: feat, fix, refactor, docs, style, test, chore, perf

### 2. Learning Progress Tracking
Automatically update:
- `PROGRESS.md` with completed tasks
- `learning-journal/week-X.md` with session summary
- Commit messages with learning insights

### 3. Branch Management
- Create feature branches for User Stories: `feature/US-XXX-description`
- Manage branch lifecycle (create, switch, merge)
- Keep branch naming consistent

### 4. Quality Checks
Before committing:
- Verify tests pass (if applicable)
- Check code formatting
- Ensure no sensitive data (API keys, passwords)
- Validate commit message format

## Workflow Steps

### Step 1: Analyze Changes
```bash
# Check what files changed
git status
git diff
```

**Claude should:**
- List all modified files
- Summarize changes in plain language
- Identify which User Story this relates to
- Determine appropriate commit type

### Step 2: Generate Commit Message
Based on changes, create structured commit message:

**Template:**
```
<type>(<scope>): <short description> (US-XXX)

- Detailed change 1
- Detailed change 2
- Detailed change 3

Learning notes:
- Concept/pattern learned
- Resource consulted
- Challenges overcome

[Optional: Tests: X passed, Coverage: Y%]
```

**Examples:**

```
feat(employees): implement employee list view with pagination (US-001)

- Add Employee Django model with core fields (name, email, role, hire_date)
- Create GET /api/employees/ endpoint with DRF ModelViewSet
- Implement pagination (20 items per page) and sorting
- Build EmployeeList.vue component using Composition API
- Add unit tests for model validation and API endpoint

Learning notes:
- Understood Django QuerySet optimization with select_related()
- Mastered DRF pagination classes and filters
- Learned Vue 3 Composition API with ref() and reactive()
- Discovered importance of database indexing for performance

Tests: 12 passed, Coverage: 85%
```

```
refactor(auth): extract JWT token logic into service layer (US-011)

- Create auth_service.py with token generation methods
- Move token validation from views to service
- Apply Single Responsibility Principle
- Improve testability through dependency injection

Learning notes:
- Deep dive into SOLID principles (SRP focus)
- Understood benefits of service layer pattern
- Learned JWT refresh token rotation best practices
- Resource: https://testdriven.io/blog/django-rest-auth/

Tests: 8 passed, Coverage: 92%
```

```
fix(contracts): prevent duplicate active contracts per employee

- Add database constraint for unique active contract
- Update contract activation logic to deactivate previous
- Create migration with data cleanup
- Enhance error messaging for better UX

Fixes: Issue #12
Related: US-005

Learning notes:
- Learned when to use DB constraints vs app-level validation
- Understood Django migrations: data vs schema migrations
- Discovered CheckConstraint for complex validation
```

### Step 3: Update Learning Documentation

**Before committing, update:**

**PROGRESS.md:**
```markdown
## Week X: [Current Topic]
- [x] US-XXX: [Description] ← Mark as done
  - Key takeaway: [What you learned]
  - Time spent: ~X hours
  
### Concepts mastered this week:
- [New concept from this commit]
```

**learning-journal/week-X.md:**
```markdown
### Session [Date] - [Duration]

**Focus**: US-XXX - [Description]

**What I built:**
- [Feature/component implemented]

**What I learned:**
- [Concept 1]: [Brief explanation]
- [Concept 2]: [Brief explanation]

**Challenges faced:**
- [Challenge]: [How you solved it]

**Resources used:**
- [Link/documentation]

**Next steps:**
- [ ] [What's next]
```

### Step 4: Execute Git Commands

```bash
# Stage changes
git add [specific files]  # NOT git add . - be explicit

# Commit with message
git commit -m "[generated message]"

# Push to remote (if appropriate)
git push origin [branch-name]
```

### Step 5: Provide Summary
Give user a clear summary:
```
✅ Committed: feat(employees): implement employee list view (US-001)

📝 Files changed:
- backend/employees/models.py
- backend/employees/serializers.py
- backend/employees/views.py
- frontend/src/components/EmployeeList.vue
- backend/employees/tests/test_api.py

📚 Learning docs updated:
- PROGRESS.md (US-001 marked complete)
- learning-journal/week-1.md (session notes added)

🔗 Ready to push to GitHub? (yes/no)
```

## Advanced Workflows

### Feature Branch Workflow

**Creating new feature:**
```bash
# From main/develop
git checkout -b feature/US-XXX-short-description

# Work on feature...

# When complete
git add [files]
git commit -m "[message]"
git push origin feature/US-XXX-short-description

# Create PR (manual on GitHub)
```

**Claude should:**
1. Ask which User Story user is starting
2. Generate appropriate branch name
3. Create branch and switch to it
4. Remind about PR when feature is done

### Multi-commit Feature

For large features (>100 lines), break into logical commits:

```bash
# Commit 1: Models
feat(employees): add Employee model and migrations (US-001)

# Commit 2: API
feat(employees): implement CRUD API endpoints (US-001)

# Commit 3: Frontend
feat(employees): build employee list UI component (US-001)

# Commit 4: Tests
test(employees): add comprehensive test coverage (US-001)
```

**Each commit:**
- Is atomic (works independently)
- Has clear purpose
- Includes learning notes

### Checkpoint Commits

For learning sessions, create checkpoint commits:

```bash
chore(learning): checkpoint - [topic] exploration

Saved progress on understanding [concept].
Not production-ready yet, experimental code.

Learning notes:
- Explored [topic]
- Tested [approach]
- Questions remaining: [list]

TODO:
- [ ] Refactor after understanding improves
- [ ] Add proper error handling
- [ ] Write tests
```

## Git Best Practices for This Project

### DO:
✅ Write commits in imperative mood ("Add feature" not "Added feature")
✅ Keep subject line under 50 characters
✅ Separate subject from body with blank line
✅ Reference User Story (US-XXX) in subject
✅ Include learning notes in every commit
✅ Update PROGRESS.md before committing
✅ Be explicit with `git add` (avoid `git add .`)
✅ Review changes with `git diff` before committing

### DON'T:
❌ Commit without understanding what changed
❌ Use generic messages like "fix stuff" or "updates"
❌ Commit commented-out code or TODOs without explanation
❌ Include secrets, API keys, or passwords
❌ Commit node_modules, __pycache__, .env files
❌ Skip learning notes (they're crucial!)
❌ Commit directly to main (use feature branches)

## Quality Checks Before Commit

### Pre-commit Checklist:
```python
def pre_commit_checks():
    checks = [
        "Tests pass? (if applicable)",
        "Code formatted? (black, prettier)",
        "No console.log or print() debug statements?",
        "No commented code without explanation?",
        "Secrets removed? (.env file used?)",
        "Learning notes written?",
        "PROGRESS.md updated?",
        "User Story reference included?",
    ]
    return all(check_passed(c) for c in checks)
```

Claude should run through this mentally and flag issues.

## Interactive Commit Flow

**Ideal user interaction:**

```
User: "I finished implementing the employee list, commit this"

Claude: 
"Great! Let me review what we've done.

📊 Changes detected:
- 5 files modified (3 backend, 2 frontend)
- ~250 lines added
- Tests included ✓

This appears to be US-001: Employee List View.

🤔 Before committing, let me ask:
1. Did the tests pass? 
2. Is there anything you want to add to the learning notes?
3. What was the most challenging part you overcame?

[User responds]

Perfect! Here's the commit I'll create:

```
feat(employees): implement employee list view with pagination (US-001)

[detailed description]

Learning notes:
- [based on user's answers]
```

Does this look good? (yes/edit/cancel)

[If yes]
✅ Committed successfully!
📝 Updated PROGRESS.md
📚 Added session to learning-journal/week-1.md

Would you like to push to GitHub now?
```

## Error Handling

### Common Issues:

**Merge conflicts:**
```bash
# Claude detects conflict
git status
# Show conflicting files
# Guide user through resolution
# Don't auto-resolve - teach instead
```

**Committed to wrong branch:**
```bash
# Undo last commit, keep changes
git reset HEAD~1

# Switch to correct branch
git checkout [correct-branch]

# Re-commit
```

**Forgot to add files:**
```bash
# Amend last commit
git add [forgotten-files]
git commit --amend --no-edit
```

## Integration with Learning Goals

### Weekly Review Commit
At end of week, create summary commit:

```
docs(learning): week X summary and reflection

Completed User Stories:
- US-001: Employee CRUD
- US-002: Authentication

Key learnings:
- Django ORM optimization
- Vue Composition API
- REST API design patterns

Challenges overcome:
- JWT token refresh mechanism
- N+1 query problem

Next week focus:
- Docker containerization
- AWS deployment basics

Hours logged: ~25h
Progress: On track for 8-week goal
```

## Repository Health Checks

Periodically check:
```bash
# Branch cleanup
git branch --merged  # Safe to delete
git branch -d [branch]

# Size check
git count-objects -vH

# Commit frequency
git log --since="1 week ago" --oneline | wc -l
```

Claude should suggest cleanups when needed.

## Example Session

```
User: "Let's commit my work on the employee API"

Claude:
"Sure! Let me analyze what we've built today.

🔍 Analyzing changes...

Files modified:
- backend/employees/models.py (+45 lines)
- backend/employees/serializers.py (+32 lines)
- backend/employees/views.py (+28 lines)
- backend/employees/tests/test_models.py (+67 lines)

This looks like US-001 (Employee CRUD). 

Summary of work:
✅ Created Employee model with validation
✅ Built DRF serializer with custom fields
✅ Implemented ViewSet with filtering
✅ Added comprehensive unit tests

🧪 Should I run the tests first? (Recommended)

[User: yes]

Running tests...
```bash
cd backend && pytest employees/tests/
```

✅ All 12 tests passed! Coverage: 87%

📝 Now, help me with learning notes. What was your biggest 'aha' moment today?

[User: "Understanding how Django ORM generates SQL queries"]

Perfect! Here's my proposed commit:

```
feat(employees): implement employee CRUD operations (US-001)

- Add Employee model with fields: name, email, role, hire_date, is_active
- Implement custom validators for email and hire_date
- Create EmployeeSerializer with read-only id field
- Build EmployeeViewSet with filtering by role and is_active
- Add comprehensive unit tests for model and API

Learning notes:
- Deep dive into Django ORM query generation (used django-debug-toolbar)
- Understood difference between select_related and prefetch_related
- Learned DRF serializer validation flow (field → object → save)
- Discovered importance of database indexes for filter performance

Tests: 12 passed, Coverage: 87%
```

Does this accurately capture your work? (yes/edit/cancel)

[User: yes]

✅ Committing...

Done! 

📋 Next steps:
1. Updated PROGRESS.md (US-001 marked complete)
2. Added session notes to learning-journal/week-1.md
3. Commit created on branch: feature/US-001-employee-crud

🚀 Ready to push to GitHub? This will make your work visible in your portfolio.

(yes/no/later)

[User: yes]

```bash
git push origin feature/US-001-employee-crud
```

✅ Pushed successfully!

🎯 Next: You can create a Pull Request on GitHub or continue with US-002.

Great work today! You've learned:
- Django ORM fundamentals
- DRF basics
- Test-driven development

Keep it up! 💪
```

## Tips for User

**When to commit:**
- After completing a logical unit of work
- End of coding session (even if incomplete)
- Before trying risky refactoring
- When switching contexts

**Commit frequency:**
- Small, focused commits > Large monolithic commits
- Aim for 2-5 commits per coding session
- Each commit should be reviewable in < 5 minutes

**Learning mindset:**
- Every commit is a learning artifact
- Commits = your technical diary
- Future you will thank present you for detailed notes
- Quality > Quantity

## Conclusion

This skill turns Git from a chore into a learning tool. Every commit documents not just code changes, but your growth as a developer.

**Remember:** 
The goal isn't perfect code on first try. The goal is to show:
1. Your thought process
2. Your learning ability  
3. Your professional discipline
4. Your growth over time

Your commit history will be a compelling story for Jet HR's CTO. 🚀
