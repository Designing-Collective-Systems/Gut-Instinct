import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import subprocess
import sys

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", package], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            print(f"Failed to install {package}")

# Install required packages if not available
packages_to_install = [
    "numpy"
    "matplotlib"
     # Add this!
]

for package in packages_to_install:
    try:
        __import__(package.replace("-", "_"))  # Convert package name to import name
    except ImportError:
        print(f"Installing {package}...")
        install_package(package)

# Now import your actual dependencies
try:
    import numpy as np
    import matplotlib.pyplot as plt 
    import matplotlib.colors as mcolors
     # Add this import too
    print("All packages imported successfully!")
except ImportError as e:
    print(f"Import error: {e}")
    # Try alternative import for skbio if it fails
    try:
        import skbio
        from skbio.stats.ordination import pcoa
    except ImportError:
        print("skbio still not available, continuing without it...")

def generate_discrete_colors(num_categories):
    """Generate distinct colors for discrete categories"""
    # Extended color palette for discrete variables
    discrete_colors = [
        '#1f77b4',  # blue
        '#ff7f0e',  # orange
        '#2ca02c',  # green
        '#d62728',  # red
        '#9467bd',  # purple
        '#FFFFFF',  # white
        '#000000'   # black

        # '#8c564b',  # brown
        # '#e377c2',  # pink
        # '#7f7f7f',  # gray
        # '#bcbd22',  # olive
        # '#17becf',  # cyan
        # '#aec7e8',  # light blue
        # '#ffbb78',  # light orange
        # '#98df8a',  # light green
        # '#ff9896',  # light red
        # '#c5b0d5',  # light purple
        # '#c49c94',  # light brown
        # '#f7b6d3',  # light pink
        # '#c7c7c7',  # light gray
        # '#dbdb8d',  # light olive
        # '#9edae5'   # light cyan
    ]
    
    # If we need more colors than available, generate additional ones
    if num_categories > len(discrete_colors):
        # Use matplotlib's tab20 colormap for additional colors
        tab20 = plt.cm.get_cmap('tab20')
        additional_colors = [mcolors.rgb2hex(tab20(i)) for i in np.linspace(0, 1, num_categories)]
        return additional_colors
    
    return discrete_colors[:num_categories]

def generate_gradient_colors(num_bins):
    """Generate gradient colors using Yellow-Orange-Red scheme"""
    
    # Use matplotlib's YlOrRd colormap
    cmap = plt.cm.get_cmap('YlOrRd')
    # Generate colors from light (0.2) to dark (1.0) to ensure we get the full range
    # Starting at 0.2 instead of 0.0 to avoid too pale colors
    colors = [mcolors.rgb2hex(cmap(0.2 + (0.8 * i / (num_bins - 1)))) for i in range(num_bins)]
    
    return colors