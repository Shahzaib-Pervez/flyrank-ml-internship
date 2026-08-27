"""
===============================================================================
EXECUTE_W07_CELLS.PY
Populates executed outputs for each code cell in w07_action_playbook.ipynb.
===============================================================================
"""

import json
import os
import sys
import io
import contextlib

def run_w07_cells():
    nb_path = "work/notebooks/w07_action_playbook.ipynb"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    exec_idx = 1
    gl = {"__name__": "__main__"}

    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            cell["execution_count"] = exec_idx
            code = "".join(cell["source"])
            
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                try:
                    exec(code, gl)
                except Exception as e:
                    print(f"Exception during cell execution: {e}")
                    
            out_text = buf.getvalue()
            if out_text:
                cell["outputs"] = [
                    {
                        "name": "stdout",
                        "output_type": "stream",
                        "text": out_text.splitlines(keepends=True)
                    }
                ]
            else:
                cell["outputs"] = []
                
            exec_idx += 1

    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2)

    print(f"[Execution Complete] Saved populated notebook to {nb_path}")

if __name__ == "__main__":
    run_w07_cells()
