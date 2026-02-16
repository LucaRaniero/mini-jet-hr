# Mini Jet HR - User Stories

## MVP Scope
Focus: Sistema base di gestione dipendenti con automazione onboarding

---

## EPIC 1: Gestione Anagrafica Dipendenti
*Obiettivo learning: Django models, ORM, Admin, REST API basics*

### US-001: Visualizzare lista dipendenti ✅
**Come** responsabile HR
**Voglio** vedere una lista di tutti i dipendenti
**Così che** possa avere una visione d'insieme del personale

**Acceptance Criteria:**
- [x] Lista mostra: nome, cognome, email, ruolo, data assunzione
- [x] Ordinabile per nome e data assunzione
- [x] Filtrabile per ruolo (employee, manager, admin)
- [x] Paginazione (20 items per pagina)

**Technical Notes:**
- Django Model: Employee
- API endpoint: GET /api/employees/
- Vue component: EmployeeList.vue
- Focus: Django QuerySet, DRF serializers, Vue list rendering

---

### US-002: Creare nuovo dipendente ✅
**Come** responsabile HR
**Voglio** aggiungere un nuovo dipendente al sistema
**Così che** possa gestire l'anagrafica completa

**Acceptance Criteria:**
- [x] Form con campi: nome, cognome, email, ruolo, data assunzione, dipartimento
- [x] Validazione email univoca
- [x] Validazione data assunzione (non futura)
- [x] Messaggio di successo dopo creazione
- [x] Redirect alla lista dipendenti

**Technical Notes:**
- API endpoint: POST /api/employees/
- Vue component: EmployeeForm.vue
- Focus: Django validators, DRF validation, Vue form handling, reactive state

---

### US-003: Modificare dati dipendente ✅ (audit trail deferred)
**Come** responsabile HR
**Voglio** aggiornare le informazioni di un dipendente
**Così che** possa mantenere i dati sempre aggiornati

**Acceptance Criteria:**
- [x] Form pre-compilato con dati attuali
- [x] Tutti i campi modificabili tranne email (immutabile)
- [x] Validazioni come in creazione
- [ ] Log delle modifiche (chi, quando, cosa) — deferred to future session

**Technical Notes:**
- API endpoint: PUT/PATCH /api/employees/{id}/
- Focus: Partial updates, audit trail pattern, Vue computed properties

---

### US-004: Eliminare dipendente (soft delete) ✅ (restore deferred)
**Come** responsabile HR
**Voglio** rimuovere un dipendente dal sistema
**Così che** possa gestire uscite senza perdere storico

**Acceptance Criteria:**
- [x] Conferma prima dell'eliminazione
- [x] Soft delete (is_active=False, non cancellazione fisica)
- [x] Dipendenti inattivi non visibili in lista default
- [ ] Possibilità di ripristinare dipendente inattivo — deferred to future session

**Technical Notes:**
- API endpoint: DELETE /api/employees/{id}/
- Focus: Soft delete pattern, Django managers custom, confirmations in Vue

---

## EPIC 2: Gestione Contratti
*Obiettivo learning: Foreign keys, relazioni, file upload*

### US-005: Associare contratto a dipendente ✅ (API done, PDF upload deferred)
**Come** responsabile HR
**Voglio** caricare e associare un contratto a un dipendente
**Così che** possa digitalizzare i documenti contrattuali

**Acceptance Criteria:**
- [ ] Upload PDF del contratto — deferred to Phase 2 (file upload + S3)
- [x] Campi: tipo contratto (indeterminato/determinato/stage), data inizio, data fine, RAL
- [x] Un dipendente può avere più contratti (storico)
- [x] Solo l'ultimo contratto è "attivo" (end_date IS NULL)
- [ ] Preview PDF nel browser — deferred to Phase 2

**Technical Notes:**
- Django Model: Contract (ForeignKey to Employee)
- API endpoint: POST /api/employees/{id}/contracts/
- Additional fields: CCNL (metalmeccanico, commercio)
- Active contract: derived from end_date IS NULL (no redundant is_active flag)
- Focus: Foreign Keys, one-to-many relations, nested API routes, cross-field validation

