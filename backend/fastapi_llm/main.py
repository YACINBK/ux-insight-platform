from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import chromadb
from sentence_transformers import SentenceTransformer
import requests
import json
import os
from pathlib import Path

app = FastAPI()

def get_descriptive_screen_type(screen_type: str, confidence: float) -> str:
    """Transform generic screen types into descriptive, meaningful descriptions with confidence"""
    confidence_percentage = int(confidence * 100)
    
    if confidence < 0.5:
        return f"interface screen (detected as: {screen_type} with {confidence_percentage}% confidence)"
    
    screen_mappings = {
        "profile": "user profile management screen",
        "login": "user authentication screen", 
        "dashboard": "main dashboard interface",
        "settings": "application settings screen",
        "home": "home page interface",
        "search": "search results interface",
        "product": "product details screen",
        "cart": "shopping cart interface",
        "checkout": "checkout process screen",
        "payment": "payment processing interface",
        "account": "account management screen",
        "menu": "navigation menu interface",
        "form": "data entry form interface",
        "list": "content listing interface",
        "detail": "detailed view interface"
    }
    
    descriptive_type = screen_mappings.get(screen_type.lower(), f"{screen_type} interface")
    return f"{descriptive_type} (detected with {confidence_percentage}% confidence)"

# Initialize ChromaDB
print("🔍 Initializing ChromaDB...")
# Use DATA_DIR env (default to ./data) to avoid hardcoded personal paths
data_dir = os.getenv("DATA_DIR", "data")
chroma_path = os.path.join(data_dir, "chroma_db")
Path(chroma_path).mkdir(parents=True, exist_ok=True)
client = chromadb.PersistentClient(path=chroma_path)
print("✅ ChromaDB client created")

try:
    collection = client.get_collection("ux_heuristics")
    print("✅ ChromaDB collection 'ux_heuristics' loaded successfully")
    # Test the collection
    count = collection.count()
    print(f"📊 ChromaDB contains {count} documents")
except Exception as e:
    print(f"❌ Error loading ChromaDB collection: {e}")
    raise

print("🤖 Loading embedding model...")
embedder = SentenceTransformer('BAAI/bge-small-en-v1.5')  # Match the model used in populate_chroma.py
print("✅ Embedding model loaded successfully")
print("🚀 LLM Service ready with ChromaDB RAG!")

class QueryRequest(BaseModel):
    question: str
    tracked_data: Optional[List[Dict[str, Any]]] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    vision: Optional[List[Dict[str, Any]]] = None

class QueryResponse(BaseModel):
    question: str
    relevant_context: List[str]
    metadata: List[Dict[str, Any]]
    answer: str
    sources: List[str]

@app.get("/")
async def root():
    return {"message": "UX LLM Service is running"}

