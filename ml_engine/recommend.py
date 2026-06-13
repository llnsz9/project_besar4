"""
recommend.py — Merekomendasikan model AI terbaik untuk dataset yang diberikan
Usage: python recommend.py <file_path> <target_column>
Output: JSON ke stdout
"""
import sys
import json
import os
import pandas as pd
import numpy as np
import warnings
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

# Classification Models
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

# Regression Models
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor

warnings.filterwarnings('ignore')

def safe_val(v):
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v) if not np.isnan(v) else None
    return v

def recommend_models(file_path, target_col):
    # --- Load file ---
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            for sep in [',', ';', '\t']:
                try:
                    df = pd.read_csv(file_path, sep=sep, encoding='utf-8')
                    if df.shape[1] > 1:
                        break
                except Exception:
                    continue
    except Exception as e:
        return {"error": f"Gagal membaca file: {str(e)}"}

    if target_col not in df.columns:
        return {"error": f"Kolom target '{target_col}' tidak ditemukan."}

    # Hapus baris di mana target missing
    df = df.dropna(subset=[target_col])
    
    if len(df) < 20:
        return {"error": "Data terlalu sedikit (kurang dari 20 baris efektif)."}

    # --- Preprocessing Target ---
    y = df[target_col]
    task_type = "classification"
    
    # Deteksi Task
    if pd.api.types.is_numeric_dtype(y) and y.nunique() > 15:
        task_type = "regression"
    else:
        # Jika klasifikasi tapi berupa string, encode
        if y.dtype == 'object' or str(y.dtype) == 'category':
            le = LabelEncoder()
            y = le.fit_transform(y)
    
    X = df.drop(columns=[target_col])
    
    # --- Preprocessing Features ---
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Batasi kategorikal features yang cardinality-nya terlalu tinggi (misal > 20)
    categorical_features = [c for c in categorical_features if X[c].nunique() <= 20]
    
    X = X[numeric_features + categorical_features]
    
    if X.shape[1] == 0:
        return {"error": "Tidak ada fitur numerik atau kategorikal yang valid untuk dilatih."}

    # Buat preprocessor
    from sklearn.preprocessing import OneHotEncoder
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    # --- Definisikan Model Benchmark ---
    if task_type == "classification":
        models = {
            "Logistic Regression": LogisticRegression(max_iter=500, random_state=42),
            "Decision Tree": DecisionTreeClassifier(random_state=42),
            "Random Forest": RandomForestClassifier(n_estimators=50, random_state=42),
            "SVM": SVC(kernel='rbf', probability=True, random_state=42),
            "KNN": KNeighborsClassifier(n_neighbors=min(5, len(X)//2))
        }
        scoring = 'accuracy'
    else:
        models = {
            "Linear Regression": LinearRegression(),
            "Decision Tree": DecisionTreeRegressor(random_state=42),
            "Random Forest": RandomForestRegressor(n_estimators=50, random_state=42),
            "SVR": SVR(kernel='rbf'),
            "KNN": KNeighborsRegressor(n_neighbors=min(5, len(X)//2))
        }
        scoring = 'r2'

    # Sampling jika data terlalu besar agar cepat
    sample_size = min(len(X), 2000)
    X_sample, _, y_sample, _ = train_test_split(X, y, train_size=sample_size, stratify=y if task_type=='classification' else None, random_state=42)
    
    cv_splits = min(5, len(np.unique(y_sample)) if task_type=='classification' else 5)
    if cv_splits < 2:
        cv_splits = 2

    results = []
    
    for name, model in models.items():
        clf = Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])
        try:
            scores = cross_val_score(clf, X_sample, y_sample, cv=cv_splits, scoring=scoring, n_jobs=-1)
            mean_score = np.mean(scores)
            results.append({
                "model_name": name,
                "score": max(0, safe_val(mean_score)), # Cegah skor R2 negatif ekstrim
                "metric": scoring
            })
        except Exception as e:
             results.append({
                "model_name": name,
                "score": 0.0,
                "metric": scoring,
                "error": str(e)
            })

    # Sort dari skor tertinggi
    results.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    # Tambahkan penjelasan
    for r in results:
        name = r['model_name']
        desc = ""
        if name == "Random Forest":
            desc = "Sangat kuat menangani data kompleks dan non-linear. Tahan terhadap overfitting."
        elif name in ["Logistic Regression", "Linear Regression"]:
            desc = "Cepat, sederhana, dan mudah diinterpretasikan. Cocok untuk hubungan linear."
        elif name == "SVM" or name == "SVR":
            desc = "Bagus untuk dataset berukuran kecil hingga sedang dengan batas keputusan yang rumit."
        elif name == "Decision Tree":
            desc = "Mudah dipahami seperti aturan IF-THEN, namun rentan overfitting jika tidak dibatasi."
        elif name == "KNN":
            desc = "Mencari pola berdasarkan kemiripan data terdekat. Cukup lambat untuk data besar."
        r["description"] = desc

    return {
        "task_type": task_type,
        "target_column": target_col,
        "recommendations": results
    }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: python recommend.py <file_path> <target_column>"}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    target_col = sys.argv[2]
    
    result = recommend_models(file_path, target_col)
    print(json.dumps(result, ensure_ascii=False))
