import sys
sys.path.append('scripts')
from rag.retrieval_engine import RetrievalEngine

engine = RetrievalEngine()
context = engine.get_context_for_llm('Partner plank band row', n_results=1, domain='exercise')
print("--- RETRIEVED CONTEXT ---")
print(context)
