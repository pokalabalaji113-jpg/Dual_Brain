"""
utils/claude_client.py
Shim — routes all calls to llm_client.py (LangChain + Groq LLaMA 3.3 70B)
"""
from utils.llm_client import call_llm as call_groq
from utils.llm_client import call_llm_with_history as call_groq_with_history

# Keep old names working too
call_claude = call_groq
call_claude_with_history = call_groq_with_history
