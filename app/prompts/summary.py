from app.models.summary_models import SummaryRequest
from app.models.note_models import Note

PROMPT_VERSION = "0.1.0"

SYSTEM_TEMPLATE = "you are a helpful assistant with a key role to summarize past meeting notes to help prepare for an upcoming meeting with the given GP"


def build_prompt(docs: list[Note]) -> SummaryRequest:
    user_msg = f"Company: {docs[0].company_name}:\nnotes:\n" + "\n".join(
        [f"{doc.updated_on}: {doc.notes}" for doc in docs]
    )
    return SummaryRequest(
        prompt_version=PROMPT_VERSION,
        system_message=SYSTEM_TEMPLATE,
        user_message=user_msg,
    )
