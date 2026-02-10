# Git Learning Project Skill

A Claude skill for managing Git versioning in learning projects with semantic commits, automatic learning tracking, and professional workflow management.

## What This Skill Does

This skill transforms Claude into your Git mentor, helping you:

✅ **Create professional semantic commits** with learning annotations  
✅ **Automatically update learning documentation** (PROGRESS.md, learning journal)  
✅ **Manage feature branches** for User Stories  
✅ **Run quality checks** before committing  
✅ **Track your learning progress** through Git history  
✅ **Follow best practices** for enterprise-ready commits  

## Perfect For

- Learning projects (like Mini Jet HR)
- Portfolio development
- Career transition projects
- Bootcamp students
- Anyone documenting their learning journey through code

## Installation

### Option 1: Claude Desktop / Claude Code (Recommended)

1. **Copy the skill folder** to your skills directory:
   ```bash
   # MacOS/Linux
   cp -r git-learning-project-skill ~/.claude/skills/
   
   # Windows
   xcopy git-learning-project-skill %USERPROFILE%\.claude\skills\ /E /I
   ```

2. **Verify installation**:
   ```bash
   # Check if skill is present
   ls ~/.claude/skills/git-learning-project-skill/
   ```

3. **Restart Claude Code** (if running)

### Option 2: Project-Specific Installation

Copy the skill to your project's `.claude/skills/` directory:

```bash
cd mini-jet-hr
mkdir -p .claude/skills
cp -r /path/to/git-learning-project-skill .claude/skills/
```

Then reference it in your `.claude/CLAUDE.md`:

```markdown
## Active Skills
- git-learning-project: For all Git operations and learning tracking
```

## Usage

Once installed, the skill activates automatically when you:

### Trigger Phrases

- "Commit these changes"
- "Save my progress"
- "Push to GitHub"
- "Create a feature branch for US-XXX"
- "I finished US-001, let's commit"
- "Update my learning journal"
- "Version this work"

### Example Workflow

```
You: "I just finished implementing the employee list API. Let's commit this."

Claude: [Activates git-learning-project skill]

🔍 Analyzing changes...

Files modified:
- backend/employees/models.py (+45)
- backend/employees/serializers.py (+32)
- backend/employees/views.py (+28)
- backend/employees/tests/test_api.py (+67)

This looks like US-001 (Employee CRUD).

🧪 Should I run tests first? (Recommended)

[You: yes]

✅ 12 tests passed! Coverage: 87%

📝 What was your biggest learning from this session?

[You: Understanding Django ORM query optimization]

Perfect! Here's my proposed commit:

```
feat(employees): implement employee CRUD API (US-001)

- Add Employee model with validation
- Create DRF serializer and viewset
- Implement filtering and pagination
- Add comprehensive unit tests

Learning notes:
- Mastered Django ORM select_related for query optimization
- Understood DRF serializer validation flow
- Learned importance of database indexing

Tests: 12 passed, Coverage: 87%
```

Does this look good? (yes/edit/cancel)
```

## What Gets Automated

### 1. Commit Message Generation

The skill creates structured commits following this template:

```
<type>(<scope>): <description> (US-XXX)

- Detailed change 1
- Detailed change 2

Learning notes:
- Key concept learned
- Pattern discovered
- Challenge overcome

Tests: X passed, Coverage: Y%
```

### 2. Learning Documentation Updates

Automatically updates:

**PROGRESS.md:**
```markdown
## Week X
- [x] US-001: Employee CRUD ← Marked complete
  - Key takeaway: Django ORM optimization
  - Time: ~4 hours
```

**learning-journal/week-X.md:**
```markdown
### Session [Date]
**Focus**: US-001 - Employee API
**Learned**: Django ORM, DRF basics
**Challenges**: N+1 query problem
**Resources**: Django docs, DRF tutorial
```

### 3. Branch Management

Creates and manages feature branches:
```bash
feature/US-001-employee-crud
feature/US-002-authentication
feature/US-003-contract-management
```

### 4. Pre-Commit Quality Checks

Before committing, verifies:
- Tests pass (if applicable)
- No debug statements
- No secrets/API keys
- Code formatting
- Learning notes included

## Configuration

### Customize for Your Project

Edit the skill's `SKILL.md` to adjust:

**Commit template:**
```markdown
## Your Custom Template

feat(<scope>): <description>

[Your custom fields]

Learning: [Your tracking method]
```

**Branch naming:**
```markdown
## Branch Convention
feature/[prefix]-[description]
bugfix/[description]
experiment/[topic]
```

**Learning tracking:**
```markdown
## Tracking Files
- PROGRESS.md
- learning-journal/week-X.md
- .claude/LEARNING_LOG.md  # Optional
```

## Advanced Usage

### Multi-Commit Features

For large features, the skill helps break work into logical commits:

