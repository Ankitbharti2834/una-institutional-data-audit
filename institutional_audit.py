"""
Project 7: Institutional Data Audit & Interdepartmental Database Integration
University of North Alabama — Enterprise Internal Project

Demonstrates the ETL-based data audit methodology used to identify and resolve
data quality gaps across departmental systems, standardise interdepartmental
databases, and produce a single audit-ready reporting structure.
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

AUDIT_PATH  = "data/institutional_audit.csv"
OUTPUT_PATH = "data/"


# ═══════════════════════════════════════════════════════════════════════════
# 1. LOAD & PROFILE
# ═══════════════════════════════════════════════════════════════════════════

def load_and_profile(path: str) -> tuple:
    df = pd.read_csv(path)
    profile = {
        "total_records":       len(df),
        "columns":             list(df.columns),
        "null_counts":         df.isnull().sum().to_dict(),
        "duplicate_records":   df.duplicated().sum(),
        "departments_found":   df["department"].nunique(),
        "source_systems_found":df["source_system"].nunique(),
        "issue_types_found":   df["issue_type"].value_counts().to_dict()
    }
    return df, profile


# ═══════════════════════════════════════════════════════════════════════════
# 2. STANDARDISATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════

FIELD_STANDARDISATION_RULES = {
    "student_id":       lambda v: str(v).strip().upper().replace(" ", ""),
    "email":            lambda v: str(v).strip().lower(),
    "enrollment_date":  lambda v: _normalise_date(v),
    "department_code":  lambda v: str(v).strip().upper(),
    "gpa":              lambda v: _clamp_gpa(v),
}


def _normalise_date(val) -> str:
    """Handles mixed date formats found across Banner_ERP, Jenzabar, and legacy DBs."""
    formats = ["%Y-%m-%d", "%m/%d/%Y", "%d-%b-%Y", "%Y%m%d"]
    for fmt in formats:
        try:
            return datetime.strptime(str(val).strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return "INVALID_DATE"


def _clamp_gpa(val) -> float:
    try:
        gpa = float(val)
        return round(min(max(gpa, 0.0), 4.0), 2)
    except (ValueError, TypeError):
        return np.nan


def standardise_records(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies field-level standardisation rules to reconcile format
    inconsistencies across Banner_ERP, Jenzabar, Manual_Excel,
    Legacy_DB, and SharePoint source systems.
    """
    df = df.copy()
    for field, rule in FIELD_STANDARDISATION_RULES.items():
        if field in df["field_name"].values:
            mask = df["field_name"] == field
            df.loc[mask, "standardized_value"] = df.loc[mask, "original_value"].apply(
                lambda v: rule(v) if pd.notna(v) else np.nan
            )
    return df


# ═══════════════════════════════════════════════════════════════════════════
# 3. DUPLICATE DETECTION & DEDUPLICATION
# ═══════════════════════════════════════════════════════════════════════════

def detect_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifies duplicate record_ids within each source system.
    Flags records for manual review before system migration.
    """
    dupes = df[df.duplicated(subset=["record_id","source_system"], keep=False)].copy()
    dupes["duplicate_flag"] = "DUPLICATE"
    return dupes


# ═══════════════════════════════════════════════════════════════════════════
# 4. DEPARTMENT RECONCILIATION REPORT
# ═══════════════════════════════════════════════════════════════════════════

def department_reconciliation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Produces a cross-departmental reconciliation report showing data quality
    scores per department and source system. Used by department leads during
    UAT sign-off sessions.
    """
    summary = (
        df.groupby(["department","source_system"])
        .agg(
            total_records   = ("record_id",    "count"),
            issues_found    = ("issue_type",   lambda x: (x != "").sum()),
            corrected       = ("corrected",    lambda x: (x == "Y").sum()),
            missing_values  = ("original_value", lambda x: x.isnull().sum())
        )
        .reset_index()
    )
    summary["correction_rate_pct"] = (
        summary["corrected"] / summary["issues_found"].replace(0, np.nan) * 100
    ).round(1).fillna(0)

    summary["data_quality_score"] = (
        100 - (summary["issues_found"] / summary["total_records"] * 100)
    ).round(1).clip(0, 100)

    return summary.sort_values(["department","data_quality_score"])


# ═══════════════════════════════════════════════════════════════════════════
# 5. ETL RECONCILIATION PIPELINE
# ═══════════════════════════════════════════════════════════════════════════

def run_reconciliation_pipeline(path: str) -> dict:
    """
    Full pipeline: load → profile → standardise → deduplicate → reconcile → report.
    Output feeds the UAT dashboard and department sign-off documentation.
    """
    df, profile = load_and_profile(path)

    std_df    = standardise_records(df)
    dupes_df  = detect_duplicates(df)
    recon_df  = department_reconciliation(std_df)

    # Save outputs
    std_df.to_csv(f"{OUTPUT_PATH}standardised_records.csv", index=False)
    recon_df.to_csv(f"{OUTPUT_PATH}department_reconciliation.csv", index=False)
    if not dupes_df.empty:
        dupes_df.to_csv(f"{OUTPUT_PATH}duplicate_flags.csv", index=False)

    return {
        "profile":            profile,
        "standardised_count": len(std_df),
        "duplicate_count":    len(dupes_df),
        "departments_audited":recon_df["department"].nunique(),
        "avg_quality_score":  round(recon_df["data_quality_score"].mean(), 1)
    }


# ═══════════════════════════════════════════════════════════════════════════
# MAIN RUNNER
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*60)
    print("University of North Alabama — Institutional Data Audit")
    print("="*60)

    results = run_reconciliation_pipeline(AUDIT_PATH)

    print("\n[1] Data Profile:")
    for k, v in results["profile"].items():
        print(f"  {k:<28}: {v}")

    df_std   = pd.read_csv(f"{OUTPUT_PATH}standardised_records.csv")
    df_recon = pd.read_csv(f"{OUTPUT_PATH}department_reconciliation.csv")

    print("\n[2] Department Reconciliation Report:")
    print(df_recon.to_string(index=False))

    print(f"\n[3] Pipeline Summary:")
    print(f"  Standardised records : {results['standardised_count']:,}")
    print(f"  Duplicates detected  : {results['duplicate_count']:,}")
    print(f"  Departments audited  : {results['departments_audited']}")
    print(f"  Avg quality score    : {results['avg_quality_score']}%")
    print("\n✅ Institutional audit pipeline complete.")
