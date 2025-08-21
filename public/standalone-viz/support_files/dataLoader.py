# support_files/dataLoader.py
import os
import re
import sys
import pandas as pd
from typing import List, Tuple, Optional

# ----------------------------- helpers -----------------------------

def _normalize(name: str) -> str:
    """Lowercase and remove spaces/underscores/punctuation for robust matching."""
    if not name:
        return ""
    return re.sub(r'[\W_]+', '', str(name).strip().lower())

def _find_dataset_dir(script_dir: str) -> str:
    """Locate the iMSMS_dataset folder relative to this file."""
    candidates = [
        os.path.join(script_dir, 'iMSMS_dataset'),
        os.path.join(script_dir, '..', 'iMSMS_dataset'),
        os.path.join(script_dir, '..', '..', 'iMSMS_dataset'),
        'iMSMS_dataset',  # cwd-relative
    ]
    for loc in candidates:
        if os.path.exists(os.path.join(loc, 'Supplementary_Dataset_S1.xlsx')):
            return loc
    print("Dataset not found in any of:", *(os.path.abspath(c) for c in candidates), sep="\n  - ")
    sys.exit(1)

def _resolve_s6_sheet(requested: Optional[str], s6_path: str) -> Tuple[str, List[str]]:
    """
    Resolve requested S6 worksheet name to a real sheet:
      1) case-insensitive exact
      2) normalized (ignore spaces/underscores/punct)
      3) fallback to common taxa levels
      4) fallback to the first sheet
    """
    xls = pd.ExcelFile(s6_path, engine="openpyxl")
    sheets = xls.sheet_names
    if not sheets:
        raise ValueError(f"No worksheets found in {s6_path}")

    # 1) case-insensitive exact
    lower_map = {s.lower(): s for s in sheets}
    if requested and requested.lower() in lower_map:
        return lower_map[requested.lower()], sheets

    # 2) normalized
    norm_map = {_normalize(s): s for s in sheets}
    req_norm = _normalize(requested or "")
    if req_norm and req_norm in norm_map:
        return norm_map[req_norm], sheets

    # 3) preferred fallbacks
    prefs = ["genus", "species", "asv", "otu", "class", "counts", "abundance", "sheet6"]
    for pref in prefs:
        for s in sheets:
            if pref in s.lower():
                return s, sheets

    # 4) first sheet
    return sheets[0], sheets

def _ensure_age_column(df: pd.DataFrame) -> pd.DataFrame:
    """Create/standardize an 'Age' column if a close variant exists; coerce to numeric."""
    if 'Age' in df.columns:
        df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
        return df

    # Likely variants
    candidates = [
        r'^age\b',
        r'^age\s*\(years?\)',
        r'^age_years$',
        r'^ageyears$',
        r'^years\s*of\s*age$'
    ]
    for col in df.columns:
        name = col.strip().lower()
        if any(re.match(p, name) for p in candidates):
            df['Age'] = pd.to_numeric(df[col], errors='coerce')
            print(f"[dataLoader] Standardized '{col}' -> 'Age'")
            return df

    print("[dataLoader] WARNING: No 'Age' column (or variant) found in demographics.")
    return df

def _candidate_id_columns() -> List[str]:
    """Common sample ID column names seen across microbiome spreadsheets."""
    return [
        'imsms_id', 'iMSMS_ID', 'iMSMS ID', 'sampleid', 'sample id', 'sample',
        '#sampleid', 'subjectid', 'subject id', 'id', 'sample_name', 'sample name'
    ]

