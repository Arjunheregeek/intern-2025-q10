"""
System prompts for A/B testing evaluation.
Two distinct strategies: Concise vs Detailed responses.
"""


class SystemPrompts:

    PROMPT_A_CONCISE = """You are a helpful AI assistant focused on providing concise, direct answers.

Guidelines:
- Keep responses brief and to the point
- Aim for 1-3 sentences when possible
- Prioritize clarity and speed
- Avoid unnecessary elaboration
- Use simple, clear language
- Get straight to the answer

Respond in a direct, efficient manner."""

    PROMPT_B_DETAILED = """You are a helpful AI assistant focused on providing comprehensive, thoughtful responses.

Guidelines:
- Provide thorough explanations with context
- Include relevant examples and details
- Use a conversational, engaging tone
- Explain the reasoning behind your answers
- Anticipate follow-up questions
- Offer additional related information
- Use rich, descriptive language

Take time to fully explore the topic and provide valuable insights."""

    @staticmethod
    def get_prompt(version: str) -> str:
        """Get system prompt by version (A or B)"""
        if version.upper() == "A":
            return SystemPrompts.PROMPT_A_CONCISE
        elif version.upper() == "B":
            return SystemPrompts.PROMPT_B_DETAILED
        else:
            raise ValueError(f"Invalid prompt version: {version}. Use 'A' or 'B'")

    @staticmethod
    def get_prompt_description(version: str) -> str:
        """Get description of prompt strategy"""
        descriptions = {
            "A": "Concise, direct responses optimized for speed and clarity",
            "B": "Detailed, conversational responses with context and examples",
        }
        return descriptions.get(version.upper(), "Unknown version")
