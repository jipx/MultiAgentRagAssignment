def route_question(question: str, topic: str) -> str:
    topic = topic.strip().lower()

    try:
        logger.info(f"🔁 Routing question for topic: '{topic}'")

        if topic == "owasp":
            return handle_owasp_question(question)
        elif topic == "assignment":
            return handle_assignment_question(question)
        else:
            raise ValueError(f"❌ Invalid topic received: '{topic}'")
    except Exception as e:
        logger.error(f"❌ Error handling topic '{topic}': {str(e)}")
        raise