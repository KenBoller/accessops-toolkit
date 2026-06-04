"""
AccessOps Toolkit - Access Management Controller
------------------------------------------------
CLI-first controller for checking, granting, and removing user access.

This script is the source of truth for access workflows.
The GUI should call this script instead of duplicating access logic.
"""

import argparse
import logging
import os
import subprocess
import sys
from datetime import datetime
from getpass import getpass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SYSTEMS_DIR = os.path.join(BASE_DIR, "systems", "UIs")
LOG_DIR = os.path.join(BASE_DIR, "logs")
UTILS_DIR = os.path.join(BASE_DIR, "utils")

os.makedirs(LOG_DIR, exist_ok=True)
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, UTILS_DIR)

LOG_FILE = os.path.join(LOG_DIR, "access_management.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


try:
    from utils.ticket_manager import add_comment
except ModuleNotFoundError:
    def add_comment(ticket_id: str, comment: str) -> None:
        logging.warning("RT/ticket helper not found. Skipping ticket comment for %s.", ticket_id)

console = Console()

def authenticate_operator(username: str | None, password: str | None, mock_mode: bool) -> bool:
    """Authenticate the operator before allowing access actions."""
    if mock_mode:
        operator = username or "mock_operator"
        print(f"[MOCK AUTH] Authenticated operator: {operator}")
        logging.info("Mock authentication successful for operator: %s", operator)
        return True

    if not username:
        username = input("Operator username: ").strip()

    if not password:
        password = getpass("Operator password: ")

    if username and password:
        print(f"Authenticated operator: {username}")
        logging.info("Authentication successful for operator: %s", username)
        return True

    print("Authentication failed. Username and password are required.")
    logging.warning("Authentication failed. Missing username or password.")
    return False


def discover_system_scripts() -> dict[str, str]:
    """Find available system modules in systems/UIs."""
    system_scripts: dict[str, str] = {}

    if not os.path.isdir(SYSTEMS_DIR):
        print(f"Systems directory not found: {SYSTEMS_DIR}")
        logging.error("Systems directory not found: %s", SYSTEMS_DIR)
        return system_scripts

    for filename in os.listdir(SYSTEMS_DIR):
        if not filename.endswith(".py"):
            continue

        if filename.startswith("_"):
            continue

        system_name = filename[:-3].lower()
        system_scripts[system_name] = os.path.join(SYSTEMS_DIR, filename)

    return system_scripts


def list_available_systems() -> None:
    """Print discovered systems in a formatted table."""
    system_scripts = discover_system_scripts()

    if not system_scripts:
        console.print("[yellow]No system scripts found.[/yellow]")
        return

    table = Table(title="Available AccessOps Systems")
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("System", style="green")

    for index, system_name in enumerate(sorted(system_scripts), start=1):
        table.add_row(str(index), system_name)

    console.print()
    console.print(table)

def run_system_script(
    script_path: str,
    action: str,
    target_user: str,
    mock_mode: bool = False,
    dry_run: bool = False,
) -> subprocess.CompletedProcess:
    command = [sys.executable, script_path, action, target_user]

    if mock_mode:
        command.append("--mock")

    if dry_run:
        command.append("--dry-run")

    logging.info("Running command: %s", " ".join(command))

    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def print_script_output(result: subprocess.CompletedProcess) -> None:
    """Print stdout/stderr from a system module."""
    if result.stdout.strip():
        print(result.stdout.strip())

    if result.stderr.strip():
        print("ERROR:")
        print(result.stderr.strip())


def select_systems(system_scripts: dict[str, str], requested_system: str | None) -> dict[str, str]:
    """Return either all systems or one requested system."""
    if not requested_system:
        return system_scripts

    system_name = requested_system.lower()

    if system_name not in system_scripts:
        print(f"System not found: {requested_system}")
        print("Use --list-systems to see available systems.")
        logging.error("Requested system not found: %s", requested_system)
        return {}

    return {system_name: system_scripts[system_name]}


def build_check_summary(target_user: str, timestamp: str, results: list[str]) -> str:
    """Build a human-readable summary for console, logs, or ticket comments."""
    header = f"Access check for {target_user} at {timestamp}"
    divider = "-" * len(header)

    return "\n".join(
        [
            header,
            divider,
            *results,
        ]
    )


def check_access(target_user: str, system: str | None = None, rt_ticket: str | None = None) -> list[str]:
    """Check access for one system or all systems."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    console.print()
    console.print(Panel.fit(
        f"[bold]Checking access for:[/bold] [cyan]{target_user}[/cyan]\n"
        f"[bold]Timestamp:[/bold] {timestamp}",
        title="Access Audit",
        border_style="blue",
    ))

    logging.info("Checking access for user: %s", target_user)

    system_scripts = discover_system_scripts()
    systems_to_check = select_systems(system_scripts, system)

    found_access: list[str] = []
    summary_lines: list[str] = []

    for system_name, script_path in systems_to_check.items():
        console.print(f"\n[bold blue][{system_name}][/bold blue] Running access check...")

        result = run_system_script(
            script_path=script_path,
            action="check",
            target_user=target_user,
        )

        print_script_output(result)

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode == 0:
            found_access.append(system_name)
            summary_lines.append(f"[FOUND] {system_name}: {stdout}")
            logging.info("%s check found access for %s", system_name, target_user)
        else:
            summary_lines.append(f"[NOT FOUND] {system_name}: {stdout or 'No access found.'}")
            logging.info("%s check found no access for %s", system_name, target_user)

        if stderr:
            summary_lines.append(f"[ERROR] {system_name}: {stderr}")
            logging.error("%s stderr: %s", system_name, stderr)

    summary = build_check_summary(target_user, timestamp, summary_lines)

    logging.info("\n%s", summary)

    if rt_ticket:
        add_comment(rt_ticket, summary)
        logging.info("Added check summary to ticket %s", rt_ticket)

    return found_access


def run_single_action(
    action: str,
    target_user: str,
    system: str,
    mock_mode: bool,
    dry_run: bool = False,
    rt_ticket: str | None = None,
) -> None:
    """Run grant/remove for one system."""
    system_scripts = discover_system_scripts()
    system_name = system.lower()

    if system_name not in system_scripts:
        print(f"System not found: {system}")
        print("Use --list-systems to see available systems.")
        logging.error("System not found for %s action: %s", action, system)
        return

    console.print()
    console.print(Panel.fit(
        f"[bold]Action:[/bold] {action}\n"
        f"[bold]User:[/bold] [cyan]{target_user}[/cyan]\n"
        f"[bold]System:[/bold] [green]{system_name}[/green]",
        title="Access Action",
        border_style="green" if action == "grant" else "red",
    ))

    if mock_mode:
        console.print("[yellow]Mock mode is ON. Updating local mock access_state.json only.[/yellow]")

    result = run_system_script(
        script_path=system_scripts[system_name],
        action=action,
        target_user=target_user,
        mock_mode=mock_mode,
        dry_run=dry_run,
    )

    print_script_output(result)

    if result.returncode == 0:
        message = f"{action.capitalize()} completed for {target_user} in {system_name}."
        print(message)
        logging.info(message)

        if rt_ticket:
            add_comment(rt_ticket, message)

    else:
        message = f"{action.capitalize()} failed for {target_user} in {system_name}."
        print(message)
        logging.error(message)

        if rt_ticket:
            add_comment(rt_ticket, message)


def grant_access(target_user: str, system: str, mock_mode: bool = False, dry_run: bool = False, rt_ticket: str | None = None) -> None:
    run_single_action("grant", target_user, system, mock_mode, dry_run, rt_ticket)


def remove_access(target_user: str, system: str, mock_mode: bool = False, dry_run: bool = False, rt_ticket: str | None = None) -> None:
    run_single_action("remove", target_user, system, mock_mode, dry_run, rt_ticket)


def interactive_mode(mock_mode: bool = False) -> None:
    """CLI-friendly guided workflow."""
    print("\nAccessOps Toolkit Interactive Mode")
    print("----------------------------------")

    if not authenticate_operator(None, None, mock_mode):
        sys.exit(1)

    target_user = input("Target username: ").strip()

    if not target_user:
        print("Target username is required.")
        return

    found_access = check_access(target_user)

    if found_access:
        print("\nAccess found in:")
        for system_name in sorted(found_access):
            print(f"  - {system_name}")

    print("\nWhat would you like to do next?")
    print("  1. Grant access")
    print("  2. Remove access")
    print("  3. Exit")

    choice = input("Select an option: ").strip()

    if choice == "1":
        list_available_systems()
        system = input("System to grant access in: ").strip()
        grant_access(target_user, system, mock_mode)

    elif choice == "2":
        list_available_systems()
        system = input("System to remove access from: ").strip()
        remove_access(target_user, system, mock_mode)

    else:
        print("No further action taken.")


def parse_arguments() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="AccessOps Toolkit access management controller."
    )

    parser.add_argument(
        "action",
        choices=["check", "grant", "remove", "interactive"],
        nargs="?",
        default="interactive",
    )

    parser.add_argument(
        "target_user",
        nargs="?",
        help="Target user to check, grant, or remove access for.",
    )

    parser.add_argument(
        "--system",
        help="Specific system to manage.",
    )

    parser.add_argument(
        "--operator-user",
        help="Operator username.",
    )

    parser.add_argument(
        "--operator-pass",
        help="Operator password. Avoid using this in shared terminals.",
    )

    parser.add_argument(
        "--rt-ticket",
        help="Optional ticket number for audit comments.",
    )

    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run in safe mock mode.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without changing access_state.json.",
    )

    parser.add_argument(
        "--list-systems",
        action="store_true",
        help="List discovered system scripts and exit.",
    )

    return parser.parse_args()


def main() -> None:
    """Program entry point."""
    args = parse_arguments()

    if args.list_systems:
        list_available_systems()
        return

    if args.action == "interactive":
        interactive_mode(mock_mode=args.mock)
        return

    if not args.target_user:
        print("Target user is required for check, grant, and remove actions.")
        sys.exit(1)

    if not authenticate_operator(args.operator_user, args.operator_pass, args.mock):
        sys.exit(1)

    if args.action == "check":
        check_access(args.target_user, args.system, args.rt_ticket)

    elif args.action == "grant":
        if not args.system:
            print("Grant requires --system.")
            sys.exit(1)

        grant_access(args.target_user, args.system, args.mock, args.dry_run, args.rt_ticket)

    elif args.action == "remove":
        if not args.system:
            print("Remove requires --system.")
            sys.exit(1)

        remove_access(args.target_user, args.system, args.mock, args.dry_run, args.rt_ticket)


if __name__ == "__main__":
    main()