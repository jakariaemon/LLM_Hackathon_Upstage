import os
import gradio as gr
import requests
import json 
from openai import OpenAI 

API_TOKEN_PREDIBASE_1 = os.getenv("API_TOKEN")
API_TOKEN_PREDIBASE_2 = os.getenv("API_TOKEN_PREDIBASE_2")
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")

client = OpenAI(
    api_key=UPSTAGE_API_KEY,
    base_url="https://api.upstage.ai/v1/solar"
) 

def get_response_classification(input_prompt, adapter_id):
    url = "https://serving.app.predibase.com/b716c42b/deployments/v2/llms/solar-1-mini-chat-240612/generate"
    
    payload = {
        "inputs": input_prompt,
        "parameters": {
            "adapter_id": adapter_id,
            "adapter_source": "pbase",
            "max_new_tokens": 50,
            "temperature": 0.1
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_TOKEN_PREDIBASE_2}"
    }
    
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response.json()


def get_response(input_prompt, adapter_id):
    if adapter_id == "JBL-01/2": 
        url = "https://serving.app.predibase.com/b716c42b/deployments/v2/llms/solar-1-mini-chat-240612/generate"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_TOKEN_PREDIBASE_2}"
        }
    else: 
        url = "https://serving.app.predibase.com/7acd7e70/deployments/v2/llms/solar-1-mini-chat-240612/generate"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_TOKEN_PREDIBASE_1}"
        }
    
    payload = {
        "inputs": input_prompt,
        "parameters": {
            "adapter_id": adapter_id,
            "adapter_source": "pbase",
            "max_new_tokens": 50,
            "temperature": 0.1
        }
    }
    
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response.json()

def translate_to_english(text):
    stream = client.chat.completions.create(
        model="solar-1-mini-translate-koen",
        messages=[
            {
                "role": "user",
                "content": text
            }
        ],
        stream=False,
    )
    return stream.choices[0].message.content 

def format_result(classification, answer):
    formatted_result = f"Automatically Selected Adapater via Classification: {classification} \nDomain Specific Answer: {answer}"
    return formatted_result

def law_advisor(passage, adapter_id, translate):
    input_prompt_classification = f"""
    <|im_start|>system\nYou are an expert classifer. Based on the given Sentece, Classfity them as one of the four category:korean general law, korean business law, japanese general law,japanese business law<|im_end|>
<|im_start|>Input
{passage} <|im_end|>
<|im_start|>Class
    """
    input_prompt_domain_kgl = f"""
    <|im_start|>system
You are a Law Answer generator. Generate a concise answer based on the law. Always response in korean. <|im_end|>
<|im_start|>Question
{passage} <|im_end|>
<|im_start|>Answer
    """

    input_prompt_domain_jgl = f"""
<|im_start|>system
You are a law expert. Based on the given question, generate a single line answer concisely. Always answer in japanese. <|im_end|>
<|im_start|>Question
{passage}
<|im_start|>Answer
"""
    input_prompt_domain_kbl =f"""
<|im_start|>system
You are an bunisee law expert. Based on the given question, generate a single line answer concisely. <|im_end|>
<|im_start|>Question
{passage}
<|im_start|>Answer
"""
    input_prompt_domain_jbl = f"""
<|im_start|>system
You are a law expert. Based on the given question, generate a single line answer concisely. <|im_end|>
<|im_start|>Question
{passage}
<|im_start|>Answer
"""

    response = get_response_classification(input_prompt_classification, adapter_id)
    classification =  response.get("generated_text", "No response")
    
    adapter_map = {
        "korean business law": "KBL-01/1",
        "korean general law": "KGL-01-ko/1",
        "japanese business law": "JBL-01/2",
        "japanese general law": "JGL-01/2"
    }
    domain_adapter_id = adapter_map.get(classification, None) 
    system_prompt_map = {
    "KGL-01-ko/1": input_prompt_domain_kgl, 
    "JGL-01/2": input_prompt_domain_jgl, 
    "KBL-01/1": input_prompt_domain_kbl, 
    "JBL-01/2": input_prompt_domain_jbl,

    }
    domain_prompt = system_prompt_map.get(domain_adapter_id, None)

    domain_response = get_response(domain_prompt, domain_adapter_id)
    answer = domain_response.get("generated_text", "No response")

    if translate:
        answer = translate_to_english(answer)

    formatted_result = format_result(classification, answer)    
    return formatted_result


examples = [
    ["피고인이 피해자에게 욕설을 하고 위험한 물건을 던져 폭행한 행위는 어떤 법률 조항에 해당하는가?"], 
    ["相続等により取得した土地所有権の国庫への帰属に関する法律に基づく政令の施行日はいつですか？"], 
    ["What is the importance of staying up to date on FTA updates for exporters to Korea?"],
    ["What is the registration and license tax in Japan?"]
]

with gr.Blocks() as demo:
    gr.Markdown("# Law Advisor / 법률 자문")
    gr.Markdown("""
**Features / 주요 기능:**
                
    - Automatic Adapter Selection / 자동 어댑터 선택: 도메인별 특화된 분류 어댑터를 통해 자동으로 도메인별 어댑터를 선택합니다.
                
    - Translation Option / 번역 옵션:한국어를 영어로 번역할 수 있는 옵션을 제공합니다.
                
    **Supported Adapters** 
                
    - Korean General Law QA / 한국 일반 법률 질의응답: 한국 일반 법률에 관한 질문에 답변을 제공합니다.
                
    - Japanese General Law QA / 일본 일반 법률 질의응답: 일본 일반 법률에 관한 질문에 답변을 제공합니다.
                
    - Korean Business Law Support / 한국 비즈니스 법률 지원: 한국 비즈니스 법률에 대한 지원을 제공합니다.
                
    - Japanese Business Law Support / 일본 비즈니스 법률 지원: 일본 비즈니스 법률에 대한 지원을 제공합니다.
                
    """)
    
    with gr.Row():
        with gr.Column():
            passage = gr.Textbox(label="Enter your legal query / 법률 질문을 입력하세요", lines=5)
            adapter_id = gr.Dropdown(choices=["adapter-classifer-01/2"], label="Select Adapter / 어댑터 선택")
            translate = gr.Checkbox(label="Translate to English / 영어로 번역") 
            submit_button = gr.Button("Submit / 제출")
        
        with gr.Column():
            output = gr.Textbox(label="Response / 응답", lines=10)
    
    submit_button.click(law_advisor, inputs=[passage, adapter_id, translate], outputs=output)
    
    gr.Examples(
        examples=examples,
        inputs=[passage, adapter_id],
        outputs=output,
        fn=law_advisor,
        cache_examples=False,
        label="Example / 예시"
    )

demo.launch()