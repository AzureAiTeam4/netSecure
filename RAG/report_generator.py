import json
import re
import logging
from openai import AzureOpenAI
import config
from schemas import SecurityEvent, SecurityReport
from search_client import search_documents
from prompt_builder import build_search_query, build_system_prompt, build_user_prompt

logger = logging.getLogger(__name__)

_openai = AzureOpenAI(
    azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
    api_key=config.AZURE_OPENAI_KEY,
    api_version="2024-02-01",
)


def _parse_json(text: str) -> dict:
    # ```json ... ``` 코드블록 제거
    text = re.sub(r"```json\s*|\s*```", "", text).strip()
    return json.loads(text)


def generate_security_report(event: SecurityEvent) -> SecurityReport:
    # 1. 검색 쿼리 생성
    query = build_search_query(event)

    # 2. Azure AI Search에서 관련 문서 검색
    chunks = search_documents(query)

    # 3. 프롬프트 생성
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(event, chunks)

    # 4. GPT-4o 호출
    response = _openai.chat.completions.create(
        model=config.AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    raw = response.choices[0].message.content

    # 5. JSON 파싱
    try:
        report = _parse_json(raw)
        return report
    except json.JSONDecodeError as e:
        logger.error("JSON 파싱 실패\n원본 응답:\n%s\n에러: %s", raw, e)
        raise
