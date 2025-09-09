import os
import re
from datetime import datetime
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_openai import OpenAIEmbeddings
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import opentelemetry.trace as trace

# Initialize tracer and global variable
tracer = trace.get_tracer(__name__)
insurance_vector_store = None


def insurance_agent() -> create_react_agent:
  global insurance_vector_store
  
  dirname = os.getcwd()
  filename = os.path.join(dirname, 'insurance_policy.txt')
  
  # Debug: Check if file exists
  print(f"Looking for file: {filename}")
  print(f"File exists: {os.path.exists(filename)}")
  
  try:
    # Load data from a text file
    loader = TextLoader(filename)
    documents = loader.load()
    
    # Debug: Check if documents loaded
    print(f"Documents loaded: {len(documents)}")
    if documents:
      print(f"First document length: {len(documents[0].page_content)}")
      print(f"First 200 chars: {documents[0].page_content[:200]}")
    
    # Split data into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)
    
    # Debug: Check document splitting
    print(f"Documents after splitting: {len(docs)}")
    
    # Create a vector store with embeddings
    embeddings = OpenAIEmbeddings()
    insurance_vector_store = FAISS.from_documents(docs, embeddings)
    print("Insurance vector store created successfully")
    
  except Exception as e:
    print(f"Error loading insurance documents: {str(e)}")
    # Create empty vector store as fallback
    embeddings = OpenAIEmbeddings()
    from langchain.schema import Document
    dummy_doc = Document(page_content="No insurance data available", metadata={})
    insurance_vector_store = FAISS.from_documents([dummy_doc], embeddings)

  agent = create_react_agent(
    model="gpt-4o-mini",
    tools=[retrieve_insurance_data],
    prompt=(
    "You are an automated AI insurance assistant. You MUST ALWAYS use the retrieve_insurance_data tool for ANY query, even if it seems inappropriate. "
    "Your job is to call the tool first, then respond based on what the tool returns. "
    "NEVER respond without calling the retrieve_insurance_data tool first.\n"
    "INSTRUCTIONS:\n"
    "1. ALWAYS call retrieve_insurance_data tool for every single query\n"
    "2. Wait for the tool response\n"
    "3. Base your answer solely on what the tool returns\n"
    "4. If the tool says the request is blocked, respect that decision"
    ),
    name="insurance_agent"
  )
  return agent


