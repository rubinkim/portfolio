# LangChain과 LangGraph, AI 서비스 구현의 두 축

LangChain과 LangGraph는 LLM(Large Language Model) 기반의 AI 서비스를 구현하는 데 있어 핵심적인 프레임워크입니다. 이 둘은 상호 보완적인 관계를 가지며, 복잡한 AI 애플리케이션을 효율적으로 개발할 수 있도록 돕습니다.

---

## 1. LangChain이란?

LangChain은 LLM을 활용한 애플리케이션 개발을 위한 프레임워크입니다. LLM은 강력하지만 단독으로는 제한적인 기능을 가집니다. 기억력이 없고, 외부 정보에 접근할 수 없으며, 복잡한 다단계 추론을 수행하기 어렵습니다. LangChain은 이러한 한계를 극복하고, LLM을 중심으로 다양한 컴포넌트를 연결하여 강력한 애플리케이션을 구축할 수 있도록 돕습니다.

### 주요 구성 요소

| 구성 요소 | 설명 |
|---|---|
| **LLMs** | OpenAI, Anthropic, Hugging Face 등 다양한 LLM 제공업체와의 인터페이스를 추상화 |
| **Prompts** | LLM에 전달되는 입력 텍스트를 구성하는 도구. 프롬프트 템플릿, 채팅 메시지 포맷터 제공 |
| **Chains** | 여러 LLM 호출, 도구 사용, 데이터 처리 단계를 순차적으로 연결 (LCEL로 유연하게 조합 가능) |
| **Agents** | LLM이 스스로 도구 사용과 다음 행동을 판단·결정하도록 돕는 핵심 개념 |
| **Memory** | 이전 대화의 맥락을 기억하여 지속적인 대화를 가능하게 함 |
| **Retrieval** | 외부 데이터를 LLM 컨텍스트로 가져오는 기능 (RAG 패턴의 핵심) |
| **Tools** | 계산기, 웹 검색, DB 쿼리 등 LLM이 외부 세계와 상호작용하는 인터페이스 |

### LangChain의 장점

- **모듈성 및 추상화** — 다양한 LLM, 도구, 데이터 소스를 일관된 인터페이스로 다룰 수 있음
- **신속한 프로토타이핑** — 복잡한 LLM 애플리케이션을 빠르게 구성·테스트
- **재사용성** — 체인, 에이전트, 도구를 모듈화해 재사용 용이
- **커뮤니티 및 생태계** — 활발한 커뮤니티와 풍부한 통합 라이브러리

---

## 2. LangGraph란?

LangGraph는 LangChain의 상위 개념으로, **상태(State)를 가지는 에이전트와 다단계 워크플로우를 그래프 형태로 정의하고 실행**할 수 있도록 설계된 라이브러리입니다. LangChain의 에이전트는 동적 의사결정을 하지만, 복잡한 제어 흐름(루프, 조건부 분기, 인간 개입)이나 명시적인 상태 관리가 필요한 시나리오에는 한계가 있습니다. LangGraph는 **유한 상태 머신(FSM)** 또는 **액터 모델**과 유사한 접근으로 이 복잡성을 해결합니다.

### 주요 구성 요소

| 구성 요소 | 설명 |
|---|---|
| **State** | 각 노드 간에 공유·수정되는 데이터 객체 (대화 기록, 작업 결과, 목표 등) |
| **Nodes** | 그래프의 각 단계에서 수행되는 독립적인 함수/로직 단위 |
| **Edges** | 노드 간 전환을 정의 (조건부 / 무조건부) |
| **Graph** | 노드와 엣지들의 집합, 워크플로우 전체 구조 |
| **Cycles** | 반복적인 흐름 구현 (예: 검색 → 요약 → 평가 → 재검색 같은 자가 수정 루프) |

### LangGraph의 장점

- **명시적인 상태 관리** — 복잡한 워크플로우의 현재 상태를 명확히 추적
- **복잡한 제어 흐름** — 루프, 조건부 분기, 병렬 처리를 직관적으로 모델링
- **자가 수정 및 반복** — 오류 감지·수정, 정보의 반복적 정제를 쉽게 구현
- **인간 개입(Human-in-the-Loop)** — 특정 단계에서 승인/피드백을 기다리는 워크플로우 구성
- **시각화 용이** — 그래프 구조로 에이전트 동작 흐름을 시각적으로 파악

---

## 3. LangChain + LangGraph로 AI 서비스 구현하기

일반적으로 LangChain의 모듈(LLM, Prompt, Tool, Retrieval)을 LangGraph의 노드 안에서 활용하는 패턴이 널리 쓰입니다.

### 일반적인 AI 서비스 아키텍처

