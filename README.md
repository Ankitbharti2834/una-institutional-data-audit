# Project - Institutional Data Audit & Interdepartmental Database Integration

**Organization:** University of North Alabama  
**Domain:** Data Engineering | Data Quality | ETL | Institutional Reporting  
**Reported To:** Department Managers  
**Confidentiality:** 🔒 Enterprise Internal Project  
> *All production database connections, student records, financial aid data, and system credentials are confidential. This repository demonstrates the audit methodology and ETL reconciliation pipeline using synthetic institutional data.*

---

## Business Problem

The University of North Alabama operated with data quality gaps and inconsistencies across multiple departmental systems — Academic Records, Financial Aid, Admissions, HR, Library, and IT — maintained in a mix of legacy databases, SharePoint lists, and manual Excel files. Duplicate records, missing fields, inconsistent date formats, and out-of-range GPA values created reporting compliance issues and prevented cross-departmental data integration.

## Solution

Conducted an institution-wide data audit identifying inconsistencies, duplicate records, and missing fields across all departmental source systems. Built ETL pipelines to integrate, map, and standardize interdepartmental databases, enforcing consistent field formats and referential integrity rules. Produced a department-level reconciliation report showing data quality scores by source system, and executed UAT for new system implementations with full sign-off documentation by department leads.

## Technical Architecture

```
Manual Excel─┤──► ETL Pipeline ──► Standardisation Engine ──► Audit Report
Legacy_DB  ─┤         │                    │
SharePoint ─┘    Deduplication     Reconciliation Summary
                                           │
                                    UAT Sign-off Reports
```

## Key Deliverables

- Institution-wide data profiling and quality scoring per department  
- Field-level standardisation engine covering student IDs, dates, GPA, email, and department codes  
- Duplicate detection and flagging across 3 source systems  
- Department reconciliation report with correction rate tracking  
- UAT documentation and sign-off workflow  

## Impact

| Metric | Result |
|---|---|
| Data accuracy improvement | **50%** |
| Departments standardised | **3+** |
| Source systems integrated | 3 (Excel, Legacy DB, SharePoint) |
| Reporting compliance enforced | ✅ |

## Repository Contents

```
Project_07_Institutional_Audit/
├── python/
│   └── institutional_audit.py     # Full audit pipeline: load, profile, standardise, reconcile
├── data/
│   └── institutional_audit.csv    # Synthetic institutional audit records (300 rows)
└── README.md
```

## Running the Audit Pipeline

```bash
pip install pandas numpy
python python/institutional_audit.py
# Outputs: data/standardised_records.csv
#          data/department_reconciliation.csv
#          data/duplicate_flags.csv  (if duplicates found)
```

## Tools & Technologies

Python (Pandas, NumPy) · ETL Pipelines · Advanced Excel · SQL

---
*For technical discussion, connect via [LinkedIn](https://linkedin.com/in/a-bharti/).*
