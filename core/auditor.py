"""
Auditor Module: Audits Cisco running-configurations against CIS Benchmarks and Best Practices.
"""
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AuditResult:
    rule_id: str
    title: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    passed: bool
    details: str
    remediation: str


class ConfigAuditor:
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        with open(self.config_path, "r", encoding="utf-8", errors="ignore") as f:
            self.raw_text = f.read()
        self.lines = [line.strip() for line in self.raw_text.splitlines() if line.strip()]

    def _has_regex(self, pattern: str, flags: int = 0) -> bool:
        """Helper: checks if a regex pattern exists in config."""
        return re.search(pattern, self.raw_text, flags) is not None

    def run_audit(self) -> list[AuditResult]:
        """Executes all compliance and security audit checks."""
        results = []

        # 1. Password Encryption
        rule_pass = self._has_regex(r"^service password-encryption", re.MULTILINE)
        results.append(AuditResult(
            rule_id="SEC-001",
            title="Service Password Encryption",
            severity="HIGH",
            passed=rule_pass,
            details="Password encryption is enabled" if rule_pass else "Passwords may be stored in reversible or clear text",
            remediation="service password-encryption"
        ))

        # 2. Enable Secret vs Enable Password
        has_enable_secret = self._has_regex(r"^enable secret", re.MULTILINE)
        has_plain_password = self._has_regex(r"^enable password", re.MULTILINE)
        rule_pass = has_enable_secret and not has_plain_password
        results.append(AuditResult(
            rule_id="SEC-002",
            title="Enable Secret Enforced",
            severity="CRITICAL",
            passed=rule_pass,
            details="Strong enable secret is used" if rule_pass else "Legacy 'enable password' detected or enable secret missing",
            remediation="no enable password\nenable secret <strong_password>"
        ))

        # 3. SSH Version 2 Enforced
        has_ssh_v2 = self._has_regex(r"^ip ssh version 2", re.MULTILINE)
        results.append(AuditResult(
            rule_id="SEC-003",
            title="SSH Version 2",
            severity="HIGH",
            passed=has_ssh_v2,
            details="SSHv2 is explicitly configured" if has_ssh_v2 else "SSHv1 or default negotiation may allow downgrade attacks",
            remediation="ip ssh version 2"
        ))

        # 4. Disable Insecure HTTP Server
        http_server = self._has_regex(r"^ip http server", re.MULTILINE)
        no_http_server = self._has_regex(r"^no ip http server", re.MULTILINE)
        rule_pass = no_http_server or (not http_server)
        results.append(AuditResult(
            rule_id="SEC-004",
            title="Disable Plaintext HTTP Server",
            severity="CRITICAL",
            passed=rule_pass,
            details="Plaintext HTTP administration is disabled" if rule_pass else "Insecure 'ip http server' is active (cleartext credentials)",
            remediation="no ip http server"
        ))

        # 5. VTY Transport Input SSH Only
        vty_ssh_only = False
        vty_telnet_detected = False
        vty_blocks = re.findall(r"line vty \d+ \d+[\s\S]*?(?=line|end|$)", self.raw_text)
        for block in vty_blocks:
            if re.search(r"transport input.*(all|telnet)", block):
                vty_telnet_detected = True
            if re.search(r"transport input ssh\b", block):
                vty_ssh_only = True

        rule_pass = vty_ssh_only and not vty_telnet_detected
        results.append(AuditResult(
            rule_id="SEC-005",
            title="VTY Transport Protocol (SSH Only)",
            severity="CRITICAL",
            passed=rule_pass,
            details="VTY lines restrict transport to SSH only" if rule_pass else "Telnet or unencrypted transport allowed on VTY lines",
            remediation="line vty 0 15\n transport input ssh"
        ))

        # 6. Session Timeout (exec-timeout)
        exec_timeout = self._has_regex(r"exec-timeout \d+", re.MULTILINE)
        results.append(AuditResult(
            rule_id="SEC-006",
            title="Console & VTY Exec-Timeout",
            severity="MEDIUM",
            passed=exec_timeout,
            details="Inactivity timeouts are configured" if exec_timeout else "No exec-timeout found; sessions may remain open indefinitely",
            remediation="line con 0 / line vty 0 15\n exec-timeout 10 0"
        ))

        # 7. Warning Banner (Banner MOTD)
        has_banner = self._has_regex(r"^banner motd", re.MULTILINE)
        results.append(AuditResult(
            rule_id="SEC-007",
            title="Legal Notice / Login Banner",
            severity="LOW",
            passed=has_banner,
            details="Login MOTD banner is configured" if has_banner else "No login banner configured (legal liability risk)",
            remediation="banner motd ^C Authorized Access Only ^C"
        ))

        # 8. Centralized Logging (Syslog)
        has_syslog = self._has_regex(r"^logging (?:host )?\d+\.\d+\.\d+\.\d+", re.MULTILINE)
        results.append(AuditResult(
            rule_id="OPS-001",
            title="Centralized Syslog Host",
            severity="HIGH",
            passed=has_syslog,
            details="Remote syslog logging host configured" if has_syslog else "No remote syslog host; audit logs only reside in local memory buffer",
            remediation="logging host <syslog_ip>"
        ))

        # 9. Time Synchronization (NTP)
        has_ntp = self._has_regex(r"^ntp server", re.MULTILINE)
        results.append(AuditResult(
            rule_id="OPS-002",
            title="NTP Time Synchronization",
            severity="MEDIUM",
            passed=has_ntp,
            details="NTP time synchronization is configured" if has_ntp else "No NTP server found; log timestamps may desynchronize",
            remediation="ntp server <ntp_ip>"
        ))

        # 10. Insecure SNMP Communities
        has_weak_snmp = self._has_regex(r"snmp-server community (public|private)", re.MULTILINE | re.IGNORECASE)
        results.append(AuditResult(
            rule_id="SEC-008",
            title="SNMP Community Hardening",
            severity="CRITICAL",
            passed=not has_weak_snmp,
            details="No default SNMP communities found" if not has_weak_snmp else "Default SNMP community string ('public' or 'private') detected!",
            remediation="no snmp-server community public\nno snmp-server community private"
        ))

        return results

    def calculate_score(self, results: list[AuditResult]) -> tuple[int, str]:
        """Calculates security score (0-100) and assigns an academic grade (A-F)."""
        weights = {"CRITICAL": 25, "HIGH": 15, "MEDIUM": 10, "LOW": 5}
        total_possible = sum(weights[r.severity] for r in results)
        earned = sum(weights[r.severity] for r in results if r.passed)
        score = int((earned / total_possible) * 100) if total_possible > 0 else 0

        if score >= 90:
            grade = "A (Exemplary)"
        elif score >= 80:
            grade = "B (Good)"
        elif score >= 70:
            grade = "C (Needs Attention)"
        elif score >= 60:
            grade = "D (Poor)"
        else:
            grade = "F (High Risk)"

        return score, grade
