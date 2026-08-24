"""앱 진입점. FastAPI 인스턴스를 만들고, 라우터들을 연결하고, 시작할 때 DB를 준비시킨다."""
import asyncio

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import wait_for_db, ensure_tables
from routers import auth, posts, account, files, export, activity, products, admin, weather, backup
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


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.on_event("startup")
async def on_startup():
    wait_for_db()
    ensure_tables()
    seed_products()
    # 서버가 켜져있는 동안 계속 돌면서, 주기적으로 외부 날씨 데이터를 가져오는 백그라운드 작업 시작
    asyncio.create_task(weather_background_loop())
    # 서버가 켜져있는 동안 계속 돌면서, 주기적으로 게시글을 MongoDB에 백업하는 백그라운드 작업 시작
    asyncio.create_task(backup_background_loop())
