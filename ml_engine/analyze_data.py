"""
analyze_data.py — Analisis dataset yang diunggah user
Usage: python analyze_data.py <file_path> [target_column]
Output: JSON ke stdout
"""
import sys
import json
import os
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def safe_val(v):
    """Konversi nilai numpy/pandas ke tipe Python standar agar JSON-serializable."""
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v) if not np.isnan(v) else None
    if isinstance(v, (np.ndarray,)):
        return v.tolist()
    if isinstance(v, pd.Series):
        return v.tolist()
    return v

def analyze(file_path, target_col=None):
    # --- Load file ---
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            # Coba beberapa separator
            for sep in [',', ';', '\t']:
                try:
                    df = pd.read_csv(file_path, sep=sep, encoding='utf-8')
                    if df.shape[1] > 1:
                        break
                except Exception:
                    continue
    except Exception as e:
        return {"error": f"Gagal membaca file: {str(e)}"}

    n_rows, n_cols = df.shape
    
    # --- Profiling kolom ---
    columns_info = []
    numeric_cols = []
    categorical_cols = []
    
    for col in df.columns:
        dtype = str(df[col].dtype)
        missing = int(df[col].isna().sum())
        unique = int(df[col].nunique())
        
        col_info = {
            "name": col,
            "dtype": dtype,
            "missing": missing,
            "missing_pct": round(missing / n_rows * 100, 1),
            "unique": unique,
        }
        
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric_cols.append(col)
            col_info["type"] = "numeric"
            col_info["min"] = safe_val(df[col].min())
            col_info["max"] = safe_val(df[col].max())
            col_info["mean"] = safe_val(round(df[col].mean(), 4)) if not df[col].isna().all() else None
            col_info["std"] = safe_val(round(df[col].std(), 4)) if not df[col].isna().all() else None
            # Sample histogram (10 bins)
            try:
                counts, edges = np.histogram(df[col].dropna(), bins=10)
                col_info["histogram"] = {
                    "counts": counts.tolist(),
                    "edges": [round(float(e), 4) for e in edges]
                }
            except Exception:
                pass
        else:
            categorical_cols.append(col)
            col_info["type"] = "categorical"
            top_vals = df[col].value_counts().head(5).to_dict()
            col_info["top_values"] = {str(k): int(v) for k, v in top_vals.items()}
        
        columns_info.append(col_info)
    
    # --- Deteksi task type berdasar kolom target ---
    task_type = "unknown"
    target_info = {}
    
    if target_col and target_col in df.columns:
        col = df[target_col]
        n_unique = col.nunique()
        if pd.api.types.is_numeric_dtype(col) and n_unique > 15:
            task_type = "regression"
        else:
            task_type = "classification"
            classes = col.value_counts().to_dict()
            target_info["classes"] = {str(k): int(v) for k, v in classes.items()}
            target_info["n_classes"] = n_unique
            # Cek class imbalance
            counts = list(classes.values())
            if counts and max(counts) / sum(counts) > 0.8:
                target_info["imbalance_warning"] = True
    elif target_col is None:
        # Auto-detect: kolom terakhir biasanya target
        last_col = df.columns[-1]
        n_unique_last = df[last_col].nunique()
        if pd.api.types.is_numeric_dtype(df[last_col]) and n_unique_last > 15:
            task_type = "regression"
        else:
            task_type = "classification"
    
    # --- Korelasi numerik ---
    correlation = {}
    if len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr().round(3)
        correlation = {
            col: {c: safe_val(v) for c, v in row.items() if pd.notna(v)}
            for col, row in corr_matrix.to_dict().items()
        }
    
    # --- Preview data ---
    preview = df.head(5).fillna("").astype(str).to_dict(orient='records')
    
    # --- Skor kualitas data ---
    total_cells = n_rows * n_cols
    total_missing = df.isna().sum().sum()
    quality_score = round((1 - total_missing / total_cells) * 100, 1) if total_cells > 0 else 0

    result = {
        "shape": {"rows": n_rows, "cols": n_cols},
        "quality_score": quality_score,
        "columns": columns_info,
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "task_type": task_type,
        "target_info": target_info,
        "correlation": correlation,
        "preview": preview,
        "suggested_target": df.columns[-1] if len(df.columns) > 0 else None
    }
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python analyze_data.py <file_path> [target_column]"}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    target_col = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = analyze(file_path, target_col)
    print(json.dumps(result, ensure_ascii=False))
