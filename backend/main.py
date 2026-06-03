from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import events   # events.py 연결
from api import stats    # stats.py 연결
from api import report   # report.py 연결
from api import predict  # predict.py 연결

app = FastAPI()

# 프론트엔드 연결 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "NIDS API 서버 작동 중"}

app.include_router(events.router)   # events 라우터 등록
app.include_router(stats.router)    # stats 라우터 등록
app.include_router(report.router)   # report 라우터 등록
app.include_router(predict.router)  # predict 라우터 등록