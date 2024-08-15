import csv
import time
from tqdm import tqdm
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
import requests
from openai import OpenAI

from datasets import load_dataset

ds = load_dataset("lawcompany/KLAID") 

client = OpenAI(
  api_key="",
  base_url="https://api.upstage.ai/v1/solar"
) 

class RateLimitError(Exception):
    pass

@retry(wait=wait_exponential(multiplier=1, min=4, max=60), stop=stop_after_attempt(5), retry=retry_if_exception_type(RateLimitError))
def generate_qa(entry):
    fact = entry["fact"]
    law = entry["laws_service"]
    user_content = f"fact: {fact} law: {law}"

    try:
        stream = client.chat.completions.create(
            model="solar-1-mini-chat",
            messages=[
                {
                    "role": "system",
                    "content": "You are a QA generator. Please generate a descriptive question based on the fact and generate a concise answer based on the law. All in korean language. Do not add additional info.Generation format-  질문: 답변:"
                },
                {
                    "role": "user",
                    "content": user_content
                }
            ],
            stream=False,
        )

        response_content = stream.choices[0].message.content
        parts = response_content.split("\n")
        question = answer = None
        for part in parts:
            if part.startswith("질문:"):
                question = part
            elif part.startswith("답변:"):
                answer = part

        if question and answer:
            return (question.strip(), answer.strip())
        else:
            return ("Error", "Error in splitting response")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print(f"Rate limit error occurred for entry {entry}: {e}")
            raise RateLimitError(e)
        else:
            print(f"An HTTP error occurred for entry {entry}: {e}")
            return ('Error', str(e))
    except Exception as e:
        print(f"An error occurred for entry {entry}: {e}")
        return ('Error', str(e))


with open('qa_results.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['question', 'answer'])

for entry in tqdm(ds["train"], desc="Processing entries"):
    question, answer = generate_qa(entry)
    with open('qa_results.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([question, answer])
    time.sleep(0.1)

print("Results saved to qa_results.csv")
