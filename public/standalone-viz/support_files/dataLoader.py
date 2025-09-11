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
        # Check for TSV files instead of CSV files
        if os.path.exists(os.path.join(loc, 'metadata.tsv')):
            return loc
    # print("Dataset not found in any of:", *(os.path.abspath(c) for c in candidates), sep="\n  - ")
    sys.exit(1)

def _resolve_s6_csv(requested: Optional[str], dataset_dir: str) -> Tuple[str, List[str]]:
    """
    Resolve requested S6 CSV file name to a real CSV file:
      1) case-insensitive exact
      2) normalized (ignore spaces/underscores/punct)
      3) fallback to common taxa levels
      4) fallback to the first available file
    """
    # Available S6 CSV files based on the conversion output
    s6_files = [
        'phylum', 'class', 'order', 'family', 'genus', 'species', 'pathway'
    ]
    
    # Check which files actually exist
    existing_files = []
    for file_suffix in s6_files:
        csv_path = os.path.join(dataset_dir, f'Supplementary_Dataset_S6_{file_suffix}.csv')
        if os.path.exists(csv_path):
            existing_files.append(file_suffix)
    
    if not existing_files:
        raise ValueError(f"No S6 CSV files found in {dataset_dir}")

    # 1) case-insensitive exact
    lower_map = {s.lower(): s for s in existing_files}
    if requested and requested.lower() in lower_map:
        return lower_map[requested.lower()], existing_files

    # 2) normalized
    norm_map = {_normalize(s): s for s in existing_files}
    req_norm = _normalize(requested or "")
    if req_norm and req_norm in norm_map:
        return norm_map[req_norm], existing_files

    # 3) preferred fallbacks
    prefs = ["genus", "species", "class", "family", "order", "phylum", "pathway"]
    for pref in prefs:
        if pref in existing_files:
            return pref, existing_files

    # 4) first available file
    return existing_files[0], existing_files

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
            # print(f"[dataLoader] Standardized '{col}' -> 'Age'")
            return df

    # print("[dataLoader] WARNING: No 'Age' column (or variant) found in demographics.")
    return df

def _candidate_id_columns() -> List[str]:
    """Common sample ID column names seen across microbiome spreadsheets."""
    return [
        'sample-id', 'sample_id', 'sampleid', 'sample id', 'sample',
        '#sampleid', 'subjectid', 'subject id', 'id', 'sample_name', 'sample name'
    ]

def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Trim, dedupe spaces, and fix weird header artifacts."""
    df = df.copy()
    df.columns = [re.sub(r'\s+', ' ', str(c)).strip() for c in df.columns]
    return df

def _try_find_id_column(df: pd.DataFrame) -> Optional[str]:
    """Return the column name that should be used as 'sample-id', if found."""
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
    """If index looks like sample IDs, promote it to a 'sample-id' column."""
    if df.index is None:
        return None
    idx = df.index
    if idx.isnull().any():
        return None
    # Heuristic: index unique and mostly non-numeric strings
    if idx.is_unique and (idx.astype(str) != pd.RangeIndex(len(idx)).astype(str)).any():
        out = df.copy()
        out = out.reset_index().rename(columns={'index': 'sample-id'})
        return out
    return None

def _first_column_as_id(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """If first column looks like an ID column, rename it to 'sample-id'."""
    if df.shape[1] == 0:
        return None
    first = df.columns[0]
    series = df[first]
    # Heuristics: object-like, mostly unique, not mostly numeric float
    if series.dtype == object or series.map(lambda x: isinstance(x, str)).mean() > 0.5:
        if series.nunique(dropna=True) >= 0.8 * len(series):
            out = df.copy()
            out = out.rename(columns={first: 'sample-id'})
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
    If detected, transpose to samples x features and add 'sample-id'.
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
        transposed.index.name = 'sample-id'
        transposed = transposed.reset_index()
        # print(f"[dataLoader] Detected wide taxa x samples matrix; transposed to samples x features.")
        return transposed

    return None

def _finalize_sheet6(sample_feat_df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure:
      - 'sample-id' exists as a column (string)
      - Only numeric feature columns (drop non-numeric except ID)
    """
    df = _standardize_columns(sample_feat_df).copy()

    # Ensure ID column present
    id_col = _try_find_id_column(df)
    if id_col and id_col != 'sample-id':
        df = df.rename(columns={id_col: 'sample-id'})
    elif not id_col and 'sample-id' not in df.columns:
        # try index -> column
        promoted = _promote_index_as_id(df.set_index(df.columns[0])) if df.columns.size > 0 else None
        if isinstance(promoted, pd.DataFrame) and 'sample-id' in promoted.columns:
            df = promoted
        else:
            # try first column heuristic on original df
            heur = _first_column_as_id(df)
            if isinstance(heur, pd.DataFrame) and 'sample-id' in heur.columns:
                df = heur
            else:
                raise KeyError("Could not find or infer a sample ID column for S6. "
                               "Expected something like 'sample-id', 'SampleID', '#SampleID', etc.")

    # Make IDs strings
    df['sample-id'] = df['sample-id'].astype(str).str.strip()

    # Keep only numeric features besides ID
    numeric_cols = []
    for c in df.columns:
        if c == 'sample-id':
            continue
        try:
            df[c] = pd.to_numeric(df[c], errors='coerce')
            numeric_cols.append(c)
        except Exception:
            pass

    keep_cols = ['sample-id'] + numeric_cols
    df = df[keep_cols]
    return df

