# Example: Using Git Learning Skill in Mini Jet HR

This document shows real examples of how to use the Git Learning Skill in your Mini Jet HR project.

## Scenario 1: First Commit - Project Setup

**You say:**
```
"I've setup the project structure. Let's make the first commit."
```

**Claude responds:**
```
Great! Let me help you create a professional initial commit.

🔍 Analyzing project setup...

Files to commit:
- .claude/CLAUDE.md (project manifesto)
- .claude/LEARNING_MODE.md (learning configuration)
- .claude/PROGRESS.md (progress tracker)
- docs/USER_STORIES.md (feature specifications)
- docs/PROJECT_BRIEF.md (project overview)
- learning-journal/week-1.md (learning diary)
- .gitignore
- README.md
- .gitmessage (commit template)

This is your project initialization. Here's my proposed commit:

```
chore: initial project setup with learning framework

Setup complete Mini Jet HR learning project structure:
- Configure Claude Code as senior mentor
- Define 15 user stories (MVP scope)
- Create learning tracking system
- Setup git workflow with semantic commits

Project goals:
- Learn Django/Vue/Docker/AWS stack
- Build HR automation platform
- Prepare for Jet HR Software Engineer role

Learning approach:
- AI-assisted learning (Claude as mentor)
- Production-ready code from day 1
- Document every concept learned
- 8-week timeline to completion

Initial structure:
- .claude/ - AI collaboration config
- docs/ - Project documentation
- learning-journal/ - Weekly progress tracking

Ready to start Week 1: Django fundamentals 🚀
```

Does this capture your project launch? (yes/edit/cancel)
```

**You:** "yes"

**Claude executes:**
```bash
git add .claude/ docs/ learning-journal/ .gitignore README.md .gitmessage
git commit -F /tmp/commit-msg.txt
git push origin main
```

**Result:**
```
✅ First commit created!
📋 Learning framework established
🚀 Ready to start coding

Next step: Create feature branch for US-001 (Employee CRUD)

Would you like me to create it now?
```

---

## Scenario 2: Implementing User Story

**You say:**
```
"I've implemented the Employee model and API. Ready to commit."
```

**Claude responds:**
```
Excellent! Let's commit your first feature.

🔍 Analyzing implementation...

Files changed:
✅ backend/employees/models.py (new, 78 lines)
✅ backend/employees/serializers.py (new, 45 lines)
✅ backend/employees/views.py (new, 32 lines)
✅ backend/employees/urls.py (new, 12 lines)
✅ backend/employees/tests/test_models.py (new, 89 lines)
✅ backend/employees/tests/test_api.py (new, 112 lines)

Total: ~368 lines of production code + tests

This implements US-001: Employee CRUD Operations

🧪 Running tests first...
```bash
cd backend && python manage.py test employees
```

✅ Creating test database...
✅ Running 18 tests...
✅ All tests passed! 

Coverage:
- employees/models.py: 95%
- employees/serializers.py: 88%
- employees/views.py: 91%
- Overall: 91%

📚 Learning reflection time!

1. What was the most challenging part of this implementation?
```

**You:** "Understanding Django ORM relationships and how to optimize queries"

**Claude:**
```
2. What resources helped you the most?
```

**You:** "Django docs and your explanations of select_related"

**Claude:**
```
3. What would you do differently next time?
```

**You:** "Write tests first (TDD approach)"

**Claude:**
```
Perfect! Here's your commit:

```
feat(employees): implement employee CRUD with REST API (US-001)

Backend implementation for employee management system.

Models:
- Employee model with fields: name, email, role, hire_date, is_active
- Custom validators for email uniqueness and hire_date
- Soft delete support with is_active flag
- __str__ method for admin interface

API:
- EmployeeViewSet with full CRUD operations
- Filtering by role and is_active status
- Ordering by name and hire_date
- Pagination (20 items per page)
- Custom permission checks for sensitive operations

Serializers:
- EmployeeSerializer with all fields
- EmployeeListSerializer (optimized for list view)
- Nested department serialization (read-only)

Tests:
- Model validation tests (8 tests)
- API endpoint tests (10 tests)
- Edge cases covered (invalid data, permissions)

Learning notes:
- Mastered Django ORM relationship optimization with select_related()
- Understood difference between select_related (ForeignKey) and prefetch_related (ManyToMany)
- Learned DRF viewset customization and action decorators
- Discovered importance of database indexing on frequently filtered fields
- Implemented TDD approach (will use from next US)
- Resources: Django ORM docs, DRF viewset docs, your guidance on query optimization

Performance:
- List endpoint: <100ms with 1000 records
- Detail endpoint: <50ms
- N+1 query problem solved with select_related

Next steps:
- Add employee photo upload (US-001 enhancement)
- Implement Contract model (US-005)

