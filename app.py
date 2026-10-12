from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database.database import init_db
from routers import records, analysis
import os

app = FastAPI(
    title="운동기록앱 API",
    description="AI 차트 이미지 분석 기능을 포함한 운동 기록 관리 시스템",
    version="1.0.0"
)

# 라우터 등록
app.include_router(records.router)
app.include_router(analysis.router)

# 정적 파일 제공 (프론트엔드)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# 업로드 이미지 제공
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.on_event("startup")
async def startup_event():
    """앱 시작 시 데이터베이스 초기화"""
    # 업로드 디렉토리 생성 (Vercel에서는 /tmp 사용)
    upload_base = "/tmp" if os.getenv("VERCEL") else "."
    os.makedirs(f"{upload_base}/uploads/analyzed", exist_ok=True)
    os.makedirs(f"{upload_base}/uploads/temp", exist_ok=True)

    # DB 테이블 생성
    await init_db()
    print("✓ 데이터베이스 초기화 완료")
    print("✓ 서버 시작: http://localhost:8000")


@app.get("/")
async def root():
    """메인 페이지"""
    return FileResponse("frontend/index.html")


@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy", "message": "운동기록앱 API 정상 작동 중"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