# ------------------------------ public API ------------------------------

def load_imsms_data(variable2: Optional[str]):
    """
    Load and merge iMSMS dataset files from TSV format.

    Args:
        variable2 (str|None): Not used anymore since we're loading bray-curtis-distance-matrix.tsv

    Returns:
        demographic_data (pd.DataFrame): subset of demographic/clinical columns incl. sample-id
        sheet6_class (pd.DataFrame): Bray-Curtis distance matrix
        dependentvar (str): 'bray-curtis' (fixed value)
        weighted_unifrac_df (pd.DataFrame): weighted UniFrac distance matrix
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # print("[dataLoader] Loading iMSMS data from TSV files...")

    dataset_dir = _find_dataset_dir(script_dir)

    # TSV file paths
    METADATA_PATH = os.path.join(dataset_dir, 'metadata.tsv')
    BRAY_CURTIS_PATH = os.path.join(dataset_dir, 'bray-curtis-distance-matrix.tsv')
    WEIGHTED_UNIFRAC_PATH = os.path.join(dataset_dir, 'weighted-unifrac-distance-matrix.tsv')

    # Ensure IDs are read consistently across TSV files
    read_kwargs = dict(dtype={'sample-id': 'object'}, sep='\t')

    # Read metadata TSV file
    demographic_data = pd.read_csv(METADATA_PATH, **read_kwargs)

    # Validate presence of IDs in demographics
    if 'sample-id' not in demographic_data.columns:
        raise KeyError("Column 'sample-id' missing from metadata file.")

    # Standardize/ensure Age
    demographic_data = _ensure_age_column(demographic_data)

    # Keep a tidy subset (case-insensitive)
    want = {'body-site', 'year', 'subject', 'reported-antibiotic-usage'}
    lower_to_orig = {c.lower(): c for c in demographic_data.columns}
    keep = [lower_to_orig[k] for k in want if k in lower_to_orig]
    if 'sample-id' not in keep:
        keep.append('sample-id')
    demographic_data = demographic_data[keep]
    # print(f"[dataLoader] Included demographic columns: {keep}")

    # Load Bray-Curtis distance matrix
    sheet6_class = pd.read_csv(BRAY_CURTIS_PATH, sep='\t', index_col=0)
    # Convert to format expected by rest of code (samples x features format)
    # Reset index to make sample IDs a column
    sheet6_class = sheet6_class.reset_index()
    if sheet6_class.columns[0] != 'sample-id':
        sheet6_class = sheet6_class.rename(columns={sheet6_class.columns[0]: 'sample-id'})

    # Normalize ID types to string to guarantee join compatibility
    demographic_data['sample-id'] = demographic_data['sample-id'].astype(str).str.strip()
    sheet6_class['sample-id'] = sheet6_class['sample-id'].astype(str).str.strip()

    # print(f"[dataLoader] Bray-Curtis matrix shape after processing: {sheet6_class.shape} (rows=samples)")

    # Load the weighted UniFrac distance matrix TSV
    # print("Loading weighted UniFrac distance matrix from TSV...")
    weighted_unifrac_df = pd.read_csv(WEIGHTED_UNIFRAC_PATH, sep='\t', index_col=0)
    # print(f"Loaded weighted UniFrac matrix with shape: {weighted_unifrac_df.shape}")

    # Set dependentvar to indicate we're using Bray-Curtis
    dependentvar = 'bray-curtis'

    return demographic_data, sheet6_class, dependentvar, weighted_unifrac_df