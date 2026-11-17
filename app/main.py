# from fastapi import FastAPI
# from pydantic import BaseModel,Field

# #创建一个应用实例
# app = FastAPI(title="AI Portfolio", version="1.0.0")

# # @app.get("/health", tags=["Health Check"])
# # def health() -> str:
# #     return "500111"
# #构建统一的请求返回模型
# class AskRequest(BaseModel):
#     question: str = Field(min_length=10, max_length=500, description="用户问题")

# class AskResponse(BaseModel):
#     answer: str
#     cost_ms: int

# @app.get("/health")
# def health() -> dict[str, str]:
#     return {"status": "ok"}

# @app.post("/ask", response_model=AskResponse, tags=["问答"])
# def ask(req: AskRequest) -> AskResponse:
#     fake = f"收到问题：{req.question}(当前为占位回答)"
#     return AskResponse(answer=fake, cost_ms=20)

import logging

from fastapi import FastAPI

from app.api.routes import router
from app.core.config import get_settings

settings = get_settings()

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    force=True,
)

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(router)
