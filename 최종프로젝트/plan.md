# 시니어 건강 관리 텔레그램 봇 — 프로젝트 계획서

## 1. 프로젝트 개요

고령층은 매일 반복적으로 건강 수치를 기록하고, 정해진 시간에 약을 챙겨 먹고, 날씨에 맞는 운동을 하는 등의 관리를 스스로 지속하기 어려운 경우가 많다. 본 프로젝트는 **텔레그램 봇을 통해 하루 일과를 자동으로 안내하고, 사용자의 응답을 받아 후속 조치를 수행하는 건강 관리 자동화 시스템**을 n8n 워크플로우로 구현하는 것을 목표로 한다.

핵심은 단순 알림 발송이 아니라, **"아침에 봇이 먼저 질문 → 사용자가 답장 → 그 답변에 따라 기록·분석·후속 알림이 이어지는" 상호작용형 구조**를 설계하는 데 있다.

## 2. 대상 사용자 및 문제 정의

- **대상**: 만성질환 관리가 필요하거나, 규칙적인 생활 루틴 유지가 어려운 시니어 연령 사용자
- **문제**:
  1. 매일 체온·혈압·심박수·혈당을 측정하고 기록하는 습관을 유지하기 어렵고, 추세를 스스로 파악하기 힘들다.
  2. 그날의 날씨나 컨디션에 맞는 운동량을 스스로 판단하기 어렵다.
  3. 여러 개의 약을 정해진 시간에 챙겨 먹는 것을 잊기 쉽다.

## 3. 전체 시스템 아키텍처

### 3.1 사용 기술 스택
| 구성 요소 | 도구 |
|---|---|
| 워크플로우 오케스트레이션 | n8n |
| 사용자 인터페이스 | Telegram Bot |
| 데이터 저장소 | Google Sheets |
| 날씨 정보 | Open-Meteo API |
| 그래프 생성 | QuickChart API (또는 동급의 차트 이미지 생성 API) |
| AI 모델 | Gemini-3-flash-preview |

### 3.2 설계상 핵심 과제 — 대화 상태(state) 관리

기존에 진행한 워크플로우(`내지역_날씨_네이버블로그_텔레그램`)는 "메시지 수신 → 처리 → 응답"으로 끝나는 1턴 구조였다. 이번 프로젝트는 **봇이 먼저 질문을 던지고, 사용자가 시간이 지난 뒤 응답하는 구조**이므로, 사용자의 응답이 "어떤 질문에 대한 답변인지"를 구분할 방법이 필요하다.

n8n의 Telegram Trigger 자체는 상태를 기억하지 못하므로, Google Sheets에 **`user_state` 시트**를 두어 "현재 사용자가 응답을 기다리는 항목(예: 혈압 입력 대기, 복약 확인 대기)"을 기록해두고, 응답이 들어오면 이 상태값을 조회하여 분기 처리한다. 이 상태 관리 로직이 본 프로젝트의 기술적 핵심이다.

### 3.3 노드 유형 구분 — 트리거 노드 vs 처리 노드

워크플로우를 정확히 설계하려면 "언제 시작되는가"와 "무엇을 하는가"를 구분해야 한다. 이 프로젝트에서 각 노드는 아래 두 유형 중 하나로 나뉜다.

| 유형 | 역할 | 이 프로젝트에서 사용하는 노드 |
|---|---|---|
| **트리거 노드** | 워크플로우를 "언제" 시작할지만 결정한다. 조회·판단·전송 등의 실제 작업은 하지 않는다. | Schedule Trigger(정해진 시각에 시작), Telegram Trigger(사용자 메시지 수신 시 시작) |
| **처리 노드** | 트리거 이후 실행되며, 데이터 조회·조건 판단·가공·전송 등 실제 작업을 수행한다. | Google Sheets(조회/기록/갱신), IF(조건 분기), Code/Set(데이터 가공), HTTP Request(외부 API 호출), AI Agent(추천 문장 생성), Telegram(메시지/사진 전송) |

즉 "Schedule Trigger가 조회해서 알림을 보낸다"는 표현은 정확히는 "Schedule Trigger가 워크플로우를 시작시키고, 그 뒤에 연결된 Google Sheets·IF·Telegram 노드가 조회·판단·전송을 수행한다"는 의미다. 아래 3.4절과 5절에서는 이 구분에 따라 각 흐름을 노드 단위로 표기한다.

### 3.4 전체 흐름도

