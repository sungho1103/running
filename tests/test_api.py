"""
운동기록앱 API 테스트
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app import app


@pytest.mark.asyncio
async def test_health_check():
    """헬스체크 엔드포인트 테스트"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_record():
    """운동 기록 생성 테스트"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/records",
            json={
                "date": "2026-10-13",
                "distance": 5.2,
                "duration": 30,
                "pace": "5:46",
                "notes": "테스트 러닝"
            }
        )
    assert response.status_code == 201
    data = response.json()
    assert data["distance"] == 5.2
    assert data["duration"] == 30


@pytest.mark.asyncio
async def test_get_records():
    """운동 기록 목록 조회 테스트"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/records")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_stats():
    """통계 조회 테스트"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/records/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_records" in data
    assert "total_distance" in data
    assert "total_duration" in data


@pytest.mark.asyncio
async def test_update_record():
    """운동 기록 수정 테스트"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 먼저 기록 생성
        create_response = await client.post(
            "/api/records",
            json={
                "date": "2026-10-13",
                "distance": 3.0,
                "duration": 20,
                "pace": "6:40",
                "notes": "수정 전"
            }
        )
        record_id = create_response.json()["id"]

        # 수정
        update_response = await client.put(
            f"/api/records/{record_id}",
            json={
                "date": "2026-10-13",
                "distance": 5.0,
                "duration": 30,
                "pace": "6:00",
                "notes": "수정 후"
            }
        )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["distance"] == 5.0
    assert data["notes"] == "수정 후"


@pytest.mark.asyncio
async def test_delete_record():
    """운동 기록 삭제 테스트"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 먼저 기록 생성
        create_response = await client.post(
            "/api/records",
            json={
                "date": "2026-10-13",
                "distance": 3.0,
                "duration": 20,
                "pace": "6:40",
                "notes": "삭제 테스트"
            }
        )
        record_id = create_response.json()["id"]

        # 삭제
        delete_response = await client.delete(f"/api/records/{record_id}")

    assert delete_response.status_code == 200
