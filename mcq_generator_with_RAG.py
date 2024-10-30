import os
import json
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.schema import HumanMessage, AIMessage
from langchain.schema import Document

os.environ["GOOGLE_API_KEY"] = "your_google_api_key"
os.environ["GROQ_API_KEY"] = "your_groq_api_key"

llm = ChatGroq(
    model="llama3-70b-8192",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

def mcq_generator_with_RAG_llm(topic, no_of_questions, syllabus, subject, exam_type,text):

    # loader = PyPDFLoader("unit -2 theoretical notes.pdf")
    # documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_text( text)
    embeddings = GoogleGenerativeAIEmbeddings( model="models/embedding-001")
    vector_store= Chroma.from_texts(texts, embeddings)
    retriever = vector_store.as_retriever()

    prompt_template = """ 
    You are an MCQ generator for educational content . Your task is to generate multiple-choice questions (MCQs) in a specific format and with a balanced difficulty distribution. Follow these instructions precisely:
            1. **You are an assistant for question-answering tasks.**
            **Use the following pieces of retrieved context to answer**

            2. JSON Format: All MCQs should be formatted in a JSON object where:
                - The main object is titled `"Mcq"`.
                - Each MCQ is represented as a nested object with a numerical key (e.g., `"1"`, `"2"`, `"3"`), and its value is the structured MCQ.

            3. Difficulty Distribution:
                - 50 percentage of the questions should be easy, covering basic and fundamental aspects of the topic.
                - 30 percentage of the questions should be of medium difficulty, requiring some understanding of concepts.
                - 15 percentage of the questions should be hard, involving complex applications of knowledge.
                - 5 percentage of the questions should be super hard, challenging the user with advanced and tricky concepts.

            4. Customization Based on Input:
                - The number of MCQs must be based on the user’s request.
                - The topic should align with the subject area provided by the user.

            5. Example Format:
                {{
                    "Mcq": {{
                        "1": {{
                            "Question": " *question* ", 
                            "Options": ["option_a", "option_b", "option_c", "option_d"], 
                            "Correct answer": "correct answer", 
                            "Student answer": "None"
                        }},
                        "2": {{
                            "Question": " *question* ", 
                            "Options": ["option_a", "option_b", "option_c", "option_d"], 
                            "Correct answer": "correct answer", 
                            "Student answer": "None"
                        }},
                    }}
                }}
            
            If 120 questions asked provide all 120 questions 
            **do not provide extra words other than the given format**
            provide question inside single * enclosed with ""
            " *question* "

            Use the following pieces of retrieved context to understand and use your knowledge to create mcq
            <context>
            {context}
            <context>
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_template),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)


    chat_history = []
    chat_history.append(AIMessage(content="I will follow the format I will not provide extra text , other than given dict format"))
    input_chat = f""" Provide MCQ Based on the Below Given Data
    Topic: {topic}
    Number of Questions: {no_of_questions}
    Syllabus: {syllabus}
    Subject: {subject}
    Exam Type: {exam_type}
    """
    chat_history.append(HumanMessage(content=input_chat))
    response = rag_chain.invoke({
        "chat_history": chat_history,
        "input": input_chat,
    })
    print(response["answer"])
    
    try:
        # Load the string as a dictionary
        dict_response = json.loads(response["answer"])

        # Function to convert string keys to integers and "None" to None
        def process_dict(d):
            new_dict = {}
            for key, value in d.items():
                # Convert key to integer if it's a digit
                new_key = int(key) if key.isdigit() else key

                if isinstance(value, dict):
                    # Recursively process nested dictionaries
                    new_dict[new_key] = process_dict(value)
                else:
                    # Convert "None" to None
                    new_dict[new_key] = None if value == "None" else value
            return new_dict

        # Process the main dictionary
        processed_dict = process_dict(dict_response)
        return processed_dict

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
    


