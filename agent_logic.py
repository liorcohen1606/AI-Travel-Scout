import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

load_dotenv()

def run_travel_scout(destination, month, vibes, include_hotels=False):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
    
    tools = [TavilySearchResults(k=5)]
    
    query = f"Research a trip to {destination} in {month}. Style: {', '.join(vibes)}. Find 3 hidden gems and local tips."
    
    if include_hotels:
        query += " Also, recommend 2-3 specific hotels matching this travel style."

    agent_executor = create_react_agent(llm, tools)
    
    response = agent_executor.invoke({"messages": [HumanMessage(content=query)]})
    
    raw_content = response["messages"][-1].content
    
    # Extract the clean text if the response is a list of content blocks
    if isinstance(raw_content, list):
        for block in raw_content:
            if isinstance(block, dict) and "text" in block:
                return block["text"]
        return str(raw_content)
        
    return raw_content