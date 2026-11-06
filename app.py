import os
import runpy
import sys


project_dir = os.path.join(os.path.dirname(__file__), "Plotly Projects")
sys.path.insert(0, project_dir)
os.chdir(project_dir)
runpy.run_path(os.path.join(project_dir, "app.py"), run_name="__main__")
