#!/usr/bin/env python3
"""
Cisco-NetAudit & Config Engine
Main CLI Entrypoint
"""
import argparse
import sys
from pathlib import Path

from core.generator import ConfigGenerator
from core.auditor import ConfigAuditor
from core.reporter import print_banner, display_audit_report, display_generation_success, console


def cmd_generate(args):
    """Generates Cisco configs from YAML data using Jinja2."""
    generator = ConfigGenerator(template_dir=args.templates)
    files = generator.generate_all(data_path=args.data, output_dir=args.output)
    display_generation_success(files)


def cmd_audit(args):
    """Runs compliance audit on a single config file."""
    config_path = Path(args.config)
    if not config_path.exists():
        console.print(f"[bold red]Error:[/] File '{args.config}' not found.")
        sys.exit(1)

    auditor = ConfigAuditor(str(config_path))
    results = auditor.run_audit()
    score, grade = auditor.calculate_score(results)
    display_audit_report(config_path.name, results, score, grade)


def cmd_demo(args):
    """Runs a complete demonstration of generation and auditing."""
    console.print("\n[bold yellow]=== STEP 1: Generating Standardized Cisco Configs from YAML ===[/bold yellow]")
    generator = ConfigGenerator(template_dir="templates")
    generated = generator.generate_all(data_path="data/inventory.yaml", output_dir="output")
    display_generation_success(generated)

    console.print("\n[bold yellow]=== STEP 2: Auditing Hardened Config (Compliant Baseline) ===[/bold yellow]")
    auditor_clean = ConfigAuditor("data/sample_configs/clean_router.ios")
    res_clean = auditor_clean.run_audit()
    score, grade = auditor_clean.calculate_score(res_clean)
    display_audit_report("clean_router.ios", res_clean, score, grade)

    console.print("\n[bold yellow]=== STEP 3: Auditing Legacy/Vulnerable Config (Non-Compliant) ===[/bold yellow]")
    auditor_vuln = ConfigAuditor("data/sample_configs/vulnerable_router.ios")
    res_vuln = auditor_vuln.run_audit()
    score, grade = auditor_vuln.calculate_score(res_vuln)
    display_audit_report("vulnerable_router.ios", res_vuln, score, grade)


def main():
    print_banner()

    parser = argparse.ArgumentParser(
        description="Cisco-NetAudit & Config Engine: Automate & audit enterprise Cisco configurations."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate Cisco configs from YAML data.")
    gen_parser.add_argument("--data", default="data/inventory.yaml", help="Path to inventory YAML")
    gen_parser.add_argument("--templates", default="templates", help="Path to templates directory")
    gen_parser.add_argument("--output", default="output", help="Directory for generated configs")
    gen_parser.set_defaults(func=cmd_generate)

    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Audit a Cisco configuration file.")
    audit_parser.add_argument("config", help="Path to Cisco .ios configuration file")
    audit_parser.set_defaults(func=cmd_audit)

    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run full automated demo (Generate + Audit).")
    demo_parser.set_defaults(func=cmd_demo)

    args = parser.parse_args()

    if not args.command:
        # Default behavior if run without args: run demo!
        cmd_demo(args)
    else:
        args.func(args)


if __name__ == "__main__":
    main()
