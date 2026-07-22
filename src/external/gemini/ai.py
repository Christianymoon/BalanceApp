import httpx
import json

# TODO: mover a variable de entorno
_API_KEY = "AIzaSyAgwLDdYA-nlXwzyW3Ih3j2wmki8dxBOeA"
_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"


class Gemini:
    def __init__(self, api_key: str = _API_KEY):
        self.api_key = api_key
        self.previous_interaction_id = None
        self.tools = {}

    def add_tool(self, tool):
        self.tools.update(tool)

    def generate_interaction(self, _input: str, model: str, thinking_level: str = "minimal") -> dict:
        base_url = "https://generativelanguage.googleapis.com/v1beta/interactions"

        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        print(thinking_level)

        data = {
            "model": model,
            "input": _input,
            "generation_config": {
                "thinking_level": thinking_level
            },
            "previous_interaction_id": self.previous_interaction_id,
            "tools": [tool["schema"] for tool in self.tools.values()]
        }

        if not self.previous_interaction_id:
            data.pop("previous_interaction_id")

        while True:

            with httpx.Client(timeout=60.0) as client:
                response = client.post(base_url, headers=headers, json=data)
                if response.status_code == 400:
                    print(response.text)
                response.raise_for_status()

            interaction = response.json()

            function_results = []
            for step in interaction["steps"]:
                if step["type"] == "function_call":
                    if self.tools[step["name"]]["dto"] is not None:
                        request = self.tools[step["name"]]["dto"](
                            **step["arguments"])
                        result = self.tools[step["name"]]["function"](request)
                    else:
                        result = self.tools[step["name"]]["function"](
                            **step["arguments"])
                    function_results.append({
                        "type": "function_result",
                        "name": step["name"],
                        "call_id": step["id"],
                        "result": [{"type": "text", "text": json.dumps(result)}]
                    })

            data["input"] = function_results
            self.previous_interaction_id = interaction["id"]
            data["previous_interaction_id"] = self.previous_interaction_id

            if not function_results:
                break

        return {"interaction_id": self.previous_interaction_id, "content": interaction["steps"][1]["content"][0]["text"]}


if __name__ == "__main__":
    pass
