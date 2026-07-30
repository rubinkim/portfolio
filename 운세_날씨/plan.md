# 매일 아침 날씨+운세 디스코드 알림 — n8n 워크플로우 계획

## 1. 목표
매일 아침 9시 20분, 다음 두 정보를 합쳐 1~2줄로 디스코드 채널에 자동 전송한다.
- 우리 동네(경기도 성남시 분당구 백현동) 오늘 날씨 (Open-Meteo API)
- 오늘의 띠별 운세 (Gemini `gemini-3-flash-preview`, 가벼운 버전)

모든 자동화는 **n8n Cloud**에서 실행하고, 디스코드 전송은 **Webhook** 방식을 쓴다.

## 2. 입력 정보 (확정)
| 항목 | 값 |
|---|---|
| 동네 | 경기도 성남시 분당구 백현동 |
| 이름 | 김한용 |
| 생년월일 (양력) | 1959-08-14 |
| 태어난 시간 | 23:30 |
| 성별 | 남 |
| 띠 | 기해년(己亥年) 돼지띠 (1959년생) |
| 운세 스타일 | 가벼운 "오늘의 띠별 운세" (사주 만세력 계산 없이, 띠 기준 한두 줄) |

- 백현동 좌표는 정확한 지번 대신 판교/백현동 인근 대표 좌표(위도 37.3948, 경도 127.1112)를 사용. Open-Meteo 지오코딩 API가 한국 동 단위를 지원하지 않아 확정.

## 3. 전체 아키텍처 (n8n 워크플로우 노드 구성)

```
[Schedule Trigger: 매일 09:20, Asia/Seoul]
        │
        ├──▶ [HTTP Request: Open-Meteo 날씨 조회]
        │
        ├──▶ [HTTP Request: Gemini API 운세 생성]
        │
        ▼
[Merge (두 결과 합치기)]
        │
        ▼
[Code/Set: 1~2줄 메시지로 가공]
        │
        ▼
[Discord: Webhook으로 전송]
```

- 날씨 조회와 운세 생성은 서로 의존성이 없으므로 **병렬 브랜치**로 두고 Merge 노드에서 합친다.
- Gemini 호출은 매번 같은 형식(오늘 날짜 + 돼지띠)으로 프롬프트를 구성하므로 별도 입력 없이 고정 프롬프트 + 오늘 날짜만 넣어도 충분.

## 4. 단계별 진행 순서 (하나씩 확인하며 진행)

1. **날씨 노드부터 단독 검증**
   - Open-Meteo `https://api.open-meteo.com/v1/forecast` 호출, 위도/경도/필요 필드(최고/최저기온, 강수확률 등) 확인.
   - n8n에서 실행(Execute Node)해서 JSON 응답이 정상적으로 오는지 확인.
2. **Gemini 운세 노드 단독 검증**
   - Gemini API 자격증명(HTTP Header Auth 등)을 n8n Credential로 등록.
   - `gemini-3-flash-preview` 모델로 "1959년생 돼지띠, 오늘 날짜 기준 가벼운 오늘의 운세 한 줄" 프롬프트 호출 후 텍스트 응답 확인.
3. **두 결과 합치기**
   - Merge 노드로 두 브랜치 결과를 하나의 아이템으로 합침.
   - Code(또는 Set) 노드에서 "오늘 성남 분당 날씨: OO / 오늘의 운세: OO" 형태로 1~2줄 문자열 조합.
4. **디스코드 전송 검증**
   - 디스코드 채널에 Webhook 생성 → n8n Discord(Webhook) 노드에 URL 등록 → 조합된 텍스트 전송 테스트.
5. **스케줄 연결**
   - 앞의 1~4번이 모두 개별적으로 잘 동작하는 것을 확인한 뒤, Schedule Trigger(Cron, 매일 09:20, 타임존 Asia/Seoul)를 맨 앞에 연결.
   - 워크플로우 활성화(Active) 전환.
6. **최종 확인**
   - 수동 실행(Execute Workflow) 1회로 실제 디스코드 메시지가 정상 도착하는지 확인.
   - 다음날 09:20 자동 실행 여부 확인.

## 5. 필요한 자격증명 / 준비물
- **Gemini API 키**: 기존 `.env`의 `GEMINI_API_KEY` 재사용 가능 (n8n Credential로 별도 등록, 코드에 하드코딩하지 않음).
- **Discord Webhook URL**: 알림 받을 채널의 채널 설정 → 연동 → 웹후크에서 새로 생성 필요 (사용자가 직접 생성).
- **n8n Cloud 계정**: 이미 사용 중이거나 신규 가입 필요.

## 6. 산출물
- `운세_날씨/` 폴더에 n8n으로 바로 가져오기(Import) 가능한 워크플로우 JSON 파일.
- 자격증명 등록 및 워크플로우 활성화를 위한 간단한 설정 가이드.

## 7. 완료 현황 (2026-07-30 기준)

전체 6단계 모두 완료, n8n Cloud에서 워크플로우 **Published(활성화)** 완료.

| 단계 | 상태 | 비고 |
|---|---|---|
| 1. 날씨 노드 | 완료 | HTTP Request → Open-Meteo `/v1/forecast`, 위도 37.3948 / 경도 127.1112 |
| 2. Gemini 운세 노드 | 완료 | HTTP Request → `models/gemini-3-flash-preview:generateContent` (계획 당시 예상한 `interactions` 엔드포인트 대신 `generateContent` 사용, Header Auth 크리덴셜) |
| 3. Merge + 메시지 조합 | 완료 | Merge(Combine by Position) → Code 노드에서 WMO 코드 매핑 + 2줄 메시지 조합 |
| 4. Discord 전송 | 완료 | 전용 **Discord 노드**(Connection Type: Webhook, Operation: Send a Message) 사용 — 계획 당시의 범용 HTTP Request 대신 전용 노드로 변경 |
| 5. Schedule Trigger 연결 | 완료 | 매일 09:20, 타임존은 n8n 계정 기본값이 이미 Asia/Seoul이라 별도 설정 불필요. 수동 트리거("When clicking 'Execute workflow'")도 테스트용으로 함께 유지 |
| 6. 실행 테스트 및 활성화 | 완료 | 디스코드 `#09-김한용` 채널에 실제 메시지 도착 확인, 워크플로우 Published 전환 |

**작업 방식 관련 특이사항**
- 실제 워크플로우는 처음 테스트하던 워크플로우를 **Duplicate**해서 별도 워크플로우("운세_날씨_스케줄버전")로 만들어 5~6단계를 진행함 (원본은 수동 테스트용으로 보존).
- Gemini API 호출 시 Git Bash에서 curl로 한글 프롬프트를 직접 넘기면 인코딩이 깨져 엉뚱한 응답이 나오는 문제가 있었음 → payload를 파일로 만들어 `--data-binary @file`로 전송해 해결. n8n 자체에서는 이 문제가 발생하지 않음(브라우저가 UTF-8 처리).

**다음에 참고할 만한 확인 포인트**
- 다음날 09:20에 스케줄이 자동으로 실행되는지 n8n Executions 탭에서 확인 필요 (아직 미확인).
- 디스코드 채널이 "AI Agents Cohort 01" 서버의 개인 채널이라, 서버/채널 소속이 바뀌면 Webhook을 다시 만들어야 함.
