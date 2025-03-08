import os
import pandas as pd

def save_results_to_csv(data, output_path):
    """Save the results to a CSV file, creating the directory if needed."""
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))
    data.to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")

