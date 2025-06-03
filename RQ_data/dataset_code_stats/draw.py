

import matplotlib.pyplot as plt
import json
import numpy as np

# Load the data from the JSON file
output_file_path = r"boxplot_data.json"
try:
    with open(output_file_path, "r", encoding="utf-8") as infile:
        plot_data = json.load(infile)
    print(f"Data loaded from {output_file_path}")
except FileNotFoundError:
    print(f"Error: File not found at {output_file_path}.")
    plot_data = None
except json.JSONDecodeError:
    print(f"Error: Invalid JSON in {output_file_path}.")
    plot_data = None


def is_data_valid(data):
    """Checks if the data is a list of lists containing numerical values."""
    if not isinstance(data, list):
        return False
    if not all(isinstance(sublist, list) for sublist in data):
        return False
    if not all(
        all(isinstance(value, (int, float)) for value in sublist)
        for sublist in data
    ):
        return False
    return True


if plot_data:
    # Plotting
    fig, axes = plt.subplots(1, 4, figsize=(16, 5), constrained_layout=True)  # Match template layout
    plot_sections = [
        ("Versions", "versions", False),
        ("Size (MB)", "Size", False),
        ("Classes", "Classes", True),
        ("KLOC", "KLOC", True),
    ]

    for i, (title, key, use_k_format) in enumerate(plot_sections):
        try:
            data_to_plot = [
                plot_data[key]["DOWN"],
                plot_data[key]["UP"]
            ]
        except KeyError:
            print(f"Warning: Missing key for {key}. Skipping.")
            continue

        if not is_data_valid(data_to_plot) or not any(data_to_plot):
            print(f"Warning: Invalid or empty data for {title}. Skipping plot.")
            continue

        # Plot boxplot without outliers
        axes[i].boxplot(data_to_plot, labels=["DOWN", "UP"], showfliers=False, widths=0.7)
        axes[i].set_title(title, fontsize=24)  # Match template

        # Set font sizes for ticks
        plt.sca(axes[i])
        plt.xticks(fontsize=24)
        plt.yticks(fontsize=24)

        # Format y-tick labels if needed
        if use_k_format:
            yticks = axes[i].get_yticks()
            ylabels = [
                "" if y < 0 else
                f"{int(y / 1000)}K" if y >= 1000 and y % 1000 == 0 else
                f"{y / 1000:.1f}K" if y >= 1000 else
                str(int(y))
                for y in yticks
            ]
            axes[i].set_yticks(yticks)
            axes[i].set_yticklabels(ylabels)

        # Offset text style
        offset_text = axes[i].yaxis.get_offset_text()
        offset_text.set_fontsize(18)
        offset_text.set_horizontalalignment("center")

    plt.tight_layout()
    plt.savefig(r"Statistics_data_set.pdf", dpi=600)
    plt.show()