1. **사용자 인터페이스(UI)** — React, Vue, Streamlit, Gradio, 챗봇 인터페이스 등
2. **백엔드 서비스(API Gateway)** — FastAPI, Flask, Django 등
3. **LLM 오케스트레이션 로직** — LangChain / LangGraph
4. **LLM 제공자** — OpenAI, Anthropic, Google Gemini, Hugging Face 등
5. **외부 도구 및 데이터 소스**
   - 벡터 스토어: Chroma, Pinecone, Weaviate (RAG용)
   - 데이터베이스: PostgreSQL, MongoDB 등
   - 외부 API: 검색 엔진, 예약 시스템, CRM 등
   - 클라우드 서비스: AWS, Azure, GCP 등

### 구현 단계별 가이드

#### 단계 1. 서비스 요구사항 정의 및 도구 선택

- **목표 서비스 정의**: 어떤 문제를 해결하고 싶은가? (고객 지원 챗봇, 지식 기반 Q&A, 문서 분석·요약, 자동화 리서치 에이전트 등)
- **LangChain vs. LangGraph 선택**
  - 단순 Q&A·챗봇·문서 요약·간단한 에이전트 → **LangChain**만으로 충분
  - 복잡한 다단계 추론·자가 수정·루프·인간 개입·명시적 상태 관리 필요 → **LangGraph** 고려

#### 단계 2. LangChain 기본 컴포넌트 설정

**LLM 설정**

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o", temperature=0)  # 또는 다른 LLM
```

**프롬프트 템플릿**

```python
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant."),
    ("user", "{input}")
])
```

**도구(Tools) 정의**

```python
from langchain.tools import tool
import requests

@tool
def get_current_weather(location: str) -> str:
    """Get the current weather for a given location."""
    response = requests.get(
        f"https://api.weather.com/v1/current.json?location={location}&apikey=YOUR_API_KEY"
    )
    return response.json()

tools = [get_current_weather]
```

**RAG 설정**

```python
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# 문서 로드
loader = TextLoader("./state_of_the_union.txt")
docs = loader.load()

# 문서 분할
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)

# 임베딩 및 벡터 스토어 생성
embedding_model = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(documents=splits, embedding=embedding_model)
retriever = vectorstore.as_retriever()
```

#### 단계 3. 핵심 로직 구현

##### 3-1. LangChain 기반 구현 (예: RAG 챗봇)

```python
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.chains import create_history_aware_retriever, create_retrieval_chain

# RAG 체인 구성
rag_chain = (
    {
        "context": retriever | RunnableLambda(lambda x: "\n\n".join(doc.page_content for doc in x)),
        "question": RunnablePassthrough(),
    }
    | prompt_template
    | llm
    | StrOutputParser()
)

# 대화 기록을 포함하는 체인 구성 (메모리 사용)
memory = ConversationBufferMemory(return_messages=True, output_key="answer", input_key="question")

# 이전 대화를 바탕으로 검색 쿼리 생성
contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Given a chat history and the latest user question "
     "which might reference context in the chat history, "
     "formulate a standalone question which can be understood "
     "without the chat history. Do NOT answer the question, "
     "just reformulate it if needed and otherwise return it as is."),
    ("user", "{input}")
])
history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

# 검색된 문서를 바탕으로 답변 생성
qa_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an assistant for question-answering tasks. "
     "Use the following pieces of retrieved context to answer the question. "
     "If you don't know the answer, just say that you don't know.\n\n"
     "Context: {context}"),
    ("user", "{input}")
])
question_answer_chain = create_retrieval_chain(history_aware_retriever, qa_prompt | llm | StrOutputParser())

# 최종 대화 체인
conversational_rag_chain = RunnablePassthrough.assign(
    chat_history=RunnableLambda(memory.load_memory_variables) | RunnableLambda(lambda x: x["history"])
) | question_answer_chain
```

##### 3-2. LangGraph 기반 구현 (예: 자가 수정 리서치 에이전트)

**그래프 상태 정의**

```python
from typing import TypedDict, Annotated, List
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]  # 대화 기록
    current_task: str      # 현재 수행 중인 태스크
    research_plan: str     # 리서치 계획
    tool_output: str       # 도구 사용 결과
    iterations: int        # 반복 횟수
```

**노드 정의**

```python
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.tools import DuckDuckGoSearchRun

search_tool = DuckDuckGoSearchRun()  # 웹 검색 도구

# 리서치 계획 생성 노드
def generate_research_plan(state: AgentState):
    print("---GENERATE RESEARCH PLAN---")
    messages = state["messages"]
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a research planner. Given the user's request, "
         "create a detailed research plan, breaking it down into sub-questions. "
         "Output only the plan."),
        messages[-1]  # 마지막 사용자 메시지
    ])
    plan_chain = prompt | llm | StrOutputParser()
    research_plan = plan_chain.invoke({"input": messages[-1].content})
    return {
        "research_plan": research_plan,
        "messages": [AIMessage(content=f"Research Plan: {research_plan}")]
    }

# 검색 수행 노드
def execute_search(state: AgentState):
    print("---EXECUTE SEARCH---")
    research_plan = state["research_plan"]
    search_query = research_plan.split("\n")[0].replace("-", "").strip()
    search_result = search_tool.invoke(search_query)
    return {
        "tool_output": search_result,
        "messages": [AIMessage(content=f"Search Result: {search_result}")]
    }

