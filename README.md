# 고양이 울음소리 해석 — 웹앱 스캐폴딩

이 저장소는 `고양이 울음소리 해석.pptx`를 웹 슬라이드로 보여주는 간단한 React+Vite 앱 템플릿입니다.

설치 및 사용

1. Python으로 PPTX에서 텍스트·이미지를 추출합니다.

```bash
pip install python-pptx
python extract_pptx.py "C:\\Users\\504\\Desktop\\SEO\\고양이 울음소리 해석.pptx" .
```

2. Node 의존성을 설치하고 개발 서버를 실행합니다.

```bash
cd webapp-cat-sounds
npm install
npm run dev
```

3. 브라우저에서 https://bine.kdt2025.com 에 접속하세요.

빌드 및 배포

정적 사이트로 배포하려면 빌드 후 생성된 `dist` 폴더를 정적 호스팅에 업로드하세요.

```bash
cd webapp-cat-sounds
npm run build
# 로컬에서 미리보기
npm run preview
```

간단한 정적 서버로 테스트하려면 `serve` 같은 패키지를 사용하거나, GitHub Pages, Netlify, Vercel 등에 업로드하세요.

자동 배포 설정

- GitHub Pages: 이 리포지토리를 `main` 브랜치에 푸시하면 GitHub Actions가 자동으로 `webapp-cat-sounds` 폴더를 빌드하고 `gh-pages` 브랜치로 배포합니다. 워크플로우 파일은 `.github/workflows/gh-pages.yml`입니다.
- Netlify: `netlify.toml`을 포함했으므로 Netlify에 연결하면 빌드 명령 `npm run build`와 배포 디렉토리 `dist`가 자동으로 사용됩니다.
- Vercel: `vercel.json`이 포함되어 있어 Vercel에 프로젝트를 연결하면 정적 빌드가 자동으로 구성됩니다.

보안 및 주의사항
- 배포 전에 민감한 정보(API 키 등)는 `.env`에 넣고 `.gitignore`에 추가하세요. 리포지토리에 노출된 비밀은 즉시 회수하세요.

서버 기반 오디오 분석 (선택)

프로젝트에 간단한 서버 기반 오디오 분석이 추가되어 있습니다. 로컬에서 실행하려면 Python 가상환경을 만들고 `server/requirements.txt`를 설치한 뒤 서버를 실행하세요.

```bash
cd webapp-cat-sounds
python -m venv .venv
.\.venv\Scripts\activate    # Windows
pip install -r server/requirements.txt
python server/app.py
```

개발 서버(Vite)는 `/api` 경로를 `http://localhost:5000`으로 프록시하도록 설정되어 있습니다. 오디오 업로드 시 프론트엔드에서 서버로도 분석을 전송해 더 상세한 특성(스펙트럴 중심 주파수, RMS 등)을 반환합니다.


기능
- 슬라이드 텍스트 및 슬라이드 내 이미지를 보여줍니다.
- 오디오 업로드 UI가 있으며, 업로드된 오디오의 간단한 메타데이터(재생시간)를 표시합니다. 실제 울음소리 해석은 별도 모델 연동이 필요합니다.

다음 단계 제안
- 오디오 해석 모델(로컬 또는 외부 API) 연동
- 슬라이드 레이아웃/스타일 개선
- 이미지 고해상도 렌더링 및 다운로드 기능


머신러닝 프로토타입 (추가 기능)
--------------------------------
이 프로젝트에는 간단한 특징 기반 학습/예측 엔드포인트가 서버에 추가되어 있습니다. 로컬에서 라벨링된 샘플을 모아 모델을 학습하고 예측할 수 있습니다.

- 요구사항: `server/requirements.txt`에 `scikit-learn`, `joblib`가 추가되었습니다. 서버 가상환경에서 설치하세요.

- 엔드포인트 요약:
	- `POST /api/feature` : 오디오 파일 업로드와 선택적 `label` 폼 필드로 특징(MFCC)을 추출해 `server/dataset`에 저장합니다.
	- `POST /api/train` : `server/dataset`에 저장된 라벨된 샘플로 학습을 수행하고 `server/model.joblib`에 모델을 저장합니다.
	- `POST /api/predict` : 오디오 파일을 업로드하면 학습된 모델로 라벨과 확률을 반환합니다.

예제 사용 순서

1) 샘플 업로드(라벨 포함)

```bash
# curl 예제: 파일과 라벨을 같이 전송
curl -X POST -F "file=@/path/to/meow.wav" -F "label=hunger" http://localhost:5000/api/feature
```

2) 학습 실행

```bash
curl -X POST http://localhost:5000/api/train
```

3) 예측(학습된 모델 필요)

```bash
curl -X POST -F "file=@/path/to/unknown_meow.wav" http://localhost:5000/api/predict
# 반환 예: {"label":"hunger","probability":0.87}
```

주의사항
- 초기 프로토타입은 소규모 데이터·간단 분류기(랜덤포레스트)를 사용합니다. 실서비스용으로 사용하려면 데이터 수집, 검증, 모델 개선(전이학습/CNN 등)이 필요합니다.
- `server/dataset` 폴더에 저장된 `.npz` 파일이 학습 데이터입니다. 라벨이 없는 샘플은 학습에서 제외됩니다.

원하시면 README에 스크린샷과 CI 배지도 추가해드리겠습니다.
