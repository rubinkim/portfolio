from langchain.prompts import PromptTemplate

# from_template()함수를 사용하는 예제
template = PromptTemplate.from_template(
    "당신은 친절한 AI입니다.\n질문: {question}\n답변:"
)

print(template.format(question="FastAPI가 뭐죠?"))

# 생성자를 호출해서 PromptTemplate 객체를 생성하는 예제
template = PromptTemplate(
    input_variables=["article", "style"],
    template="다음 기사를 {style}로 요약하세요:\n\n{article}"
)

print(template.format(article="OpenAI가 GPT-5를 공개했다...", style="뉴스"))

# load_prompt()함수를 사용해서 파일에서 읽어서 PromptTemplate객체를 생성하는 예제
import os
import yaml
from langchain.prompts import load_prompt

# 현재 디렉토리 절대 경로
current_dir_path = os.path.dirname(os.path.abspath(__file__))

# YAML 파일을 UTF-8로 직접 읽기
yaml_path = f"{current_dir_path}/template_example.yaml"
with open(yaml_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

file_prompt = PromptTemplate(**config)
print(file_prompt.format(context="서울은 한국 수도이다.", question="수도는?"))

# partial 변수를 사용하는 예제
base_prompt = PromptTemplate.from_template("'{text} 문장을 {lang}로 번역하세요.")
ko_prompt = base_prompt.partial(lang="Korean")
en_prompt = base_prompt.partial(lang="English")

print(ko_prompt.format(text="Hello"))
print(en_prompt.format(text="안녕하세요"))