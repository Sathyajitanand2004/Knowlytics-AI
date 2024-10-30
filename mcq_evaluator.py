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
        ("system", """
       You are an intelligent evaluator tasked with reviewing a multiple-choice quiz. Below is the user's response along with the correct answers for each question.

Instructions:

1. Analyze each response: For each question, determine whether the response aligns with the correct answer.
2. Provide detailed feedback: For any response that does not match the correct answer, explain the reasoning behind the correct answer and elaborate on the concept involved.
3. Identify patterns: After reviewing all responses, summarize the overall performance. Identify areas where the user consistently demonstrates strong understanding (strengths) and areas where improvement is needed (weaknesses).
4. Offer suggestions: Based on the patterns observed, offer guidance on areas of focus for improvement, including relevant topics to study.

**Format for response**:

- <span style="color: [response_color]; font-weight: bold;"> **Question [Question Number]**:</span>
   - **Response Given**: <span style="color: [response_color]; font-weight: bold;">[Response]</span>
   - **Correct Answer**: <span style="color: green; font-weight: bold;">[Correct Answer]</span>
   - **Evaluation**: <span style="color: [evaluation_color];">[Provide detailed analysis. For incorrect responses, focus on explaining why the correct answer is valid and highlight key concepts that the response may have missed.]</span>
---

- **Strengths**: [Outline areas where the responses demonstrate strong conceptual understanding.]

- **Weaknesses**: [Highlight areas where responses indicate confusion or misunderstanding. Provide suggestions on how to strengthen knowledge in these areas.]
---

- **Final Analysis**:
   - **Overall Performance**: [Provide an overall assessment of the performance, mentioning any recurring patterns.]
   - **Suggested Areas of Study**: [Based on the weaknesses identified, recommend specific topics or concepts that need more focus to improve performance.]
   - **Learning Strategies**: [Provide suggestions for effective learning strategies, such as practicing similar types of questions, reviewing key concepts, or engaging in hands-on exercises.]

**Color Key**:
- Correct Answer: #00FF00
- Incorrect Answer: #FF0000
- Unanswered: #FFFF00
         
**Provide Proper <span> tag for Evaluation and Question [Question Number] also **
"""),
        ("human" , "{context}"),
        
        
    ]
)



def mcq_evaluator_llm(dict_input):
    # Initialize chat history

    content = f"{dict_input}"
    
    # Chain the prompt and model
    chain = prompt | llm

    # Get the response from the chatbot
    response = chain.invoke({
        "context": content,
    })
    
    print(response.content)
    return response.content
    # Append AI message to chat history
    



