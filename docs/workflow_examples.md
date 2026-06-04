# Workflow Examples

## Access Review Workflow

```bash
python access_management.py check kboller
```

### Result

- Discover systems
- Execute checks
- Aggregate results
- Generate audit summary

---

## New Hire Provisioning Workflow

```bash
python access_management.py grant janesmith --system jira --mock
```

### Result

- Validate system
- Provision access
- Record audit event
- Return confirmation

---

## Employee Separation Workflow

```bash
python access_management.py remove janesmith --system ticketing --dry-run
```

### Result

- Validate ownership
- Review open tickets
- Reassign operational assets
- Remove access
- Log audit event