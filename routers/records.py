from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from database.database import get_db
from database.models import WorkoutRecord
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter(prefix="/api/records", tags=["records"])


class WorkoutRecordCreate(BaseModel):
    date: str  # YYYY-MM-DD
    distance: Optional[float] = None
    duration: Optional[int] = None
    pace: Optional[str] = None
    notes: Optional[str] = None


class WorkoutRecordResponse(BaseModel):
    id: int
    date: str
    distance: Optional[float]
    duration: Optional[int]
    pace: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class WorkoutStats(BaseModel):
    total_records: int
    total_distance: float
    total_duration: int
    avg_pace: Optional[str]


@router.post("", response_model=WorkoutRecordResponse, status_code=201)
async def create_record(record: WorkoutRecordCreate, db: AsyncSession = Depends(get_db)):
    """운동 기록 생성"""
    new_record = WorkoutRecord(**record.dict())
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)
    return new_record


@router.get("", response_model=List[WorkoutRecordResponse])
async def get_records(db: AsyncSession = Depends(get_db)):
    """전체 운동 기록 조회 (날짜 역순)"""
    result = await db.execute(
        select(WorkoutRecord).order_by(desc(WorkoutRecord.date))
    )
    records = result.scalars().all()
    return records


@router.get("/stats", response_model=WorkoutStats)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """운동 통계 조회"""
    result = await db.execute(
        select(
            func.count(WorkoutRecord.id).label("total_records"),
            func.sum(WorkoutRecord.distance).label("total_distance"),
            func.sum(WorkoutRecord.duration).label("total_duration")
        )
    )
    stats = result.first()

    return {
        "total_records": stats.total_records or 0,
        "total_distance": stats.total_distance or 0.0,
        "total_duration": stats.total_duration or 0,
        "avg_pace": None  # 간단한 계산은 프론트에서 처리
    }


@router.get("/{record_id}", response_model=WorkoutRecordResponse)
async def get_record(record_id: int, db: AsyncSession = Depends(get_db)):
    """단일 운동 기록 조회"""
    result = await db.execute(
        select(WorkoutRecord).where(WorkoutRecord.id == record_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다")

    return record


@router.put("/{record_id}", response_model=WorkoutRecordResponse)
async def update_record(
    record_id: int,
    record_update: WorkoutRecordCreate,
    db: AsyncSession = Depends(get_db)
):
    """운동 기록 수정"""
    result = await db.execute(
        select(WorkoutRecord).where(WorkoutRecord.id == record_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다")

    for key, value in record_update.dict().items():
        setattr(record, key, value)

    await db.commit()
    await db.refresh(record)
    return record


@router.delete("/{record_id}")
async def delete_record(record_id: int, db: AsyncSession = Depends(get_db)):
    """운동 기록 삭제"""
    result = await db.execute(
        select(WorkoutRecord).where(WorkoutRecord.id == record_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다")

    await db.delete(record)
    await db.commit()
    return {"message": "삭제되었습니다"}
