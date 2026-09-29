# Vireo Support Intelligence ⚡

Operational analysis, SLA attribution audit, policy compliance sentinel, and automated ticket triage toolkit for **Vireo Audio Support Desk**.

---

## 📌 Problem Overview

Vireo Audio's customer support desk (44 agents across Bengaluru and Indore) faced two critical operational issues:
1. **SLA Credit Line Surge:** First-response SLA breach penalties in the P&L roughly tripled since summer 2025, costing over Rs 8.5 Lakhs.
2. **Morning Shift Blame:** Standard helpdesk reporting attributed the majority of breaches to Morning shift agents, leading to team demoralization.

### Key Analysis Findings
- **The Morning Shift Fallacy:** **64.2% of all recorded breaches (1,566 out of 2,440)** were tickets submitted overnight (22:00 to 06:00 IST) when **zero agents** were scheduled following the June 2025 Indore night shift restructuring. Morning agents responded in an average of 4 minutes upon shift login, but the helpdesk's default reporting attributed the breach to the resolving agent rather than queue arrival time.
- **Identified Policy Leakages:**
  - **95 orders** received both a cash refund and an RMA hardware replacement (**Rs 4,37,418** in combined financial loss).
  - **45 tickets** exceeded the Rs 500 goodwill cap under reason code `GW-OTHER` without Team Lead sign-off (**Rs 1,38,605** in excess unapproved payouts).
  - **1,129 internal team transfers** caused by intake bot misrouting (**Rs 3,44,345** at Rs 305/transfer).
- **Zero-Hiring Solution:** Rebalancing 3 agents from Bengaluru Day shift to Indore Night shift eliminates ~85% of overnight breaches, cutting quarterly SLA credit penalties by **~Rs 1.4 to 1.6 Lakhs / quarter (Rs 5.6 to 6.4 Lakhs / year)** without violating the Q4 headcount freeze.

---

## 🚀 Quickstart Guide

### 1. Installation
Clone the repository and install dependencies:

```bash
git clone https://github.com/SubhadeepBhadra/vireo-support-intelligence.git
cd vireo-support-intelligence
pip install -r requirements.txt
```

### 2. Launch the Web Dashboard
Launch the interactive Streamlit dashboard:

```bash
python -m streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

The dashboard provides 5 modules:
- **Executive Overview:** High-level KPI summary, SLA penalty trends, and shift cross-analysis.
- **SLA Breach Attribution Audit:** Hourly queue arrival vs agent handle time analysis.
- **Financial Leakage Sentinel:** Searchable audit tables of double-dipping cases, goodwill limit overrides, and transfer friction.
- **AI Triage & Response Drafter:** Real-time intent classification, target team routing, and policy-guarded draft generation.
- **Shift & ROI Simulator:** Interactive scenario planner to model quarterly cost savings from roster adjustments.

### 3. Command Line Interface (CLI)

```bash
# Run full SLA and Policy Compliance Audit in terminal:
python main.py --audit

# Test intent classifier and response drafter on a sample customer message:
python main.py --triage "My pulse 2 earbuds arrived yesterday and won't charge in the case"

# Export the 95 duplicate double-dipping leakage orders to CSV:
python main.py --export-leakages double_dipping_orders.csv

# Run the 7-test unit suite:
python tests/test_suite.py

# Run the ML classifier statistical evaluation benchmark:
python tests/evaluate_model.py
```

---

## 📁 Repository Structure

```
vireo-support-intelligence/
├── data/                      # 8 Dataset files (tickets, agents, orders, products, customers, policy PDF)
│   ├── tickets.csv            # 18 months of support ticket records (11,200 unique tickets)
│   ├── agents.csv             # Support roster with temporal shift assignments
│   ├── orders.csv             # Order transactions and LOT codes
│   ├── products.csv           # Product catalog, unit costs & retail prices
│   ├── customers.csv          # Customer database
│   ├── support-policy.pdf     # Vireo Support Operating Policy v3.2
│   ├── email-thread.txt       # Stakeholder context & email communications
│   └── README.txt             # Data dictionary
├── src/                       # Production Modules
│   ├── data_loader.py         # Fast parser, deduplicator & UTC-to-IST converter
│   ├── sla_engine.py          # Fair SLA attribution & queue latency analyzer
│   ├── leakage_detector.py    # Double-dipping, goodwill caps & transfer auditor
│   ├── classifier.py          # NLP intent classifier (TF-IDF + Logistic ML + rule boosts)
│   └── responder.py           # Policy-compliant auto-response generator
├── tests/                     # Unit Tests & Benchmarks
│   ├── test_suite.py          # 7/7 automated unit tests
│   └── evaluate_model.py      # Statistical evaluation benchmark (82.03% accuracy on 11,183 samples)
├── app.py                     # Streamlit Executive & Operations Web Dashboard
├── main.py                    # Terminal CLI Runner
├── memo_neha_kulkarni.md      # Executive Memorandum to Neha Kulkarni
├── analysis_report.md         # Full Quantitative & Financial Diagnostic Report
├── submission-form.md         # Completed ATSLite Submission Pack
├── requirements.txt           # Lightweight dependencies
└── README.md                  # Project documentation
```

---

## 🧪 Model Performance

- **Dataset Size:** 11,183 labeled customer messages
- **Out-of-Sample Test Accuracy:** **82.03%**
- **Test Error Rate:** **17.97%**
- **Inference Latency:** **< 15 milliseconds**
- **Cost per Month:** **Rs 0.00** (Runs locally on CPU)
