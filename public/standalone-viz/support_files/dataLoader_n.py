import pandas as pd
import os
from skbio import OrdinationResults
import re

def _normalize(name: str) -> str:
    """Lowercase and remove spaces/underscores/punctuation for robust matching."""
    if not name:
        return ""
    return re.sub(r'[\W_]+', '', str(name).strip().lower())

def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Trim, dedupe spaces, and fix weird header artifacts."""
    df = df.copy()
    df.columns = [re.sub(r'\s+', ' ', str(c)).strip() for c in df.columns]
    return df

def load_new_data():
    ordination_path = "qza_contents/dd0d4900-ef53-43d9-9e54-e8962809a385/data/ordination.txt"
    if not os.path.exists(ordination_path):
        raise FileNotFoundError(f"Error: {ordination_path} not found")

    with open(ordination_path, 'r') as f:
        lines = f.readlines()

    site_start_index = -1
    for i, line in enumerate(lines):
        if line.startswith('Site'):
            site_start_index = i + 2
            break

    if site_start_index == -1:
        raise ValueError("Error: Could not find Site data in ordination.txt")

    eigvals = pd.Series([float(x) for x in lines[1].strip().split('\t')[1:]])
    proportion_explained = pd.Series([float(x) for x in lines[3].strip().split('\t')[1:]])

    samples = []
    for line in lines[site_start_index:]:
        if not line.strip():
            break
        parts = line.strip().split('\t')
        samples.append(parts)

    coords = pd.DataFrame([s[1:] for s in samples], index=[s[0] for s in samples])
    coords = coords.astype(float)

    metadata_path = "metadata.tsv"
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"Error: {metadata_path} not found")

    metadata_df = pd.read_csv(metadata_path, sep="\t", skiprows=[1])
    metadata_df = _standardize_columns(metadata_df)
    
    # The first column is the sample ID
    metadata_df = metadata_df.set_index(metadata_df.columns[0])

    # Find common sample IDs
    common_samples = coords.index.intersection(metadata_df.index)

    # Filter both dataframes
    coords = coords.loc[common_samples]
    metadata_df = metadata_df.loc[common_samples]

    num_axes = coords.shape[1]
    eigvals = eigvals[:num_axes]
    proportion_explained = proportion_explained[:num_axes]

    pcoa_results = OrdinationResults(
        short_method_name='PCoA',
        long_method_name='Principal Coordinate Analysis',
        eigvals=eigvals,
        samples=coords,
        proportion_explained=proportion_explained
    )

    return pcoa_results, metadata_df