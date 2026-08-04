from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

"""
# gemini-2.5-flash 모델을 초기화한다.
model = init_chat_model(model="gemini-2.5-flash", model_provider="google-genai")

# invoke()함수로 받은 질문을 LLM에게 보낸다.
response = model.invoke("LangChain이 뭔가요?")

# 결과값의 문자열만 출력한다.
print(f"모델의 응답은 :\n{response.content}")

from langchain_core.messages import HumanMessage
response = model.invoke([HumanMessage(content="LangGraph가 뭔가요?")])
print(f"모델의 응답은 :\n{response.content}")

"""

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

chat_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
)

messages = [
    SystemMessage(content="당신은 AI에 대해 전문적인 지식을 많이 가진 어시스트입니다."),
    HumanMessage(content="LangChain과 LangGraph에 대해 설명해주고 이들을 이용해서 AI서비스를 구현하는 방법을 간단하게 알려주세요."),
    AIMessage(content="LangChain은 LLM을 활용해서 애플리케이션을 구축하기 위한 프레임워크입니다."),
    HumanMessage(content="각각의 주요 기능 3가지만 알려주세요.")
]

response = chat_model.invoke(messages)
print(f"AI의 응답: \n\n{response.content}")