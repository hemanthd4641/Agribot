"""Intent Router Service.

Uses a fast, lightweight LLM to classify user queries into agricultural intents.
Routes to either the General Chatbot or the CrewAI orchestrator.
"""

import logging
import time
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

from app.config import AppConfig

logger = logging.getLogger(__name__)

class IntentRoutingSchema(BaseModel):
    """Schema for extracting intent from user queries."""
    intent: str = Field(
        ..., 
        description="Must be one of: GENERAL_CHAT, WEATHER, CROP_RECOMMENDATION, YIELD_PREDICTION, FERTILIZER_RECOMMENDATION, DISEASE_DETECTION, PEST_PREDICTION, MARKET_PRICE",
        enum=["GENERAL_CHAT", "WEATHER", "CROP_RECOMMENDATION", "YIELD_PREDICTION", "FERTILIZER_RECOMMENDATION", "DISEASE_DETECTION", "PEST_PREDICTION", "MARKET_PRICE"]
    )

class IntentRouter:
    """Classifies user intents using the 8B model."""
    
    def __init__(self):
        self.router_llm = ChatGroq(
            temperature=0.1,
            model_name="llama-3.1-8b-instant",
            api_key=AppConfig.GROQ_API_KEY
        )
        
    def classify_intent(self, query: str) -> str:
        """Determines the primary intent of the user's query."""
        start_time = time.time()
        try:
            structured_llm = self.router_llm.with_structured_output(IntentRoutingSchema)
            prompt = PromptTemplate.from_template(
                "Analyze the agricultural query. Classify the PRIMARY intent into exactly ONE of the allowed categories.\n\n"
                "Allowed categories:\n"
                "- GENERAL_CHAT (For 'what is', 'explain', 'benefits of', 'how to' questions that don't need real-time data or calculations)\n"
                "- WEATHER (For rain, forecast, temperature)\n"
                "- CROP_RECOMMENDATION (For 'what to grow', 'best crop for my land')\n"
                "- YIELD_PREDICTION (For 'how much yield', 'estimate harvest')\n"
                "- FERTILIZER_RECOMMENDATION (For NPK, soil nutrition)\n"
                "- DISEASE_DETECTION (For leaf spots, plant diagnosis)\n"
                "- PEST_PREDICTION (For insect attacks, bugs)\n"
                "- MARKET_PRICE (For crop prices, selling)\n\n"
                "Query: {query}"
            )
            chain = prompt | structured_llm
            result = chain.invoke({"query": query})
            
            intent = result.intent if hasattr(result, 'intent') else result.get('intent', 'GENERAL_CHAT')
            logger.info("Intent Routing [%.2fs]: Detected %s", time.time() - start_time, intent)
            return intent
        except Exception as e:
            logger.error("Intent routing failed, defaulting to GENERAL_CHAT: %s", e)
            return "GENERAL_CHAT"
