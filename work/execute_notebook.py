"""
===============================================================================
EXECUTE_NOTEBOOK.PY
Executes code cells in w07_action_playbook.ipynb and populates output objects.
===============================================================================
"""

import json
import os
import sys
import io
import contextlib

def run_and_populate_notebook(nb_path="work/notebooks/w07_action_playbook.ipynb"):
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    exec_counter = 1

    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            cell["execution_count"] = exec_counter
            code = "".join(cell["source"])
            
            output_buf = io.StringIO()
            with contextlib.redirect_stdout(output_buf), contextlib.redirect_stderr(output_buf):
                try:
                    exec(code, globals())
                except Exception as e:
                    print(f"Cell execution exception: {e}")
                    
            output_str = output_buf.getvalue()
            cell["outputs"] = [
                {
                    "name": "stdout",
                    "output_type": "stream",
                    "text": output_str.splitlines(keepends=True)
                }
            ]
            exec_counter += 1

    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2)

    print(f"[Notebook Executed & Saved] {nb_path}")

if __name__ == "__main__":
    run_and_populate_notebook()
