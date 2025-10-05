# AI Quiz Maker

## Overview

AI Quiz Maker is a Streamlit-based web application that generates interactive quizzes using Google's Gemini AI. The application allows users to create custom quizzes on any topic, take them interactively, and track their performance over time. Key features include:

- AI-powered quiz generation with customizable difficulty levels
- Interactive quiz-taking experience with immediate feedback
- Performance tracking and historical statistics
- PDF export of quiz results
- PostgreSQL database for persistent storage

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Technology**: Streamlit web framework

**Design Pattern**: Single-page application with component-based UI

The application uses Streamlit's built-in state management (`st.session_state`) to handle quiz flow and user interactions. The interface is divided into functional sections (quiz generation, quiz taking, history viewing) managed through Streamlit's native components.

**Rationale**: Streamlit was chosen for rapid development of data-centric applications with minimal frontend code. It provides built-in state management and reactive UI updates without requiring separate frontend/backend architecture.

### Backend Architecture

**Technology**: Python with Streamlit server

**Key Components**:
- **Quiz Generation Logic**: Handles interaction with Gemini AI API using structured output (Pydantic models)
- **Database Operations**: SQLAlchemy ORM for data persistence
- **PDF Generation**: ReportLab for creating downloadable quiz reports

**Design Pattern**: The application follows a modular architecture with separation of concerns:
- `app.py`: Main application logic and UI
- `database.py`: Data persistence layer
- `pdf_generator.py`: Report generation

**Rationale**: This modular approach keeps business logic separated and maintainable. Using Pydantic models ensures type safety and structured data validation from the AI responses.

### Data Storage

**Technology**: PostgreSQL database via SQLAlchemy ORM

**Schema Design**:
- `QuizHistory` table stores: topic, difficulty, number of questions, score, percentage, quiz data (JSON), and timestamp
- Quiz questions and answers are serialized as JSON in the `quiz_data` TEXT column

**Rationale**: PostgreSQL provides reliable relational data storage with JSON support for flexible quiz data. SQLAlchemy ORM abstracts database operations and provides database-agnostic code. The hybrid approach (relational metadata + JSON payload) balances structure with flexibility for storing variable quiz content.

**Configuration**: Database connection is configured via `DATABASE_URL` environment variable, supporting various deployment environments.

### Authentication and Authorization

**Current State**: No authentication system implemented

The application currently operates without user authentication, allowing open access to all features.

**Future Consideration**: User authentication could be added to support multi-user environments with personalized quiz histories.

## External Dependencies

### AI Service Integration

**Google Gemini API**
- **Purpose**: AI-powered quiz question generation
- **Integration Method**: Official `google-genai` Python SDK
- **Configuration**: API key provided via `GEMINI_API_KEY` environment variable
- **Data Flow**: Structured output using Pydantic models (`QuizQuestion`, `QuizData`) to ensure consistent response format
- **Features Used**: Text generation with structured JSON responses

### Database Service

**PostgreSQL**
- **Purpose**: Persistent storage of quiz history and statistics
- **Integration Method**: SQLAlchemy ORM
- **Configuration**: Connection string via `DATABASE_URL` environment variable
- **Tables**: `quiz_history` for storing quiz attempts with metadata and results

### PDF Generation

**ReportLab**
- **Purpose**: Generate downloadable PDF reports of quiz results
- **Integration Method**: Python library (local, no external service)
- **Features Used**: Document templates, tables, paragraphs, custom styling

### Python Libraries

**Core Dependencies**:
- `streamlit`: Web application framework
- `google-genai`: Google Gemini API client
- `pydantic`: Data validation and structured outputs
- `sqlalchemy`: Database ORM
- `reportlab`: PDF generation

**Deployment Note**: The application expects a PostgreSQL database to be provisioned and accessible via the `DATABASE_URL` environment variable. Database tables are automatically created on initialization.