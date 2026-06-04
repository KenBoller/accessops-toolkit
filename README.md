# AccessOps Toolkit

AccessOps Toolkit is a modular Python-based access management automation platform designed to simulate real-world onboarding, offboarding, and access auditing workflows.

This project was rebuilt and generalized from earlier internal automation concepts into a portfolio-safe standalone application suitable for demonstrating:

- Python automation architecture
- CLI and GUI tooling
- Modular system integrations
- Access provisioning workflows
- Mock identity/authentication systems
- Logging and audit trails
- Safe dry-run / mock execution
- Multi-system orchestration

---

# Features

## CLI-Based Access Management

```bash
python access_management.py check jsmith
python access_management.py grant jsmith --system adtrack --mock
python access_management.py remove jsmith --system adtrack --mock
```

## Optional GUI Interface

Tkinter GUI wrapper included:

```bash
python soctool.py
```

The GUI is intentionally lightweight and delegates all logic to `access_management.py`.

---

# Current Architecture

```text
accessops-toolkit/
│
├── access_management.py
├── soctool.py
│
├── config/
│   ├── creds.example.json
│   └── creds.json            # local only (gitignored)
│
├── data/
│   └── access_state.json
│
├── logs/
│
├── systems/
│   └── UIs/
│       └── adtrack.py
│
└── utils/
    └── get_secret.py
```

---

# System Module Design

Each system integration is self-contained and follows a standard interface:

```bash
python adtrack.py check jsmith
python adtrack.py grant jsmith --mock
python adtrack.py remove jsmith --mock
```

This allows the controller to dynamically discover and execute system modules.

---

# Mock Mode

Mock mode allows safe testing without modifying any real systems.

Example:

```bash
python access_management.py grant jsmith --system adtrack --mock
```

Mock mode is enabled by default in the GUI.

---

# Configuration

Secrets and configuration values are loaded from:

```text
config/creds.json
```

Example template:

```json
{
  "LDAP_HOST": "ldap.example.com",
  "POSTGRES_HOST": "localhost",
  "POSTGRES_USER": "demo_user",
  "POSTGRES_PASS": "demo_password"
}
```

---

# Safety

This repository intentionally contains:

- No real company credentials
- No real infrastructure endpoints
- No production authentication systems
- No proprietary internal code

All integrations are mocked, generalized, or sanitized for portfolio use.

---

# Roadmap

Planned improvements include:

- Flask/FastAPI web frontend
- React dashboard
- SQLite/PostgreSQL backend
- Role-based access templates
- Onboarding workflow automation
- Audit history viewer
- API-based system connectors
- Docker deployment
- Unit/integration testing
- CI/CD pipeline

---

# Why This Project Exists

This project demonstrates the design and implementation of operational automation tooling similar to what internal SOC, IT, IAM, and DevOps teams use for:

- onboarding
- offboarding
- audit reviews
- entitlement verification
- access remediation

while remaining fully safe for public GitHub hosting and portfolio review.