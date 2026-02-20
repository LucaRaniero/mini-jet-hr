# Mini Jet HR - API Design

Base URL: `http://localhost:8000/api/`

## Employees

### List Employees
```
GET /api/employees/
```

Returns a paginated list of active employees.

**Query Parameters:**
| Parameter | Type | Description |
|---|---|---|
| `role` | string | Filter by role: `employee`, `manager`, `admin` |
| `ordering` | string | Sort field. Prefix `-` for descending. Options: `last_name`, `first_name`, `hire_date` |
| `page` | integer | Page number (20 items per page) |

**Response** `200 OK`:
```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "first_name": "Mario",
      "last_name": "Rossi",
      "email": "mario@example.com",
      "role": "employee",
      "department": "Engineering",
      "hire_date": "2024-01-15",
      "is_active": true,
      "created_at": "2026-02-11T20:06:21.917Z",
      "updated_at": "2026-02-11T21:17:36.841Z"
    }
  ]
}
```

**Examples:**
```bash
# All active employees
curl http://localhost:8000/api/employees/

# Only managers
curl http://localhost:8000/api/employees/?role=manager

# Sorted by hire date descending
curl http://localhost:8000/api/employees/?ordering=-hire_date

# Page 2
curl http://localhost:8000/api/employees/?page=2
```

---

### Create Employee
```
POST /api/employees/
```

**Request Body:**
```json
{
  "first_name": "Anna",
  "last_name": "Bianchi",
  "email": "anna@example.com",
  "role": "employee",
  "department": "HR",
  "hire_date": "2024-06-01"
}
```

**Required Fields:** `first_name`, `last_name`, `email`, `hire_date`

**Optional Fields:** `role` (default: `employee`), `department` (default: `""`)

**Validation Rules:**
- `email`: must be unique across all employees
- `hire_date`: must not be in the future
- `role`: must be one of `employee`, `manager`, `admin`

**Response** `201 Created`: the created employee object

**Response** `400 Bad Request`: validation errors

---

### Retrieve Employee
```
GET /api/employees/{id}/
```

**Response** `200 OK`: single employee object

**Response** `404 Not Found`: employee does not exist or is inactive

---

### Update Employee
```
PATCH /api/employees/{id}/
```

Partial update. Send only the fields to update.

**Immutable Fields:** `email` (cannot be changed after creation)

**Request Body (example):**
```json
{
  "department": "Engineering",
  "role": "manager"
}
```

**Response** `200 OK`: updated employee object

**Response** `400 Bad Request`: validation errors (e.g., attempting to change email)

---

### Delete Employee (Soft Delete)
```
DELETE /api/employees/{id}/
```

Sets `is_active=False`. The employee record is preserved in the database but excluded from list results.

**Response** `204 No Content`

---

## Data Model

### Employee
| Field | Type | Constraints |
|---|---|---|
| `id` | integer | Auto-generated primary key |
| `first_name` | string (max 100) | Required |
| `last_name` | string (max 100) | Required |
| `email` | string (email) | Required, unique, immutable on update |
| `role` | string | `employee` (default), `manager`, `admin` |
| `department` | string (max 100) | Optional, default `""` |
| `hire_date` | date | Required, must not be future |
| `is_active` | boolean | Default `true`, set to `false` on delete |
| `created_at` | datetime | Auto-set on creation (read-only) |
| `updated_at` | datetime | Auto-set on every save (read-only) |

---

## HTTP Status Codes

| Status | Meaning | When |
|---|---|---|
| `200 OK` | Success | GET, PATCH |
| `201 Created` | Resource created | POST |
| `204 No Content` | Success, no body | DELETE |
| `400 Bad Request` | Validation failed | Invalid data in POST/PATCH |
| `404 Not Found` | Resource not found | Invalid ID or inactive employee |

---

## Pagination

All list endpoints return paginated responses (20 items per page):

```json
{
  "count": 42,
  "next": "http://localhost:8000/api/employees/?page=3",
  "previous": "http://localhost:8000/api/employees/?page=1",
  "results": [...]
}
```

## Contracts

Nested under employees. Each employee can have multiple contracts (historical).

### List Contracts
```
GET /api/employees/{employee_id}/contracts/
```

Returns paginated list of contracts for the specified employee, ordered by start_date descending.

