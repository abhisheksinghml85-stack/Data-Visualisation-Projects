import os
import runpy
import sys


project_dir = os.path.join(os.path.dirname(__file__), "..", "Plotly Projects")
project_dir = os.path.abspath(project_dir)
sys.path.insert(0, project_dir)
os.chdir(project_dir)
runpy.run_path(os.path.join(project_dir, "pages", "Rural vs Urban.py"), run_name="__main__")
