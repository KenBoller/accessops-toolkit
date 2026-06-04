# AccessOps Toolkit

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-green)
![Status](https://img.shields.io/badge/Status-Portfolio_Ready-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Interface](https://img.shields.io/badge/Interface-CLI_+_GUI-orange)

AccessOps Toolkit is a Python-based Identity and Access Management (IAM) automation platform that simulates real-world onboarding, offboarding, access auditing, entitlement reviews, and access remediation workflows.

The project demonstrates how operational teams can manage user access across multiple systems through a centralized controller while maintaining auditability, consistency, and workflow validation.

Originally inspired by internal operational tooling concepts, this version has been rebuilt as a portfolio-safe standalone application suitable for public GitHub hosting and technical review.

---

# Highlights

✅ FastAPI REST API

✅ Swagger / OpenAPI Documentation

✅ Rich Terminal Interface

✅ Tkinter GUI

✅ Modular System Connectors

✅ Access Audit Workflows

✅ Provisioning & Deprovisioning

✅ Ticket Ownership Validation

✅ Workflow Documentation

✅ Architecture Documentation

---

# Technologies Used

- Python 3
- FastAPI
- Swagger / OpenAPI
- Tkinter
- Rich
- JSON
- argparse
- pathlib
- Logging
- Git
- GitHub

Concepts Demonstrated:

- Identity & Access Management (IAM)
- Workflow Automation
- Operational Tooling
- API Development
- Modular Architecture
- Audit Logging
- Access Provisioning
- Access Reviews
- Entitlement Management

---

# REST API

Start the API:

```bash
uvicorn api.main:app --reload
```

### Swagger Documentation

![Swagger](docs/screenshots/swagger-ui3.png)
![Swagger](docs/screenshots/swagger-ui4.png)


### Systems Endpoint

![Systems](docs/screenshots/swagger-systems.png)

### Stats Endpoint

![Stats](docs/screenshots/swagger-stats.png)

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Available endpoints:

```http
GET    /api/systems
GET    /api/users/{username}/access

POST   /api/users/{username}/grant/{system}
POST   /api/users/{username}/remove/{system}
```

---

# API Documentation

## Swagger UI

![Swagger](docs/screenshots/swagger-ui.png)

### System Discovery Endpoint

![Swagger](docs/screenshots/swagger-ui1.png)

### User Access Audit Endpoint

![Swagger](docs/screenshots/swagger-ui2.png)

---

# CLI Examples

## List Available Systems

```bash
python access_management.py --list-systems
```

## Audit User Access

```bash
python access_management.py check kboller
```

## Grant Access

```bash
python access_management.py grant janesmith --system jira --mock
```

## Remove Access

```bash
python access_management.py remove janesmith --system ticketing --dry-run
```

---

# Screenshots

## Available Systems

![System Discovery](docs/screenshots/python%20access_management.py%20--list-systems.png)

## Access Audit

![Access Check](docs/screenshots/python%20access_management.py%20check%20kboller.png)

## Grant Access

![Grant Access](docs/screenshots/python%20access_management.py%20grant%20janesmith%20--system%20jira%20--mock.png)

## Dry Run Removal

![Dry Run Removal](docs/screenshots/python%20access_management.py%20remove%20janesmith%20--system%20ticketing%20--dry-run.png)

---

# Architecture

![Architecture](docs/architecture.png)

### High-Level Flow

```text
Operator
    │
    ▼
Access Management Controller
    │
    ├── Authentication
    ├── System Discovery
    ├── Access Workflows
    ├── Audit Logging
    └── Ticket Validation
            │
            ▼
      System Modules
            │
            ▼
        Data Layer
```

Additional documentation:

- docs/architecture.md
- docs/workflow_examples.md
- docs/credentials.md

---

# Project Structure

```text
accessops-toolkit/
│
├── access_management.py
├── soctool.py
│
├── api/
│   ├── main.py
│   └── routes/
│
├── config/
│
├── data/
│
├── docs/
│
├── logs/
│
├── reports/
│
├── systems/
│
├── tools/
│
├── tests/
│
└── utils/
```

---

# Example Workflows

## Access Review

```bash
python access_management.py check kboller
```

1. Authenticate operator
2. Discover systems
3. Execute checks
4. Aggregate results
5. Generate audit output

### API Equivalent

```http
GET /api/users/kboller/access
```

---

## New Hire Provisioning

```bash
python access_management.py grant janesmith --system jira --mock
```

1. Validate target system
2. Execute provisioning workflow
3. Record audit event
4. Return confirmation

### API Equivalent

```http
POST /api/users/janesmith/grant/jira
```

---

## Employee Separation

```bash
python access_management.py remove janesmith --system ticketing --dry-run
```

1. Verify ownership
2. Review tickets
3. Reassign operational assets
4. Remove access
5. Record audit history

### API Equivalent

```http
POST /api/users/janesmith/remove/ticketing
```

---

# Configuration

Configuration values are loaded from:

```text
config/creds.json
```

Example:

```json
{
  "LDAP_HOST": "ldap.example.com",
  "LDAP_BASE_DN": "dc=example,dc=com",
  "POSTGRES_HOST": "localhost",
  "POSTGRES_PORT": 5432
}
```

Sensitive values are intentionally excluded from source control.

---

# Safety

This repository intentionally contains:

- No proprietary source code
- No production credentials
- No customer information
- No internal infrastructure
- No real authentication systems

All integrations are mocked, generalized, or sanitized for portfolio use.

---

# Roadmap

## Version 2.x

- Access history tracking
- Role templates
- User lifecycle management
- Enhanced reporting

## Version 3.x

- Expanded FastAPI functionality
- Authentication layer
- REST-based connectors
- Approval workflows

## Future

- Docker deployment
- CI/CD pipeline
- Automated testing
- Web dashboard

---

# Why This Project Exists

AccessOps Toolkit demonstrates the design of operational automation platforms commonly used by:

- Security Operations (SOC)
- IT Operations
- IAM Teams
- Platform Engineering
- DevOps Organizations

The project showcases practical automation patterns for:

- Employee onboarding
- Employee offboarding
- Access reviews
- Entitlement verification
- Audit preparation
- Access remediation

while remaining completely safe for public portfolio use.