from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from graph.tools.sql_tool import query_football_analytics_db

class RouteQuery(BaseModel):
    """Fallback structural path tracking if no tool queries are triggered."""
    datasource: str = Field(
        description="The ultimate destination for the question. Choose 'websearch' or 'vectorstore'."
    )

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# Bind the SQL function natively to the router model
router_model_with_tools = llm.bind_tools([query_football_analytics_db])
structured_fallback_router = llm.with_structured_output(RouteQuery)

system_prompt = (
    "You are a master triage routing controller guiding questions through a data graph.\n\n"
    "CRITERIA:\n"
    "1. If a question contains unknown statistical properties or dynamic variable metrics "
    "(e.g., 'top scorer', 'most cards', 'highest market value'), you MUST call 'query_football_analytics_db'.\n"
    "2. If the prompt targets explicit static structural regulations or rule definitions without dynamic lookups, "
    "DO NOT use tools. Simply choose your fallback destination path."
)

route_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{question}")
])

# Export both specialized execution elements
router_base_chain = route_prompt | router_model_with_tools
fallback_router_chain = route_prompt | structured_fallback_router