# 운동기록앱 - AI 차트 이미지 분석

로컬 웹 기반 운동 기록 관리 및 AI 차트 이미지 분석 시스템

## 주요 기능

- ✅ 운동 기록 입력/저장/조회 (날짜, 거리, 시간, 페이스, 메모)
- 🤖 AI 차트 이미지 분석 (OpenAI Vision API - gpt-4o-mini)
- 📊 운동 통계 (총 거리, 총 시간, 총 기록 수)
- 📱 반응형 웹 UI (모바일/데스크톱 지원)
- 💾 로컬 SQLite 데이터베이스 (데이터 완전 통제)
- 🔐 환경변수 기반 API 키 관리

## 차별점

- **앱 중립적 AI 분석**: Strava, Nike Run Club 등 다른 앱의 차트 스크린샷 분석 가능
- **로컬 우선 아키텍처**: 서버 비용 없이 로컬 실행
- **저비용 AI**: gpt-4o-mini 활용으로 분석당 약 $0.0003 (월 $0.30 예상)
- **이미지 최적화**: 자동 리사이징/압축으로 토큰 70% 절감

---

## 설치 방법

### 1. 사전 요구사항
- Python 3.9 이상
- OpenAI API 키 ([발급 방법](https://platform.openai.com/api-keys))

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정
`.env` 파일 생성 (`.env.example` 참고):
```bash
cp .env.example .env
```

`.env` 파일에 OpenAI API 키 입력:
```
OPENAI_API_KEY=sk-proj-your-api-key-here
```

---

## 실행 방법

### 서버 시작
```bash
python app.py
```

또는

```bash
uvicorn app:app --reload
```

### 접속
브라우저에서 다음 주소 열기:
```
http://localhost:8000
```

---

## 사용 방법

### 1. 운동 기록 입력
1. "운동 기록" 탭 선택
2. 날짜, 거리, 시간, 페이스, 메모 입력
3. "기록 저장" 클릭

### 2. AI 차트 분석
1. "AI 차트 분석" 탭 선택
2. Strava, Nike Run Club 등의 차트 스크린샷 업로드 (JPG/PNG, 최대 2MB)
3. "AI 분석 시작" 클릭
4. 5초 이내 분석 결과 표시

### 3. 히스토리 조회
1. "기록 히스토리" 탭 선택
2. 과거 운동 기록 및 AI 분석 결과 확인

---

## 프로젝트 구조

```
deliverable/
├── app.py                      # FastAPI 진입점
├── requirements.txt            # Python 의존성
├── .env.example                # 환경변수 예시
├── database/
│   ├── database.py             # SQLAlchemy 연결 설정
│   └── models.py               # ORM 모델 (WorkoutRecord, AIAnalysis)
├── services/
│   ├── openai_analyzer.py      # OpenAI Vision API 통합
│   └── image_processor.py      # 이미지 전처리 (리사이징, 압축)
├── routers/
│   ├── records.py              # 운동 기록 CRUD API
│   └── analysis.py             # AI 분석 API
├── frontend/
│   ├── index.html              # 메인 UI
│   ├── styles.css              # 스타일
│   └── app.js                  # 프론트엔드 로직
├── uploads/                    # 업로드 이미지 저장 (git ignore)
│   ├── analyzed/               # 분석 완료 이미지
│   └── temp/                   # 임시 이미지
└── workout.db                  # SQLite 데이터베이스 (자동 생성)
```

---

## API 엔드포인트

### 운동 기록
- `POST /api/records` - 기록 생성
- `GET /api/records` - 전체 목록 조회
- `GET /api/records/{id}` - 단일 조회
- `PUT /api/records/{id}` - 수정
- `DELETE /api/records/{id}` - 삭제
- `GET /api/records/stats` - 통계

### AI 분석
- `POST /api/analyses` - 이미지 업로드 + 분석
- `GET /api/analyses` - 분석 이력 조회
- `GET /api/analyses/{id}` - 단일 분석 조회

### 기타
- `GET /` - 메인 페이지
- `GET /health` - 헬스체크

자세한 API 문서는 서버 실행 후 `http://localhost:8000/docs` 참고

---

## 예상 비용

### 개발 비용
- 약 $0.012 (1회)

### 운영 비용 (월간)
- **최적화 전**: 월 30회 분석 → 약 $2.70
- **최적화 후**: 월 30회 분석 → 약 $0.30 (이미지 압축 + 프롬프트 최적화)
- **1회 분석당**: 약 $0.0003

### 절감 포인트
1. 이미지 자동 리사이징 (1024x1024) - 70% 토큰 절감
2. `detail: "low"` 옵션 - 85% 이미지 토큰 절감
3. 프롬프트 최적화 (간결한 지시) - 60% 토큰 절감
4. 응답 토큰 제한 (max_tokens=300)

---

## 문제 해결

### OpenAI API 키 오류
- `.env` 파일에 올바른 API 키가 설정되었는지 확인
- API 키 유효성 확인: https://platform.openai.com/api-keys

### 이미지 업로드 실패
- 파일 크기 2MB 이하 확인
- JPG/PNG 형식 확인
- `uploads/temp`, `uploads/analyzed` 디렉토리 쓰기 권한 확인

### 데이터베이스 오류
- `workout.db` 파일 삭제 후 재실행 (데이터베이스 재생성)

---

## 향후 개선 계획

### 단기
- [ ] AI 프롬프트 개선 (차트 유형별 최적화)
- [ ] 드래그 앤 드롭 이미지 업로드
- [ ] 에러 메시지 개선

### 중기
- [ ] 배치 이미지 분석 (여러 차트 동시 비교)
- [ ] 데이터 내보내기 (CSV, JSON)
- [ ] 분석 템플릿 (주간 요약, 월간 추세)

### 장기
- [ ] 웨어러블 기기 연동 (Apple Health, Google Fit)
- [ ] 커뮤니티 기능 (익명화된 분석 결과 공유)
- [ ] Fine-tuned 모델로 운동 특화 분석 강화

---

## 라이선스
MIT

## 문의
GitHub Issues: [프로젝트 링크]

---

## 기술 스택
- **백엔드**: FastAPI 0.115, SQLAlchemy 2.0, aiosqlite
- **AI**: OpenAI gpt-4o-mini Vision API
- **프론트엔드**: Vanilla HTML/CSS/JavaScript
- **데이터베이스**: SQLite
- **이미지 처리**: Pillow
