# agents/assignment_agent.py

def handle_assignment_question(question: str) -> str:
    """
    Simulates a response to assignment-related questions.

    Args:
        question (str): The assignment question.

    Returns:
        str: A simulated or hardcoded answer.
    """
    # Example logic: In a real use case, this would query an LLM or knowledge base
    if "deadline" in question.lower():
        return "Assignment deadlines are posted on the course portal."
    elif "format" in question.lower():
        return "Assignments should be submitted as PDF files via the LMS."
    else:
        return f"Thanks for your question. Please refer to the assignment guidelines for more info on: '{question}'"