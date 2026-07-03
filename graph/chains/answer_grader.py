from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

class GradeAnswer(BaseModel):
    """Binary score to check if the generation addresses the question."""
    binary_score: str = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
structured_llm_grader = llm.with_structured_output(GradeAnswer)

system_prompt = (
    "You are a grader assessing whether an answer completely addresses and resolves a user's question.\n"
    "Give a binary score 'yes' or 'no'. 'yes' means the answer directly answers the question. "
    "'no' means the answer is completely off-topic or fails to resolve the prompt."
)

answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "User question: {question}\n\nLLM Generation: {generation}"),
    ]
)

answer_grader_chain = answer_prompt | structured_llm_grader