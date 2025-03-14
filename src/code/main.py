from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import gradio as gr
import os
from html_string import main_html, plain_html
from upload_file import *
from create_kb import *
from chat import get_model_response


def user(user_message, history):
    print(user_message)
    return {"text": "", "files": user_message["files"]}, history + [[user_message["text"], None]]


def get_chat_block():
    with gr.Blocks(
        theme=gr.themes.Base(),
        css="""
        .gradio_container { background-color: #f0f0f0; }
        .thinking-process { 
            background-color: #f0f0f0; 
            border-left: 4px solid #d0d0d0; 
            padding: 5px 10px; 
            margin: 5px 0;
        }
        .thinking-process span { 
            color: gray !important; 
            font-style: italic;
        }
        .stats {
            margin-top: 12px;
            padding: 8px;
            background: #f5f5f5;
            border-radius: 2px;
            font-size: 0.9em;
            color: #666;
        }
        """,
    ) as chat:
        gr.HTML(plain_html)
        with gr.Row():
            with gr.Column(scale=10):
                chatbot = gr.Chatbot(
                    label="Chatbot",
                    height=600,
                    avatar_images=("images/user.jpeg", "images/deepseek.png"),
                    render_markdown=True,
                    sanitize_html=False,
                )
                stats_display = gr.HTML(
                    value="<div class='stats'>Waiting for the first request...</div>"
                )
                with gr.Row():
                    input_message = gr.MultimodalTextbox(
                        label="Input",
                        file_types=[".xlsx", ".csv", ".docx", ".pdf", ".txt"],
                        scale=7,
                    )
                    clear_btn = gr.ClearButton(chatbot, input_message, scale=1)
            with gr.Column(scale=5):
                knowledge_base = gr.Dropdown(
                    choices=os.listdir(DB_PATH),
                    label="Load Knowledge Base",
                    interactive=True,
                    scale=2,
                )
                with gr.Accordion(label="Retrieved Chunks", open=False):
                    chunk_text = gr.Textbox(
                        label="Retrieved Text Chunks", interactive=False, scale=5, lines=10
                    )
                with gr.Accordion(label="Model Settings", open=True):
                    model = gr.Dropdown(
                        choices=["cap-deepseek-r1"],
                        label="Select Model",
                        interactive=True,
                        value="cap-deepseek-r1",
                        scale=2,
                    )
                    temperature = gr.Slider(
                        maximum=2,
                        minimum=0,
                        interactive=True,
                        label="Temperature",
                        step=0.01,
                        value=0.85,
                        scale=2,
                    )
                    max_tokens = gr.Slider(
                        maximum=2000,
                        minimum=0,
                        interactive=True,
                        label="Max Tokens",
                        step=50,
                        value=1024,
                        scale=2,
                    )
                    history_round = gr.Slider(
                        maximum=30,
                        minimum=1,
                        interactive=True,
                        label="History Rounds",
                        step=1,
                        value=3,
                        scale=2,
                    )
                with gr.Accordion(label="RAG Parameters", open=True):
                    chunk_cnt = gr.Slider(
                        maximum=20,
                        minimum=1,
                        interactive=True,
                        label="Chunk Count",
                        step=1,
                        value=5,
                        scale=2,
                    )
                    similarity_threshold = gr.Slider(
                        maximum=1,
                        minimum=0,
                        interactive=True,
                        label="Similarity Threshold",
                        step=0.01,
                        value=0.2,
                        scale=2,
                    )
        input_message.submit(
            fn=user, inputs=[input_message, chatbot], outputs=[input_message, chatbot], queue=False
        ).then(
            fn=get_model_response,
            inputs=[
                input_message,
                chatbot,
                model,
                temperature,
                max_tokens,
                history_round,
                knowledge_base,
                similarity_threshold,
                chunk_cnt,
            ],
            outputs=[chatbot, chunk_text, stats_display],
        )
        chat.load(update_knowledge_base, [], knowledge_base)
        chat.load(clear_tmp)
    return chat


