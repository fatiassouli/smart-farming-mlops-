import json

for nb_path in ["notebooks/yield_regression_final.ipynb", "notebooks/yield_regression_executed.ipynb"]:
    try:
        with open(nb_path, "r", encoding="utf-8") as f:
            nb = json.load(f)
    except FileNotFoundError:
        print(f"(absent: {nb_path})")
        continue

    print(f"\n=== {nb_path} ===")
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        if "Année" in source or "Year" in source and "min()" in source:
            for out in cell.get("outputs", []):
                if "text" in out:
                    print("".join(out["text"]))
                elif "data" in out and "text/plain" in out["data"]:
                    print("".join(out["data"]["text/plain"]))