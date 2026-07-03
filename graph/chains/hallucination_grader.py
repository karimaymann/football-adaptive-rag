from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

class GradeHallucinations(BaseModel):
    """Binary score for hallucination check in generation."""
    binary_score: str = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
structured_llm_grader = llm.with_structured_output(GradeHallucinations)

system_prompt = (
    "You are a strict auditor checking if an LLM generation is grounded in / supported by a set of facts.\n"
    "Give a binary score 'yes' or 'no'. 'yes' means the answer is completely supported by the facts and makes no unbacked claims. "
    "'no' means the answer contains hallucinated or completely unsupported information."
)

hallucination_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "Set of facts:\n\n{documents}\n\nLLM Generation: {generation}"),
    ]
)

hallucination_grader_chain = hallucination_prompt | structured_llm_grader