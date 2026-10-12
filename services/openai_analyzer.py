import os
import base64
from openai import AsyncOpenAI, AuthenticationError, RateLimitError, APIError
from dotenv import load_dotenv

load_dotenv()

# 최적화된 분석 프롬프트 (토큰 절감)
ANALYSIS_PROMPT = """이 운동 기록 차트를 분석해서 다음 정보를 추출해주세요:
1. 운동 종류 (조깅, 런닝 등)
2. 거리, 시간, 페이스 (있다면)
3. 심박수, 고도 등 추가 지표 (있다면)
4. 간단한 운동 피드백 (2문장 이내)

JSON 형식으로 응답:
{
  "type": "조깅",
  "distance": "5.2km",
  "duration": "28분",
  "pace": "5:30/km",
  "feedback": "꾸준한 페이스 유지, 다음은 거리를 늘려보세요"
}"""


def encode_image(image_path: str) -> str:
    """이미지를 base64로 인코딩"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def calculate_cost(usage) -> float:
    """
    토큰 사용량 기반 비용 계산 (gpt-4o-mini 기준)

    Args:
        usage: OpenAI API 응답의 usage 객체

    Returns:
        예상 비용 ($)
    """
    # gpt-4o-mini 가격 (2026년 기준)
    input_price = 0.00015 / 1000  # $0.15/1M tokens
    output_price = 0.0006 / 1000  # $0.60/1M tokens

    input_cost = usage.prompt_tokens * input_price
    output_cost = usage.completion_tokens * output_price

    return input_cost + output_cost


async def analyze_workout_chart(image_path: str) -> dict:
    """
    OpenAI Vision API를 사용해 운동 차트 이미지 분석

    Args:
        image_path: 분석할 이미지 파일 경로

    Returns:
        분석 결과 딕셔너리 {analysis, tokens, cost}
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다")

    client = AsyncOpenAI(api_key=api_key)

    # 이미지 base64 인코딩
    image_b64 = encode_image(image_path)

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": ANALYSIS_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}",
                            "detail": "low"  # 토큰 절감 (저해상도 분석)
                        }
                    }
                ]
            }],
            max_tokens=300  # 응답 토큰 제한
        )

        analysis_text = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        cost = calculate_cost(response.usage)

        return {
            "analysis": analysis_text,
            "tokens": tokens_used,
            "cost": cost
        }
    except AuthenticationError:
        raise ValueError("OpenAI API 키가 올바르지 않습니다. .env 파일의 OPENAI_API_KEY를 확인하세요.")
    except RateLimitError:
        raise ValueError("OpenAI API 할당량 초과입니다. 잠시 후 다시 시도하거나 플랜을 업그레이드하세요.")
    except APIError as e:
        raise ValueError(f"OpenAI 서버 오류: {str(e)}. 잠시 후 다시 시도하세요.")
    except Exception as e:
        raise ValueError(f"이미지 분석 실패: {str(e)}")
