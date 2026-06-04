"""
AccessOps Toolkit - Optional GUI Wrapper
----------------------------------------
Simple Tkinter GUI for access_management.py and tools/alert_ticket_closer.py.

Important:
- This file is only the GUI layer.
- It does not contain access logic.
- It does not authenticate users directly.
- access_management.py remains the main access controller.
"""

import logging
import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")

ACCESS_MANAGEMENT_SCRIPT = os.path.join(BASE_DIR, "access_management.py")
ALERT_TICKET_CLOSER_SCRIPT = os.path.join(BASE_DIR, "tools", "alert_ticket_closer.py")

os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "soctool.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def run_command(command: list[str], log_area: scrolledtext.ScrolledText) -> None:
    """Runs a command in the background and streams output to the GUI."""

    def worker() -> None:
        logging.info("Running command: %s", " ".join(command))

        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                bufsize=1,
            )

            for line in process.stdout:
                log_area.insert(tk.END, line)
                log_area.see(tk.END)

            for line in process.stderr:
                log_area.insert(tk.END, f"ERROR: {line}")
                log_area.see(tk.END)

            process.wait()

            log_area.insert(tk.END, f"\nProcess finished with exit code {process.returncode}.\n")
            log_area.see(tk.END)

        except Exception as error:
            message = f"Failed to run command: {error}\n"
            log_area.insert(tk.END, message)
            log_area.see(tk.END)
            logging.exception(message)

    threading.Thread(target=worker, daemon=True).start()


def open_access_window(action: str, requires_system: bool) -> None:
    """Opens a small window for check, grant, or remove."""

    window = tk.Toplevel(root)
    window.title(f"AccessOps - {action.capitalize()} Access")
    window.geometry("560x520")

    tk.Label(window, text=f"{action.capitalize()} User Access", font=("Arial", 14, "bold")).pack(pady=10)

    tk.Label(window, text="Target username:").pack()
    target_user_entry = tk.Entry(window, width=45)
    target_user_entry.pack(pady=5)

    tk.Label(window, text="System name:").pack()
    system_entry = tk.Entry(window, width=45)
    system_entry.pack(pady=5)

    if not requires_system:
        tk.Label(
            window,
            text="Optional for check. Leave blank to check all systems.",
            fg="gray",
        ).pack()

    mock_mode = tk.BooleanVar(value=True)
    tk.Checkbutton(window, text="Enable mock mode", variable=mock_mode).pack(pady=5)

    tk.Label(window, text="Output:").pack()
    log_area = scrolledtext.ScrolledText(window, width=65, height=14)
    log_area.pack(pady=5)

    def execute_action(event=None) -> None:
        target_user = target_user_entry.get().strip()
        system_name = system_entry.get().strip()

        if not target_user:
            messagebox.showerror("Missing target user", "Target username is required.")
            return

        if requires_system and not system_name:
            messagebox.showerror("Missing system", "Grant and remove require a system name.")
            return

        command = [
            sys.executable,
            ACCESS_MANAGEMENT_SCRIPT,
            action,
            target_user,
        ]

        if system_name:
            command.extend(["--system", system_name])

        if mock_mode.get():
            command.append("--mock")

        log_area.insert(tk.END, f"Running: {' '.join(command)}\n\n")
        log_area.see(tk.END)

        run_command(command, log_area)

    tk.Button(window, text="Execute", command=execute_action, width=20).pack(pady=10)

    window.bind("<Return>", execute_action)
    target_user_entry.focus_set()


def open_list_systems_window() -> None:
    """Shows systems discovered by access_management.py."""

    window = tk.Toplevel(root)
    window.title("AccessOps - Available Systems")
    window.geometry("560x420")

    tk.Label(window, text="Available Systems", font=("Arial", 14, "bold")).pack(pady=10)

    log_area = scrolledtext.ScrolledText(window, width=65, height=18)
    log_area.pack(pady=5)

    command = [
        sys.executable,
        ACCESS_MANAGEMENT_SCRIPT,
        "--list-systems",
    ]

    run_command(command, log_area)


def open_alert_ticket_closer_window() -> None:
    """Opens a GUI window for running alert ticket auto-close automation."""

    window = tk.Toplevel(root)
    window.title("AccessOps - Alert Ticket Closer")
    window.geometry("620x470")

    tk.Label(window, text="Alert Ticket Closer", font=("Arial", 14, "bold")).pack(pady=10)

    dry_run = tk.BooleanVar(value=True)
    tk.Checkbutton(window, text="Dry run mode", variable=dry_run).pack(pady=5)

    tk.Label(window, text="Output:").pack()
    log_area = scrolledtext.ScrolledText(window, width=72, height=18)
    log_area.pack(pady=5)

    def execute_closer(event=None) -> None:
        command = [
            sys.executable,
            ALERT_TICKET_CLOSER_SCRIPT,
        ]

        if dry_run.get():
            command.append("--dry-run")

        log_area.insert(tk.END, f"Running: {' '.join(command)}\n\n")
        log_area.see(tk.END)

        run_command(command, log_area)

    tk.Button(window, text="Run Ticket Closer", command=execute_closer, width=22).pack(pady=10)

    window.bind("<Return>", execute_closer)


root = tk.Tk()
root.title("AccessOps Toolkit")
root.geometry("420x430")
root.resizable(False, False)

tk.Label(root, text="AccessOps Toolkit", font=("Arial", 16, "bold")).pack(pady=20)

tk.Button(
    root,
    text="Check User Access",
    font=("Arial", 12),
    command=lambda: open_access_window("check", requires_system=False),
    width=28,
    height=2,
).pack(pady=5)

tk.Button(
    root,
    text="Grant User Access",
    font=("Arial", 12),
    command=lambda: open_access_window("grant", requires_system=True),
    width=28,
    height=2,
).pack(pady=5)

tk.Button(
    root,
    text="Remove User Access",
    font=("Arial", 12),
    command=lambda: open_access_window("remove", requires_system=True),
    width=28,
    height=2,
).pack(pady=5)

tk.Button(
    root,
    text="List Available Systems",
    font=("Arial", 12),
    command=open_list_systems_window,
    width=28,
    height=2,
).pack(pady=5)

tk.Button(
    root,
    text="Run Alert Ticket Closer",
    font=("Arial", 12),
    command=open_alert_ticket_closer_window,
    width=28,
    height=2,
).pack(pady=5)

root.mainloop()