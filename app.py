import streamlit as st
import json
import os
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List, Dict, Any
import time

# Configure page
st.set_page_config(
    page_title="AI Quiz Maker",
    page_icon="🧠",
    layout="wide"
)

# Initialize Gemini client
@st.cache_resource
def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY", "AIzaSyC1Ya4UKEypukBUOZyUkajjLsMLaA9d_Pw")
    return genai.Client(api_key=api_key)

client = get_gemini_client()

# Pydantic models for structured responses
class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: int  # Index of correct answer (0-3)
    explanation: str

class QuizData(BaseModel):
    questions: List[QuizQuestion]

def generate_quiz(topic: str, num_questions: int) -> List[Dict[str, Any]]:
    """Generate quiz questions using Gemini API"""
    try:
        system_prompt = (
            f"You are an expert quiz maker. Create {num_questions} multiple-choice questions about {topic}. "
            f"Each question should have exactly 4 options (A, B, C, D). "
            f"Provide the correct answer as an index (0 for A, 1 for B, 2 for C, 3 for D). "
            f"Include a brief explanation for each correct answer. "
            f"Make sure questions are educational and appropriately challenging. "
            f"Respond with a JSON object containing a 'questions' array."
        )

        prompt = f"Generate {num_questions} multiple-choice questions about {topic}."

        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[
                types.Content(role="user", parts=[types.Part(text=prompt)])
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=QuizData,
            ),
        )

        if response.text:
            quiz_data = json.loads(response.text)
            return quiz_data.get("questions", [])
        else:
            st.error("Failed to generate quiz questions. Please try again.")
            return []

    except Exception as e:
        st.error(f"Error generating quiz: {str(e)}")
        return []

def display_question(question_data: Dict[str, Any], question_num: int, total_questions: int):
    """Display a single question with multiple choice options"""
    st.subheader(f"Question {question_num} of {total_questions}")
    st.write(question_data["question"])
    
    # Create radio buttons for options
    options = question_data["options"]
    option_labels = [f"{chr(65+i)}. {option}" for i, option in enumerate(options)]
    
    selected_option = st.radio(
        "Choose your answer:",
        options=range(len(options)),
        format_func=lambda x: option_labels[x],
        key=f"question_{question_num}"
    )
    
    return selected_option

def show_result(user_answer: int, correct_answer: int, explanation: str, options: List[str]):
    """Show the result with visual feedback"""
    if user_answer == correct_answer:
        st.success("✅ Correct!")
        st.balloons()
    else:
        st.error("❌ Incorrect!")
        st.write(f"**Correct answer:** {chr(65+correct_answer)}. {options[correct_answer]}")
        st.info(f"**Explanation:** {explanation}")

