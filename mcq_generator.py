from langchain.schema import HumanMessage, AIMessage
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
import json

# Set API key for ChatGroq
os.environ["GROQ_API_KEY"] = "your_groq_api_key"

# Initialize the language model
llm = ChatGroq(
    model="llama3-70b-8192",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# Define the chat prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """You are an MCQ generator for educational content. Your task is to generate multiple-choice questions (MCQs) in a specific format and with a balanced difficulty distribution. Follow these instructions precisely:

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
                        "Question": "*question*", 
                        "Options": ["option_a", "option_b", "option_c", "option_d"], 
                        "Correct answer": "correct answer", 
                        "Student answer": "None"
                    }},
                    "2": {{
                        "Question": "*question*", 
                        "Options": ["option_a", "option_b", "option_c", "option_d"], 
                        "Correct answer": "correct answer", 
                        "Student answer": "None"
                    }},
                }}
            }}
         
         If 120 questions asked provide all 120 questions 
         do not provide extra words other than the given format
         provide question inside single *
"""),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
    ]
)

def mcq_generator_llm(topic, no_of_questions, syllabus, subject, exam_type):
    # Initialize chat history
    chat_history = []
    chat_history.append(AIMessage(content="I will follow the format I will not provide extra text , other than given dict format"))
    # Format input message
    input_chat = f""" Provide MCQ Based on the Below Given Data
    Topic: {topic}
    Number of Questions: {no_of_questions}
    Syllabus: {syllabus}
    Subject: {subject}
    Exam Type: {exam_type}
    """
    
    # Append user message to chat history
    chat_history.append(HumanMessage(content=input_chat))

    # Chain the prompt and model
    chain = prompt | llm

    # Get the response from the chatbot
    response = chain.invoke({
        "chat_history": chat_history,
        "input": input_chat,
    })
    
    print(response.content)
    # Append AI message to chat history
    chat_history.append(AIMessage(content=response.content))

    try:
        # Load the string as a dictionary
        dict_response = json.loads(response.content)

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
