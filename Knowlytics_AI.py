import streamlit as st
import matplotlib.pyplot as plt
import time
from PyPDF2 import PdfReader
from io import BytesIO
import json

# Import the mcq_generator_llm and mcq_evaluator_llm modules
from mcq_generator import mcq_generator_llm
from mcq_evaluator import mcq_evaluator_llm
from mcq_generator_with_RAG import mcq_generator_with_RAG_llm

# Initialize session state for quiz settings
st.set_page_config(page_title="Knowlytics AI")  # Set page title


if 'quiz_setup_complete' not in st.session_state:
    st.session_state.quiz_setup_complete = False

# Helper function to set the question number when a button is clicked
def set_question(question_number):
    st.session_state.q_no = question_number

# Function to display the question navigation box with color-coded buttons
def display_question_navigation(total_questions):
    num_columns = 5  # Number of buttons per row

    # CSS styling for button colors based on question status
    st.sidebar.markdown(
        """
        <style>
        .button-container {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 8px;
        }
        .button {
            padding: 8px;
            text-align: center;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
            border: 1px solid;
        }
        .default { background-color: #FFFFFF; color: black; border-color: #DDDDDD; }
        .answered { background-color: #4CAF50; color: white; border-color: #4CAF50; }
        .unanswered { background-color: #FFD700; color: black; border-color: #FFD700; }
        .current { background-color: #800080; color: white; border-color: #800080; }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Display buttons in a grid layout
    question_placeholder = st.sidebar.container()
    cols = question_placeholder.columns(num_columns)
    for i in range(1, total_questions + 1):
        # Determine button style based on question status
        if i == st.session_state.q_no:
            button_style = "current"
        elif i in st.session_state.answers:
            button_style = "answered" if st.session_state.answers[i] != "None" else "unanswered"
        else:
            button_style = "default"

        # Render each button using Streamlit's native button and apply CSS classes
        with cols[(i - 1) % num_columns]:
            if st.button(f"{i}", key=f"question_{i}", help="", 
                         on_click=set_question, args=(i,)):
                st.session_state.q_no = i
            st.markdown(f"<div class='button {button_style}'></div>", unsafe_allow_html=True)

# Function to display the MCQ exam page
def display_mcq_exam():
    # Initialize session state for question number, score, finished status, and timer
    if 'q_no' not in st.session_state:
        st.session_state.q_no = 1
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'finished' not in st.session_state:
        st.session_state.finished = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = time.time()
    if 'answers' not in st.session_state:
        st.session_state.answers = {}  # Store answers in session state

    # Total quiz time (5 minutes = 300 seconds)
    total_quiz_time = len(st.session_state.mcq_data["Mcq"]) * 60


    # Display the live countdown timer
    timer_placeholder = st.empty()  # Placeholder for the timer

    # Calculate remaining time
    elapsed_total_time = time.time() - st.session_state.start_time
    remaining_total_time = total_quiz_time - elapsed_total_time

    # Automatically end the quiz if the time is up
    if remaining_total_time <= 0:
        st.session_state.finished = True
        st.warning("Time's up! The quiz is now finished.")

    # Display the remaining time in minutes and seconds
    mins, secs = divmod(remaining_total_time, 60)
    timer_placeholder.markdown(
        f"<div style='text-align: right; font-size: 20px;'>Time left: {int(mins)}:{int(secs):02d} minutes</div>",
        unsafe_allow_html=True
    )

    # Display question navigation box in the sidebar
    display_question_navigation(len(st.session_state.mcq_data["Mcq"]))

    # If the current question is still within the range
    if not st.session_state.finished and st.session_state.q_no <= len(st.session_state.mcq_data["Mcq"]):
        q_data = st.session_state.mcq_data["Mcq"][st.session_state.q_no]

        # Display the question
        st.write(f"Question {st.session_state.q_no}: {q_data['Question']}")

        # Check if the user has already answered this question
        current_answer = st.session_state.answers.get(st.session_state.q_no, None)

        # Display options as radio buttons without pre-selection
        selected_option = st.radio(
            "Choose your answer",
            q_data["Options"],
            index=q_data["Options"].index(current_answer) if current_answer in q_data["Options"] else None,
            key=f"question_{st.session_state.q_no}_option"
        )

        # Button layout: Previous and Save & Next
        col1, col2 = st.columns([1, 2])

        with col2:
            # Save and Next button action
            if st.button("Save and Next", key=f"next_{st.session_state.q_no}"):
                # If no option is selected, treat it as unanswered
                if selected_option:
                    st.session_state.answers[st.session_state.q_no] = selected_option
                else:
                    st.session_state.answers[st.session_state.q_no] = "None"

                # Check if the answer is correct and update the score
                if selected_option == q_data["Correct answer"]:
                    st.session_state.score += 1

                # Move to the next question
                st.session_state.q_no += 1

                # Finish the quiz if the last question is answered
                if st.session_state.q_no > len(st.session_state.mcq_data["Mcq"]):
                    st.session_state.finished = True

                st.experimental_rerun()

        with col1:
            # Previous button action
            if st.session_state.q_no > 1 and st.button("Previous", key=f"prev_{st.session_state.q_no}"):
                st.session_state.q_no -= 1
                st.experimental_rerun()

    # If the quiz is finished, display results
    if st.session_state.finished:
        st.write("--- Test Completed ---")
        correct_answers = 0
        wrong_answers = 0
        unanswered_questions = 0

        # Create a final_answer dictionary to store the entire MCQ data along with user answers
        final_answer = {
            "Topic": st.session_state.get("topic"),
            "Subject": st.session_state.get("subject"),
            "No_of_Questions": st.session_state.get("no_of_questions"),
            "MCQs": {}
        }

        # Display each question with the user's answer and the correct answer
        for q_no, q_data in st.session_state.mcq_data["Mcq"].items():
            user_answer = st.session_state.answers.get(q_no, "None")
            if user_answer == "None":
                unanswered_questions += 1
            elif user_answer == q_data["Correct answer"]:
                correct_answers += 1
            else:
                wrong_answers += 1

            # Save each question, user's answer, and correct answer in the final_answer dictionary
            final_answer["MCQs"][q_no] = {
                "Question": q_data["Question"],
                "Options": q_data["Options"],
                "Correct Answer": q_data["Correct answer"],
                "User Answer": user_answer
            }

        # Display final score
        st.write(f"Your final score is: {correct_answers}/{len(st.session_state.mcq_data['Mcq'])}")

        # Generate pie chart for correct vs wrong vs unanswered questions
        labels = ['Correct Answers', 'Wrong Answers', 'Unanswered']
        sizes = [correct_answers, wrong_answers, unanswered_questions]
        colors = ['#4CAF50', '#FF6347', '#FFD700']
        explode = (0.1, 0, 0)

        fig, ax = plt.subplots()
        ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')

        st.pyplot(fig)

        # Button to view performance analysis
        col1, col2 = st.columns(2)

        with col1:
            if st.button("View Performance Analysis"):
                st.session_state.mcq_analysis_data = mcq_evaluator_llm(final_answer)
                st.session_state.view_analysis = True
                st.experimental_rerun()

        with col2:
            if st.button("Retake Test"):
                # Reset quiz-related session state without clearing quiz setup
                st.session_state.q_no = 1
                st.session_state.score = 0
                st.session_state.finished = False
                st.session_state.answers = {}
                st.session_state.view_analysis = False
                st.session_state.start_time = time.time()
                st.experimental_rerun()

# Function to display the quiz setup form
def display_quiz_setup_form():
    st.title("Knowlytics AI")  # Display title at the top
    with st.form(key="quiz_details_form"):
        st.subheader("Quiz Setup")
        subject = st.text_input("Subject:")
        syllabus = st.text_input("Syllabus:")
        topic = st.text_input("Topic:")
        no_of_questions = st.selectbox("Number of questions:", [10, 20, 25, 30, 50])
        document = st.file_uploader("Upload syllabus document:" , type= "pdf")
        exam_type = st.text_input("Type of Exam:")

        submit_button = st.form_submit_button(label="Submit")

    # Handle form submission
    if submit_button:
        # Ensure required fields are provided
        if not subject or not topic or not exam_type:
            st.warning("Please provide Subject, Topic, and Type of Exam to proceed.")
            return

        # Save form data to session state
        st.session_state["topic"] = topic
        st.session_state["no_of_questions"] = no_of_questions
        st.session_state["syllabus"] = syllabus
        st.session_state["subject"] = subject
        st.session_state["exam_type"] = exam_type

        # Generate MCQs using the mcq_generator_llm function
        if document:
            text = ""
            pdf_reader = PdfReader(BytesIO(document.read()))
            for page in pdf_reader.pages:
                text += page.extract_text()

            st.session_state.mcq_data = mcq_generator_with_RAG_llm(
                topic, no_of_questions, syllabus, subject, exam_type, text
            )
            print(text)
        else:
            st.session_state.mcq_data = mcq_generator_llm(topic, no_of_questions, syllabus, subject, exam_type)

        st.session_state.quiz_setup_complete = True
        st.success("Quiz setup complete! Redirecting to the exam page...")
        st.experimental_rerun()

# Function to display performance analysis
def display_performance_analysis():
    st.write("### Performance Analysis")
    st.markdown(st.session_state.mcq_analysis_data, unsafe_allow_html=True)

    # Button to retake the test
    if st.button("Retake Test"):
        st.session_state.q_no = 1
        st.session_state.score = 0
        st.session_state.finished = False
        st.session_state.answers = {}
        st.session_state.view_analysis = False
        st.session_state.start_time = time.time()
        st.experimental_rerun()

# Main logic to check which page to display
if 'view_analysis' in st.session_state and st.session_state.view_analysis:
    display_performance_analysis()
elif not st.session_state.quiz_setup_complete:
    display_quiz_setup_form()
else:
    display_mcq_exam()
