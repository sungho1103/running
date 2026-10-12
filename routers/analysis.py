import os
import uuid
import hashlib
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database.database import get_db
from database.models import AIAnalysis
from services.openai_analyzer import analyze_workout_chart
from services.image_processor import preprocess_image, validate_image
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter(prefix="/api/analyses", tags=["analyses"])

UPLOAD_DIR = "uploads/analyzed"


def calculate_image_hash(file_path: str) -> str:
    """이미지 파일의 SHA-256 해시 계산"""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


class AnalysisResponse(BaseModel):
    id: int
    image_path: str
    analysis_result: str
    tokens_used: Optional[int]
    cost: Optional[float]
    created_at: datetime
    record_id: Optional[int]

    class Config:
        from_attributes = True


@router.post("", response_model=AnalysisResponse)
async def create_analysis(
    image: UploadFile = File(...),
    record_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """이미지 업로드 및 AI 분석 실행"""

    # 파일 형식 검증
    if image.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="JPG/PNG만 지원됩니다")

    # 임시 저장
    temp_filename = f"{uuid.uuid4()}.jpg"
    temp_filepath = f"uploads/temp/{temp_filename}"

    try:
        # 파일 저장
        content = await image.read()
        with open(temp_filepath, "wb") as f:
            f.write(content)

        # 파일 검증
        if not validate_image(temp_filepath):
            raise HTTPException(status_code=400, detail="유효하지 않은 이미지 파일입니다")

        # 이미지 전처리
        processed_path = preprocess_image(temp_filepath)

        # 이미지 해시 계산 (캐싱용)
        image_hash = calculate_image_hash(processed_path)

        # 캐시 확인: 동일 이미지 분석 이력 조회
        cache_result = await db.execute(
            select(AIAnalysis).where(AIAnalysis.image_hash == image_hash)
        )
        cached_analysis = cache_result.scalar_one_or_none()

        if cached_analysis:
            # 캐시 히트: 기존 분석 결과 재사용
            os.remove(processed_path)  # 전처리된 임시 파일 삭제
            return cached_analysis

        # 최종 저장 경로로 이동
        final_filename = f"{uuid.uuid4()}.jpg"
        final_filepath = f"{UPLOAD_DIR}/{final_filename}"
        os.rename(processed_path, final_filepath)

        # AI 분석
        result = await analyze_workout_chart(final_filepath)

        # DB 저장
        new_analysis = AIAnalysis(
            image_path=final_filepath,
            image_hash=image_hash,
            analysis_result=result["analysis"],
            tokens_used=result["tokens"],
            cost=result["cost"],
            record_id=record_id
        )
        db.add(new_analysis)
        await db.commit()
        await db.refresh(new_analysis)

        return new_analysis

    except ValueError as e:
        # 에러 시 임시 파일 정리
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 에러 시 임시 파일 정리
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        raise HTTPException(status_code=500, detail=f"분석 실패: {str(e)}")


@router.get("", response_model=List[AnalysisResponse])
async def get_analyses(db: AsyncSession = Depends(get_db)):
    """AI 분석 이력 조회 (최신순)"""
    result = await db.execute(
        select(AIAnalysis).order_by(desc(AIAnalysis.created_at))
    )
    analyses = result.scalars().all()
    return analyses


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: int, db: AsyncSession = Depends(get_db)):
    """단일 AI 분석 조회"""
    result = await db.execute(
        select(AIAnalysis).where(AIAnalysis.id == analysis_id)
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다")

    return analysis
