"""환경변수로부터 읽어오는 설정값들을 한 곳에 모아둔 파일."""
import os

DB_CONFIG = {
    "host": os.environ["DB_HOST"],
    "port": os.environ["DB_PORT"],
    "dbname": os.environ["DB_NAME"],
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
}

SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "change-this-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 리프레시 토큰(자동 로그인 연장용)이 살아있는 기간. 액세스 토큰(30분)보다 훨씬 길게 잡아서,
# 액세스 토큰이 만료돼도 이 기간 안에는 재로그인 없이 새 액세스 토큰을 계속 받아올 수 있게 한다.
REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS") or "14")

# 회원가입 화면에서 "관리자로 가입"을 선택했을 때 맞춰 입력해야 하는 코드.
# 이 코드를 아는 사람만 관리자 계정을 만들 수 있음 (실제 배포 시에는 꼭 바꿔서 쓸 것).
ADMIN_SIGNUP_CODE = os.environ.get("ADMIN_SIGNUP_CODE") or "admin1234"

UPLOAD_DIR = os.environ.get("UPLOAD_DIR") or "uploads"
MAX_FILE_SIZE_MB = 20

# 날씨 데이터 전용 MongoDB 연결 정보 (PostgreSQL과는 완전히 별개의 DB)
MONGO_URI = os.environ.get("MONGO_URI") or "mongodb://mongo:27017"

# 날씨를 가져올 위치 (기본값: 서울). 완전 무료 API인 Open-Meteo는 위도/경도로 조회해요.
# `.env`가 없어서 값이 빈 문자열("")로 넘어와도 죽지 않도록, "or"로 기본값을 한 번 더 걸어뒀어요.
# (os.environ.get(key, default)는 key가 "존재하는데 빈 값"이면 default를 안 씀 — 빈 문자열도 값이라서요)
WEATHER_CITY_NAME = os.environ.get("WEATHER_CITY_NAME") or "서울"
WEATHER_LAT = float(os.environ.get("WEATHER_LAT") or "37.5665")
WEATHER_LON = float(os.environ.get("WEATHER_LON") or "126.9780")

# 날씨를 자동으로 새로 가져오는 주기(초). 기본 1800초 = 30분.
WEATHER_FETCH_INTERVAL_SECONDS = int(os.environ.get("WEATHER_FETCH_INTERVAL_SECONDS") or "1800")

# PostgreSQL의 게시글을 MongoDB로 자동 백업(복사)하는 주기(초). 기본 3600초 = 1시간.
BACKUP_SYNC_INTERVAL_SECONDS = int(os.environ.get("BACKUP_SYNC_INTERVAL_SECONDS") or "3600")

# PostgreSQL의 날씨 기록을 MongoDB로 자동 백업(복사)하는 주기(초). 기본 600초 = 10분.
# 게시글보다 훨씬 자주 백업하는 이유는, 날씨는 30분마다 계속 새로 쌓이는 데이터라
# 백업이 너무 뜸하면 최근 기록 여러 개가 한꺼번에 밀려서 백업되기 때문이다.
WEATHER_BACKUP_INTERVAL_SECONDS = int(os.environ.get("WEATHER_BACKUP_INTERVAL_SECONDS") or "600")
