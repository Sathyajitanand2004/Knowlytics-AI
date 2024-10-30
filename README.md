# Knowlytics AI

Knowlytics AI is a personalized, AI-powered tool designed to generate multiple-choice questions (MCQs) based on any topic or uploaded document. With its Retrieval-Augmented Generation (RAG) capability, Knowlytics AI allows users to assess their knowledge through dynamic quizzes and receive targeted insights for improvement.

---

### **Project Description**

**Knowlytics AI** is an innovative application where users can create custom quizzes on specific topics by simply providing relevant content in PDF format. The tool leverages RAG to generate high-quality MCQs tailored to the uploaded content, helping users test their knowledge and gain a deeper understanding of the material. After completing each quiz, users receive immediate, AI-driven feedback that highlights areas of strength and suggests areas for improvement. Whether for exam preparation or personal learning, Knowlytics AI delivers targeted insights to support efficient self-study.

Key features of **Knowlytics AI** include:
- **Dynamic MCQ Generation** based on user-uploaded PDF documents or chosen topics.
- **Retrieval-Augmented Generation (RAG)** for generating high-quality, context-specific questions.
- **Real-Time Feedback** on quiz performance, identifying strengths and suggesting areas of focus.
- **Comprehensive Performance Analytics** to track progress over time.
- **User-Friendly Interface** for intuitive question navigation and time tracking.

Knowlytics AI empowers users to take control of their learning, providing a structured yet flexible approach to self-assessment.

---

### **Installation and Setup**

To set up and run the **Knowlytics AI** application locally, follow the steps below:

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/Knowlytics-AI.git
   cd Knowlytics-AI
   ```

2. **Set Up a Virtual Environment:**
   
   It's recommended to use a virtual environment to manage dependencies.

   ```bash
   python -m venv venv
   source venv/bin/activate   # For Linux/Mac
   venv\Scripts\activate      # For Windows
   ```

3. **Install the Required Dependencies:**

   Install all the necessary packages by running:

   ```bash
   pip install -r requirements.txt
   ```

   Ensure you have the following packages specified in `requirements.txt`:

   ```txt
   streamlit
   matplotlib
   PyPDF2
   langchain
   langchain-core
   langchain-schema
   langchain-groq
   langchain-google-genai
   langchain-community
   chroma
   chromadb
   groq
   google-generative-ai
   ```

4. **Configure API Keys**:

To use the full functionality of **Knowlytics AI**, set your **GROQ** and **Google Generative AI** API keys in each relevant Python file.

In each file that uses these API keys, add the following lines at the top (or replace existing key settings):

1. **GROQ API Key**:
   ```python
   os.environ["GROQ_API_KEY"] = "your_groq_api_key"
   ```

2. **Google Generative AI API Key**:
   ```python
   os.environ["GOOGLE_API_KEY"] = "your_google_api_key"
   ```

Replace `"your_groq_api_key"` and `"your_google_api_key"` with your actual API keys in every file that includes a reference to the `groq` and `google-generative-ai` modules.

Files to update:
- `mcq_generator_with_RAG.py`
- `mcq_generator.py`
- `mcq_evaluator.py`


---



5. **Run the Application**:

   Once everything is set up, run the application using the following command:

   ```bash
   python -m streamlit run Knowlytics_AI.py
   ```

   This will launch the **Knowlytics AI** web application in your browser.

---

### **How Knowlytics AI Works**

1. **Topic and Document-Based Quiz Setup**:  
   Users can define quiz parameters, including the topic, syllabus, and the number of questions. Upload a PDF syllabus or document to tailor the quiz content specifically to the material.

2. **MCQ Generation with RAG**:  
   The RAG framework enhances MCQ generation by retrieving and embedding relevant information from the uploaded document. This provides high-quality, context-specific questions tailored to the user's needs.

3. **Real-Time Quiz Interaction**:  
   Users can navigate through questions, save responses, and track quiz time with a user-friendly interface. Knowlytics AI also supports immediate feedback on each attempt.

4. **Performance Evaluation and Self-Evaluation Insights**:  
   After quiz completion, the app evaluates responses, providing users with strengths, weaknesses, and targeted improvement suggestions. Performance analytics allow users to track progress and adapt their learning strategies over time.

---

### **Contributing**

Contributions are welcome! Please fork this repository and submit a pull request for any features, improvements, or bug fixes.

--- 

