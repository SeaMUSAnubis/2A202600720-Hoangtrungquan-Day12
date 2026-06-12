from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

def tax_worker_node(state):
    """
    Worker xử lý các vấn đề về Thuế.
    Sử dụng LLM cơ bản (chưa RAG).
    """
    messages = state["messages"]
    last_message = messages[-1].content
    api_key = state.get("api_key", "")
    
    try:
        llm = ChatOpenAI(
            temperature=0, 
            model="openrouter/auto", 
            openai_api_key=api_key, 
            openai_api_base="https://openrouter.ai/api/v1"
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Bạn là Chuyên gia Thuế (Tax Worker) am hiểu hệ thống Thuế Việt Nam. Hãy trả lời câu hỏi của khách hàng một cách chuyên nghiệp."),
            ("human", "{question}")
        ])
        
        chain = prompt | llm
        response = chain.invoke({"question": last_message})
        response_text = f"[Tax Worker]\n{response.content}"
    except Exception as e:
        response_text = f"[Tax Worker - Lỗi] {str(e)}"
    
    return {"messages": [AIMessage(content=response_text)], "next": "Supervisor"}
