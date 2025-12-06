import requests
import sys
from config.logger import setup_logging
from plugins_func.register import register_function, ToolType, ActionResponse, Action

TAG = __name__
logger = setup_logging()

# Define base function description template
SEARCH_FROM_RAGFLOW_FUNCTION_DESC = {
    "type": "function",
    "function": {
        "name": "search_from_ragflow",
        "description": "Query information from knowledge base",
        "parameters": {
            "type": "object",
            "properties": {"question": {"type": "string", "description": "Query question"}},
            "required": ["question"],
        },
    },
}


@register_function(
    "search_from_ragflow", SEARCH_FROM_RAGFLOW_FUNCTION_DESC, ToolType.SYSTEM_CTL
)
def search_from_ragflow(conn, question=None):
    # Ensure string parameters are properly encoded
    if question and isinstance(question, str):
        # Ensure question parameter is UTF-8 encoded string
        pass
    else:
        question = str(question) if question is not None else ""

    base_url = conn.config["plugins"]["search_from_ragflow"].get("base_url", "")
    api_key = conn.config["plugins"]["search_from_ragflow"].get("api_key", "")
    dataset_ids = conn.config["plugins"]["search_from_ragflow"].get("dataset_ids", [])

    url = base_url + "/api/v1/retrieval"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # Ensure all strings in payload are UTF-8 encoded
    payload = {"question": question, "dataset_ids": dataset_ids}

    try:
        # Use ensure_ascii=False to ensure proper handling of Chinese characters during JSON serialization
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=5,
            verify=False,
        )

        # Explicitly set response encoding to utf-8
        response.encoding = "utf-8"

        response.raise_for_status()

        # Get text content first, then manually handle JSON decoding
        response_text = response.text
        import json

        result = json.loads(response_text)

        if result.get("code") != 0:
            error_detail = response.get("error", {}).get("detail", "")
            # Safely log error information
            logger.bind(tag=TAG).error(
                "Failed to get information from RAGflow, reason: %s", str(error_detail)
            )
            return ActionResponse(Action.RESPONSE, None, "RAG interface returned exception")

        chunks = result.get("data", {}).get("chunks", [])
        contents = []
        for chunk in chunks:
            content = chunk.get("content", "")
            if content:
                # Safely process content string
                if isinstance(content, str):
                    contents.append(content)
                elif isinstance(content, bytes):
                    contents.append(content.decode("utf-8", errors="replace"))
                else:
                    contents.append(str(content))

        if contents:
            # Organize knowledge base content in reference mode
            context_text = f"# Regarding question 【{question}】, found in knowledge base:\n"
            context_text += "```\n\n\n".join(contents[:5])
            context_text += "\n```"
        else:
            context_text = "According to knowledge base query results, no relevant information found."
        return ActionResponse(Action.REQLLM, context_text, None)

    except Exception as e:
        # Use safe method to log exception, avoid encoding issues
        logger.bind(tag=TAG).error("Failed to get information from RAGflow, reason: %s", str(e))
        return ActionResponse(Action.RESPONSE, None, "RAG interface returned exception")
