import json
import pandas as pd
from pathlib import Path

path = Path('Fixers_list.xlsx')
if not path.exists():
    print(json.dumps({"error": "Fixers_list.xlsx not found"}))
    raise SystemExit(0)

xls = pd.ExcelFile(path)
summary = {"sheets": []}
for s in xls.sheet_names:
    info = {"sheet": s}
    try:
        df = pd.read_excel(xls, sheet_name=s)
        info["columns"] = list(df.columns.astype(str))
        cols_req = ["Category", "Module", "Language", "Fixers Email"]
        info["has_required_columns"] = all(c in df.columns for c in cols_req)
        # Count rows with missing fixer emails
        info["missing_fixers_count"] = int(df.get("Fixers Email").isna().sum()) if "Fixers Email" in df.columns else None
        # Sample a few rows missing fixers
        if "Fixers Email" in df.columns:
            sample = df[df["Fixers Email"].isna()].head(5)
            info["sample_missing_rows"] = sample.to_dict(orient="records")
    except Exception as e:
        info["error"] = str(e)
    summary["sheets"].append(info)

print(json.dumps(summary, ensure_ascii=False))
