# AccessOps Toolkit Architecture

AccessOps Toolkit is a portfolio-safe operations automation platform that simulates common SOC, IT, IAM, and incident-response workflows.

The project is intentionally mock-based. It uses local JSON files instead of real company systems, credentials, APIs, or infrastructure.

---

# Core Goals

- Demonstrate Python automation architecture
- Simulate enterprise-style operational workflows
- Support CLI and GUI usage
- Keep integrations modular and easy to extend
- Provide safe mock/dry-run modes
- Preserve audit-style logs and state transitions

---

# High-Level Architecture

```text
User / Operator
      |
      v
CLI or Tkinter GUI
      |
      v
Workflow Controllers
      |
      v
Shared Utilities
      |
      v
JSON Mock Data Stores




Project Structure
accessops-toolkit/
│
├── access_management.py
├── soctool.py
│
├── systems/
│   ├── base_system.py
│   └── UIs/
│       ├── adtrack.py
│       ├── jira.py
│       └── _template_system.py
│
├── tools/
│   ├── alert_handler.py
│   ├── alert_ticket_closer.py
│   ├── auth_validator.py
│   ├── new_hire_onboarding.py
│   └── outage_manager.py
│
├── utils/
│   ├── access_state.py
│   ├── get_secret.py
│   ├── id_generator.py
│   └── ticket_manager.py
│
├── data/
│   ├── access_state.json
│   ├── alerts.json
│   ├── bridges.json
│   ├── incidents.json
│   ├── new_hires.json
│   ├── notifications.json
│   ├── operators.json
│   └── tickets.json
│
├── docs/
│   └── architecture.md
│
├── logs/
├── tests/
├── config/
│   ├── creds.example.json
│   └── creds.json
│
└── README.md
Main Components
access_management.py

The primary access-control workflow controller.

Responsibilities:

Discover available system modules
Check user access
Grant user access
Remove user access
Support mock mode
Optionally attach workflow summaries to tickets
Serve as the backend for the GUI

Example:

python access_management.py check kboller --mock
python access_management.py grant janesmith --system jira --mock
python access_management.py remove janesmith --system adtrack --mock
soctool.py

Optional Tkinter GUI wrapper.

Responsibilities:

Provide buttons/forms for common workflows
Run backend scripts as subprocesses
Stream command output into GUI log windows
Keep GUI logic separate from automation logic

The GUI does not own business logic. It delegates to controllers and tools.

System Module Architecture

System modules live in:

systems/UIs/

Each system follows this command contract:

python system_name.py check username
python system_name.py grant username --mock
python system_name.py remove username --mock

Current examples:

adtrack.py
jira.py

Most behavior is inherited from:

systems/base_system.py

This keeps each system module small and consistent.

Example system:

from systems.base_system import BaseSystem


class JiraSystem(BaseSystem):
    SYSTEM_NAME = "jira"
    DEFAULT_GROUPS = ["standard-user"]


if __name__ == "__main__":
    JiraSystem().run()
Access State

Access records are stored in:

data/access_state.json

Example:

{
  "jira": {
    "janesmith": {
      "enabled": true,
      "granted_at": "2026-05-28T17:00:00",
      "updated_at": "2026-05-28T17:00:00",
      "groups": ["standard-user"]
    }
  }
}

Shared helper:

utils/access_state.py
Ticketing Layer

Ticket records are stored in:

data/tickets.json

Ticket utility functions live in:

utils/ticket_manager.py

Responsibilities:

Load/save ticket records
Get open tickets
Get ticket details
Add comments/history entries
Resolve tickets
Reopen tickets

This replaces old RT-specific logic with a safe local mock API.

Alert Workflow
Alert Handler

File:

tools/alert_handler.py

Input:

data/alerts.json

Output:

data/tickets.json
data/incidents.json

Workflow:

Read alerts
  |
  v
Detect high severity
  |
  v
Create ticket
  |
  v
Create incident
  |
  v
Skip duplicates on later runs

Example:

python tools/alert_handler.py --dry-run
python tools/alert_handler.py
Alert Ticket Closer

File:

tools/alert_ticket_closer.py

Workflow:

Read open alert tickets
  |
  v
Search history for clear/recovery keywords
  |
  v
Resolve cleared tickets
  |
  v
Append automation history

Example:

python tools/alert_ticket_closer.py --dry-run
python tools/alert_ticket_closer.py
Outage Workflow

File:

tools/outage_manager.py

The outage manager simulates a major incident response workflow.

Workflow:

Outage declared
  |
  v
Create outage ticket
  |
  v
Create incident
  |
  v
Open bridge record
  |
  v
Create team notification

Outputs:

data/tickets.json
data/incidents.json
data/bridges.json
data/notifications.json

Example:

python tools/outage_manager.py "Major API outage affecting production" --severity critical --dry-run
python tools/outage_manager.py "Major API outage affecting production" --severity critical
New Hire Onboarding Workflow

File:

tools/new_hire_onboarding.py

Input:

data/new_hires.json

Workflow:

Read new hire records
  |
  v
Validate required fields
  |
  v
Create onboarding ticket
  |
  v
Grant requested system access
  |
  v
Append ticket automation comment

Example:

python tools/new_hire_onboarding.py --dry-run
python tools/new_hire_onboarding.py
Auth Validation

File:

tools/auth_validator.py

Input:

data/operators.json

Purpose:

Validate mock operator credentials
Show active/inactive account handling
Display role information

Example:

python tools/auth_validator.py --list-users
python tools/auth_validator.py admin password123

This replaces unsafe legacy LDAP testing scripts.

Mock Data Layer

The project uses JSON as a lightweight mock data layer.

This makes the toolkit:

easy to run
safe for GitHub
easy to inspect
simple to reset
dependency-light

Important files:

data/access_state.json
data/alerts.json
data/tickets.json
data/incidents.json
data/new_hires.json
data/operators.json
data/bridges.json
data/notifications.json
Safety Modes
Mock Mode

Used for access workflows.

Example:

python access_management.py grant janesmith --system jira --mock

Mock mode previews access changes without modifying access_state.json.

Dry Run Mode

Used for operational workflows.

Example:

python tools/alert_handler.py --dry-run

Dry-run mode previews workflow actions without saving records.

Logging

Logs are stored in:

logs/

Examples:

logs/access_management.log
logs/alert_handler.log
logs/outage_manager.log
logs/ticket_manager.log

Logs are excluded from Git by .gitignore.

Design Principles
Separation of Concerns

Each layer has one job:

GUI       -> user interaction
Controller -> orchestration
Systems   -> system-specific access behavior
Tools     -> operational workflows
Utils     -> shared helpers
Data      -> mock persistence
Portfolio Safety

The project does not include:

real company credentials
real LDAP servers
real RT systems
real Slack webhooks
real PagerDuty services
real production APIs
Extensibility

New systems can be added by creating a new file in:

systems/UIs/

and inheriting from BaseSystem.

Current Workflow Map
Access Management
-----------------
operator -> access_management.py -> system module -> access_state.json

New Hire Onboarding
-------------------
new_hires.json -> new_hire_onboarding.py -> access_management.py -> access_state.json
                                      |
                                      v
                                 tickets.json

Alert Handling
--------------
alerts.json -> alert_handler.py -> tickets.json
                              -> incidents.json

Ticket Closing
--------------
tickets.json -> alert_ticket_closer.py -> tickets.json

Outage Handling
---------------
outage_manager.py -> tickets.json
                  -> incidents.json
                  -> bridges.json
                  -> notifications.json
Future Improvements

Planned or possible enhancements:

FastAPI REST layer
Web dashboard
SQLite/PostgreSQL backend
Unit tests
Integration tests
Docker support
CI/CD with GitHub Actions
Role-based permissions
AI-assisted alert triage
Searchable audit history
Better GUI navigation
Demo video / screenshots