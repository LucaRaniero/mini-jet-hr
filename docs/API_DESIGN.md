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

## CORS

The API allows requests from:
- `http://localhost:5173` (Vue dev server)
