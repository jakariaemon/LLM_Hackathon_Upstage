import PyPDF2
import requests
import json
import csv
import logging
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def split_pdf(file_path, pages_per_chunk):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        total_pages = len(reader.pages)
        num_chunks = (total_pages + pages_per_chunk - 1) // pages_per_chunk
        chunk_paths = []

        for chunk in range(num_chunks):
            writer = PyPDF2.PdfWriter()
            start_page = chunk * pages_per_chunk
            end_page = min(start_page + pages_per_chunk, total_pages)

            for page in range(start_page, end_page):
                writer.add_page(reader.pages[page])

            output_file_path = f'output/pdf_chunk/chunk_{chunk + 1}.pdf'
            with open(output_file_path, 'wb') as output_file:
                writer.write(output_file)
            
            chunk_paths.append(output_file_path)
            logger.info(f'Saved {output_file_path}')
    
    return chunk_paths

def extract_text_from_pdf(api_key, pdf_chunk_path):
    url = "ocr-url"
    headers = {"Authorization": f"Bearer {api_key}"}
    files = {"document": open(pdf_chunk_path, "rb")}
    response = requests.post(url, headers=headers, files=files)
    response_data = response.json()

    return response_data["text"]

def save_to_csv(terminal_output, csv_file_path):
    lines = terminal_output.strip().split('\n')

    questions = []
    answers = []

    for line in lines:
        if line.startswith("Question:"):
            questions.append(line.replace("Question: ", "").strip())
        elif line.startswith("Answer:"):
            answers.append(line.replace("Answer: ", "").strip())

    qa_pairs = list(zip(questions, answers))

    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        file.seek(0, 2) 
        if file.tell() == 0:
            writer.writerow(["Question", "Answer"]) 
        
        writer.writerows(qa_pairs)  

    logger.info(f"Data has been successfully appended to {csv_file_path}")

def chat_with_upstage(api_key, text):
    prompt = """Please generate at least 10 Q/A based on the provided information. Please align the Q/A with the context. Do not include additional information. QA format as follows: 
Question: 
Answer:
Must obey the format."""
    base_url = "base_url"
    model = "solar-1-mini-chat"
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": text + prompt
        }
    ]

    client = OpenAI(api_key=api_key, base_url=base_url)
    stream_response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )

    response_text = ""
    for chunk in stream_response:
        if chunk.choices[0].delta.content is not None:
            response_text += chunk.choices[0].delta.content
    
    return response_text

def process_pdf(file_path, pages_per_chunk, api_key):
    chunk_paths = split_pdf(file_path, pages_per_chunk)
    extracted_texts = []

    for chunk_path in chunk_paths:
        text = extract_text_from_pdf(api_key, chunk_path)
        extracted_texts.append(text)
        response = chat_with_upstage(api_key, text)
        csv_file_path = 'dataset.csv'
        save_to_csv(response, csv_file_path)
        #print(response)
    
    with open("output/json_file/response.json", "w") as json_file:
        json.dump(extracted_texts, json_file, indent=4)
    return response

api_key = "API-KEY"
file_path = "pdf_file"
pages_per_chunk = 1

logger.info('Processing PDF...')
result = process_pdf(file_path, pages_per_chunk, api_key)
logger.info('Processing complete')

print("Done")



