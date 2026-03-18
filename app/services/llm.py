from openai import AsyncAzureOpenAI
from collections.abc import AsyncGenerator
from app.models.summary_models import (
    SummaryRequest,
    SummaryResponse,
)
from app.models.note_models import Note
from app.config import Settings
from app.prompts.summary import build_prompt


class LLMService:
    def __init__(self, settings: Settings):
        self.client = AsyncAzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key,
            api_version=settings.azure_openai_api_version,
        )
        self.deployment = settings.azure_openai_deployment_name

    async def generate_summary(self, docs: list[Note]) -> SummaryResponse:
        prompt: SummaryRequest = build_prompt(docs)
        model_response = await self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt.system_message,
                },
                {
                    "role": "user",
                    "content": prompt.user_message,
                },
            ],
            max_completion_tokens=600,
            model=self.deployment,
        )
        res_text = model_response.choices[0].message.content
        if not res_text:
            raise ValueError("LLM returned empty response")
        return SummaryResponse(summary=res_text, prompt_version=prompt.prompt_version)

    async def generate_summary_stream(
        self, docs: list[Note]
    ) -> AsyncGenerator[str, None]:  # type: ignore
        prompt: SummaryRequest = build_prompt(docs)
        stream = await self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt.system_message,
                },
                {
                    "role": "user",
                    "content": prompt.user_message,
                },
            ],
            max_completion_tokens=600,
            model=self.deployment,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                delta_content = chunk.choices[0].delta.content
                yield delta_content
