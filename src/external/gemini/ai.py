import logging
import httpx
import json
import os
import dataclasses

try:
    from dotenv import load_dotenv
    load_dotenv()
    _API_KEY = os.getenv("GEMINI_API_KEY")
except ImportError:
    _API_KEY = "YOUR_API_KEY_HERE"


def default_json_serializer(obj):
    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    return str(obj)


_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"


class Gemini:
    def __init__(self, api_key: str = _API_KEY):
        self.api_key = api_key
        self.previous_interaction_id = None
        self.tools = {}

    def add_tool(self, tool):
        self.tools.update(tool)

    def generate_interaction(self, _input: str, model: str, thinking_level: str = "minimal", instance=None) -> dict:
        base_url = "https://generativelanguage.googleapis.com/v1beta/interactions"

        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }

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
                    pass
                if response.status_code == 429:
                    raise Exception(
                        "Rate limit excedido utiliza otro modelo o disminuye la velocidad de las peticiones")
                response.raise_for_status()

            interaction = response.json()

            _tool_phrases = {
                "fetch_transactions": "Consultando transacciones",
                "fetch_categories": "Obteniendo categorías",
                "fetch_subcategories": "Obteniendo subcategorías",
                "set_transaction": "Registrando transacción",
                "update_transaction": "Actualizando transacción",
                "get_accounts": "Consultando cuentas",
                "fetch_summary": "Calculando resumen",
                "fetch_today": "Obteniendo fecha actual",
            }

            function_results = []
            for step in interaction["steps"]:
                if step["type"] == "function_call":
                    tool_name = step["name"]
                    phrase = _tool_phrases.get(tool_name, tool_name)

                    if instance:
                        instance.set_thinking_phrase(f"{phrase}...")

                    if self.tools[tool_name]["dto"] is not None:
                        request = self.tools[tool_name]["dto"](
                            **step["arguments"])
                        logging.info(
                            f"Requested {tool_name} with dto {request}")
                        result = self.tools[tool_name]["function"](request)
                    else:
                        logging.info(f"Requested {tool_name} without dto")
                        result = self.tools[tool_name]["function"](
                            **step["arguments"])

                    if instance:
                        instance.set_thinking_phrase(f"{phrase} ✓")
                    function_results.append({
                        "type": "function_result",
                        "name": step["name"],
                        "call_id": step["id"],
                        "result": [{"type": "text", "text": json.dumps(result, default=default_json_serializer)}]
                    })

            data["input"] = function_results
            self.previous_interaction_id = interaction["id"]
            data["previous_interaction_id"] = self.previous_interaction_id

            if not function_results:
                break

        return {"interaction_id": self.previous_interaction_id, "content": interaction["steps"][1]["content"][0]["text"]}


if __name__ == "__main__":
    pass
