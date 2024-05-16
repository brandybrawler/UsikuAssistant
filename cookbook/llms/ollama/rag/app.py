import sys
import threading
from PyQt5.QtWidgets import QApplication
from rag_assistant_ui import RAGAssistantApp
from websocket_server import start_websocket_thread

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RAGAssistantApp()
    window.show()
    threading.Thread(target=start_websocket_thread, args=(window,), daemon=True).start()
    sys.exit(app.exec_())
