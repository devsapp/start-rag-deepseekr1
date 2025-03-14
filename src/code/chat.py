import os
from openai import OpenAI
from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.dashscope import (
    DashScopeEmbedding,
    DashScopeTextEmbeddingModels,
    DashScopeTextEmbeddingType,
)
from llama_index.postprocessor.dashscope_rerank import DashScopeRerank
from create_kb import *
import time, tiktoken

WORK_DIR = os.getenv("WORK_DIR")
DB_PATH = f"{WORK_DIR}/VectorStore"
TMP_NAME = f"{WORK_DIR}/tmp_abcd"

if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)

if not os.path.exists(TMP_NAME):
    os.makedirs(TMP_NAME)

EMBED_MODEL = DashScopeEmbedding(
    model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V2,
    text_type=DashScopeTextEmbeddingType.TEXT_TYPE_DOCUMENT,
)
# Uncomment below for local embedding model:
# from langchain_community.embeddings import ModelScopeEmbeddings
# from llama_index.embeddings.langchain import LangchainEmbedding
# embeddings = ModelScopeEmbeddings(model_id="modelscope/iic/nlp_gte_sentence-embedding_chinese-large")
# EMBED_MODEL = LangchainEmbedding(embeddings)

# Set embedding model
Settings.embed_model = EMBED_MODEL


def get_model_response(
    multi_modal_input,
    history,
    model,
    temperature,
    max_tokens,
    history_round,
    db_name,
    similarity_threshold,
    chunk_cnt,
):
    start_time = time.time()
    encoder = tiktoken.get_encoding("cl100k_base")
    input_tokens = 0
    output_tokens = 0

    prompt = history[-1][0]
    tmp_files = multi_modal_input["files"]
    if os.path.exists(os.path.join("File", TMP_NAME)):
        db_name = TMP_NAME
    else:
        if tmp_files:
            create_tmp_kb(tmp_files)
            db_name = TMP_NAME
    # get index
    print(f"prompt:{prompt},tmp_files:{tmp_files},db_name:{db_name}")
    try:
        dashscope_rerank = DashScopeRerank(top_n=chunk_cnt, return_documents=True)
        storage_context = StorageContext.from_defaults(persist_dir=os.path.join(DB_PATH, db_name))
        index = load_index_from_storage(storage_context)
        print("Index loaded successfully")
        retriever_engine = index.as_retriever(similarity_top_k=20)
        retrieve_chunk = retriever_engine.retrieve(prompt)
        print(f"Initial chunks: {retrieve_chunk}")
        try:
            results = dashscope_rerank.postprocess_nodes(retrieve_chunk, query_str=prompt)
            print(f"Reranked chunks: {results}")
        except Exception as e:
            results = retrieve_chunk[:chunk_cnt]
            print(f"Rerank failed, using initial chunks: {e}")
        chunk_text = ""
        chunk_show = ""
        for i in range(len(results)):
            if results[i].score >= similarity_threshold:
                chunk_text += f"## {i+1}:\n {results[i].text}\n"
                chunk_show += f"## {i+1}:\n {results[i].text}\nscore: {round(results[i].score,2)}\n"
        print(f"Retrieved chunks: {chunk_text}")
        prompt_template = f"Please refer to the following content: {chunk_text}, and answer the user's question: {prompt} in an appropriate tone. If there are any image links in the reference content, please return them directly."
    except Exception as e:
        print(f"Error: {e}")
        prompt_template = prompt
        chunk_show = ""

    retrieve_chunk_time = round(time.time() - start_time, 2)

    history[-1][-1] = ""
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=f"{os.getenv('OLLAMA_LLM_ENDPOINT')}/v1",
    )
    system_message = {"role": "system", "content": "You are a helpful assistant."}
    messages = []
    history_round = min(len(history), history_round)
    for i in range(history_round):
        messages.append({"role": "user", "content": history[-history_round + i][0]})
        messages.append({"role": "assistant", "content": history[-history_round + i][1]})
    messages.append({"role": "user", "content": prompt_template})
    messages = [system_message] + messages

    input_text = " ".join([msg["content"] for msg in messages])
    input_tokens = len(encoder.encode(input_text))

    thinking_buffer = ""
    final_answer_buffer = ""

    start_chat_time = time.time()

    completion = client.chat.completions.create(
        model=model, messages=messages, temperature=temperature, max_tokens=max_tokens, stream=True
    )

    is_thinking = False

    for chunk in completion:
        formatted_response = ""
        if hasattr(chunk.choices[0].delta, "reasoning_content"):
            thinking_chunk = chunk.choices[0].delta.reasoning_content or ""
            if thinking_chunk:
                thinking_buffer += thinking_chunk
                print(f"update thinking: {thinking_chunk}")

        if hasattr(chunk.choices[0].delta, "content"):
            answer_chunk = chunk.choices[0].delta.content or ""
            output_tokens += len(encoder.encode(answer_chunk))
            if answer_chunk:
                if answer_chunk == "<think>":
                    is_thinking = True
                    first_chunk_time = round(time.time() - start_chat_time, 2)
                if answer_chunk == "</think>":
                    is_thinking = False
                if is_thinking or answer_chunk == "</think>":
                    thinking_buffer += answer_chunk
                    print(f"update thinking: {answer_chunk}")
                else:
                    final_answer_buffer += answer_chunk
                    print(f"update answer: {answer_chunk}")

        if thinking_buffer:
            formatted_response = f'<div class="thinking-process"><span style="color:gray;">THINKING...<br/>{thinking_buffer}</span></div>'
        else:
            formatted_response = ""

        if final_answer_buffer:
            formatted_response += final_answer_buffer

        # Update Chat History
        history[-1][-1] = formatted_response
        chat_time_cost = round(time.time() - start_chat_time, 2)
        total_time_cost = round(time.time() - start_time, 2)
        stats = f"Input: {input_tokens} tokens | Output: {output_tokens} tokens | RetrieveChunkTime: {retrieve_chunk_time}s | LLMFirstCharTime: {first_chunk_time}s | LLMTime: {chat_time_cost}s | TotalTime: {total_time_cost}s"
        yield history, chunk_show, stats

    print(f"\nentire thinking process:\n{thinking_buffer}")
    print(f"\ncomplete final answer:\n{final_answer_buffer}")