---

### US-006: Visualizzare storico contratti (API done, frontend deferred)
**Come** responsabile HR
**Voglio** vedere tutti i contratti di un dipendente
**Così che** possa avere visibilità sullo storico lavorativo

**Acceptance Criteria:**
- [x] API: GET /api/employees/{id}/contracts/ returns contracts ordered by start_date DESC
- [ ] Timeline dei contratti in ordine cronologico (frontend)
- [ ] Evidenziato il contratto attivo (frontend)
- [ ] Download PDF per ogni contratto — deferred to Phase 2
- [ ] Indicatore se contratto in scadenza (<30 giorni) (frontend)

**Technical Notes:**
- API endpoint: GET /api/employees/{id}/contracts/
- Vue component: ContractTimeline.vue (to be built)
- Focus: Nested serializers, date calculations, file downloads

---

## EPIC 3: Automazione Onboarding
*Obiettivo learning: Business logic, async tasks, email*

### US-007: Processo onboarding automatico
**Come** sistema  
**Voglio** automatizzare l'onboarding di nuovi dipendenti  
**Così che** HR risparmi tempo e non dimentichi passaggi

**Acceptance Criteria:**
- [ ] Trigger: creazione nuovo dipendente
- [ ] Azioni automatiche:
  - [ ] Invio email di benvenuto
  - [ ] Creazione checklist onboarding
  - [ ] Generazione badge ID (PDF)
  - [ ] Notifica al manager del dipendente
- [ ] Dashboard per monitorare stato onboarding

**Technical Notes:**
- Django signals per trigger
- Celery per async tasks (o Huey più semplice)
- Email backend (console per dev, SMTP per prod)
- PDF generation: ReportLab o WeasyPrint
- Focus: Signals, async tasks, email templates, PDF generation

---

### US-008: Checklist onboarding interattiva
**Come** nuovo dipendente  
**Voglio** vedere e completare la mia checklist onboarding  
**Così che** sappia cosa devo fare nei primi giorni

**Acceptance Criteria:**
- [ ] Lista task: "Firma contratto", "Setup email", "Training sicurezza", etc.
- [ ] Checkbox per completare task
- [ ] Barra progresso
- [ ] Notifica HR quando completato al 100%

**Technical Notes:**
- Django Model: OnboardingTask, OnboardingProgress
- API endpoint: GET/PATCH /api/onboarding/{employee_id}/
- Vue component: OnboardingChecklist.vue
- Focus: Many-to-many relations, progress tracking, real-time updates

---

## EPIC 4: Dashboard e Analytics
*Obiettivo learning: Aggregazioni, charts, caching*

### US-009: Dashboard HR overview
**Come** responsabile HR  
**Voglio** una dashboard con KPI principali  
**Così che** possa monitorare lo stato del personale

**Acceptance Criteria:**
- [ ] Metriche visualizzate:
  - Totale dipendenti (attivi/inattivi)
  - Nuove assunzioni mese corrente
  - Contratti in scadenza
  - Onboarding in corso
- [ ] Grafici: crescita headcount, distribuzione per dipartimento
- [ ] Refresh dati ogni 5 minuti

**Technical Notes:**
- API endpoint: GET /api/dashboard/stats/
- Chart library: Chart.js o ApexCharts
- Caching: Django cache framework
- Focus: Aggregations (Count, Sum), query optimization, charts in Vue, caching

---

### US-010: Report esportabili
**Come** responsabile HR  
**Voglio** esportare report in Excel/PDF  
**Così che** possa condividere dati con management

**Acceptance Criteria:**
- [ ] Export lista dipendenti (Excel)
- [ ] Export singolo contratto (PDF)
- [ ] Export dashboard stats (PDF con grafici)
- [ ] Download asincrono per report pesanti

**Technical Notes:**
- Libraries: openpyxl (Excel), WeasyPrint (PDF)
- Async generation con Celery
- Focus: File generation, async downloads, binary responses

---

## EPIC 5: Autenticazione e Permessi
*Obiettivo learning: Auth, permissions, security*