def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Trim, dedupe spaces, and fix weird header artifacts."""
    df = df.copy()
    df.columns = [re.sub(r'\s+', ' ', str(c)).strip() for c in df.columns]
    return df

def _try_find_id_column(df: pd.DataFrame) -> Optional[str]:
    """Return the column name that should be used as 'iMSMS_ID', if found."""
    lower_map = {c.lower(): c for c in df.columns}
    for cand in _candidate_id_columns():
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    # Try exact normalized match
    norm_map = {_normalize(c): c for c in df.columns}
    for cand in _candidate_id_columns():
        if _normalize(cand) in norm_map:
            return norm_map[_normalize(cand)]
    return None

def _promote_index_as_id(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """If index looks like sample IDs, promote it to an 'iMSMS_ID' column."""
    if df.index is None:
        return None
    idx = df.index
    if idx.isnull().any():
        return None
    # Heuristic: index unique and mostly non-numeric strings
    if idx.is_unique and (idx.astype(str) != pd.RangeIndex(len(idx)).astype(str)).any():
        out = df.copy()
        out = out.reset_index().rename(columns={'index': 'iMSMS_ID'})
        return out
    return None

def _first_column_as_id(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """If first column looks like an ID column, rename it to 'iMSMS_ID'."""
    if df.shape[1] == 0:
        return None
    first = df.columns[0]
    series = df[first]
    # Heuristics: object-like, mostly unique, not mostly numeric float
    if series.dtype == object or series.map(lambda x: isinstance(x, str)).mean() > 0.5:
        if series.nunique(dropna=True) >= 0.8 * len(series):
            out = df.copy()
            out = out.rename(columns={first: 'iMSMS_ID'})
            return out
    return None

def _taxa_metadata_columns() -> List[str]:
    """Common taxonomy/feature metadata columns to exclude when identifying sample columns."""
    return [
        'kingdom', 'domain', 'phylum', 'class', 'order', 'family', 'genus', 'species',
        'taxonomy', 'taxon', 'taxa', 'otu', 'asv', 'feature id', 'featureid',
        'consensus lineage', 'lineage', 'clade', 'name', 'id', 'otu id', 'asv id'
    ]

def _transpose_if_wide_matrix(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Detect a wide matrix where rows are taxa/features and columns are sample IDs.
    If detected, transpose to samples x features and add 'iMSMS_ID'.
    """
    df2 = _standardize_columns(df)
    lower_cols = [c.lower() for c in df2.columns]
    taxa_cols = [c for c in df2.columns if _normalize(c) in {_normalize(x) for x in _taxa_metadata_columns()}]
    # Treat any obviously non-numeric taxonomy/label columns as taxa metadata as well
    # if they have very few unique values compared to rows:
    for c in df2.columns:
        if c not in taxa_cols:
            s = df2[c]
            # If it looks like a label column (strings, many repeats) and small unique cardinality
            if s.dtype == object and s.nunique(dropna=True) <= 0.5 * len(s):
                # If values are not numeric-ish, consider it metadata
                try:
                    pd.to_numeric(s, errors='raise')
                except Exception:
                    taxa_cols.append(c)

    abundance_part = df2.drop(columns=list(dict.fromkeys(taxa_cols)), errors='ignore')

    # If most of the remaining columns are numeric-like, assume they are sample columns
    numeric_like = 0
    for c in abundance_part.columns:
        try:
            pd.to_numeric(abundance_part[c], errors='raise')
            numeric_like += 1
        except Exception:
            pass

    # Heuristic: if >=60% of remaining columns are numeric, we assume wide sample columns
    if abundance_part.shape[1] > 0 and numeric_like >= 0.6 * abundance_part.shape[1]:
        transposed = abundance_part.T
        transposed.index.name = 'iMSMS_ID'
        transposed = transposed.reset_index()
        print(f"[dataLoader] Detected wide taxa x samples matrix; transposed to samples x features.")
        return transposed

    return None

