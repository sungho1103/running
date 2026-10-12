from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class WorkoutRecord(Base):
    """운동 기록 모델"""
    __tablename__ = "workout_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD
    distance = Column(Float)  # km
    duration = Column(Integer)  # 분
    pace = Column(String)  # min/km (예: "5:30")
    notes = Column(Text)  # 사용자 메모
    created_at = Column(DateTime, server_default=func.now())


class AIAnalysis(Base):
    """AI 분석 이력 모델"""
    __tablename__ = "ai_analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    image_path = Column(String, nullable=False)  # 업로드 이미지 경로
    image_hash = Column(String(64), nullable=True, index=True)  # SHA-256 해시 (캐싱용)
    analysis_result = Column(Text, nullable=False)  # AI 분석 결과 (JSON)
    tokens_used = Column(Integer)  # 소모 토큰 수
    cost = Column(Float)  # 예상 비용 ($)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    record_id = Column(Integer, ForeignKey("workout_records.id"), nullable=True)