```
[Schedule Trigger: 매일 08:00] (트리거)
        │
        ▼
[Telegram: Send Message] (처리) — "체온/혈압/심박수/혈당을 알려주세요" 전송
        │
        ▼
[Google Sheets: Update Row] (처리) — user_state를 "건강수치 대기"로 갱신
        │
        ▼ (사용자 응답 대기)
[Telegram Trigger: 응답 수신] (트리거)
        │
        ▼
[Google Sheets: Lookup Row] (처리) — chat_id로 user_state 조회
        │
        ▼
[IF] (처리) — 상태값이 "건강수치 대기"인가?
        │ Yes
        ▼
[Code/Set] (처리) — 응답 텍스트를 체온/혈압/심박수/혈당 값으로 파싱
        │
        ▼
[Google Sheets: Append Row] (처리) — health_log에 기록
        │
        ▼
[IF] (처리) — 위험 범위 수치인가? (예: 수축기 혈압 180 이상)
        │ Yes                                  │ No
        ▼                                      │
[Telegram: Send Message] (처리) — 즉시 경고 메시지 전송
        │                                      │
        └──────────────────┬───────────────────┘
                            ▼
              [HTTP Request: QuickChart API] (처리) — health_log 최근 1년 데이터로 그래프 이미지 생성
                            │
                            ▼
              [Telegram: Send Photo] (처리) — 그래프 이미지 전송
                            │
                            ▼
              [HTTP Request: Open-Meteo API] (처리) — 당일 날씨 조회
                            │
                            ▼
              [Code/Set] (처리) — 날씨 데이터 요약
                            │
                            ▼
              [AI Agent] (처리) — 날씨 + 건강 수치를 반영해 운동 코스·강도 추천 문장 생성
                            │
                            ▼
              [Telegram: Send Message] (처리) — 추천 메시지 전송
                            │
                            ▼
              [Google Sheets: Update Row] (처리) — user_state를 "대기 없음"으로 초기화


[Schedule Trigger: 매시 정각] (트리거)
        │
        ▼
[Google Sheets: Lookup Row] (처리) — medication_schedule에서 현재 시각과 일치하는 약 조회
        │
        ▼
[IF] (처리) — 지금 시간에 복용할 약이 있는가?
        │ Yes
        ▼
[Telegram: Send Message] (처리) — 복약 알림 전송
        │
        ▼
[Google Sheets: Update Row] (처리) — user_state를 "복약확인 대기"로 갱신
        │
        ▼ (일정 시간 내 응답 대기)
[Telegram Trigger: 응답 수신] (트리거)
        │
        ▼
[Google Sheets: Lookup Row] (처리) — user_state 조회
        │
        ▼
[IF] (처리) — 상태값이 "복약확인 대기"인가?
        │ Yes
        ▼
[Google Sheets: Append Row] (처리) — medication_log에 복용 여부 기록

[Schedule Trigger: N분 후 재확인] (트리거) — 복약확인 대기 상태가 아직 남아있는지 확인
        │
        ▼
[Google Sheets: Lookup Row] (처리) — user_state 재조회
        │
        ▼
[IF] (처리) — 여전히 "복약확인 대기"인가?
        │ Yes
        ▼
[Telegram: Send Message] (처리) — 재알림 전송
        │
        ▼ (그래도 미응답)
[Telegram: Send Message] (처리, 확장 기능) — 보호자에게 알림 전송
```

## 4. 데이터 구조 (Google Sheets)

| 시트명 | 주요 컬럼 | 용도 |
|---|---|---|
| `health_log` | 날짜, 체온, 혈압(수축/이완), 심박수, 혈당 | 일별 건강 수치 누적 기록, 추세 그래프의 원본 데이터 |
| `medication_schedule` | 약 이름, 복용 시간, 복용 요일 | 사용자가 최초 등록하는 복약 스케줄 |
| `medication_log` | 날짜, 약 이름, 복용 시간, 복용 여부 | 실제 복약 이행 기록 |
| `user_state` | 사용자 ID(chat_id), 현재 대기 항목, 상태 갱신 시각 | 대화 상태 추적 (본 프로젝트의 핵심 테이블) |

## 5. 기능별 상세 설계

### 5.1 아침 건강 체크
- **Schedule Trigger**(매일 08:00)로 워크플로우를 시작하고, **Telegram: Send Message** 노드로 체온/혈압/심박수/혈당 입력을 요청한다.
- 이후 **Telegram Trigger**로 사용자 응답을 수신하면, **Google Sheets: Lookup Row**로 `user_state`를 조회하고 **IF** 노드로 "건강수치 대기" 상태인지 확인한 뒤에만 다음 단계를 진행한다.
- **Code/Set** 노드에서 응답 텍스트를 항목별 수치로 파싱하고, **Google Sheets: Append Row**로 `health_log`에 기록한다.
- **IF** 노드로 위험 범위(예: 수축기 혈압 180 이상 등) 여부를 판단해, 해당 시 **Telegram: Send Message**로 즉시 경고를 보낸다.
- **HTTP Request**(QuickChart API)로 `health_log`의 최근 1년 데이터를 그래프 이미지로 생성하고, **Telegram: Send Photo**로 전송한다.

