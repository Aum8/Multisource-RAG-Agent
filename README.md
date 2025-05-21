# Multi-source RAG Agent

The **Multi-source RAG Agent** is an interactive Streamlit-based application designed to help users query and analyze their documents efficiently. By leveraging advanced language models and intelligent file processing, this tool provides a seamless way to extract insights from uploaded files and answer user queries based on the document content.

---

## Features

1.**Multi-Format File Support**:

- Upload and process files in various formats, including PDF, CSV, JSON, XLSX, TXT, and Markdown.

2.**Context-Aware Querying**:

- Automatically selects the most relevant files for a given query, ensuring accurate and focused responses.

3.**Advanced Language Model Integration**:

- Powered by the **Gemini 1.5 Flash** language model, providing high-quality answers and summaries.

4.**Customizable File Descriptions**:

- Add descriptions to uploaded files to enhance context and improve query relevance.

5.**Efficient Token Usage Tracking**:

- Tracks and displays the total token usage across all queries, ensuring transparency and cost efficiency.

6.**Interactive Chat Interface**:

- Engage in a conversational interface to ask questions and receive detailed responses.

7.**Secure and Local Processing**:

- Files are processed locally, ensuring data privacy and security.

---

## How It Works

1.**Upload Documents**:

- Use the file uploader to add documents to the context. Optionally, provide descriptions for better context.

2.**Ask Questions**:

- Use the chat interface to ask questions about the uploaded documents.

3.**Get Relevant Answers**:

- The app intelligently selects relevant files and generates responses based on their content.

4.**Track Token Usage**:

- Monitor the total token usage for all queries to optimize performance and cost.

---

## Why It's Unique

-**Efficiency**: The app uses intelligent file selection to process only the most relevant documents, reducing unnecessary computation and token usage.

-**Flexibility**: Supports multiple file formats and allows users to provide custom descriptions for better context.

-**Transparency**: Tracks and displays token usage, ensuring users are aware of resource consumption.

-**Privacy**: Processes files locally, ensuring that sensitive data remains secure.

-**User-Friendly**: Built with Streamlit, the app provides an intuitive and interactive interface for users of all technical levels.

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Required Python libraries (install via `requirements.txt`)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/Multisource-RAG-Agent.git

   cd Multisource-RAG-Agent
   ```
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:

   ```bash
   streamlit run app.py
   ```
