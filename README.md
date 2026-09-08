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

3. 브라우저에서 http://localhost:5173 에 접속하세요.

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