### 5.2 날씨 기반 운동 추천
- 건강 수치 기록이 끝난 직후, 같은 흐름 안에서 **HTTP Request**(Open-Meteo API)로 당일 날씨(기온, 강수확률, 풍속 등)를 조회한다.
- **Code/Set** 노드로 날씨 데이터를 요약하고, 방금 기록된 건강 수치(특히 혈압·심박수)를 함께 **AI Agent** 노드에 전달한다.
- AI Agent가 날씨·건강 상태를 종합해 운동 코스와 적정 시간대, 운동 강도를 문장으로 추천한다(수치가 좋지 않은 날은 저강도 운동을 권하도록 프롬프트에 지시).
- **Telegram: Send Message**로 추천 문장을 전송한다.

### 5.3 복약 알림
- 사용자가 최초 1회 복약 스케줄(약 이름, 시간)을 `medication_schedule` 시트에 등록해둔다.
- **Schedule Trigger**(매시 정각)로 워크플로우가 시작되면, **Google Sheets: Lookup Row**가 `medication_schedule`을 조회하고 **IF** 노드가 "지금 시간에 복용할 약이 있는가"를 판단한다. 이 조회·판단은 트리거가 아니라 트리거 뒤에 연결된 처리 노드들이 수행한다.
- 해당하는 약이 있으면 **Telegram: Send Message**로 알림을 보내고, **Google Sheets: Update Row**로 `user_state`를 "복약확인 대기"로 갱신한다.
- 사용자가 **Telegram Trigger**로 "복용함" 등으로 응답하면, **Google Sheets: Lookup Row + IF**로 상태를 확인한 뒤 **Google Sheets: Append Row**로 `medication_log`에 기록한다.
- 일정 시간(N분) 후 별도의 **Schedule Trigger**가 다시 실행되어 `user_state`를 재조회하고, 여전히 "복약확인 대기"이면 재알림을 전송한다.

## 6. 단계별 구현 순서

1. Telegram Trigger 및 봇 토큰 연동 확인
2. Google Sheets 연동 확인 (`health_log`, `user_state` 등 시트 생성 및 읽기/쓰기 테스트)
3. 08:00 Schedule Trigger → 건강 수치 입력 요청 메시지 전송 흐름 구현
4. 사용자 응답 수신 → `user_state` 조회 → `health_log` 기록 흐름 구현
5. 이상 수치 감지 로직 추가
6. 추세 그래프 생성 및 전송 기능 구현
7. Open-Meteo 날씨 연동 + AI 운동 추천 흐름 구현
8. 복약 스케줄 등록 및 `medication_schedule` 시트 연동
9. 매시 Schedule Trigger → 복약 알림 → 응답 확인 흐름 구현
10. 전체 흐름 통합 및 테스트, Active 전환

## 7. 필요한 자격증명 / 준비물

- 텔레그램 봇 토큰 (BotFather 발급)
- Google Sheets API 연동을 위한 Google 계정 인증 (n8n Credential)
- AI 모델 API 키 (Gemini 또는 OpenAI)
- (선택) QuickChart 등 그래프 생성 API

## 8. MVP 범위 및 향후 확장 아이디어

**1차 구현 범위(MVP)**
1. 아침 건강 수치 입력 및 추세 그래프
2. 복약 알림 및 응답 확인
3. 날씨 기반 운동 추천

**향후 확장 아이디어**
- 위험 수치 감지 시 보호자에게 자동 알림
- 복약 미응답 지속 시 보호자 알림
- 수분 섭취·수면 시간 체크
- 간단한 인지 상태 체크(치매 조기 발견 목적)
- 위급 상황 SOS 키워드 감지 및 보호자 알림
- 주간/월간 건강 리포트 자동 생성 및 가족에게 공유

## 9. 기대 효과

정해진 시간에 능동적으로 말을 걸고 응답을 처리하는 구조를 통해, 시니어 사용자가 별도의 앱 조작 없이 익숙한 텔레그램 대화만으로 건강 관리 루틴을 유지할 수 있도록 돕는다. 또한 누적된 데이터를 통해 장기적인 건강 추세를 시각적으로 확인할 수 있어, 사용자 본인뿐 아니라 보호자의 건강 모니터링에도 활용 가능하다.
