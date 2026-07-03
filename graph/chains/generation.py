from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Define a focused system prompt instructing the LLM to behave like a strict rule scholar
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert football referee and legal rules analyst. "
            "Answer the user's question accurately using ONLY the provided context. "
            "If the context does not contain the answer, explicitly state that you do not know.\n\n"
            "Context:\n{context}",
        ),
        ("human", "{question}"),
    ]
)

# 2. Initialize the Gemini Chat model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0  # Zero temperature forces factual precision
)

# 3. Pipe them into a tight, clean LCEL chain
generation_chain = prompt | llm | StrOutputParser()