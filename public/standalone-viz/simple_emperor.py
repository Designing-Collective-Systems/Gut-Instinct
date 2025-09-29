
import subprocess
import sys
import os
import pandas as pd
import numpy as np
from emperor import Emperor
from skbio import OrdinationResults

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        print(f"Failed to install {package}", file=sys.stderr)

for pkg in ["pandas", "numpy", "emperor", "scikit-bio"]:
    try:
        __import__(pkg.replace("-", "_"))
    except ImportError:
        install_package(pkg)

ordination_path = "qza_contents/dd0d4900-ef53-43d9-9e54-e8962809a385/data/ordination.txt"
if not os.path.exists(ordination_path):
    print(f"Error: {ordination_path} not found", file=sys.stderr)
    sys.exit(1)

# Parse ordination.txt
with open(ordination_path, 'r') as f:
    lines = f.readlines()

# Find where the site data starts
site_start_index = -1
for i, line in enumerate(lines):
    if line.startswith('Site'):
        site_start_index = i + 2
        break

if site_start_index == -1:
    print("Error: Could not find Site data in ordination.txt", file=sys.stderr)
    sys.exit(1)

eigvals = pd.Series([float(x) for x in lines[1].strip().split('\t')[1:]])
proportion_explained = pd.Series([float(x) for x in lines[3].strip().split('\t')[1:]])

samples = []
for line in lines[site_start_index:]:
    if not line.strip():
        break
    parts = line.strip().split('\t')
    samples.append(parts)

coords = pd.DataFrame([s[1:4] for s in samples], index=[s[0] for s in samples], columns=['PC1', 'PC2', 'PC3'])
coords = coords.astype(float)

# The number of axes in coords should match the number of eigvals and proportion_explained
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

metadata_path = "metadata.tsv"
if not os.path.exists(metadata_path):
    print(f"Error: {metadata_path} not found", file=sys.stderr)
    sys.exit(1)

metadata_df = pd.read_csv(metadata_path, sep="\t", skiprows=[1], index_col='SampleID')

# Create Emperor plot
viz = Emperor(pcoa_results, metadata_df)

# Print HTML to stdout
emperor_html = viz.make_emperor(standalone=True)
print(emperor_html)