def get_upload_block():
    with gr.Blocks(theme=gr.themes.Base()) as upload:
        gr.HTML(plain_html)
        with gr.Tab("Unstructured Data"):
            with gr.Accordion(label="Create Category", open=True):
                with gr.Column(scale=2):
                    unstructured_file = gr.Files(file_types=["pdf", "docx", "txt"])
                    with gr.Row():
                        new_label = gr.Textbox(
                            label="Category Name", placeholder="Enter category name", scale=5
                        )
                        create_label_btn = gr.Button("Create Category", variant="primary", scale=1)
            with gr.Accordion(label="Manage Categories", open=False):
                with gr.Row():
                    data_label = gr.Dropdown(
                        choices=os.listdir(UNSTRUCTURED_FILE_PATH),
                        label="Manage Categories",
                        interactive=True,
                        scale=8,
                        multiselect=True,
                    )
                    delete_label_btn = gr.Button("Delete Category", variant="stop", scale=1)
        with gr.Tab("Structured Data"):
            with gr.Accordion(label="Create Data Table", open=True):
                with gr.Column(scale=2):
                    structured_file = gr.Files(file_types=["xlsx", "csv"])
                    with gr.Row():
                        new_label_1 = gr.Textbox(
                            label="Table Name", placeholder="Enter table name", scale=5
                        )
                        create_label_btn_1 = gr.Button("Create Table", variant="primary", scale=1)
            with gr.Accordion(label="Manage Tables", open=False):
                with gr.Row():
                    data_label_1 = gr.Dropdown(
                        choices=os.listdir(STRUCTURED_FILE_PATH),
                        label="Manage Tables",
                        interactive=True,
                        scale=8,
                        multiselect=True,
                    )
                    delete_data_table_btn = gr.Button("Delete Table", variant="stop", scale=1)
        delete_label_btn.click(delete_label, inputs=[data_label]).then(
            fn=update_label, outputs=[data_label]
        )
        create_label_btn.click(
            fn=upload_unstructured_file, inputs=[unstructured_file, new_label]
        ).then(fn=update_label, outputs=[data_label])
        delete_data_table_btn.click(delete_data_table, inputs=[data_label_1]).then(
            fn=update_datatable, outputs=[data_label_1]
        )
        create_label_btn_1.click(
            fn=upload_structured_file, inputs=[structured_file, new_label_1]
        ).then(fn=update_datatable, outputs=[data_label_1])
        upload.load(update_label, [], data_label)
        upload.load(update_datatable, [], data_label_1)
    return upload


def get_knowledge_base_block():
    with gr.Blocks(theme=gr.themes.Base()) as knowledge:
        gr.HTML(plain_html)
        # Unstructured Data KB
        with gr.Tab("Unstructured Data"):
            with gr.Row():
                data_label_2 = gr.Dropdown(
                    choices=os.listdir(UNSTRUCTURED_FILE_PATH),
                    label="Select Categories",
                    interactive=True,
                    scale=2,
                    multiselect=True,
                )
                knowledge_base_name = gr.Textbox(
                    label="KB Name", placeholder="Enter knowledge base name", scale=2
                )
                create_knowledge_base_btn = gr.Button("Create KB", variant="primary", scale=1)
        # Structured Data KB
        with gr.Tab("Structured Data"):
            with gr.Row():
                data_label_3 = gr.Dropdown(
                    choices=os.listdir(STRUCTURED_FILE_PATH),
                    label="Select Tables",
                    interactive=True,
                    scale=2,
                    multiselect=True,
                )
                knowledge_base_name_1 = gr.Textbox(
                    label="KB Name", placeholder="Enter knowledge base name", scale=2
                )
                create_knowledge_base_btn_1 = gr.Button("Create KB", variant="primary", scale=1)
        with gr.Row():
            knowledge_base = gr.Dropdown(
                choices=os.listdir(DB_PATH), label="Manage KBs", interactive=True, scale=4
            )
            delete_db_btn = gr.Button("Delete KB", variant="stop", scale=1)
        create_knowledge_base_btn.click(
            fn=create_unstructured_db, inputs=[knowledge_base_name, data_label_2]
        ).then(update_knowledge_base, outputs=[knowledge_base])
        delete_db_btn.click(delete_db, inputs=[knowledge_base]).then(
            update_knowledge_base, outputs=[knowledge_base]
        )
        create_knowledge_base_btn_1.click(
            fn=create_structured_db, inputs=[knowledge_base_name_1, data_label_3]
        ).then(update_knowledge_base, outputs=[knowledge_base])
        knowledge.load(update_knowledge_base, [], knowledge_base)
        knowledge.load(update_label, [], data_label_2)
        knowledge.load(update_datatable, [], data_label_3)
    return knowledge


app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def read_main():
    html_content = main_html
    return HTMLResponse(content=html_content)


app = gr.mount_gradio_app(app, get_chat_block(), path="/chat")
app = gr.mount_gradio_app(app, get_upload_block(), path="/upload_data")
app = gr.mount_gradio_app(app, get_knowledge_base_block(), path="/create_knowledge_base")
