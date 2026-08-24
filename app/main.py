"""앱 진입점. FastAPI 인스턴스를 만들고, 라우터들을 연결하고, 시작할 때 DB를 준비시킨다."""
import asyncio
import os

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import wait_for_db, ensure_tables
from routers import (auth, posts, account, files, export, activity, products,
                     admin, weather, backup, notifications, games)
from seed_data import seed_products
from weather_fetcher import weather_background_loop
from backup_sync import backup_background_loop

app = FastAPI(title="jwt-auth-practice")
templates = Jinja2Templates(directory="templates")

# 프론트엔드 CSS/JS 정적 파일 서빙 (/static/css/style.css, /static/js/app.js)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(account.router)
app.include_router(files.router)
app.include_router(export.router)
app.include_router(activity.router)
app.include_router(products.router)
app.include_router(admin.router)
app.include_router(weather.router)
app.include_router(backup.router)
app.include_router(notifications.router)
app.include_router(games.router)


def _asset_version(*path_parts: str) -> int:
    """정적 파일(css/js)의 마지막 수정 시각을 정수로 돌려준다.
    이 값을 주소 끝에 ?v=... 로 붙여서, 파일 내용이 바뀔 때마다 브라우저가
    "이건 예전에 저장해둔 파일이랑 다른 주소네" 하고 캐시를 안 쓰고 새로 받아가게 만든다
    (이렇게 안 하면 브라우저가 오래된 css/js를 계속 재사용해서 화면이 안 바뀐 것처럼 보인다)."""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    return int(os.path.getmtime(os.path.join(static_dir, *path_parts)))


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "css_version": _asset_version("css", "style.css"),
        "js_version": _asset_version("js", "app.js"),
    })


@app.on_event("startup")
async def on_startup():
    wait_for_db()
    ensure_tables()
    seed_products()
    # 서버가 켜져있는 동안 계속 돌면서, 주기적으로 외부 날씨 데이터를 가져오는 백그라운드 작업 시작
    asyncio.create_task(weather_background_loop())
    # 서버가 켜져있는 동안 계속 돌면서, 주기적으로 게시글을 MongoDB에 백업하는 백그라운드 작업 시작
    asyncio.create_task(backup_background_loop())
