from flask import Flask, request, jsonify
import os
import uuid
import librosa
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

app = Flask(__name__)
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)
DATASET_DIR = os.path.join(os.path.dirname(__file__), 'dataset')
os.makedirs(DATASET_DIR, exist_ok=True)
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.joblib')


def analyze_audio(path):
    y, sr = librosa.load(path, sr=None, mono=True)
    duration = librosa.get_duration(y=y, sr=sr)
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    centroid_mean = float(centroid.mean()) if centroid.size else 0.0
    rms = float(librosa.feature.rms(y=y).mean())

    # approximate dominant frequency from centroid
    dominant_freq = centroid_mean

    # heuristic labeling
    if dominant_freq > 2000:
        label = '높은 음 — 긍정/관심 요청 가능성'
    elif dominant_freq > 800:
        label = '중간 음 — 일반적 요청'
    else:
        label = '낮은 음 — 경고/불만 가능성'

    # urgency from RMS
    urgency = '낮음'
    if rms > 0.05:
        urgency = '높음'
    elif rms > 0.02:
        urgency = '중간'

    return {
        'duration': round(duration, 2),
        'dominant_freq': round(dominant_freq, 1),
        'rms': round(rms, 5),
        'label': label,
        'urgency': urgency
    }


def extract_features(path, n_mfcc=13):
    y, sr = librosa.load(path, sr=None, mono=True)
    # MFCC mean and std
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    mfcc_mean = mfcc.mean(axis=1)
    mfcc_std = mfcc.std(axis=1)
    features = np.concatenate([mfcc_mean, mfcc_std])
    return features


@app.route('/api/feature', methods=['POST'])
def upload_feature():
    if 'file' not in request.files:
        return jsonify({'error': 'file missing'}), 400
    f = request.files['file']
    label = request.form.get('label')  # optional label for supervised data
    filename = f.filename or f"upload_{uuid.uuid4().hex}.wav"
    save_path = os.path.join(UPLOAD_DIR, filename)
    f.save(save_path)

    try:
        feats = extract_features(save_path)
        sample_id = uuid.uuid4().hex
        out_path = os.path.join(DATASET_DIR, f"{sample_id}.npz")
        np.savez(out_path, features=feats, label=label)
        return jsonify({'status': 'saved', 'sample': sample_id, 'label': label})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/train', methods=['POST'])
def train_model():
    # load dataset
    files = [os.path.join(DATASET_DIR, p) for p in os.listdir(DATASET_DIR) if p.endswith('.npz')]
    X = []
    y = []
    for p in files:
        try:
            d = np.load(p, allow_pickle=True)
            feats = d['features']
            lbl = d['label'].tolist() if hasattr(d['label'], 'tolist') else d['label']
            if lbl is None or lbl == 'None' or lbl == '':
                continue
            X.append(feats)
            y.append(lbl)
        except Exception:
            continue
    if len(X) < 2:
        return jsonify({'error': 'not enough labeled samples (need >=2)'}), 400

    X = np.vstack(X)
    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    clf = RandomForestClassifier(n_estimators=100)
    clf.fit(X, y_enc)
    joblib.dump({'model': clf, 'le': le}, MODEL_PATH)
    return jsonify({'status': 'trained', 'samples': len(y)})


@app.route('/api/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'file missing'}), 400
    if not os.path.exists(MODEL_PATH):
        return jsonify({'error': 'model not trained'}), 400
    f = request.files['file']
    filename = f.filename or f"upload_{uuid.uuid4().hex}.wav"
    save_path = os.path.join(UPLOAD_DIR, filename)
    f.save(save_path)

    try:
        feats = extract_features(save_path)
        data = joblib.load(MODEL_PATH)
        clf = data['model']
        le = data['le']
        probs = clf.predict_proba(feats.reshape(1, -1))[0]
        idx = int(np.argmax(probs))
        label = le.inverse_transform([idx])[0]
        return jsonify({'label': label, 'probability': float(probs[idx])})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'file missing'}), 400
    f = request.files['file']
    filename = f.filename or f"upload_{uuid.uuid4().hex}.wav"
    save_path = os.path.join(UPLOAD_DIR, filename)
    f.save(save_path)

    try:
        result = analyze_audio(save_path)
        result['name'] = filename
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
