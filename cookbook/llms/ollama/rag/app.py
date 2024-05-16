import sys
import asyncio
import websockets
from typing import List
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog, QMessageBox, QComboBox
from phi.assistant import Assistant
from phi.document import Document
from phi.document.reader.pdf import PDFReader
from phi.utils.log import logger
from assistant import get_rag_assistant
import threading

class RAGAssistantApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Usiku Farm Assistant")
        self.rag_assistant = None
        self.llm_model = None
        self.embeddings_model = None
        self.init_ui()
        self.initialize_assistant()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        self.model_selector = QComboBox()
        self.model_selector.addItems(["llama3"])
        self.model_selector.currentIndexChanged.connect(self.on_model_change)
        main_layout.addWidget(QLabel("Select Model"))
        main_layout.addWidget(self.model_selector)

        self.embeddings_selector = QComboBox()
        self.embeddings_selector.addItems(["llama3"])
        self.embeddings_selector.currentIndexChanged.connect(self.on_embeddings_change)
        main_layout.addWidget(QLabel("Select Embeddings"))
        main_layout.addWidget(self.embeddings_selector)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        main_layout.addWidget(self.chat_display)

        self.input_field = QLineEdit()
        main_layout.addWidget(self.input_field)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.on_send_message)
        main_layout.addWidget(self.send_button)

        self.add_pdf_button = QPushButton("Add PDF to Knowledge Base")
        self.add_pdf_button.clicked.connect(self.on_add_pdf)
        main_layout.addWidget(self.add_pdf_button)

        self.clear_knowledge_base_button = QPushButton("Clear Knowledge Base")
        self.clear_knowledge_base_button.clicked.connect(self.on_clear_knowledge_base)
        main_layout.addWidget(self.clear_knowledge_base_button)

        self.new_run_button = QPushButton("New Run")
        self.new_run_button.clicked.connect(self.on_new_run)
        main_layout.addWidget(self.new_run_button)

        self.run_id_selector = QComboBox()
        self.run_id_selector.currentIndexChanged.connect(self.on_run_id_change)
        main_layout.addWidget(QLabel("Run ID"))
        main_layout.addWidget(self.run_id_selector)

    def restart_assistant(self):
        self.rag_assistant = None
        self.chat_display.clear()
        self.run_id_selector.clear()
        self.initialize_assistant()

    def initialize_assistant(self):
        self.llm_model = self.model_selector.currentText()
        self.embeddings_model = self.embeddings_selector.currentText()
        logger.info(f"---*--- Creating {self.llm_model} Assistant ---*---")
        try:
            self.rag_assistant = get_rag_assistant(llm_model=self.llm_model, embeddings_model=self.embeddings_model)
            run_id = self.rag_assistant.create_run()
            self.run_id_selector.addItem(run_id)
            self.chat_display.append("....")
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Could not create assistant, is the database running?\n{str(e)}")

    def on_model_change(self):
        if self.llm_model != self.model_selector.currentText():
            self.llm_model = self.model_selector.currentText()
            self.restart_assistant()

    def on_embeddings_change(self):
        if self.embeddings_model != self.embeddings_selector.currentText():
            self.embeddings_model = self.embeddings_selector.currentText()
            self.restart_assistant()

    def on_send_message(self):
        prompt = self.input_field.text()
        if prompt:
            self.chat_display.append(f"User: {prompt}")
            self.input_field.clear()
            if self.rag_assistant is None:
                QMessageBox.warning(self, "Warning", "Assistant not initialized.")
                return
            response = ""
            try:
                for delta in self.rag_assistant.run(prompt):
                    response += delta  # type: ignore
                self.chat_display.append(f"Assistant: {response}")
            except AttributeError as e:
                QMessageBox.critical(self, "Error", f"An error occurred while generating a response: {str(e)}")

    def on_add_pdf(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Add PDF", "", "PDF Files (*.pdf)")
        if file_name:
            reader = PDFReader()
            with open(file_name, "rb") as f:
                pdf_documents: List[Document] = reader.read(f)
                if pdf_documents:
                    self.rag_assistant.knowledge_base.load_documents(pdf_documents, upsert=True)
                else:
                    QMessageBox.warning(self, "Warning", "Could not read PDF")

    def on_clear_knowledge_base(self):
        if self.rag_assistant.knowledge_base and self.rag_assistant.knowledge_base.vector_db:
            self.rag_assistant.knowledge_base.vector_db.clear()
            QMessageBox.information(self, "Success", "Knowledge base cleared")

    def on_new_run(self):
        self.restart_assistant()

    def on_run_id_change(self):
        new_run_id = self.run_id_selector.currentText()
        if self.rag_assistant and new_run_id:
            logger.info(f"---*--- Loading {self.llm_model} run: {new_run_id} ---*---")
            self.rag_assistant = get_rag_assistant(llm_model=self.llm_model, embeddings_model=self.embeddings_model, run_id=new_run_id)
            self.chat_display.clear()

async def handle_message(websocket, path, app: RAGAssistantApp):
    async for message in websocket:
        prompt = message
        response = ""
        try:
            if app.rag_assistant is None:
                await websocket.send("Assistant not initialized.")
                continue
            async for delta in app.rag_assistant.run(prompt):
                response += delta  # type: ignore
                await websocket.send(delta)
        except Exception as e:
            await websocket.send(f"Error: {str(e)}")

async def start_websocket_server(app: RAGAssistantApp):
    server = await websockets.serve(lambda ws, path: handle_message(ws, path, app), "localhost", 8765)
    await server.wait_closed()

def start_websocket_thread(app: RAGAssistantApp):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_websocket_server(app))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RAGAssistantApp()
    window.show()
    threading.Thread(target=start_websocket_thread, args=(window,), daemon=True).start()
    sys.exit(app.exec_())