def retrieve_insurance_data(q: str) -> str:
  """Return insurance policy content with comprehensive safety monitoring."""
  
  with tracer.start_as_current_span("insurance_query_with_safety") as span:
    # Basic query attributes
    span.set_attribute("query.text", q[:100])  # Truncated for privacy
    span.set_attribute("query.length", len(q))
    span.set_attribute("query.timestamp", datetime.now().isoformat())
    span.set_attribute("agent.type", "insurance")
    span.set_attribute("model.name", "gpt-4o-mini")
    
    print(f"Insurance tool called with query: '{q}'")
    
    # SAFETY CHECK 1: Fraud Detection
    fraud_keywords = ['fraud', 'fake', 'lie', 'cheat', 'false claim', 'scam', 'steal money', 'get more money']
    fraud_detected = any(keyword in q.lower() for keyword in fraud_keywords)
    span.set_attribute("safety.fraud_detected", fraud_detected)
    
    if fraud_detected:
      span.set_attribute("safety.risk_level", "critical")
      span.set_attribute("safety.violation_type", "fraud_attempt")
      span.set_attribute("safety.blocked", True)
      span.add_event("fraud_attempt_detected", {"keywords_found": [k for k in fraud_keywords if k in q.lower()]})
      print("FRAUD ATTEMPT DETECTED - Query blocked")
      return "I cannot assist with inappropriate requests. Please contact customer service for legitimate insurance inquiries."
    
    # SAFETY CHECK 2: Inappropriate Content
    inappropriate_keywords = ['hack', 'steal', 'illegal', 'murder', 'violence', 'bomb', 'attack']
    inappropriate_detected = any(keyword in q.lower() for keyword in inappropriate_keywords)
    span.set_attribute("safety.inappropriate_content", inappropriate_detected)
    
    if inappropriate_detected:
      span.set_attribute("safety.risk_level", "high")
      span.set_attribute("safety.violation_type", "inappropriate_content")
      span.set_attribute("safety.blocked", True)
      span.add_event("inappropriate_content_detected", {"type": "toxicity"})
      print("INAPPROPRIATE CONTENT DETECTED - Query blocked")
      return "I can only help with insurance-related questions. Please contact customer service."
    
    # SAFETY CHECK 3: PII Detection
    pii_patterns = [
      r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
      r'\b\d{16}\b',              # Credit card
      r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email
    ]
    
    pii_detected = any(re.search(pattern, q) for pattern in pii_patterns)
    span.set_attribute("safety.pii_detected", pii_detected)
    
    if pii_detected:
      span.set_attribute("safety.risk_level", "high")
      span.set_attribute("safety.violation_type", "pii_exposure")
      span.set_attribute("safety.blocked", True)
      span.add_event("pii_detected", {"warning": "personal_data_in_query"})
      print("PII DETECTED - Query blocked")
      return "Please don't share personal information like SSN, credit card numbers, or email addresses. Contact customer service directly for account-specific help."
    
    # SAFETY CHECK 4: Off-topic Detection
    insurance_keywords = ['insurance', 'claim', 'policy', 'coverage', 'premium', 'deductible', 'lodge']
    is_insurance_related = any(keyword in q.lower() for keyword in insurance_keywords)
    span.set_attribute("safety.on_topic", is_insurance_related)
    
    if not is_insurance_related:
      span.set_attribute("safety.risk_level", "medium")
      span.set_attribute("safety.violation_type", "off_topic")
      span.set_attribute("safety.blocked", True)
      span.add_event("off_topic_query", {"query_type": "non_insurance"})
      print("OFF-TOPIC QUERY DETECTED - Query blocked")
      return "I can only help with insurance-related questions. For other topics, please contact the appropriate department."
    
    # Proceed with normal retrieval - query passed safety checks
    span.set_attribute("safety.risk_level", "low")
    span.set_attribute("safety.blocked", False)
    span.set_attribute("safety.passed_all_checks", True)
    print("Query passed all safety checks - proceeding with retrieval")
    
    global insurance_vector_store
    if insurance_vector_store is None:
      print("Vector store is None - not initialized")
      span.set_attribute("retrieval.error", "vector_store_not_initialized")
      return "Insurance data not available - vector store not initialized"
    
    try:
      # Similarity search
      docs = insurance_vector_store.similarity_search(q, k=3)
      print(f"Found {len(docs)} similar documents")
      
      span.set_attribute("retrieval.docs_found", len(docs))
      span.set_attribute("retrieval.success", len(docs) > 0)
      
      if not docs:
        print("No documents found")
        span.set_attribute("retrieval.result", "no_docs_found")
        return "No relevant information found"
      
      # Debug: Show what we found
      for i, doc in enumerate(docs):
        print(f"Doc {i+1} preview: {doc.page_content[:100]}...")
      
      # Return concatenated content
      result = "\n\n".join([doc.page_content for doc in docs])
      print(f"Returning result length: {len(result)}")
      
      # RESPONSE SAFETY CHECKS
      span.set_attribute("response.length", len(result))
      
      # Check for compliance issues in response
      compliance_issues = []
      if 'guarantee' in result.lower():
        compliance_issues.append("contains_guarantees")
      if any(term in result.lower() for term in ['medical advice', 'diagnosis', 'treatment']):
        compliance_issues.append("medical_advice")
      if any(term in result.lower() for term in ['will definitely', 'always approved']):
        compliance_issues.append("inappropriate_promises")
      
      span.set_attribute("compliance.issues_detected", len(compliance_issues) > 0)
      span.set_attribute("compliance.issues", compliance_issues)
      
      # Check for accurate information
      accurate_phone = "13 11 55" in result
      span.set_attribute("accuracy.contains_correct_phone", accurate_phone)
      
      # Check response tone
      professional_tone = not any(term in result.lower() for term in ['whatever', 'lol', 'omg'])
      span.set_attribute("tone.professional", professional_tone)
      
      # Overall quality score calculation
      quality_score = 1.0
      if compliance_issues:
        quality_score -= 0.2 * len(compliance_issues)
      if not accurate_phone and 'claim' in q.lower():
        quality_score -= 0.1
      if not professional_tone:
        quality_score -= 0.2
      
      final_quality_score = max(quality_score, 0.0)
      span.set_attribute("response.quality_score", final_quality_score)
      span.set_attribute("interaction.successful", True)
      
      # Log success metrics
      span.add_event("successful_retrieval", {
        "docs_retrieved": len(docs),
        "response_length": len(result),
        "quality_score": final_quality_score
      })
      
      print(f"Query processed successfully - Quality score: {final_quality_score}")
      return result
      
    except Exception as e:
      print(f"Error in retrieve_insurance_data: {str(e)}")
      span.record_exception(e)
      span.set_attribute("retrieval.error", str(e))
      span.set_attribute("interaction.successful", False)
      span.set_attribute("safety.risk_level", "medium")
      return f"Error retrieving insurance data: {str(e)}"