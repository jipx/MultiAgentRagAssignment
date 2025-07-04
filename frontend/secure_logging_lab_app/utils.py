# utils.py
import os
import requests
import time
import json

def get_filename(prefix, lab, step, ext):
    """
    Generate a consistent filepath based on lab, step, and file type.

    Args:
        prefix (str): e.g. 'labnotes', 'quiz', 'solution'
        lab (str): e.g. 'Lab 1'
        step (str): e.g. 'Step 1'
        ext (str): e.g. 'txt', 'json'

    Returns:
        str: Absolute path to the generated filename
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
    os.makedirs(base_dir, exist_ok=True)

    filename = f"{prefix}_{lab.lower().replace(' ', '_')}_{step.lower().replace(' ', '_')}.{ext}"
    return os.path.join(base_dir, filename)



def poll_for_answer(get_url, request_id, max_attempts=10, delay_sec=3, debug_sidebar=None):
    """
    Polls the Get Answer API until a valid response is received or timeout occurs.

    Args:
        get_url (str): URL of the Get Answer API.
        request_id (str): Request ID returned from Ask API.
        max_attempts (int): Maximum number of polling attempts.
        delay_sec (int): Delay in seconds between attempts.
        debug_sidebar (st.sidebar or None): Optional Streamlit sidebar for debug output.

    Returns:
        dict: Parsed response JSON or empty dict if failed.
    """
    for attempt in range(max_attempts):
        time.sleep(delay_sec)
        try:
            response = requests.post(get_url, params={"request_id": request_id})
            if debug_sidebar:
                debug_sidebar.markdown(f"**📥 Poll Attempt {attempt + 1}:**")
                debug_sidebar.markdown("**Request URL:**")
                debug_sidebar.code(f"{get_url}?request_id={request_id}", language="text")
                debug_sidebar.markdown("**Raw Response:**")
                debug_sidebar.code(response.text, language="json")

            if response.status_code == 200:
                result = response.json()
                if "answer" in result and result["answer"]:
                    return result
                if "error" in result:
                    return {"error": result["error"]}
        except Exception as e:
            if debug_sidebar:
                debug_sidebar.error(f"❌ Polling error: {e}")
    return {}
