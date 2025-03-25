# Chatbot Web Platform

This project is a chatbot web platform developed using Python Streamlit. It is deployed using Docker and provides three different chatbot functionalities:

## Chatbot Types

### 1. Tutor Chatbot
- Answers students' questions.
- Aims to provide accurate and educational responses.

### 2. Tutee Chatbot
- Helps students analyze their own understanding.
- When Tutor Chatbot cannot answer accurately, students can ask Tutee Chatbot to identify errors and enhance their comprehension.

### 3. Quizzer Chatbot
- Automatically generates quizzes on different topics.
- Records students' responses for progress tracking.

## Build & Run with Docker
### Build Docker Image
```sh
docker build -t chatbot .
```

### Run Docker Container
```sh
docker run --network="host" -d --rm -v $(pwd):/app chatbot
```
