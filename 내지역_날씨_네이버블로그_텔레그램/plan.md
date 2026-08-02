# 텔레그램 "오늘 날씨 점심 추천" — n8n 워크플로우 계획

## 1. 목표
텔레그램으로 "오늘 같은 날씨에 점심 뭐 먹을지 알려줘"라고 메시지를 보내면,
1. 내 지역의 오늘 낮 12시~오후 2시 날씨를 확인하고
2. 그 날씨에 어울리는 음식을 AI가 추천한 뒤
3. 내 지역(없으면 인근 지역) 네이버 블로그에서 그 음식 맛집 후기를 최대 5개 찾아 요약해서
4. 정리된 결과를 다시 텔레그램으로 받는다.

## 2. 입력 정보 (확정 필요)
| 항목 | 값 | 비고 |
|---|---|---|
| 내 지역 | **판교** (검색용 지역명), 좌표는 위도 37.3948 / 경도 127.1112 | `운세_날씨` 프로젝트 좌표 재사용. 지역명은 AI가 추측하지 않도록 워크플로우에서 고정값으로 전달 |
| 텔레그램 봇 | 기존 봇 재사용 또는 신규 생성 | BotFather에서 토큰 발급, 내 chat_id 확인 필요 |
| 네이버 검색 API | 블로그 검색 (`https://naverapihub.apigw.ntruss.com/search/v1/blog`) | 인증 헤더: `X-NCP-APIGW-API-KEY-ID`(Client ID), `X-NCP-APIGW-API-KEY`(Client Secret) |
| AI 모델 | Gemini 또는 OpenAI 등 | AI Agent 노드의 Chat Model로 사용, 기존 프로젝트는 `gemini-3-flash-preview` 사용 |

## 3. 전체 아키텍처 (n8n 워크플로우 노드 구성)

```
[Telegram Trigger: 메시지 수신]
        │  (텍스트에 "점심"/"날씨" 등이 포함될 때만 진행하도록 IF 필터 추가 가능)
        ▼
[HTTP Request: Open-Meteo 날씨 조회]
        │  위도/경도 고정값, hourly=temperature_2m,precipitation_probability,wind_speed_10m
        │  timezone=Asia/Seoul, forecast_days=1
        ▼
[Code/Set: 12시~14시 데이터만 추출·요약 + 지역명 고정값 추가]
        │  hourly 배열 전체를 그대로 넘기면 토큰 낭비 + 혼동 위험 →
        │  "12시 22℃ 강수확률10% 풍속3km/h, 13시 23℃ ..." 같은 짧은 텍스트로 가공
        │  지역명("판교")은 AI가 추측하지 않도록 이 노드에서 고정값으로 함께 담아 전달
        ▼
[AI Agent 노드]
   ├─ Chat Model: Gemini(or OpenAI)
   ├─ Prompt(User Message): 지역명 + 날씨 요약을 함께 전달
   ├─ Tool: HTTP Request Tool → 네이버 블로그 검색 API
   │        (검색어는 $fromAI()로 에이전트가 구성하되, 지역명은 전달받은 값을 그대로 사용: "판교 + 음식 종류 + 맛집")
   └─ Output Parser: Structured Output Parser (JSON 스키마 강제)
        ▼
[Code/Set: JSON → 텔레그램용 읽기 좋은 텍스트로 변환]
        ▼
[Telegram: Send Message]
        │  Telegram Trigger에서 받은 chat.id로 회신
```

- 날씨 조회 → 요약 → AI Agent → 텔레그램 전송까지 **직렬 흐름**으로 구성한다. (Discord 프로젝트와 달리 날씨/추천이 서로 의존하므로 병렬 브랜치가 아님)
- AI Agent 노드는 도구를 여러 번 호출할 수 있으므로(ReAct 방식), "지역 내 검색 → 결과 없으면 인근 지역 재검색 → 그래도 없으면 다음 음식 후보로 재시도" 로직은 **별도 n8n 분기 노드를 만들지 않고 System Prompt로 지시**해서 에이전트가 스스로 반복 호출하게 한다.

## 4. AI Agent System Prompt 설계 (핵심 로직)

