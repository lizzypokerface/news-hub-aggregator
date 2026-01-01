import sys
import os

# Get the absolute path to the 'src' directory
# (Goes up one level from 'test' and down into 'src')
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))

# Add 'src' to the Python path so imports like 'from modules import ...' work
if src_path not in sys.path:
    sys.path.insert(0, src_path)
