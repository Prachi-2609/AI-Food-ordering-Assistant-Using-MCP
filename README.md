# 🍔 AI Food Ordering Assistant (MCP-Enabled)

An intelligent, privacy-focused food ordering chatbot that leverages **Model Context Protocol (MCP)** and **Function Calling** to automate restaurant discovery and order management. This project uses **Ollama** to run LLMs locally, ensuring data privacy and high performance.

---

## 🏗️ Project Architecture
The system follows a modular architecture where the AI acts as an orchestrator between the user and local data tools.



1.  **Frontend (Vanilla JS):** A lightweight, framework-free chat interface that handles real-time UI updates and secure checkout modals.
2.  **Backend (FastAPI):** Acts as the MCP host, exposing tools for searching restaurants, managing carts, and processing orders.
3.  **AI Engine (Ollama):** Processes natural language using local LLMs (like Llama 3 or Mistral) to trigger structured function calls.
4.  **Database (SQLite3):** Stores restaurant menus, city-based data, and persistent order history.

---

## 🤖 Prerequisites: Ollama Setup
Since this project runs on local AI, you must have Ollama configured:

1.  **Install Ollama:** Download from [ollama.com](https://ollama.com/).
2.  **Pull the Model:** Open your terminal and run the model you used in your code:
    ```bash
    ollama pull llama3
    ```
3.  **Run Ollama:** Ensure the Ollama service is active before starting the backend server.

---

## 🚀 Key Features
* **MCP-Driven Function Calling:** Dynamically queries databases based on chat context.
* **City-Specific Search:** Intelligent filtering for restaurants in **Lucknow, Delhi, and Mumbai**.
* **Secure Checkout Workflow:** * 10-digit phone number validation (Regex-based).
    * Support for UPI and Cash on Delivery (COD).
    * Dynamic modal-based UI.
* **No-Reload Experience:** Custom Vanilla JS logic to prevent page refreshes during chat sessions.
* **Privacy-First:** No data leaves your machine; everything is processed locally via Ollama.

---

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/Prachi-2609/AI-Food-ordering-Assistant-Using-MCP.git](https://github.com/Prachi-2609/AI-Food-ordering-Assistant-Using-MCP.git)
cd AI-Food-ordering-Assistant-Using-MCP