import os

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

load_dotenv()

API_KEY = os.environ["GEMINI_API_KEY"]
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"

app = Flask(__name__, template_folder=".")


def build_prompt(name, birth_date, birth_time, gender):
    # TODO: 실제 사주(만세력 계산 등) 로직은 여기서 채워넣기.
    # 지금은 기본 구조 확인용으로 아주 단순한 프롬프트만 사용.
    return (
        f"이름: {name}, 생년월일: {birth_date}, 태어난 시간: {birth_time}, "
        f"성별: {gender}. 이 사람의 사주를 간단히 봐줘."
    )


@app.route("/")
def index():
    return render_template("saju.html")


@app.route("/api/saju", methods=["POST"])
def saju():
    data = request.get_json()
    prompt = build_prompt(
        data.get("name"),
        data.get("birth_date"),
        data.get("birth_time"),
        data.get("gender"),
    )

    response = requests.post(
        GEMINI_URL,
        headers={
            "x-goog-api-key": API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "model": "gemini-3.5-flash",
            "input": prompt,
        },
    )
    response.raise_for_status()
    result = response.json()

    text = next(
        step["content"][0]["text"]
        for step in result["steps"]
        if step["type"] == "model_output"
    )

    return jsonify({"result": text})


if __name__ == "__main__":
    app.run(debug=True)