**Response** `200 OK`:
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "employee": 1,
      "contract_type": "indeterminato",
      "ccnl": "metalmeccanico",
      "ral": "35000.00",
      "start_date": "2024-01-15",
      "end_date": null,
      "document": "contracts/2026/02/contratto.pdf",
      "document_url": "http://localhost:8000/media/contracts/2026/02/contratto.pdf",
      "is_expiring": false,
      "created_at": "2026-02-15T10:00:00Z",
      "updated_at": "2026-02-15T10:00:00Z"
    }
  ]
}
```

---

### Create Contract
```
POST /api/employees/{employee_id}/contracts/
```

Supports `multipart/form-data` for PDF upload or `application/json` without document.

**Request Body:**
```json
{
  "contract_type": "determinato",
  "ccnl": "commercio",
  "ral": 30000.00,
  "start_date": "2024-06-01",
  "end_date": "2025-06-01"
}
```

**Required Fields:** `contract_type`, `ccnl`, `ral`, `start_date`

**Optional Fields:** `end_date` (null = active contract), `document` (PDF file, max 5 MB)

**Validation Rules:**
- `contract_type`: one of `determinato`, `indeterminato`, `stagista`
- `ccnl`: one of `metalmeccanico`, `commercio`
- `end_date`: must be after `start_date` (if provided)
- `document`: PDF only, max 5 MB, validated by extension + content-type + size

**Computed Fields (read-only):**
- `document_url`: absolute URL for the uploaded PDF (null if no document)
- `is_expiring`: true if contract ends within 30 days

**Response** `201 Created`: the created contract object

---

### Retrieve Contract
```
GET /api/employees/{employee_id}/contracts/{id}/
```

**Response** `200 OK`: single contract object

---

### Update Contract
```
PATCH /api/employees/{employee_id}/contracts/{id}/
```

Partial update. Send only the fields to update. Supports `multipart/form-data` for PDF upload.

**Note:** To clear `end_date`, send `"end_date": null` explicitly (omitting the field means "don't change").

**Response** `200 OK`: updated contract object

---

### Delete Contract
```
DELETE /api/employees/{employee_id}/contracts/{id}/
```

Hard delete (physical deletion, not soft delete).

**Response** `204 No Content`

---

## Contract Data Model

### Contract
| Field | Type | Constraints |
|---|---|---|
| `id` | integer | Auto-generated primary key |
| `employee` | integer | FK to Employee (read-only, from URL) |
| `contract_type` | string | `determinato`, `indeterminato`, `stagista` |
| `ccnl` | string | `metalmeccanico`, `commercio` |
| `ral` | decimal(10,2) | Required, annual gross salary |
| `start_date` | date | Required |
| `end_date` | date | Optional, null = active contract |
| `document` | file | Optional, PDF only, max 5 MB |
| `document_url` | string | Computed, absolute URL for document |
| `is_expiring` | boolean | Computed, true if expires within 30 days |
| `created_at` | datetime | Auto-set on creation (read-only) |
| `updated_at` | datetime | Auto-set on every save (read-only) |

---

## Onboarding Templates

HR-managed templates that define the onboarding checklist blueprint.

### List Templates
```
GET /api/onboarding-templates/
```

Returns paginated list of active templates, ordered by `order` then `name`.

**Response** `200 OK`:
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Firma contratto",
      "description": "Firmare tutti i documenti contrattuali.",
      "order": 1,
      "is_active": true,
      "created_at": "2026-02-20T10:00:00Z",
      "updated_at": "2026-02-20T10:00:00Z"
    }
  ]
}
```

---

### Create Template
```
POST /api/onboarding-templates/
```

**Request Body:**
```json
{
  "name": "Setup email",
  "description": "Configurare email aziendale.",
  "order": 2
}
```

**Required Fields:** `name`

**Optional Fields:** `description` (default: `""`), `order` (default: `0`)

**Response** `201 Created`: the created template object

---

### Retrieve Template
```
GET /api/onboarding-templates/{id}/
```

**Response** `200 OK`: single template object

---

### Update Template
```
PATCH /api/onboarding-templates/{id}/
```

**Response** `200 OK`: updated template object

---

### Delete Template (Soft Delete)
```
DELETE /api/onboarding-templates/{id}/
```

Sets `is_active=False`. Template is preserved but excluded from list and from new onboarding starts.

**Note:** Templates with existing onboarding steps cannot be hard-deleted (`on_delete=PROTECT`).

**Response** `204 No Content`

---

## Onboarding Template Data Model

### OnboardingTemplate
| Field | Type | Constraints |
|---|---|---|
| `id` | integer | Auto-generated primary key |
| `name` | string (max 200) | Required |
| `description` | text | Optional, default `""` |
| `order` | integer | Default `0`, used for display ordering |
| `is_active` | boolean | Default `true`, set to `false` on delete |
| `created_at` | datetime | Auto-set on creation (read-only) |
| `updated_at` | datetime | Auto-set on every save (read-only) |

---

## Onboarding Steps

Nested under employees. Tracks individual onboarding progress per employee.

### List Steps
```
GET /api/employees/{employee_id}/onboarding/
```

Returns paginated list of onboarding steps for the employee, ordered by template order.

**Response** `200 OK`:
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 10,
      "employee": 1,
      "template": 1,
      "template_name": "Firma contratto",
      "template_description": "Firmare tutti i documenti.",
      "is_completed": false,
      "completed_at": null,
      "notes": "",
      "created_at": "2026-02-20T10:00:00Z",
      "updated_at": "2026-02-20T10:00:00Z"
    }
  ]
}
```

---

### Start Onboarding (Bulk Create)
```
POST /api/employees/{employee_id}/onboarding/
```

Creates one step per active template. **No request body needed.** Idempotent: skips templates that already have a step for this employee.

**Response** `201 Created`: full list of steps (not paginated)

**Response** `404 Not Found`: employee does not exist

---

### Toggle Step Completion
```
PATCH /api/employees/{employee_id}/onboarding/{step_id}/
```

**Request Body:**
```json
{
  "is_completed": true
}
```

When `is_completed` changes:
- `true` → `completed_at` is auto-set to current timestamp
- `false` → `completed_at` is auto-cleared to `null`

**Response** `200 OK`: updated step object

---

## Onboarding Step Data Model

### OnboardingStep
| Field | Type | Constraints |
|---|---|---|
| `id` | integer | Auto-generated primary key |
| `employee` | integer | FK to Employee (read-only, CASCADE) |
| `template` | integer | FK to OnboardingTemplate (read-only, PROTECT) |
| `template_name` | string | Denormalized from template (read-only) |
| `template_description` | string | Denormalized from template (read-only) |
| `is_completed` | boolean | Default `false` |
| `completed_at` | datetime | Auto-managed (read-only) |
| `notes` | text | Optional, default `""` |
| `created_at` | datetime | Auto-set on creation (read-only) |
| `updated_at` | datetime | Auto-set on every save (read-only) |

**Constraints:** `UNIQUE(employee, template)` — one step per employee-template pair.

**Allowed HTTP methods:** `GET`, `POST`, `PATCH` only (no PUT, no DELETE).

---

## CORS

The API allows requests from:
- `http://localhost:5173` (Vue dev server)
