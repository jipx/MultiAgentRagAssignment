import logging
from agents.owasp_agent import handle_owasp_question
from agents.assignment_agent import handle_assignment_question
from agents.cloudops_agent import handle_cloudops_question  # 🆕 Import new agent

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def route_question(question: str, topic: str) -> str:
    topic = topic.strip().lower()

    try:
        logger.info(f"🔁 Routing question for topic: '{topic}'")

        if topic == "owasp":
            return handle_owasp_question(question)
        elif topic == "assignment":
            return handle_assignment_question(question)
        elif topic == "cloudops":  # 🆕 Support for cloud operations topic
            return handle_cloudops_question(question)
        else:
            raise ValueError(f"❌ Invalid topic received: '{topic}'")
    except Exception as e:
        logger.error(f"❌ Error handling topic '{topic}': {str(e)}")
        raise
