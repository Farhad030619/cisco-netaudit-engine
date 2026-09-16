# 🛡️ Cisco-NetAudit & Config Engine

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Cisco CCNP Enterprise](https://img.shields.io/badge/Cisco-CCNP%20Enterprise%20Aligned-orange.svg)](https://www.cisco.com)
[![Security Hardening](https://img.shields.io/badge/Security-CIS%20Benchmark%20Rules-green.svg)](https://www.cisecurity.org/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

An enterprise-grade **Network Automation & Security Compliance Framework** for Cisco IOS/IOS-XE devices. Built to solve real-world configuration inconsistencies, eliminate manual CLI errors, and automatically audit network configurations against CIS and NSA hardening benchmarks.

Developed by **Farhad Jelve** (B.Sc. Electrical Engineering, KTH Royal Institute of Technology | Cisco CCNP Enterprise Core & CCNA certified).

---

## 💡 Why This Project?

During extensive enterprise labbing (including 9 comprehensive KTH/Cisco Networking Academy hands-on labs with OSPF, BGP, and spanning-tree topologier), two recurring operational challenges became evident:

1. **Configuration Drift & Human Error:** Manually configuring enterprise routers via CLI creates typos, inconsistent VTY access lists, and mismatched routing parameters.
2. **Security Compliance Blindspots:** Legacy network devices in production frequently suffer from misconfigurations—such as plain-text passwords, open HTTP daemons, missing BPDU Guard, or unencrypted management protocols.

**Cisco-NetAudit & Config Engine** solves both problems with a clean, lightweight, and auditable Python architecture.

---

## ✨ Key Features

### 1. 🏗️ Single Source of Truth (SSoT) & Config Generation
- **Declarative Data Modeling:** Device parameters (hostnames, IP plans, OSPF areas, BGP peerings) are defined in clean **YAML** data models.
- **Jinja2 Templating Engine:** Automatically produces production-ready Cisco IOS/IOS-XE configuration files adhering to company standards.
- **Support for Multi-Role Devices:** Includes templates for Core/Edge Routers and Catalyst Distribution/Access Switches (VLANs, 802.1Q trunks, STP PortFast & BPDU Guard).

### 2. 🔍 Security & Compliance Auditor (CIS Benchmark Aligned)
Scans existing Cisco `running-config` files and evaluates them against 10 critical security and operational rules:
- **SEC-001:** `service password-encryption` enforced.
- **SEC-002:** `enable secret` enforced (flags obsolete `enable password`).
- **SEC-003:** SSH Version 2 explicitly enforced (prevents downgrade attacks).
- **SEC-004:** Plaintext HTTP server disabled (`no ip http server`).
- **SEC-005:** VTY Lines restricted to SSH only (`transport input ssh`).
- **SEC-006:** Console & VTY inactive session timeouts (`exec-timeout`).
- **SEC-007:** Legal warning MOTD banners configured.
- **SEC-008:** SNMP community hardening (flags default `public`/`private` strings).
- **OPS-001:** Centralized Syslog host configured for auditability.
- **OPS-002:** NTP time synchronization configured for log correlation.

### 3. 📊 Rich Terminal Visualization & Grading
- Displays formatted, color-coded audit tables with severity badges (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
- Computes a weighted **Security Compliance Score (0–100%)** and assigns an academic grade (**A** through **F**).
- Provides copy-pasteable Cisco CLI remediation snippets for every detected vulnerability.

---

## 📐 Architecture

```mermaid
flowchart LR
    subgraph Input ["Data & Configs"]
        Y[inventory.yaml]
        T[Jinja2 Templates]
        C[Cisco Running-Config]
    end

    subgraph Core ["Cisco-NetAudit Engine"]
        G[ConfigGenerator]
        A[ConfigAuditor]
        R[Rich Reporter]
    end

    subgraph Output ["Deliverables"]
        O[.ios Config Files]
        Tbl[Terminal Audit Table & Score]
    end

    Y --> G
    T --> G
    G --> O
    C --> A
    A --> R
    R --> Tbl
```

---

## 🚀 Quickstart & Usage

### 1. Clone & Setup Environment
```bash
git clone https://github.com/Farhad030619/cisco-netaudit.git
cd cisco-netaudit

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Full Automated Demo
The demo generates standard enterprise configs, audits a hardened baseline (Grade A), and audits a vulnerable legacy device (Grade F):
```bash
python main.py demo
```

### 3. Generate Configs from Your YAML Inventory
```bash
python main.py generate --data data/inventory.yaml --output output/
```
Configurations for all routers and switches are generated in the `output/` directory.

### 4. Audit Any Cisco Configuration File
```bash
python main.py audit data/sample_configs/clean_router.ios
# or audit your own downloaded running-config:
python main.py audit path/to/my_router.ios
```

---

## 📋 Sample Terminal Output

When auditing a legacy router with unhardened configurations:

```text
                 Compliance Audit Report: vulnerable_router.ios                 
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID ┃ Check Title              ┃ Severity ┃ Status ┃ Details & Remediation             ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ S1 │ Service Password Encrypt │   HIGH   │ ✘ FAIL │ Passwords stored in clear text    │
│    │                          │          │        │ Fix: service password-encryption  │
│ S2 │ Enable Secret Enforced   │ CRITICAL │ ✘ FAIL │ Legacy 'enable password' found    │
│    │                          │          │        │ Fix: no enable password           │
│ S5 │ VTY Transport Protocol   │ CRITICAL │ ✘ FAIL │ Telnet allowed on VTY lines       │
│    │                          │          │        │ Fix: transport input ssh          │
│ S8 │ SNMP Community String    │ CRITICAL │ ✘ FAIL │ Default 'public' community active │
│    │                          │          │        │ Fix: no snmp-server comm public   │
└────┴──────────────────────────┴──────────┴────────┴───────────────────────────────────┘
╭────────────── Security Summary ───────────────╮
│ Total Checks: 10  |  Passed: 0  |  Failed: 10 │
│ Compliance Score: 0%  |  Grade: F (High Risk) │
╰───────────────────────────────────────────────╯
```

---

## 💬 Technical Interview Q&A (Design Decisions)

Here are the rationales and technical design decisions behind this tool:

<details>
<summary><b>Q1: Why Jinja2 and YAML instead of raw Python strings?</b></summary>
Separating business data from network logic is the core tenet of Network as Code (NaC). By storing variables in YAML (Single Source of Truth) and templates in Jinja2, non-programmers can update network policies without modifying Python code, while engineers can version-control network intent in Git.
</details>

<details>
<summary><b>Q2: How does the auditor parse multi-line hierarchical Cisco blocks (e.g. VTY lines)?</b></summary>
Cisco IOS uses context-dependent indentation under lines like <code>line vty 0 4</code> and <code>router ospf 1</code>. The auditor uses non-greedy regex patterns with lookaheads (<code>line vty [\s\S]*?(?=line|end|$)</code>) to isolate specific sub-blocks before validating line-level commands such as <code>transport input ssh</code>.
</details>

<details>
<summary><b>Q3: How would this scale to hundreds of devices in production?</b></summary>
The core audit logic is decoupled from I/O. For fleet-wide operations, this engine can be integrated into a <b>Nornir</b> or <b>Scrapli</b> task runner to fetch running-configs via SSH/NETCONF in parallel across hundreds of devices, streaming results into a central dashboard or CI/CD pipeline.
</details>

---

## 👤 Author
**Farhad Jelve**  
- **Education:** B.Sc. in Electrical Engineering, KTH Royal Institute of Technology  
- **Certifications:** Cisco CCNP Enterprise: Core Networking (350-401 ENCOR) & CCNA  
- **Specialization:** Network Automation, NetDevOps, Routing & Switching (BGP/OSPF/EVPN), Security
- **LinkedIn:** [Farhad Jelve](https://www.linkedin.com/in/farhad-jelve)