def _finalize_sheet6(sample_feat_df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure:
      - 'iMSMS_ID' exists as a column (string)
      - Only numeric feature columns (drop non-numeric except ID)
    """
    df = _standardize_columns(sample_feat_df).copy()

    # Ensure ID column present
    id_col = _try_find_id_column(df)
    if id_col and id_col != 'iMSMS_ID':
        df = df.rename(columns={id_col: 'iMSMS_ID'})
    elif not id_col and 'iMSMS_ID' not in df.columns:
        # try index -> column
        promoted = _promote_index_as_id(df.set_index(df.columns[0])) if df.columns.size > 0 else None
        if isinstance(promoted, pd.DataFrame) and 'iMSMS_ID' in promoted.columns:
            df = promoted
        else:
            # try first column heuristic on original df
            heur = _first_column_as_id(df)
            if isinstance(heur, pd.DataFrame) and 'iMSMS_ID' in heur.columns:
                df = heur
            else:
                raise KeyError("Could not find or infer a sample ID column for S6. "
                               "Expected something like 'iMSMS_ID', 'SampleID', '#SampleID', etc.")

    # Make IDs strings
    df['iMSMS_ID'] = df['iMSMS_ID'].astype(str).str.strip()

    # Keep only numeric features besides ID
    numeric_cols = []
    for c in df.columns:
        if c == 'iMSMS_ID':
            continue
        try:
            df[c] = pd.to_numeric(df[c], errors='coerce')
            numeric_cols.append(c)
        except Exception:
            pass

    keep_cols = ['iMSMS_ID'] + numeric_cols
    df = df[keep_cols]
    return df

# ------------------------------ public API ------------------------------

def load_imsms_data(variable2: Optional[str]):
    """
    Load and merge iMSMS dataset files.

    Args:
        variable2 (str|None): desired worksheet in Supplementary_Dataset_S6.xlsx
                              (e.g., 'Genus', 'Species', 'ASV'). This is a SHEET name,
                              not a metadata column like 'Age'.

    Returns:
        demographic_data (pd.DataFrame): subset of demographic/clinical columns incl. iMSMS_ID
        sheet6_class (pd.DataFrame): samples x features abundance table (has 'iMSMS_ID')
        dependentvar (str): the resolved S6 worksheet actually used
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print("[dataLoader] Loading iMSMS data...")

    dataset_dir = _find_dataset_dir(script_dir)

    S1_PATH = os.path.join(dataset_dir, 'Supplementary_Dataset_S1.xlsx')
    S2_PATH = os.path.join(dataset_dir, 'Supplementary_Dataset_S2.xlsx')
    S3_PATH = os.path.join(dataset_dir, 'Supplementary_Dataset_S3.xlsx')
    S5_PATH = os.path.join(dataset_dir, 'Supplementary_Dataset_S5.xlsx')
    S6_PATH = os.path.join(dataset_dir, 'Supplementary_Dataset_S6.xlsx')

    # Ensure IDs are read consistently across sheets
    read_kwargs = dict(engine="openpyxl", dtype={'iMSMS_ID': 'object'})

    # Source sheets
    sheet1_2 = pd.read_excel(S1_PATH, sheet_name='Dataset S1.2', **read_kwargs)
    sheet2   = pd.read_excel(S2_PATH, sheet_name='Dataset S2',   **read_kwargs)
    sheet3   = pd.read_excel(S3_PATH, sheet_name='Dataset S3',   **read_kwargs)
    sheet5_1 = pd.read_excel(S5_PATH, sheet_name='Dataset S5.1', **read_kwargs)

    # Resolve S6 worksheet robustly
    requested = variable2 or ""
    dependentvar, all_sheets = _resolve_s6_sheet(requested, S6_PATH)
    if requested != dependentvar:
        print(f"[dataLoader] Requested S6 sheet '{requested}' not found; using '{dependentvar}'.")
        print(f"[dataLoader] Available S6 sheets: {all_sheets}")

    s6_raw = pd.read_excel(S6_PATH, sheet_name=dependentvar, engine="openpyxl")
    s6_raw = _standardize_columns(s6_raw)

    # --- Build demographics merge (keep S2 optional if you like) ---
    demographic_data = (
        sheet1_2
        .merge(sheet3,   on='iMSMS_ID', how='left')
        # .merge(sheet2, on='iMSMS_ID', how='left')  # uncomment when needed
        .merge(sheet5_1, on='iMSMS_ID', how='left')
    )

    # Validate presence of IDs in demographics
    if 'iMSMS_ID' not in demographic_data.columns:
        raise KeyError("Column 'iMSMS_ID' missing from demographic data after merges.")

    # Standardize/ensure Age
    demographic_data = _ensure_age_column(demographic_data)

    # Keep a tidy subset (case-insensitive)
    want = {'age', 'residence', 'smoking status', 'sex', 'imsms_id', 'disease'}
    lower_to_orig = {c.lower(): c for c in demographic_data.columns}
    keep = [lower_to_orig[k] for k in want if k in lower_to_orig]
    if 'iMSMS_ID' not in keep:
        keep.append('iMSMS_ID')
    demographic_data = demographic_data[keep]
    print(f"[dataLoader] Included demographic columns: {keep}")

    # --- Prepare S6 abundance: try to find ID column; else detect wide and transpose ---
    id_col = _try_find_id_column(s6_raw)
    if id_col:
        s6_df = s6_raw.rename(columns={id_col: 'iMSMS_ID'}).copy()
    else:
        # Try index promotion
        promoted = _promote_index_as_id(s6_raw.set_index(s6_raw.columns[0])) if s6_raw.columns.size > 0 else None
        if isinstance(promoted, pd.DataFrame) and 'iMSMS_ID' in promoted.columns:
            s6_df = promoted
            print("[dataLoader] Promoted index to 'iMSMS_ID' for S6.")
        else:
            # Try wide matrix transpose
            transposed = _transpose_if_wide_matrix(s6_raw)
            if isinstance(transposed, pd.DataFrame):
                s6_df = transposed
            else:
                # Try first-column-as-ID heuristic
                heur = _first_column_as_id(s6_raw)
                if isinstance(heur, pd.DataFrame) and 'iMSMS_ID' in heur.columns:
                    s6_df = heur
                    print("[dataLoader] Using first column as 'iMSMS_ID' for S6.")
                else:
                    raise KeyError(
                        "Column 'iMSMS_ID' missing in S6 and could not be inferred. "
                        f"S6 columns: {list(s6_raw.columns)[:10]} ..."
                    )

    # Finalize S6 to numeric features with explicit 'iMSMS_ID'
    sheet6_class = _finalize_sheet6(s6_df)

    # Normalize ID types to string to guarantee join compatibility
    demographic_data['iMSMS_ID'] = demographic_data['iMSMS_ID'].astype(str).str.strip()
    sheet6_class['iMSMS_ID']     = sheet6_class['iMSMS_ID'].astype(str).str.strip()

    print(f"[dataLoader] S6 shape after processing: {sheet6_class.shape} (rows=samples)")

    # Load the weighted UniFrac distance matrix from Dataset S5.2
    print("Loading weighted UniFrac distance matrix from Dataset S5.2...")
    weighted_unifrac_df = pd.read_excel(S5_PATH, sheet_name='Dataset S5.2', index_col=0)
    print(f"Loaded weighted UniFrac matrix with shape: {weighted_unifrac_df.shape}")


    return demographic_data, sheet6_class, dependentvar, weighted_unifrac_df
