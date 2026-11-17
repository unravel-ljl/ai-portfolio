import logging

from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_client = OpenAI(
    api_key=settings.deepseek_api_key,
    base_url=settings.deepseek_base_url,
    timeout=10.0,
    max_retries=0,  # 重试交给 tenacity 统一管
)

SYSTEM_PROMPT = "你是一个严谨的技术助手。回答简洁，不确定时明确说不确定。"


class LLMError(Exception):
    """业务侧统一的模型调用异常。"""


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
    retry=retry_if_exception_type((APITimeoutError, APIConnectionError)),
    reraise=True,
)
def _chat(question: str) -> str:
    resp = _client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        temperature=0.3,
        max_tokens=500,
    )
    return resp.choices[0].message.content or ""


def ask_llm(question: str) -> str:
    """调用大模型。失败时抛 LLMError（带人话提示）。"""
    try:
        return _chat(question)
    except APITimeoutError as e:
        logger.warning("llm timeout: %s", e)
        raise LLMError("模型响应超时，请稍后再试") from e
    except APIConnectionError as e:
        logger.warning("llm connection error: %s", e)
        raise LLMError("无法连接模型服务，请检查网络或代理") from e
    except APIStatusError as e:
        logger.warning("llm status error: %s %s", e.status_code, e.message)
        if e.status_code == 401:
            raise LLMError("API Key 无效或已失效") from e
        if e.status_code == 402:
            raise LLMError("账户余额不足") from e
        if e.status_code == 429:
            raise LLMError("请求过于频繁，请稍后再试") from e
        raise LLMError(f"模型服务返回错误（{e.status_code}）") from e