def main():
    st.title("🧠 AI-Powered Quiz Maker")
    st.write("Generate custom multiple-choice quizzes on any topic using AI!")

    # Initialize session state
    if 'quiz_generated' not in st.session_state:
        st.session_state.quiz_generated = False
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = []
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'show_result' not in st.session_state:
        st.session_state.show_result = False

    # Quiz setup form
    if not st.session_state.quiz_generated:
        st.header("📝 Quiz Setup")
        
        with st.form("quiz_setup"):
            col1, col2 = st.columns(2)
            
            with col1:
                topic = st.text_input(
                    "Quiz Topic",
                    placeholder="e.g., Python Programming, World History, Biology",
                    help="Enter the subject or topic you want to be quizzed on"
                )
            
            with col2:
                num_questions = st.selectbox(
                    "Number of Questions",
                    options=[5, 10, 15, 20],
                    index=1,
                    help="Choose how many questions you want in your quiz"
                )
            
            submitted = st.form_submit_button("🚀 Generate Quiz", use_container_width=True)
            
            if submitted:
                if topic.strip():
                    with st.spinner("🤖 Generating your custom quiz..."):
                        questions = generate_quiz(topic, num_questions)
                        
                        if questions:
                            st.session_state.questions = questions
                            st.session_state.quiz_generated = True
                            st.session_state.current_question = 0
                            st.session_state.user_answers = []
                            st.session_state.quiz_completed = False
                            st.session_state.show_result = False
                            st.rerun()
                        else:
                            st.error("Failed to generate quiz. Please try a different topic.")
                else:
                    st.error("Please enter a quiz topic.")

    # Quiz interface
    elif st.session_state.quiz_generated and not st.session_state.quiz_completed:
        questions = st.session_state.questions
        current_q = st.session_state.current_question
        
        if current_q < len(questions):
            question_data = questions[current_q]
            
            # Progress bar
            progress = (current_q) / len(questions)
            st.progress(progress)
            
            # Display question
            user_answer = display_question(question_data, current_q + 1, len(questions))
            
            # Submit answer button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Submit Answer", use_container_width=True, type="primary"):
                    st.session_state.user_answers.append(user_answer)
                    st.session_state.show_result = True
                    st.rerun()
            
            # Show result if answer was submitted
            if st.session_state.show_result:
                show_result(
                    user_answer,
                    question_data["correct_answer"],
                    question_data["explanation"],
                    question_data["options"]
                )
                
                # Next question or finish quiz
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if current_q < len(questions) - 1:
                        if st.button("Next Question ➡️", use_container_width=True):
                            st.session_state.current_question += 1
                            st.session_state.show_result = False
                            st.rerun()
                    else:
                        if st.button("View Final Results 🎯", use_container_width=True):
                            st.session_state.quiz_completed = True
                            st.rerun()

    # Final results
    elif st.session_state.quiz_completed:
        st.header("🎯 Quiz Results")
        
        questions = st.session_state.questions
        user_answers = st.session_state.user_answers
        
        # Calculate score
        correct_count = sum(1 for i, answer in enumerate(user_answers) 
                           if answer == questions[i]["correct_answer"])
        total_questions = len(questions)
        percentage = (correct_count / total_questions) * 100
        
        # Display overall score
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Score", f"{correct_count}/{total_questions}")
        with col2:
            st.metric("Percentage", f"{percentage:.1f}%")
        with col3:
            if percentage >= 80:
                st.metric("Grade", "🏆 Excellent!")
            elif percentage >= 60:
                st.metric("Grade", "👍 Good!")
            else:
                st.metric("Grade", "📚 Keep Learning!")
        
        # Show performance message
        if percentage >= 80:
            st.success("🎉 Outstanding performance! You've mastered this topic!")
        elif percentage >= 60:
            st.info("👏 Good job! You have a solid understanding of the topic.")
        else:
            st.warning("📖 Keep studying! Review the explanations below to improve.")
        
        st.divider()
        
        # Detailed results for each question
        st.subheader("📊 Detailed Results")
        
        for i, (question_data, user_answer) in enumerate(zip(questions, user_answers)):
            with st.expander(f"Question {i+1}: {question_data['question'][:50]}..."):
                st.write(f"**Question:** {question_data['question']}")
                
                # Show options with indicators
                for j, option in enumerate(question_data["options"]):
                    if j == question_data["correct_answer"]:
                        if j == user_answer:
                            st.success(f"✅ {chr(65+j)}. {option} (Your answer - Correct!)")
                        else:
                            st.success(f"✅ {chr(65+j)}. {option} (Correct answer)")
                    elif j == user_answer and j != question_data["correct_answer"]:
                        st.error(f"❌ {chr(65+j)}. {option} (Your answer - Incorrect)")
                    else:
                        st.write(f"{chr(65+j)}. {option}")
                
                st.info(f"**Explanation:** {question_data['explanation']}")
        
        # Option to take a new quiz
        st.divider()
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Take Another Quiz 🔄", use_container_width=True, type="primary"):
                # Reset all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

if __name__ == "__main__":
    main()