@app.post("/query", response_model=QueryResponse)
async def query_with_rag(request: QueryRequest):
    try:
        print(f"🔍 Processing query: '{request.question}'")
        
        # Embedding
        print("🤖 Generating question embedding...")
        question_embedding = embedder.encode([request.question]).tolist()
        print("✅ Question embedded successfully")
        
        # Vector search in ChromaDB
        print("🔍 Searching ChromaDB for relevant context...")
        results = collection.query(
            query_embeddings=question_embedding,
            n_results=3
        )
        docs = results["documents"][0]
        metadata = results["metadatas"][0]
        context_text = "\n".join(f"- {d}" for d in docs)
        
        print(f"📚 ChromaDB found {len(docs)} relevant documents")
        print(f"🔗 Sources: {[m.get('source', 'Unknown') for m in metadata]}")
        print(f"📄 Context preview: {context_text[:100]}...")
        
        print(f"Received query: {request.question}")
        print(f"Has tracked data: {request.tracked_data is not None}")
        print(f"Has attachments: {request.attachments is not None}")
        print(f"Has vision analysis: {request.vision is not None}")
        if request.vision:
            print(f"Number of images analyzed: {len(request.vision)}")
        
        # Build a clear, LLM-friendly prompt
        full_prompt = f"""
You are a senior UX consultant with 15+ years of experience. Analyze the user interface and usage patterns across the provided screenshots with the expertise of a seasoned professional.

**CORE REQUIREMENTS:**
- Ground all insights in detected UI elements and tracked user interactions
- For each screenshot, mention its classification and confidence level
- Use visual separators (emojis/dots) to distinguish between different screens
- Connect user actions to specific UI elements they interact with
- Provide specific, actionable recommendations
- Structure response: Key Findings → User Behavior → Recommendations → Summary
- **NEVER mention being an AI, LLM, or your role - just provide the analysis directly**
- **WRITE LIKE A SENIOR CONSULTANT** - use dynamic, engaging language that captures attention
- **HANDLE INTERACTION DATA INTELLIGENTLY** - describe user behavior patterns naturally, don't show raw coordinates
- **TRANSFORM UNKNOWN ELEMENTS** - if elements are "Unknown", describe them as "interactive elements" or "UI components"

**MULTIPLE IMAGES:** If multiple screenshots are provided, iterate through each one mentioning its classification and what you observe, then analyze the overall user journey.
## Analysis Request
{request.question}

---
## Relevant Context
{context_text}

---
## Screen & Visual Data
"""
        # Add screen classification for multiple images
        if request.vision and len(request.vision) > 0:
            full_prompt += f"- Number of screenshots analyzed: {len(request.vision)}\n"
            for i, vision_result in enumerate(request.vision):
                image_name = vision_result.get('imageName', f'Image {i+1}')
                full_prompt += f"\n### Screenshot {i+1}: {image_name}\n"
                
                # Add classification
                if 'classification' in vision_result:
                    c = vision_result['classification']
                    label = c.get('label', 'Unknown')
                    conf = c.get('confidence', 0)
                    full_prompt += f"- Screen type: {label} (confidence: {conf:.2f})\n"
                else:
                    full_prompt += "- Screen type: Unknown (confidence: 0.00)\n"
                
                # Add detected elements
                if 'detections' in vision_result:
                    full_prompt += "- Detected UI elements:\n"
                    unknown_count = 0
                    for j, det in enumerate(vision_result['detections']):
                        if isinstance(det, dict):
                            element_class = det.get('class', 'Unknown')
                            if element_class == 'Unknown':
                                unknown_count += 1
                                full_prompt += f"  {j+1}. Interactive UI element at {det.get('bbox', [])} (confidence: {det.get('confidence', 0):.2f})\n"
                            else:
                                full_prompt += f"  {j+1}. {element_class} at {det.get('bbox', [])} (confidence: {det.get('confidence', 0):.2f})\n"
                        else:
                            continue
                    
                    if unknown_count > 0:
                        full_prompt += f"\n  Note: {unknown_count} interactive elements detected but not classified. These represent user-interactive components.\n"
                else:
                    full_prompt += "- No UI elements detected.\n"
        else:
            full_prompt += "- No screenshots provided for analysis.\n"

        full_prompt += "\n---\n## Tracked User Interactions\n"
        if request.tracked_data:
            for i, td in enumerate(request.tracked_data):
                element_type = td.get('elementType', 'Unknown')
                if element_type == 'Unknown':
                    element_type = 'interactive element'
                full_prompt += f"  {i+1}. {td.get('interactionType', 'interact')} with {element_type} at {td.get('bbox', [])} (count: {td.get('interactionCount', 1)})\n"
        else:
            full_prompt += "  No tracked user interactions available.\n"

        if request.attachments:
            full_prompt += "\n---\n## Attachments\n"
            for att in request.attachments:
                full_prompt += f"- {att.get('filename', 'Unknown')} ({att.get('fileType', 'Unknown type')})\n"

        full_prompt += """
---
## Response Guidelines
- Start with overall screen types detected: "Analyzed X screenshots showing [type1] (confidence), [type2] (confidence)..."
- Use bullet points and bold for key terms
- Professional tone with minimal, effective emojis
- If bbox coordinates unclear, focus on element type and interaction patterns
- For multiple screenshots: describe user journey and flow between screens
- **CRITICAL**: Never mention being an AI, LLM, or your capabilities - provide analysis directly
- **WRITE ENGAGINGLY**: Use dynamic language, avoid robotic phrases like "The distinction between..."
- **INTERACTION INSIGHTS**: Describe user behavior patterns naturally - "Users frequently clicked the login button" not "observed at [coordinates]"
- **PROFESSIONAL TONE**: Write like a senior UX consultant, not a technical report
- **ACTIONABLE LANGUAGE**: Use "Implement", "Enhance", "Optimize" instead of "Consider" or "Revise"
- **INTERACTION HANDLING**: 
  * If coordinates are empty [], describe the interaction type and element
  * If interaction count > 1, mention frequency: "Users repeatedly clicked..."
  * Focus on user intent and behavior patterns, not technical details
  * Use natural language: "Users navigated to the profile section" not "interaction pattern observed at []"
- **UNKNOWN ELEMENT HANDLING**:
  * Replace "Unknown" elements with descriptive terms: "interactive buttons", "navigation elements", "content areas"
  * Focus on user behavior around these elements, not their technical classification
  * Describe what users likely intended when interacting with these elements
- **ENGAGING LANGUAGE EXAMPLES**:
  * Instead of "Most screens featured..." → "Users primarily engaged with..."
  * Instead of "High occurrences of..." → "A significant pattern emerged where..."
  * Instead of "Standard navigation conventions..." → "The interface follows familiar patterns..."
  * Instead of "Suggestions for enhancement" → "Strategic UX Improvements"
  * Instead of "Boost Navigation Clarity" → "Streamline Navigation Experience"

Begin your analysis below:
"""

        # Call LLM provider (env-driven)
        provider = os.getenv("LLM_PROVIDER", "openai").lower()

        def to_messages(prompt: str) -> List[Dict[str, str]]:
            return [{"role": "user", "content": prompt}]

        def call_openai(prompt: str) -> str:
            api_key = os.getenv("OPENAI_API_KEY", "")
            if not api_key:
                raise Exception("OPENAI_API_KEY is not set")
            url = "https://api.openai.com/v1/chat/completions"
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            payload = {
                "model": model,
                "messages": to_messages(prompt),
                "temperature": 0.3,
            }
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            r = requests.post(url, headers=headers, json=payload, timeout=120)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"].strip()

        def call_mistral(prompt: str) -> str:
            api_key = os.getenv("MISTRAL_API_KEY", "")
            if not api_key:
                raise Exception("MISTRAL_API_KEY is not set")
            url = "https://api.mistral.ai/v1/chat/completions"
            model = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
            payload = {
                "model": model,
                "messages": to_messages(prompt),
                "temperature": 0.3,
            }
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            r = requests.post(url, headers=headers, json=payload, timeout=120)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"].strip()

        def call_deepseek(prompt: str) -> str:
            api_key = os.getenv("DEEPSEEK_API_KEY", "")
            if not api_key:
                raise Exception("DEEPSEEK_API_KEY is not set")
            url = "https://api.deepseek.com/chat/completions"
            model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            payload = {
                "model": model,
                "messages": to_messages(prompt),
                "temperature": 0.3,
            }
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            r = requests.post(url, headers=headers, json=payload, timeout=120)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"].strip()

        def call_openrouter(prompt: str) -> str:
            api_key = os.getenv("OPENROUTER_API_KEY", "")
            if not api_key:
                raise Exception("OPENROUTER_API_KEY is not set")
            url = "https://openrouter.ai/api/v1/chat/completions"
            # Default to a widely available free/credit model if possible
            model = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")
            payload = {
                "model": model,
                "messages": to_messages(prompt),
                "temperature": 0.3,
            }
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            r = requests.post(url, headers=headers, json=payload, timeout=120)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"].strip()

        def call_ollama(prompt: str, model_env: str) -> str:
            endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
            model = os.getenv(model_env, os.getenv("OLLAMA_MODEL", "mistral:latest"))
            url = f"{endpoint}/api/chat"
            payload = {"model": model, "messages": to_messages(prompt), "stream": False}
            r = requests.post(url, json=payload, timeout=180)
            r.raise_for_status()
            data = r.json()
            # Ollama returns {message: {content: ...}}
            if isinstance(data, dict) and "message" in data:
                return data["message"].get("content", "").strip()
            # Some versions may return choices-like structure
            if "choices" in data:
                return data["choices"][0]["message"]["content"].strip()
            return json.dumps(data)

        # First pass: DeepSeek (or chosen primary model)
        if provider == "openai":
            deepseek_answer = call_openai(full_prompt)
        elif provider == "mistral":
            deepseek_answer = call_mistral(full_prompt)
        elif provider == "deepseek":
            deepseek_answer = call_deepseek(full_prompt)
        elif provider == "openrouter":
            deepseek_answer = call_openrouter(full_prompt)
        elif provider == "ollama":
            # allow specifying a primary model for first pass via OLLAMA_PRIMARY_MODEL
            deepseek_answer = call_ollama(full_prompt, "OLLAMA_PRIMARY_MODEL")
        else:
            raise Exception(f"Unsupported LLM_PROVIDER: {provider}")

        # Improved Mistral validation/enhancement prompt
        validation_prompt = (
            "You are a senior UX writing consultant. Transform this UX analysis into an engaging, dashboard-ready presentation while preserving all insights and UI element mappings.\n"
            "- Use bullet points, bold terms, and clear subheadings\n"
            "- Keep all screen classifications with confidence levels\n"
            "- Preserve visual separators between different screens\n"
            "- Maintain action-to-element connections\n"
            "- Improve visual hierarchy and formatting\n"
            "- **CRITICAL**: Never mention being an AI, LLM, or your role - provide analysis directly\n"
            "- **PRESERVE ENGAGING TONE**: Keep dynamic, consultant-level language - avoid boring technical reports\n"
            "- **ENHANCE READABILITY**: Make the content more scannable and actionable\n"
            "- **TRANSFORM UNKNOWN ELEMENTS**: Replace 'Unknown' with descriptive terms like 'interactive elements'\n"
            "- **USE CONSULTANT LANGUAGE**: Maintain professional but engaging tone throughout\n"
            "- No meta-commentary, rule mentions, or capability statements\n"
            "\n---\n\n"
            f"{deepseek_answer}\n"
            "\n---\n\n"
            "Provide the enhanced, dashboard-ready response:"
        )

        # Second pass: use Mistral-like model for enhancement; fall back to provider if needed
        try:
            if provider == "mistral":
                mistral_answer = call_mistral(validation_prompt)
            elif provider == "openai":
                mistral_answer = call_openai(validation_prompt)
            elif provider == "deepseek":
                mistral_answer = call_deepseek(validation_prompt)
            elif provider == "openrouter":
                mistral_answer = call_openrouter(validation_prompt)
            elif provider == "ollama":
                # allow specifying different enhancement model via OLLAMA_ENHANCE_MODEL
                mistral_answer = call_ollama(validation_prompt, "OLLAMA_ENHANCE_MODEL")
            else:
                mistral_answer = deepseek_answer
        except Exception:
            # If enhancement call fails, return first-pass answer
            mistral_answer = deepseek_answer

        return QueryResponse(
            question=request.question,
            relevant_context=docs,
            metadata=metadata,
            answer=mistral_answer,
            sources=[m.get("source", "Unknown") for m in metadata]
        )
    except Exception as e:
        print(f"Query error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Query error: {e}")
