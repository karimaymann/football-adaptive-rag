from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Define the structured routing choices for the LLM
class RouteQuery(BaseModel):
    """Route a user query to the most applicable datasource."""
    datasource: str = Field(
        description="The destination datasource for the query, choose 'websearch' or 'vectorstore'"
    )

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
structured_llm_router = llm.with_structured_output(RouteQuery)

system_prompt = (
    "You are an expert router directing user questions to a SQL Database, a vector store or a web search engine.\n"
    "CRITERIA FOR CHOOSING:\n"
    "1. Use 'sql_node' for inquiries seeking quantitative stats, market values, player goals, assists, contracts, or specific player/club table data.\n"
    "2. Use 'vectorstore' for conceptual rule interpretations, referee protocols, yellow/red card parameters, or official IFAB Laws.\n"
    "3. Use 'websearch' for live scores from tonight, breaking news, injuries, transfers happening right now, or real-time event tables."
)

route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{question}"),
    ]
)

# Connect it to our executable routing chain
question_router_chain = route_prompt | structured_llm_router