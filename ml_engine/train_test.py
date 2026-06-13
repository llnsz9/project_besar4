"""
train_test.py — Melatih model pilihan user dan mengembalikan metrik evaluasi
Usage: python train_test.py <file_path> <target_column> <model_name>
Output: JSON ke stdout
"""
import sys
import json
import os
import pandas as pd
import numpy as np
import warnings
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, r2_score, mean_absolute_error, mean_squared_error

# Models
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor

warnings.filterwarnings('ignore')

def safe_val(v):
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v) if not np.isnan(v) else None
    if isinstance(v, np.ndarray):
        return v.tolist()
    return v

def train_and_evaluate(file_path, target_col, model_name):
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

    df = df.dropna(subset=[target_col])
    
    # --- Preprocessing Target ---
    y = df[target_col]
    task_type = "classification"
    label_classes = []
    
    if pd.api.types.is_numeric_dtype(y) and y.nunique() > 15:
        task_type = "regression"
    else:
        if y.dtype == 'object' or str(y.dtype) == 'category':
            le = LabelEncoder()
            y = le.fit_transform(y)
            label_classes = le.classes_.tolist()
        else:
            label_classes = sorted(y.unique().tolist())
    
    X = df.drop(columns=[target_col])
    
    # --- Preprocessing Features ---
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()
    categorical_features = [c for c in categorical_features if X[c].nunique() <= 20]
    
    X = X[numeric_features + categorical_features]
    
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

    # --- Select Model ---
    model = None
    if task_type == "classification":
        if model_name == "Logistic Regression": model = LogisticRegression(max_iter=1000, random_state=42)
        elif model_name == "Decision Tree": model = DecisionTreeClassifier(random_state=42)
        elif model_name == "Random Forest": model = RandomForestClassifier(n_estimators=100, random_state=42)
        elif model_name == "SVM": model = SVC(probability=True, random_state=42)
        elif model_name == "KNN": model = KNeighborsClassifier()
        else: model = RandomForestClassifier(n_estimators=100, random_state=42) # default
    else:
        if model_name == "Linear Regression": model = LinearRegression()
        elif model_name == "Decision Tree": model = DecisionTreeRegressor(random_state=42)
        elif model_name == "Random Forest": model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_name == "SVR": model = SVR()
        elif model_name == "KNN": model = KNeighborsRegressor()
        else: model = RandomForestRegressor(n_estimators=100, random_state=42) # default

    clf = Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])
    
    # --- Split & Train ---
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y if task_type=='classification' else None)
    
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    
    # --- Evaluation ---
    metrics = {}
    extra = {}
    
    if task_type == "classification":
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        cm = confusion_matrix(y_test, y_pred)
        
        metrics = {
            "accuracy": safe_val(acc),
            "precision": safe_val(prec),
            "recall": safe_val(rec),
            "f1_score": safe_val(f1)
        }
        extra["confusion_matrix"] = safe_val(cm)
        extra["classes"] = [str(c) for c in label_classes]
    else:
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        metrics = {
            "r2_score": safe_val(r2),
            "mae": safe_val(mae),
            "rmse": safe_val(rmse)
        }
        # Ambil sampel aktual vs predikisi untuk scatter plot (max 50)
        sample_size = min(50, len(y_test))
        indices = np.random.choice(len(y_test), sample_size, replace=False)
        actual_sample = safe_val(np.array(y_test)[indices])
        pred_sample = safe_val(y_pred[indices])
        extra["scatter"] = {"actual": actual_sample, "predicted": pred_sample}

    # --- Feature Importance (if applicable) ---
    feature_importance = []
    try:
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            # Get feature names after one-hot encoding
            # This can be tricky, so we'll do a simple heuristic for numeric features at least
            # To be robust, if we can't get exact names, we skip or provide generic
            feat_names = numeric_features
            try:
                cat_encoder = preprocessor.named_transformers_['cat'].named_steps['onehot']
                cat_names = cat_encoder.get_feature_names_out(categorical_features).tolist()
                feat_names = feat_names + cat_names
            except:
                feat_names = [f"Feature {i}" for i in range(len(importances))]
                
            if len(importances) == len(feat_names):
                fi = list(zip(feat_names, importances))
                fi.sort(key=lambda x: x[1], reverse=True)
                feature_importance = [{"feature": k, "importance": safe_val(v)} for k, v in fi[:10]]
        elif hasattr(model, 'coef_'):
            importances = np.abs(model.coef_)
            if len(importances.shape) > 1:
                 importances = importances[0] # Multiclass logistic
            feat_names = numeric_features
            try:
                cat_encoder = preprocessor.named_transformers_['cat'].named_steps['onehot']
                cat_names = cat_encoder.get_feature_names_out(categorical_features).tolist()
                feat_names = feat_names + cat_names
            except:
                feat_names = [f"Feature {i}" for i in range(len(importances))]
            
            if len(importances) == len(feat_names):
                fi = list(zip(feat_names, importances))
                fi.sort(key=lambda x: x[1], reverse=True)
                feature_importance = [{"feature": k, "importance": safe_val(v)} for k, v in fi[:10]]
    except Exception:
        pass # Ignore feature importance errors safely

    return {
        "task_type": task_type,
        "model_name": model_name,
        "metrics": metrics,
        "extra": extra,
        "feature_importance": feature_importance,
        "train_samples": len(X_train),
        "test_samples": len(X_test)
    }

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(json.dumps({"error": "Usage: python train_test.py <file_path> <target_column> <model_name>"}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    target_col = sys.argv[2]
    model_name = sys.argv[3]
    
    result = train_and_evaluate(file_path, target_col, model_name)
    print(json.dumps(result, ensure_ascii=False))