```bash
feat(employees): add Employee model (US-001)
feat(employees): implement API endpoints (US-001)
feat(employees): build frontend list view (US-001)
test(employees): add test coverage (US-001)
```

### Checkpoint Commits

During exploration/learning:

```bash
chore(learning): checkpoint - Django ORM exploration

Experimenting with query optimization.
Not production-ready, for learning purposes.

TODO:
- [ ] Refactor after understanding improves
- [ ] Add error handling
```

### Weekly Review Commits

End-of-week summary:

```bash
docs(learning): week 1 summary

Completed: US-001, US-002
Learned: Django basics, DRF, Vue components
Hours: ~20h
Next: Docker, AWS basics
```

## Best Practices

### DO:
✅ Let the skill guide you through commits  
✅ Answer learning reflection questions honestly  
✅ Review generated commit messages before accepting  
✅ Use feature branches for User Stories  
✅ Commit frequently (small, focused commits)  
✅ Include what you learned in every commit  

### DON'T:
❌ Skip quality checks  
❌ Commit without understanding changes  
❌ Use generic messages ("fix stuff")  
❌ Commit secrets or sensitive data  
❌ Ignore the skill's suggestions  

## Integration with Other Tools

### With GitHub Actions

The skill prepares commits that work well with CI/CD:

```yaml
# .github/workflows/learning-progress.yml
on: [push]
jobs:
  track-progress:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Extract Learning Notes
        run: git log --grep="Learning notes" --format="%B" -1
```

### With Learning Dashboards

Export your learning data:

```bash
# Extract all learning notes from commits
git log --all --grep="Learning notes" --format="%H|%an|%ad|%s|%b" > learning-export.csv
```

## Troubleshooting

### Skill Not Activating?

1. **Check installation path:**
   ```bash
   ls ~/.claude/skills/git-learning-project-skill/SKILL.md
   ```

2. **Verify trigger phrases:**
   Use explicit phrases like "commit these changes" instead of vague "save this"

3. **Restart Claude Code:**
   Skills are loaded at startup

### Commit Message Too Long?

The skill might generate verbose messages. You can say:
- "Make it more concise"
- "Shorter version please"
- "Just the essentials"

### Wrong Branch?

```bash
# Undo last commit, keep changes
git reset HEAD~1

# Switch branch
git checkout feature/US-XXX

# Re-commit with skill
[Ask Claude to commit again]
```

## Examples from Real Projects

### Example 1: Feature Implementation

```
User: "Done with employee list, commit it"

Commit:
feat(employees): implement paginated employee list (US-001)

- Add Employee model (name, email, role, hire_date)
- Create REST API with DRF ModelViewSet
- Implement pagination (20/page) and sorting
- Build Vue component with Composition API
- Add unit tests (12 tests, 87% coverage)

Learning notes:
- Understood Django QuerySet lazy evaluation
- Mastered DRF serializer nested relations
- Learned Vue reactivity with ref() and computed()
- Discovered django-debug-toolbar for query analysis

Performance: List endpoint <100ms with 1000+ records
```

### Example 2: Bug Fix

```
User: "Fixed that authentication bug, commit"

Commit:
fix(auth): resolve token refresh race condition

- Add mutex lock around token refresh logic
- Implement exponential backoff for retries
- Update frontend to handle 401 with retry
- Add integration test for concurrent requests

Related: Issue #23
Fixes: US-011

Learning notes:
- Understood race conditions in async operations
- Learned about token bucket algorithm
- Discovered Python's threading.Lock for synchronization
- Resource: Real Python - Thread Synchronization

Tests: 8 new tests, all passing
```

## Community & Support

- **Issues**: Report bugs or request features on GitHub
- **Discussions**: Share your learning progress and tips
- **Examples**: See real commits from Mini Jet HR project

## Roadmap

Future enhancements:
- [ ] AI-powered commit message suggestions
- [ ] Learning analytics dashboard
- [ ] Integration with notion/linear for issue tracking
- [ ] Automatic changelog generation
- [ ] Learning milestone badges

## License

MIT License - Free to use and modify for your learning projects.

---

**Remember:** Good commit history is not just about code—it's the story of your learning journey. Make it compelling! 🚀

## Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│  Git Learning Project Skill - Quick Commands       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  "Commit these changes"                             │
│  → Interactive commit with learning notes           │
│                                                     │
│  "Create branch for US-XXX"                         │
│  → feature/US-XXX-description                       │
│                                                     │
│  "Push to GitHub"                                   │
│  → Push with confirmation                           │
│                                                     │
│  "Update learning journal"                          │
│  → Add session notes to journal                     │
│                                                     │
│  "Weekly summary commit"                            │
│  → End-of-week reflection commit                    │
│                                                     │
└─────────────────────────────────────────────────────┘
```
