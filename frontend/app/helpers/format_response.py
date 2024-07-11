import json
# Expected team ID


def format_response(response_json):
    response_data = json.loads(response_json["response"])
    formatted_response = f"**Answer:** {response_data['answer']}\n\n"
    if "sources" in response_data:
        formatted_response += "**Sources:**\n"
        for source in response_data["sources"]:
            formatted_response += f"- [{source}]({source})\n"
    return formatted_response
