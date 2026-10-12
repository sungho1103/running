import os
from PIL import Image
from typing import Tuple


def preprocess_image(image_path: str, max_size: Tuple[int, int] = (1024, 1024), quality: int = 85) -> str:
    """
    이미지 전처리: 리사이징 및 압축

    Args:
        image_path: 원본 이미지 경로
        max_size: 최대 크기 (가로, 세로)
        quality: JPEG 압축 품질 (1-100)

    Returns:
        처리된 이미지 경로
    """
    try:
        with Image.open(image_path) as img:
            # RGB 변환 (투명도 채널 제거)
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # 리사이징 (비율 유지)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # 압축 저장
            output_path = image_path.replace(".png", ".jpg") if image_path.endswith(".png") else image_path
            img.save(output_path, "JPEG", quality=quality, optimize=True)

            return output_path
    except Exception as e:
        raise ValueError(f"이미지 전처리 실패: {str(e)}")


def validate_image(file_path: str, max_size_mb: int = 2) -> bool:
    """
    이미지 파일 검증

    Args:
        file_path: 이미지 파일 경로
        max_size_mb: 최대 파일 크기 (MB)

    Returns:
        검증 통과 여부
    """
    if not os.path.exists(file_path):
        return False

    # 파일 크기 확인
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > max_size_mb:
        return False

    # 이미지 형식 확인
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False
