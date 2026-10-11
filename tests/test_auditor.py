"""Unit tests for ConfigAuditor verifying CIS benchmarks and score calculation."""
from pathlib import Path
from core.auditor import ConfigAuditor


def test_clean_router_audit_passes_all_checks():
    clean_config = Path("data/sample_configs/clean_router.ios")
    auditor = ConfigAuditor(str(clean_config))
    results = auditor.run_audit()

    assert len(results) == 10
    assert all(r.passed for r in results)

    score, grade = auditor.calculate_score(results)
    assert score == 100
    assert "A" in grade


def test_vulnerable_router_audit_fails_all_checks():
    vulnerable_config = Path("data/sample_configs/vulnerable_router.ios")
    auditor = ConfigAuditor(str(vulnerable_config))
    results = auditor.run_audit()

    assert len(results) == 10
    assert all(not r.passed for r in results)

    score, grade = auditor.calculate_score(results)
    assert score == 0
    assert "F" in grade


def test_partial_compliance(tmp_path):
    test_config = tmp_path / "partial.ios"
    test_config.write_text(
        "service password-encryption\n"
        "enable secret StrongSecret123\n"
        "ip ssh version 2\n"
        "no ip http server\n"
        "line vty 0 4\n"
        " transport input ssh\n"
        "end\n"
    )

    auditor = ConfigAuditor(str(test_config))
    results = auditor.run_audit()

    passed_rules = {r.rule_id for r in results if r.passed}
    assert "SEC-001" in passed_rules
    assert "SEC-002" in passed_rules
    assert "SEC-003" in passed_rules
    assert "SEC-004" in passed_rules
    assert "SEC-005" in passed_rules

    score, _ = auditor.calculate_score(results)
    assert score > 50