### US-011: Login/Logout sistema
**Come** utente del sistema  
**Voglio** autenticarmi  
**Così che** possa accedere ai miei dati in sicurezza

**Acceptance Criteria:**
- [ ] Login con email e password
- [ ] JWT tokens per API
- [ ] Logout invalida token
- [ ] Session timeout dopo 8 ore

**Technical Notes:**
- DRF authentication: JWT (djangorestframework-simplejwt)
- Vue: Vuex/Pinia per gestione auth state
- Focus: JWT flow, token refresh, secure storage

---

### US-012: Permessi basati su ruolo
**Come** sistema  
**Voglio** limitare accessi in base al ruolo  
**Così che** ogni utente veda solo ciò che gli compete

**Acceptance Criteria:**
- [ ] Employee: vede solo i propri dati
- [ ] Manager: vede dipendenti del suo team
- [ ] HR Admin: vede tutto
- [ ] API restituisce 403 per accessi non autorizzati

**Technical Notes:**
- Django permissions e groups
- DRF permission classes custom
- Vue: route guards
- Focus: Role-based access control (RBAC), permission checks

---

## EPIC 6: DevOps e Deployment
*Obiettivo learning: Docker, CI/CD, AWS*

### US-013: Containerizzazione applicazione
**Come** developer  
**Voglio** l'app dockerizzata  
**Così che** sia deployabile ovunque in modo consistente

**Acceptance Criteria:**
- [ ] Dockerfile multi-stage per Django
- [ ] Dockerfile per Vue (build production)
- [ ] docker-compose.yml per local development
- [ ] Volumes per persistenza DB e media files
- [ ] Hot reload in sviluppo

**Technical Notes:**
- Docker, Docker Compose
- PostgreSQL container
- Nginx per servire static files
- Focus: Multi-stage builds, docker-compose, volumes

---

### US-014: Deploy su AWS
**Come** developer  
**Voglio** deployare l'app su AWS  
**Così che** sia accessibile pubblicamente

**Acceptance Criteria:**
- [ ] EC2 instance con app Dockerizzata
- [ ] RDS PostgreSQL
- [ ] S3 per media files
- [ ] SSL certificate (Let's Encrypt)
- [ ] Domain name configurato

**Technical Notes:**
- AWS services: EC2, RDS, S3, Route53
- Terraform o CloudFormation (opzionale)
- Focus: Cloud deployment, security groups, IAM roles

---

## EPIC 7: Testing e Quality
*Obiettivo learning: Testing, code quality*

### US-015: Test coverage
**Come** developer  
**Voglio** test automatici  
**Così che** possa refactorare con fiducia

**Acceptance Criteria:**
- [ ] Unit tests: models, serializers, views
- [ ] Integration tests: API endpoints
- [ ] E2E tests: critical user flows
- [ ] Coverage > 80%
- [ ] CI runs tests su ogni push

**Technical Notes:**
- Django: pytest, pytest-django
- Vue: Vitest
- GitHub Actions per CI
- Focus: Test-driven development, mocking, fixtures

---

## Roadmap

### Phase 1 (Weeks 1-3): Foundation
- US-001 → US-004: CRUD dipendenti
- Setup Docker locale

### Phase 2 (Weeks 4-5): Core Features
- US-005 → US-006: Gestione contratti
- US-011 → US-012: Auth & permissions

### Phase 3 (Weeks 6-7): Automation
- US-007 → US-008: Onboarding automation
- US-009: Dashboard

### Phase 4 (Week 8): Polish & Deploy
- US-013 → US-014: Docker & AWS
- US-010: Export
- US-015: Testing (ongoing)

---

## Note per il developer

**Priorità:**
1. Funzionalità core (US-001 a US-008)
2. Security (US-011, US-012)
3. Polish (Dashboard, export, deploy)

**Ogni US deve includere:**
- Unit tests
- API documentation (Swagger/OpenAPI)
- README nella feature branch

**Definition of Done:**
- [ ] Code implementato e testato
- [ ] PR reviewed (self-review inizialmente)
- [ ] Merged in main
- [ ] Documentato in learning journal
