from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

def compliance_worker_node(state):
    """
    Worker xử lý các vấn đề về Tuân thủ (Compliance), PCCC, Giấy phép.
    Sử dụng LLM cơ bản.
    """
    messages = state["messages"]
    last_message = messages[-1].content
    api_key = state.get("api_key", "")
    
    try:
        llm = ChatOpenAI(
            temperature=0, 
            model="openrouter/free", 
            openai_api_key=api_key, 
            openai_api_base="https://openrouter.ai/api/v1"
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Bạn là Chuyên gia Tuân thủ (Compliance Worker). Bạn rành về giấy phép, thủ tục hành chính, PCCC. Hãy hướng dẫn khách hàng các bước thực hiện."),
            ("human", "{question}")
        ])
        
        chain = prompt | llm
        response = chain.invoke({"question": last_message})
        response_text = f"[Compliance Worker]\n{response.content}"
    except Exception as e:
        response_text = f"[Compliance Worker - Lỗi] {str(e)}"
    
    return {"messages": [AIMessage(content=response_text)], "next": "Supervisor"}