Tests: 18 passed, 0 failed, Coverage: 91%
```

This is a comprehensive commit showing:
✅ What you built (detailed breakdown)
✅ What you learned (optimization techniques)
✅ What you'll improve (TDD approach)
✅ Performance metrics
✅ Test coverage

Ready to commit? (yes/edit/cancel)
```

**You:** "yes"

**Claude:**
```bash
git add backend/employees/
git commit -F /tmp/commit-msg.txt

# Update learning docs
echo "- [x] US-001: Employee CRUD (91% coverage, 18 tests)" >> .claude/PROGRESS.md
```

**Result:**
```
✅ Committed: feat(employees): implement employee CRUD (US-001)

📝 Updated files:
- Committed 6 new files (~368 lines)
- Updated PROGRESS.md (US-001 marked complete)
- Updated learning-journal/week-1.md

🎯 Achievement unlocked: First feature complete!

Summary of progress:
Week 1, Day 3
- User Stories completed: 1/15 (6.7%)
- Tests written: 18
- Code coverage: 91%
- Concepts mastered: Django ORM, DRF basics

🚀 Ready to push to GitHub?
Your commit history will show professional, well-documented work!

(yes/no/later)
```

---

## Scenario 3: Bug Fix During Development

**You say:**
```
"Found a bug in employee validation, fixed it. Quick commit."
```

**Claude responds:**
```
Good catch! Let me help document this bug fix properly.

🔍 Analyzing fix...

Files changed:
- backend/employees/models.py (2 lines modified)
- backend/employees/tests/test_models.py (1 test added)

What was the bug specifically?
```

**You:** "Email validation wasn't case-insensitive, allowing duplicates like john@example.com and JOHN@example.com"

**Claude:**
```
Ah, classic case sensitivity issue! Here's the commit:

```
fix(employees): make email validation case-insensitive

Bug: Email uniqueness check was case-sensitive, allowing
duplicate emails with different casing (john@test.com vs JOHN@test.com).

Fix:
- Override save() method to lowercase email before saving
- Add database constraint for lowercase email uniqueness
- Create migration to fix existing data

Impact: Prevents duplicate user accounts

Learning notes:
- Learned about database collation and case sensitivity
- Understood when to use save() override vs clean() method
- Discovered Django's migrations can include data transformations
- Best practice: normalize emails at model level, not just form level

Tests: Added test_email_case_insensitive (now 19 tests total)
```

This fix will prevent production issues! Good debugging.

Commit now? (yes/edit/cancel)
```

---

## Scenario 4: Refactoring Code

**You say:**
```
"I refactored the employee API to use a service layer. Commit this."
```

**Claude responds:**
```
Great architectural improvement! This shows maturity.

🔍 Analyzing refactoring...

Files changed:
- backend/employees/services.py (new, 145 lines)
- backend/employees/views.py (modified, -67 lines)
- backend/employees/tests/test_services.py (new, 89 lines)

Code moved from views to services layer.

Why did you decide to refactor this?
```

**You:** "Views were getting too complex. Service layer makes it more testable and follows SOLID principles."

**Claude:**
```
Excellent reasoning! Here's your commit:

```
refactor(employees): extract business logic to service layer

Architectural improvement following Single Responsibility Principle.

Changes:
- Create EmployeeService with business logic methods:
  * create_employee()
  * update_employee()
  * deactivate_employee()
  * reactivate_employee()
  * bulk_import_employees()
- Slim down views to handle only HTTP concerns
- Move validation logic to service layer
- Improve error handling with custom exceptions

Benefits:
- Views now <50 lines (was 150+ lines)
- Business logic easily testable without HTTP layer
- Reusable service methods for management commands
- Better separation of concerns (SOLID)

Learning notes:
- Deep dive into SOLID principles (Single Responsibility focus)
- Understood benefits of service layer pattern in Django
- Learned when to use this pattern (complex business logic)
- Discovered dependency injection for better testability
- Resource: "Two Scoops of Django" - service layer chapter

Code quality:
- Reduced cyclomatic complexity of views from 12 to 4
- Service layer test coverage: 94%
- No changes to API contracts (backward compatible)

Tests: 23 total (4 new service tests), all passing
```

This refactoring makes your codebase production-ready! 🎯

(yes/edit/cancel)
```

---

## Scenario 5: End of Week Summary

**You say:**
```
"End of week 1. Let's create a summary commit."
```

**Claude responds:**
```
Great idea! Weekly summaries are invaluable for tracking progress.

Let me review your week...

📊 Week 1 Statistics:
- Commits: 12
- User Stories completed: 2/15 (US-001, US-002)
- Files created: 23
- Lines of code: ~1,200
- Tests written: 34
- Test coverage: 89%
- Hours logged: ~22h

🎓 Key learnings this week:
1. Django ORM optimization (select_related, prefetch_related)
2. DRF viewsets and serializers
3. Service layer pattern
4. Test-driven development basics
5. Database indexing strategies

💪 Challenges overcome:
- N+1 query problem in employee list
- Email case-sensitivity bug
- Complex serializer nesting

📚 Resources used:
- Django documentation (ORM section)
- DRF official tutorial
- Two Scoops of Django (service layer)
- Your guidance on architecture patterns

Here's your weekly summary commit:

```
docs(learning): week 1 summary - Django fundamentals

