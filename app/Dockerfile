FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 전체 복사 (여러 파일로 나뉜 구조라 폴더째로 복사)
COPY . .

EXPOSE 8000
# "-m uvicorn"으로 실행해야, main.py와 같은 위치의 database.py/models.py 같은
# 파일들을 문제없이 import할 수 있어요 (현재 폴더가 sys.path에 확실히 들어감).
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
