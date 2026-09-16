"""
Reporter Module: Terminal presentation using the Rich library.
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from core.auditor import AuditResult


console = Console()


def print_banner():
    banner_text = Text()
    banner_text.append("🛡️  CISCO-NETAUDIT & CONFIG ENGINE  🛡️\n", style="bold cyan")
    banner_text.append("Enterprise Network Automation & Security Compliance Framework\n", style="italic white")
    banner_text.append("Author: Farhad Jelve | Cisco CCNP Enterprise Certified", style="dim")
    console.print(Panel(banner_text, border_style="cyan", expand=False))


def display_audit_report(config_name: str, results: list[AuditResult], score: int, grade: str):
    """Renders a formatted security audit report table in the terminal."""
    table = Table(title=f"Compliance Audit Report: {config_name}", header_style="bold magenta")
    table.add_column("Rule ID", style="cyan", width=10)
    table.add_column("Check Title", style="bold white", width=32)
    table.add_column("Severity", justify="center", width=12)
    table.add_column("Status", justify="center", width=10)
    table.add_column("Details & Remediation", width=42)

    severity_styles = {
        "CRITICAL": "[bold white on red]CRITICAL[/]",
        "HIGH": "[bold red]HIGH[/]",
        "MEDIUM": "[bold yellow]MEDIUM[/]",
        "LOW": "[blue]LOW[/]",
    }

    for r in results:
        status_str = "[bold green]✔ PASS[/]" if r.passed else "[bold red]✘ FAIL[/]"
        sev_str = severity_styles.get(r.severity, r.severity)
        
        detail_text = f"[white]{r.details}[/]"
        if not r.passed and r.remediation:
            detail_text += f"\n[dim yellow]Fix: {r.remediation.splitlines()[0]}[/]"

        table.add_row(r.rule_id, r.title, sev_str, status_str, detail_text)

    console.print(table)

    # Summary Panel
    passed_count = sum(1 for r in results if r.passed)
    failed_count = len(results) - passed_count
    
    grade_color = "green" if score >= 80 else ("yellow" if score >= 70 else "red")
    
    summary_text = (
        f"[bold]Total Checks:[/] {len(results)}  |  "
        f"[bold green]Passed:[/] {passed_count}  |  "
        f"[bold red]Failed:[/] {failed_count}\n"
        f"[bold]Compliance Score:[/] [{grade_color}]{score}%[/]  |  "
        f"[bold]Grade:[/] [{grade_color}]{grade}[/]"
    )
    
    console.print(Panel(summary_text, title="Security Summary", border_style=grade_color, expand=False))


def display_generation_success(files: list[str]):
    """Displays a success message listing generated configs."""
    msg = Text()
    msg.append("✔ Successfully generated configuration files:\n", style="bold green")
    for f in files:
        msg.append(f"  • {f}\n", style="cyan")
    console.print(Panel(msg, title="Config Generation Complete", border_style="green", expand=False))
