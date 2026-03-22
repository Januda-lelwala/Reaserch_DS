"""
Qualification-Based Underemployment Proxy Construction
======================================================
Constructs a skills-based underemployment indicator by cross-referencing
each employed person's education level (EDU) against their ISCO-08
occupation major group (derived from 4-digit occupation code Q7).

A worker is flagged as "qualification-underemployed" when their education
tier exceeds the ILO-defined skill-level requirement for their occupation
major group by at least one tier.

Education tiers (Sri Lanka LFS coding):
    Tier 1 - Grade 5 and below   : EDU 0-5
    Tier 2 - Grade 6-10          : EDU 6-9
    Tier 3 - G.C.E. O/L          : EDU 10-11
    Tier 4 - G.C.E. A/L & above  : EDU 12-19

ISCO-08 major group -> minimum required education tier (ILO skill levels):
    9 (Elementary)                -> Tier 1  (Skill Level 1)
    4-8 (Clerks..Plant operators) -> Tier 2  (Skill Level 2)
    3 (Technicians/Assoc. Prof.)  -> Tier 3  (Skill Level 3)
    2 (Professionals)             -> Tier 4  (Skill Level 4)
    1 (Managers)                  -> Tier 3  (Skill Level 3+4)
    0 (Armed Forces)              -> excluded (mixed requirements)

Output: extraction/qualification_underemployment.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
import glob

# ── Education tier mapping ──────────────────────────────────────────────
def edu_to_tier(edu_code):
    """Map Sri Lanka LFS EDU code (0-19) to education tier (1-4)."""
    try:
        code = int(edu_code)
    except (ValueError, TypeError):
        return np.nan
    if 0 <= code <= 5:
        return 1  # Grade 5 and below
    elif 6 <= code <= 9:
        return 2  # Grade 6-10
    elif 10 <= code <= 11:
        return 3  # G.C.E. O/L
    elif 12 <= code <= 19:
        return 4  # G.C.E. A/L & above (diplomas, degrees, postgrad)
    else:
        return np.nan

# ── ISCO major group -> required education tier ─────────────────────────
# ILO ISCO-08 skill level mapping
ISCO_REQUIRED_TIER = {
    9: 1,  # Elementary occupations
    8: 2,  # Plant & machine operators
    7: 2,  # Craft & related trades
    6: 2,  # Skilled agricultural / forestry / fishery
    5: 2,  # Services & sales workers
    4: 2,  # Clerical support workers
    3: 3,  # Technicians & associate professionals
    2: 4,  # Professionals
    1: 3,  # Managers (ILO: skill level 3 or 4)
    # 0: Armed Forces - excluded
}


def get_isco_major_group(occ_code):
    """Extract ISCO-08 1-digit major group from a 4-digit code."""
    try:
        code_str = str(occ_code).strip()
        if len(code_str) == 0:
            return np.nan
        first = int(code_str[0])
        return first
    except (ValueError, TypeError):
        return np.nan


def process_year_file(file_path):
    """Process a single LFS 25% micro-data file and return mismatch stats."""
    print(f"  Processing: {Path(file_path).name}")
    df = pd.read_csv(file_path, low_memory=False)

    # Normalise column names to uppercase
    df.columns = [str(c).upper().strip() for c in df.columns]

    # ── Resolve column names (differ across years) ──
    def find_col(candidates):
        for c in candidates:
            if c.upper() in df.columns:
                return c.upper()
        return None

    year_col   = find_col(['YEAR'])
    sex_col    = find_col(['SEX'])
    edu_col    = find_col(['EDU'])
    occ_col    = find_col(['Q7'])
    hrs_col    = find_col(['Q40B', 'Q40_B'])
    weight_col = find_col(['ANNUALFACTOR_25PERCENT', 'ANNUALFACTOR'])

    missing = []
    if not year_col: missing.append('YEAR')
    if not edu_col: missing.append('EDU')
    if not occ_col: missing.append('Q7 (occupation)')
    if not hrs_col: missing.append('Q40B (hours)')
    if missing:
        print(f"    ⚠ Missing columns: {missing} — skipping file")
        return None

    # ── Clean data types ──
    df[hrs_col] = pd.to_numeric(
        df[hrs_col].astype(str).str.strip().replace('', np.nan), errors='coerce'
    )
    df[edu_col] = df[edu_col].astype(str).str.strip()
    df[occ_col] = df[occ_col].astype(str).str.strip()

    if weight_col:
        df[weight_col] = pd.to_numeric(
            df[weight_col].astype(str).str.strip().replace('', np.nan), errors='coerce'
        )
    else:
        # Fallback: unweighted
        df['_WEIGHT'] = 1.0
        weight_col = '_WEIGHT'

    # ── Filter to employed persons (hours > 0) ──
    employed = df[df[hrs_col] > 0].copy()
    if len(employed) == 0:
        print("    ⚠ No employed persons found — skipping")
        return None

    # ── Compute education tier and ISCO major group ──
    employed['edu_tier'] = employed[edu_col].apply(edu_to_tier)
    employed['isco_major'] = employed[occ_col].apply(get_isco_major_group)

    # Map ISCO major group → required tier
    employed['required_tier'] = employed['isco_major'].map(ISCO_REQUIRED_TIER)

    # ── Filter: keep only rows with valid education, occupation, and weight ──
    valid = employed.dropna(subset=['edu_tier', 'required_tier', weight_col]).copy()

    if len(valid) == 0:
        print("    ⚠ No valid edu × occupation observations — skipping")
        return None

    # ── Flag qualification mismatch ──
    valid['is_mismatched'] = (valid['edu_tier'] > valid['required_tier']).astype(int)

    year = int(valid[year_col].mode().iloc[0])
    w = valid[weight_col]

    # ── Compute weighted rates ──
    total_rate = (valid['is_mismatched'] * w).sum() / w.sum() * 100

    results = {'Year': year, 'Qual_Underemployment_Rate': round(total_rate, 2)}

    # Gender breakdown (SEX: 1=Male, 2=Female in SL LFS)
    if sex_col:
        valid['_SEX'] = pd.to_numeric(valid[sex_col].astype(str).str.strip(), errors='coerce')
        for sex_code, sex_label in [(1, 'Male'), (2, 'Female')]:
            subset = valid[valid['_SEX'] == sex_code]
            if len(subset) > 0:
                sw = subset[weight_col]
                rate = (subset['is_mismatched'] * sw).sum() / sw.sum() * 100
                results[f'Qual_Underemployment_{sex_label}'] = round(rate, 2)
            else:
                results[f'Qual_Underemployment_{sex_label}'] = np.nan

    # ── Diagnostics ──
    n_valid = len(valid)
    n_mismatched = valid['is_mismatched'].sum()
    print(f"    Year={year}  Valid obs={n_valid}  Mismatched={n_mismatched}  "
          f"Rate={total_rate:.1f}%")

    return results


# ── Main execution ─────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 65)
    print("Qualification-Based Underemployment Proxy Construction")
    print("=" * 65)

    base = Path(__file__).resolve().parent.parent
    csv_dir = base / 'labour' / 'csv'

    # Collect all LFS 25% micro-data files
    patterns = [
        str(csv_dir / '*_25_Percent_Datafile_Out.csv'),
        str(csv_dir / 'LFS-*-25-Percent-Data-Without-Computer*.csv'),
    ]

    files = []
    for p in patterns:
        files.extend(glob.glob(p))
    files = sorted(set(files))

    print(f"\nFound {len(files)} LFS micro-data files.\n")

    all_results = []
    for f in files:
        try:
            result = process_year_file(f)
            if result is not None:
                all_results.append(result)
        except Exception as e:
            print(f"    ✗ Error: {e}")

    if all_results:
        output = pd.DataFrame(all_results).sort_values('Year').reset_index(drop=True)
        out_path = base / 'extraction' / 'qualification_underemployment.csv'
        output.to_csv(out_path, index=False)
        print(f"\n{'=' * 65}")
        print(f"Output saved to: {out_path}")
        print(f"{'=' * 65}")
        print(output.to_string(index=False))
    else:
        print("\n✗ No results produced.")
