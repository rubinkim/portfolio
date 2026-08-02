"""기상청 API허브 - 동네예보(단기예보) 조회.

사용법:
1. .env에 KMA_API_KEY=발급받은인증키 추가
2. https://apihub.kma.go.kr 의 "예특보 > 단기예보 > 예·특보 구역정보" 탭에서
   행정동-격자좌표 매핑표를 CSV로 받아 이 파일과 같은 폴더에
   dong_grid.csv (컬럼: dong,nx,ny) 형태로 저장하면 전국 동을 조회할 수 있음.
   아직 없으면 아래 SAMPLE_GRID에 있는 동만 테스트 가능.
"""

import csv
import os
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["KMA_API_KEY"]
BASE_URL = "https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0/getVilageFcst"

# 전국 매핑표(dong_grid.csv)를 아직 준비 못했을 때를 위한 예시 좌표 몇 개.
SAMPLE_GRID = {
    "종로구": (60, 127),
    "강남구": (61, 126),
}

# 단기예보는 하루 8회(02,05,08,11,14,17,20,23시) 발표되고, 발표 후 약 10분 뒤부터 조회 가능.
ISSUE_HOURS = [2, 5, 8, 11, 14, 17, 20, 23]

CATEGORY_NAMES = {
    "POP": "강수확률(%)",
    "PTY": "강수형태",
    "TMP": "기온(℃)",
    "TMN": "최저기온(℃)",
    "TMX": "최고기온(℃)",
    "SKY": "하늘상태",
    "REH": "습도(%)",
    "WSD": "풍속(m/s)",
}

SKY_NAMES = {"1": "맑음", "3": "구름많음", "4": "흐림"}
PTY_NAMES = {"0": "없음", "1": "비", "2": "비/눈", "3": "눈", "4": "소나기"}


def load_dong_grid(csv_path="dong_grid.csv"):
    """CSV(dong,nx,ny)를 읽어 동 이름 -> (nx, ny) 딕셔너리로 변환. 없으면 샘플만 반환."""
    if not os.path.exists(csv_path):
        return SAMPLE_GRID

    grid = {}
    with open(csv_path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            grid[row["dong"]] = (int(row["nx"]), int(row["ny"]))
    return grid


def latest_base_datetime(now=None):
    """가장 최근에 발표된 단기예보의 base_date, base_time을 계산."""
    now = now or datetime.now()
    candidate = now - timedelta(minutes=10)  # 발표 후 10분간은 아직 미제공

    available_hours = [h for h in ISSUE_HOURS if h <= candidate.hour]
    if available_hours:
        base_hour = max(available_hours)
        base_date = candidate.strftime("%Y%m%d")
    else:
        base_hour = ISSUE_HOURS[-1]
        base_date = (candidate - timedelta(days=1)).strftime("%Y%m%d")

    return base_date, f"{base_hour:02d}00"


def fetch_forecast(dong_name, dong_grid):
    if dong_name not in dong_grid:
        raise ValueError(f"'{dong_name}'의 격자좌표를 찾을 수 없습니다. dong_grid.csv를 확인하세요.")

    nx, ny = dong_grid[dong_name]
    base_date, base_time = latest_base_datetime()

    response = requests.get(
        BASE_URL,
        params={
            "authKey": API_KEY,
            "pageNo": 1,
            "numOfRows": 1000,
            "dataType": "JSON",
            "base_date": base_date,
            "base_time": base_time,
            "nx": nx,
            "ny": ny,
        },
    )
    response.raise_for_status()
    body = response.json()["response"]["body"]
    return body["items"]["item"]


def summarize(items, hours=6):
    """예보 항목을 (fcstDate, fcstTime)별로 묶어서 앞으로 hours시간치만 보기 좋게 정리."""
    by_time = {}
    for item in items:
        key = (item["fcstDate"], item["fcstTime"])
        by_time.setdefault(key, {})[item["category"]] = item["fcstValue"]

    lines = []
    for (date, time), values in sorted(by_time.items())[:hours]:
        sky = SKY_NAMES.get(values.get("SKY"), values.get("SKY", "-"))
        pty = PTY_NAMES.get(values.get("PTY"), "")
        weather = pty if pty and pty != "없음" else sky
        tmp = values.get("TMP", "-")
        pop = values.get("POP", "-")
        lines.append(f"{date} {time[:2]}시 - {weather}, 기온 {tmp}℃, 강수확률 {pop}%")
    return "\n".join(lines)


if __name__ == "__main__":
    dong_grid = load_dong_grid()
    dong = input("동네 이름을 입력하세요 (예: 종로구): ").strip()

    items = fetch_forecast(dong, dong_grid)
    print(summarize(items))
