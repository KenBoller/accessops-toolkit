# 🔐 Local Secrets Handling – SOC Tool

This tool uses a simple JSON-based local credential store located at:

`/site/socbot/scripts/SocTool/Secrets/secrets.json`

## 🔧 How to Use
Secrets are accessed via the `secret.get_secret("KEY")` method.

To add a new secret:
1. SSH into the SOC workstation: `youruser@soc1.az-eus-vws.marchex.com`
2. Edit `Secrets/secrets.json` and add your new key-value pair.
3. That’s it. Scripts will auto-load from this file.

## ✅ Security Notes
- File is ignored via `.gitignore`
- Used only from the SOC VM
- Will fallback gracefully if the file is missing or malformed

## 🔍 Example Keys

| Key                 | Description                  |
|---------------------|------------------------------|
| `_ORACLE_USER`      | Oracle DB login username     |
| `_PAGERDUTY_API_KEY`| API token for PagerDuty      |
| `_LDAP_USER`        | LDAP login name              |
| `_LDAP_PASS`        | LDAP bind password           |