에이전트에게 아래 순서를 명확히 지시:
1. 전달받은 지역명("판교")과 날씨 요약(12~14시)을 확인한다. **지역명은 절대 추측하거나 다른 지역으로 바꾸지 말고, 전달받은 값을 그대로 사용**한다 (인근 지역 재검색 시에만 예외).
2. 날씨 요약을 보고 어울리는 음식 카테고리를 1순위~3순위까지 속으로 정한다.
3. 1순위 음식으로 "판교 + 음식 + 맛집" 검색어를 만들어 네이버 블로그 검색 도구를 호출한다.
4. 검색 결과가 없거나 관련성이 낮으면, 판교와 가까운 인근 지역명(예: 분당, 성남)으로 검색어를 바꿔 재검색한다.
5. 그래도 결과가 없으면 "어디까지 찾아봤는지"를 기록해두고 2순위 음식으로 넘어가 3~4번을 반복한다.
6. 최종적으로 관련 블로그 글을 최대 5개까지 골라 각 글의 제목/링크/핵심 요약을 정리한다.
7. 출력은 Output Parser가 강제하는 JSON 스키마를 반드시 지킨다.

## 5. Output Parser JSON 스키마 (예시)

```json
{
  "weather_summary": "string (12~14시 날씨 한 줄 요약)",
  "recommended_food": "string (최종 추천 음식)",
  "recommendation_reason": "string (그 음식을 추천한 이유 한 줄)",
  "search_area_used": "string (실제 검색에 사용된 지역명, 원래 지역 또는 인근 지역)",
  "fallback_notes": "string (인근 지역/차순위 음식으로 넘어갔다면 그 과정 설명, 없으면 빈 문자열)",
  "blog_posts": [
    {
      "title": "string",
      "url": "string",
      "summary": "string (핵심 정보 2~3줄 요약)"
    }
  ]
}
```

## 6. 단계별 진행 순서 (하나씩 확인하며 진행)

1. **텔레그램 트리거 단독 검증**
   - Telegram Trigger 노드에 봇 토큰 연결, 테스트 메시지 전송 후 chat.id·text가 정상 수신되는지 확인.
2. **날씨 노드 단독 검증**
   - Open-Meteo 호출 후 hourly 배열에서 12~14시 값이 정확히 뽑히는지 Code 노드로 확인.
3. **네이버 블로그 검색 도구 단독 검증**
   - HTTP Request 노드로 `https://naverapihub.apigw.ntruss.com/search/v1/blog`를 직접 호출해 `X-NCP-APIGW-API-KEY-ID`/`X-NCP-APIGW-API-KEY` 헤더 인증이 되는지, 응답 구조(title/link/description)를 확인.
4. **AI Agent 연결 (도구 + Output Parser 없이 텍스트 응답부터)**
   - 날씨 요약을 입력으로 받아 음식 추천 문장만 우선 생성되는지 확인.
5. **AI Agent에 네이버 검색 Tool 연결**
   - 에이전트가 도구를 호출해 실제 블로그 결과를 가져오는지, 검색어 구성이 의도대로 되는지 확인.
6. **폴백 로직(인근 지역 → 차순위 음식) 테스트**
   - 검색 결과가 거의 없을 법한 음식/지역으로 일부러 테스트해 재검색 흐름이 동작하는지 확인.
7. **Output Parser 연결**
   - 위 5번 스키마대로 JSON이 강제되는지 확인 (형식 깨짐 없는지).
8. **JSON → 텔레그램 메시지 변환 + 전송**
   - Code 노드에서 JSON을 사람이 읽기 좋은 텍스트로 바꾸고, Telegram Send Message 노드로 원래 chat.id에 회신되는지 확인.
9. **전체 연결 및 활성화**
   - 1~8번이 개별적으로 통과하면 전체를 연결하고 워크플로우를 Active로 전환.

## 7. 필요한 자격증명 / 준비물
- **텔레그램 봇 토큰**: BotFather 발급, n8n Telegram Credential에 등록.
- **AI 모델 API 키**: Gemini 또는 OpenAI 등, n8n Credential로 등록 (하드코딩 금지).
- **네이버 검색 API Client ID/Secret**: Naver API Hub(NCP)에서 발급, HTTP Request Tool에 `X-NCP-APIGW-API-KEY-ID`/`X-NCP-APIGW-API-KEY` 헤더로 등록.

## 8. 산출물
- `내지역_날씨_네이버블로그_텔레그램/` 폴더에 n8n Import 가능한 워크플로우 JSON 파일.
- 자격증명 등록 및 활성화를 위한 간단한 설정 가이드.

## 9. 확인이 필요한 사항 (진행 전 결정)
- AI 모델을 Gemini로 할지 OpenAI로 할지 (Chat Model 선택에 따라 Credential 종류가 달라짐).
- 텔레그램 트리거를 "아무 메시지"에나 반응시킬지, 특정 키워드(예: "점심", "날씨")가 포함될 때만 반응하도록 IF 필터를 둘지.