Week 1 (Feb 1-7, 2025) - Django & DRF Basics

Completed User Stories:
✅ US-001: Employee CRUD operations
✅ US-002: Authentication setup (JWT)

Technical achievements:
- Built complete employee management API
- Implemented JWT authentication
- Created 34 unit tests (89% coverage)
- Refactored to service layer pattern
- Setup CI/CD with GitHub Actions

Key learnings:
1. Django ORM:
   - Query optimization techniques
   - N+1 problem and solutions
   - Database indexing strategies
   
2. Django REST Framework:
   - ViewSets and Routers
   - Serializer customization
   - Pagination and filtering
   
3. Architecture:
   - Service layer pattern
   - SOLID principles in practice
   - Separation of concerns

4. Testing:
   - pytest and pytest-django
   - Test fixtures and factories
   - API testing best practices

Challenges overcome:
- Email case-sensitivity validation bug
- Complex nested serializer relationships
- Implementing proper JWT refresh flow

Code metrics:
- Files created: 23
- Lines of code: ~1,200
- Commits: 12
- Test coverage: 89%

Resources deep-dived:
- Django ORM documentation
- DRF tutorial (complete)
- Two Scoops of Django (chapters 1-5)
- Real Python - Django testing

Hours invested: ~22h (target: 20h/week)

Confidence level:
- Django basics: ████████░░ 80%
- DRF: ███████░░░ 70%
- Testing: ███████░░░ 70%
- Architecture: ██████░░░░ 60%

Week 2 goals:
- [ ] US-003: Contract management
- [ ] US-004: File uploads (S3)
- [ ] Improve test coverage to 90%+
- [ ] Learn Docker basics
- [ ] Start Vue.js fundamentals

Reflection:
Starting with backend was the right choice. Understanding 
Django ORM deeply before moving to frontend will help with 
building a coherent full-stack application. The service layer 
refactoring was challenging but necessary for maintainability.

Next week focus: Finish backend core, start Docker exploration.

Status: ✅ Week 1 complete, on track for 8-week goal
```

This summary will be incredibly valuable when you:
- Prepare for Jet HR interview
- Review before Week 2
- Update your LinkedIn/resume

Ready to commit this milestone? (yes/edit/cancel)
```

---

## Pro Tips for Using the Skill

### 1. Be Conversational
```
✅ "Finished employee API, commit please"
✅ "Quick bug fix, need to commit"
✅ "Let's save this progress"

❌ "git commit -m 'stuff'"
```

### 2. Provide Context
```
✅ "Fixed authentication bug that was causing token refresh to fail"

❌ "Fixed bug"
```

### 3. Reflect on Learning
When Claude asks "What did you learn?", be specific:
```
✅ "I learned that Django ORM's select_related only works for ForeignKey, 
    not ManyToMany. For ManyToMany, I need prefetch_related."

❌ "Learned Django stuff"
```

### 4. Use Feature Branches
```
✅ "Create branch for US-003"
   → Claude creates: feature/US-003-contract-management

❌ Working directly on main
```

### 5. Review Before Accepting
Always read the generated commit message. It's your learning record!

---

## Commit Message Quality Comparison

### ❌ Bad (without skill):
```
git commit -m "added employee stuff"
```

### ✅ Good (with skill):
```
feat(employees): implement employee CRUD with REST API (US-001)

- Add Employee model with validation
- Create DRF API endpoints
- Implement filtering and pagination
- Add comprehensive tests

Learning notes:
- Mastered Django ORM query optimization
- Understood DRF serializer patterns
- Learned TDD approach

Tests: 18 passed, Coverage: 91%
```

**Impact:** The second commit tells a story. When Jet HR's CTO reviews your GitHub, they see:
1. Technical competency (what you built)
2. Learning ability (what you understood)  
3. Professional discipline (how you document)
4. Growth mindset (TDD improvement note)

---

## Your Commit History = Your Story

After 8 weeks with this skill, your Git history will show:

```
Week 1: Django fundamentals → Solid backend skills
Week 2: File uploads, S3 → Cloud integration
Week 3: Vue.js basics → Frontend competency
Week 4: Docker deployment → DevOps understanding
Week 5: Authentication → Security awareness
Week 6: Testing & CI/CD → Quality focus
Week 7: AWS deployment → Production readiness
Week 8: Polish & documentation → Professional finish
```

Each commit is proof of your learning journey. 🚀

---

Ready to start using it? Try:

```
"I'm ready to make my first commit for Mini Jet HR"
```

And let the skill guide you! 💪