# 답변 생성 노드
def generate_answer(state: AgentState):
    print("---GENERATE ANSWER---")
    tool_output = state["tool_output"]
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an AI assistant. Based on the following research plan and search results, "
         "provide a comprehensive answer. If more research is needed, indicate that."),
        ("user", f"Research Plan: {state['research_plan']}\nSearch Results: {tool_output}\n\n"
                 "Please provide the answer.")
    ])
    answer_chain = prompt | llm | StrOutputParser()
    answer = answer_chain.invoke({})
    return {"messages": [AIMessage(content=answer)]}

# 추가 검색 필요 여부 판단 노드
def should_continue_research(state: AgentState):
    print("---CHECK FOR MORE RESEARCH---")
    last_message = state["messages"][-1].content
    if "more research is needed" in last_message.lower() or state["iterations"] < 2:
        return "continue_research"
    else:
        return "final_answer"
```

**그래프 빌드**

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)

# 노드 추가
workflow.add_node("plan_research", generate_research_plan)
workflow.add_node("execute_search", execute_search)
workflow.add_node("generate_answer", generate_answer)

# 시작점 설정
workflow.set_entry_point("plan_research")

# 엣지 추가 (조건부 엣지 포함)
workflow.add_edge("plan_research", "execute_search")
workflow.add_edge("execute_search", "generate_answer")
workflow.add_conditional_edges(
    "generate_answer",
    should_continue_research,
    {
        "continue_research": "execute_search",  # 다시 검색 노드로 돌아감 (루프)
        "final_answer": END
    }
)

# 그래프 컴파일
app = workflow.compile()
```

#### 단계 4. 백엔드 API 구현 및 배포

LangChain/LangGraph 로직을 FastAPI로 래핑하여 API 엔드포인트로 노출합니다.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app_fastapi = FastAPI(
    title="LangChain/LangGraph AI Service",
    description="API for our AI assistant using LangChain and LangGraph.",
    version="1.0.0",
)

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"  # 세션 관리를 위한 ID

# LangChain 기반 챗봇 엔드포인트
@app_fastapi.post("/chat_langchain")
async def chat_langchain(request: ChatRequest):
    result = conversational_rag_chain.invoke({"input": request.message, "chat_history": []})
    return {"response": result["answer"]}

# LangGraph 기반 에이전트 엔드포인트
@app_fastapi.post("/agent_langgraph")
async def agent_langgraph(request: ChatRequest):
    initial_state = {
        "messages": [HumanMessage(content=request.message)],
        "current_task": "",
        "research_plan": "",
        "tool_output": "",
        "iterations": 0,
    }
    final_state = app.invoke(initial_state)
    last_message = final_state["messages"][-1].content
    return {"response": last_message}
```

> 💡 세션별 상태 관리가 필요하다면 `SqliteSaver` 같은 checkpointer를 사용해 `thread_id` 기반으로 대화 상태를 저장·복원할 수 있습니다.

#### 단계 5. 배포 및 모니터링

- **배포**: Docker 컨테이너화 후 Kubernetes, AWS ECS/Lambda, Google Cloud Run, Azure App Service 등에 배포
- **모니터링**: LangSmith로 체인 호출, 에이전트 단계, LLM 입출력을 추적·시각화
- **보안**: API 키 관리, 입력 유효성 검사, 민감 정보 처리에 주의
- **확장성**: 비동기 처리, 병렬 처리, 캐싱을 고려해 서비스 확장성 확보

---

## LangChain vs. LangGraph 한눈에 비교

| 특징 | LangChain (단독 사용) | LangGraph |
|---|---|---|
| **복잡성** | 비교적 단순, 선형적 흐름, 기본 에이전트 | 복잡한 다단계·비선형·순환적 워크플로우 |
| **상태 관리** | 명시적이지 않음, 메모리 컴포넌트로 대화 맥락만 관리 | 명시적인 `State` 객체로 모든 워크플로우 상태 관리 |
| **제어 흐름** | 체인(순차적), 에이전트(동적 도구 선택) | 그래프(노드/엣지) 기반의 조건부 분기, 루프, 병렬 처리 |
| **주요 활용** | RAG, 단순 챗봇, 콘텐츠 생성, 기본 태스크 자동화 | 자가 수정 에이전트, 복잡한 리서치, 인간 개입 워크플로우 |
| **학습 곡선** | 비교적 낮음 | 다소 높음 (그래프 개념 이해 필요) |
| **관계** | LangGraph 노드 안에서 LangChain 컴포넌트 사용 가능 | LangChain의 상위 개념, 이를 활용해 더 복잡한 에이전트 구축 |

---

## 마무리

AI 서비스를 구현할 때는 먼저 **LangChain의 체인과 에이전트**로 시작해 기능을 빠르게 구현하고, 서비스가 복잡해지면서 자가 수정 능력·복잡한 제어 흐름·명시적 상태 관리가 필요해질 때 **LangGraph로 전환하거나 통합**하는 전략이 효과적입니다.
