# utils.py
import os

def get_filename(prefix, lab, step, ext):
    """
    Generate a consistent filepath based on lab, step, and file type.

    Args:
        prefix (str): e.g. 'labnotes', 'quiz', 'solution'
        lab (str): e.g. 'Lab 1'
        step (str): e.g. 'Step 1'
        ext (str): e.g. 'txt', 'json'

    Returns:
        str: Absolute path to the generated filename
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
    os.makedirs(base_dir, exist_ok=True)

    filename = f"{prefix}_{lab.lower().replace(' ', '_')}_{step.lower().replace(' ', '_')}.{ext}"
    return os.path.join(base_dir, filename)
