"""
problem_framing.py — Skrip analisis heuristik cerdas untuk Problem Framing
Menerima file (gambar/CSV/teks), dan mengeluarkan IPO (Input, Proses, Output) yang disarankan AI.
"""
import sys
import json
import os

def safe_json(data):
    print(json.dumps(data, ensure_ascii=False))
    sys.exit(0)

def analyze_image(file_path, filename):
    try:
        from PIL import Image
        with Image.open(file_path) as img:
            width, height = img.size
            mode = img.mode
            format = img.format
            
        input_desc = f"Data Gambar ({format}). Dimensi: {width}x{height} pixel. Mode warna: {mode}."
        
        # Heuristic processing logic
        if width > 1000 and height > 1000:
            process_desc = "Arsitektur Computer Vision skala besar (misal: ResNet50, YOLOv8) menggunakan Convolutional Neural Networks (CNN) dengan preprocessing resizing dan augmentasi spasial."
            output_desc = "Prediksi deteksi objek (Bounding Boxes), segmentasi pixel, atau klasifikasi kategori gambar tingkat tinggi."
            category = "klasifikasi"
            title = f"Object Detection / High-Res Vision: {filename}"
        elif mode == 'L' or (width < 256 and height < 256):
            process_desc = "Model Convolutional Neural Networks (CNN) ringan (misal: MobileNet) atau Multi-Layer Perceptron (MLP) dengan normalisasi pixel scaling (0-1)."
            output_desc = "Label kelas gambar (Classification) atau probabilitas kemiripan."
            category = "klasifikasi"
            title = f"Basic Image Classification: {filename}"
        else:
            process_desc = "Deep Learning berbasis Computer Vision (CNN/Vision Transformer) dengan ekstraksi fitur gambar 2D."
            output_desc = "Kategorisasi label gambar atau ekstraksi teks (OCR)."
            category = "klasifikasi"
            title = f"Computer Vision Model: {filename}"
            
        return {
            "title": title,
            "category": category,
            "input": input_desc,
            "process": process_desc,
            "output": output_desc
        }
    except Exception as e:
        return {"error": f"Gagal membaca gambar: {str(e)}"}

def analyze_tabular(file_path, filename):
    try:
        import pandas as pd
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)
            
        rows, cols = df.shape
        num_cols = len(df.select_dtypes(include=['number']).columns)
        cat_cols = len(df.select_dtypes(include=['object', 'category']).columns)
        
        input_desc = f"Dataset Tabular dengan {rows} baris dan {cols} kolom ({num_cols} numerik, {cat_cols} kategorikal)."
        
        # Check if Time Series
        is_timeseries = False
        for c in df.columns[:3]: # Check first few cols for dates
            if 'date' in c.lower() or 'time' in c.lower():
                is_timeseries = True
                break
                
        if is_timeseries:
            process_desc = "Model Time Series Forecasting (misal: ARIMA, LSTM, Prophet) dengan ekstraksi fitur lag dan seasonal decomposition."
            output_desc = "Prediksi deret waktu masa depan (Forecasting nilai/trend)."
            category = "regresi"
            title = f"Time Series Forecasting: {filename}"
        elif cat_cols == 0 and num_cols > 10:
            process_desc = "Model Unsupervised Learning (K-Means, PCA) atau Neural Network karena dataset full-numerik berdimensi tinggi."
            output_desc = "Clustering kelompok data atau reduksi dimensi (Anomaly Detection)."
            category = "klasterisasi"
            title = f"Numeric Clustering/Analysis: {filename}"
        else:
            process_desc = "Supervised Machine Learning (Random Forest, XGBoost, atau Regresi Logistik) dengan Encoding kategorikal dan Scaling numerik."
            output_desc = "Prediksi klasifikasi target (Label) atau prediksi nilai numerik kontinu."
            category = "klasifikasi"
            title = f"Tabular Predictive Model: {filename}"
            
        return {
            "title": title,
            "category": category,
            "input": input_desc,
            "process": process_desc,
            "output": output_desc
        }
    except Exception as e:
        return {"error": f"Gagal membaca dataset tabular: {str(e)}"}

def analyze_text(file_path, filename):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(5000) # Read up to 5k chars
            
        length = len(content)
        lines = content.split('\n')
        
        input_desc = f"Data Teks tidak terstruktur. Panjang sampel: {length} karakter, ~{len(lines)} baris."
        
        if length > 2000:
            process_desc = "Natural Language Processing (NLP) tingkat lanjut, seperti Large Language Models (LLM) atau Longformer untuk peringkasan dan ekstraksi konteks panjang."
            output_desc = "Teks ringkasan (Summarization), Ekstraksi Entitas (NER), atau Analisis Sentimen Dokumen."
            category = "klasifikasi" # Text processing mostly
            title = f"Document NLP Analysis: {filename}"
        else:
            process_desc = "Pemrosesan Teks (NLP) konvensional dengan Tokenisasi, TF-IDF, atau model Transformer ringan (BERT) untuk analisis semantik."
            output_desc = "Klasifikasi topik, Analisis Sentimen (Positif/Negatif), atau klasifikasi intent."
            category = "klasifikasi"
            title = f"Text Classification: {filename}"
            
        return {
            "title": title,
            "category": category,
            "input": input_desc,
            "process": process_desc,
            "output": output_desc
        }
    except Exception as e:
         return {"error": f"Gagal membaca file teks: {str(e)}"}

def main():
    if len(sys.argv) < 2:
        safe_json({"error": "No file path provided"})
        
    file_path = sys.argv[1]
    filename = os.path.basename(file_path)
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.webp']:
        result = analyze_image(file_path, filename)
    elif ext in ['.csv', '.xlsx', '.xls', '.json']:
        result = analyze_tabular(file_path, filename)
    elif ext in ['.txt', '.md', '.log']:
        result = analyze_text(file_path, filename)
    else:
        # Fallback
        result = {
            "title": f"Custom AI Model: {filename}",
            "category": "klasifikasi",
            "input": f"File mentah dengan ekstensi {ext}.",
            "process": "Deep Learning / Machine Learning pipeline (Feature Extraction + Prediction).",
            "output": "Pola prediksi berdasarkan struktur file khusus."
        }
        
    safe_json(result)

if __name__ == "__main__":
    main()
