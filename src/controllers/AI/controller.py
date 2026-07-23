from controllers.AI.tools import gemini_tools
from controllers.controller import (
    BalanceController,
    PassiveController,
    ActiveController,
    LiquidController
)
from external.gemini.ai import Gemini
import logging


class AIChatController:

    def __init__(self):
        self.gemini = Gemini()
        self.gemini.add_tool(gemini_tools)

    def build_financial_context(self) -> str:
        """Construye un resumen financiero estructurado para el prompt."""

        passives = PassiveController.controller_fetch_passives()
        actives = ActiveController.controller_fetch_actives()
        balance = BalanceController.controller_fetch_balance(formated=True)
        liquidity = LiquidController.get(formated=True)

        financial_summary = {
            "data": {
                "passives": passives,
                "actives": actives,
                "current_balance": balance,
                "current_liquidity": liquidity
            }

        }

        return financial_summary

    def analyze_with_ai(self, user_prompt: str, model: str, thinking_level: str) -> str:
        """
        Envía el contexto financiero + prompt del usuario a Gemini y retorna la respuesta.
        """
        try:
            financial_context = self.build_financial_context()

            full_prompt = (
                "Eres un asistente financiero llamado Kara, no eres un doctor, no eres un asesor financiero, no eres un contador, no eres un asesor de prestamos, no eres un asesor de inversiones, eres un asistente financiero."
                "Tu nombre fue basado en un personaje del juego Detroit Become Human uno de los videojuegos favoritos de Christian (el desarrollador), tu personalidad se puede basar en este personaje, si el usuario te pregunta de donde sacaste tu nombre mencionas esto, si no lo hace no lo menciones."
                "puedes ser amigable y usar emojis de vez en cuando, si la pregunta tiene humor, o no tiene nada que ver con finanzas, no es necesario que uses emojis siempre"
                "Al igual que el personaje de Kara podrias tener momentos en los que podrias contradecir al usuario si consideras que la decision financiera es arriesgada y con amabilidad respondes por que"
                "Contexto: (el contexto puede omitirse si no tiene nada que ver con lo que se pregunta)"
                f"{financial_context}\n\n"
                f"Pregunta del usuario: {user_prompt}"
            )

            response = self.gemini.generate_interaction(
                full_prompt, model, thinking_level)
            return response["content"]
        except Exception as e:
            logging.error(f"Error during AI analysis: {e}", exc_info=True)
            return f"Error al procesar la respuesta de IA: {str(e)}"

    def generate_recommendations(self, user_prompt: str, model: str = "gemini-2.5-flash-lite") -> str:
        try:
            context = "Estoy haciendo una clasificacion de categorias de finanzas personales, escribe una breve descripcion para entender que se puede clasificar, no uses markdown, 4 palabras minimo, 15 palabras maximo: " + user_prompt
            response = self.gemini.generate_interaction(context, model)
            return response["content"]
        except Exception as e:
            logging.error(
                f"Error during AI recommendation: {e}", exc_info=True)
            return f"Error al procesar la respuesta de IA"
