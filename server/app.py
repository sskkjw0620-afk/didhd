from flask import Flask, request, jsonify
import os
import uuid
import librosa

app = Flask(__name__)
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)


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
