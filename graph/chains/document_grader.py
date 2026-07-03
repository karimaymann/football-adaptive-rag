from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Define the structured schema we want back
class GradeDocuments(BaseModel):
    """Binary score for relevance check on a retrieved document."""
    binary_score: str = Field(
        description="Document is relevant to the question, 'yes' or 'no'"
    )

# Force Gemini to use this schema natively
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
structured_llm_grader = llm.with_structured_output(GradeDocuments)

system_prompt = (
    "You are a strict grader assessing relevance of a retrieved document to a user question.\n"
    "If the document contains keywords or semantic meaning related to the user question, grade it as relevant.\n"
    "Give a binary score 'yes' or 'no' to indicate whether the document is relevant."
)

grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "Retrieved document:\n\n{document}\n\nUser question: {question}"),
    ]
)

# Connect everything into our LCEL chain
document_grader_chain = grade_prompt | structured_llm_grader