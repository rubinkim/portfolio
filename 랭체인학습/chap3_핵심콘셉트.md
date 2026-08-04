LangChain은 LLM을 더 효과적으로 사용하기 위한 framework(도구들의 모음)이다.
python과 javascript 두가지 언어로 제공된다.
prompt, output parser, LLM, tool, memory, vector store등의 여러 요소들을 chain형태로 연결해서 복잡한 작업을 단순화해준다.

LangChain에서는 Chat Model이라는 개념을 사용하는데 LLM은 주로 단일 문자열 입력을 받고 문자열 응답을 생성하는 반면에,
Chat Model은 Messages라는 객체의 리스트를 입력으로 받고, AI의 응답을 Messages로 출력한다. 
Single turn으로 끝나는 시스템이 아닌 채팅처럼 AI와 메시지를 계속 주고받는 형태를 가정한다.
Messages에는 system, user, AI의 역할이 명시되어 있어, 모델이 대화 흐름과 의도를 파악하는데 도움이 된다.
도구 호출과 구조화된 출력은 거의 대부분의 모델에서 지원한다.

Messages는 Chat Model과 상호작용하는 기본 단위이다.
각 Messages는 content와 role을 가지며, 다양한 모델에서 사용할 수 있는 표준 인터페이스 역할도 담당한다.
실제로 사용하는 코드는 BaseMessage를 상속받은 class가 된다.
SystemMessage: 시스템의 역할지정. Persona 지정에 사용
HumanMessage: 사용자의 입력이나 질문
AIMessage: 채팅모델의 응답에 사용
ToolMessage: 도구 호출의 결과를 AI에게 전달할 때 사용

1. 메시지는 모델과 소통하는 기본 단위이다.
2. 모델에게 입력으로 메시지 리스트를 보낸다.
3. 모델은 메시지를 출력한다.

프롬프트를 동적으로 생산하는 PromptTemplate와 모델의 응답을 원하는 형식으로 가공하는 OutputParser가 핵심역할을 한다.
PromptTemplate는 동적으로 프롬프트를 생성하는 템플릿이다. 변수를 포함하는 템플릿을 정의하고 실행 시점에 변수의 값들을 실젯값으로 채워
넣어서 프롬프트를 완성할 수 있게 해준다. 객체로 만드는 것의 이점은 유지보수가 용이한다는 것과 동적으로 입력 처리를 할 수 있다는 점이다.
또한 PromptTemplate는 Runnable 객체이기에 LCEL(LangChain Expression Language)를 사용할 수 있다는 것이 장점이다.

