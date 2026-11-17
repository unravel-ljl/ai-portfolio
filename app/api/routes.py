
import logging
import time
from fastapi import APIRouter, HTTPException
from app.services.llm import LLMError, ask_llm
from pydantic import BaseModel, Field
from app.services.metrics import counter

logger = logging.getLogger(__name__)
router = APIRouter()


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500, description="用户问题")


class AskResponse(BaseModel):
    answer: str
    cost_ms: int


class MetricsResponse(BaseModel):
    calls: int


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/ask")
def ask(req: AskRequest) -> AskResponse:
    start = time.perf_counter()
    try:
        answer = ask_llm(req.question)
    except LLMError as e:
        logger.warning("ask failed | q_len=%d | %s", len(req.question), e)
        raise HTTPException(status_code=503, detail=str(e)) from e

    cost_ms = int((time.perf_counter() - start) * 1000)
    logger.info("ask | q_len=%d | cost_ms=%d", len(req.question), cost_ms)
    counter.incr()
    return AskResponse(answer=answer, cost_ms=cost_ms)


@router.get("/metrics")
def metrics() -> MetricsResponse:
    """累计被调用的次数（进程重启会归零）。"""
    return MetricsResponse(calls=counter.calls)
