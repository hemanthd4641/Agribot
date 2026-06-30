"""Domain Guard Service.

Validates that all inputs (text, audio, image) belong strictly to the
agriculture domain before allowing LLM processing.
"""

import json
import logging
from typing import Dict, Any, Tuple

from flask import current_app

logger = logging.getLogger(__name__)

class DomainGuard:
    """Gatekeeper for strict agricultural domain restriction."""

    # Keywords that trigger immediate rejection for documents/OCR
    FORBIDDEN_KEYWORDS = {
        "hospital", "patient", "diagnosis", "prescription", "doctor",
        "medical", "blood", "laboratory", "invoice", "court", "lawyer",
        "passport", "resume"
    }

    AGRICULTURE_KEYWORDS = {
        "crop", "farm", "soil", "pest", "fertilizer", "weather",
        "seed", "irrigation", "livestock", "harvest", "agriculture",
        "plant", "leaf", "disease", "yield"
    }

    def __init__(self):
        """Initialize the Domain Guard."""
        logger.info("DomainGuard initialized.")

    def validate_text(self, text: str) -> Tuple[bool, str]:
        """Validate if the text query is strictly related to agriculture.
        
        Args:
            text: The user's text query.
            
        Returns:
            Tuple (is_valid, error_message).
        """
        if not text or not text.strip():
            return False, "Empty query."

        # Fast keyword rejection for obvious non-agri docs (if it's a long text/PDF content)
        text_lower = text.lower()
        forbidden_hits = sum(1 for kw in self.FORBIDDEN_KEYWORDS if kw in text_lower)
        if forbidden_hits > 0:
            logger.warning("DomainGuard rejected text based on forbidden keywords.")
            return False, self._get_refusal_message()

        try:
            llm_service = current_app.llm_service
            if not llm_service.client:
                return True, "" # Skip validation if LLM is unavailable

            prompt = (
                "You are a strict domain classifier. Analyze the following text and determine if it is "
                "related to agriculture, farming, crops, livestock, soil, fertilizers, or agricultural weather.\n"
                "Return ONLY a JSON object with two keys: 'is_agriculture' (boolean) and 'confidence' (integer from 0 to 100).\n\n"
                f"Text to analyze: \"{text}\""
            )

            response = llm_service.client.chat.completions.create(
                model=llm_service.config.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            
            result_str = response.choices[0].message.content.strip()
            result = json.loads(result_str)
            
            is_agri = result.get('is_agriculture', False)
            confidence = result.get('confidence', 0)
            
            if is_agri and confidence >= 90:
                return True, ""
            else:
                logger.warning(f"DomainGuard text validation failed: {result}")
                return False, self._get_refusal_message()
                
        except Exception as e:
            logger.error("DomainGuard text validation error: %s", e)
            # Fail closed or open? Let's fail open if the LLM validation errors out to not break the app
            return True, ""

    def validate_image(self, image_b64: str, mime_type: str) -> Tuple[bool, str]:
        """Validate if the uploaded image is strictly related to agriculture.
        
        Args:
            image_b64: Base64 encoded image.
            mime_type: Image MIME type.
            
        Returns:
            Tuple (is_valid, error_message).
        """
        try:
            llm_service = current_app.llm_service
            if not llm_service.client:
                return True, ""

            prompt = (
                "You are a strict image classifier for an agriculture app. "
                "Determine if this image contains ANY of the following: "
                "Crop, Plant, Leaf, Fruit, Vegetable, Soil, Farm, Tractor, Fertilizer, Livestock, or an Agricultural document.\n"
                "If it does NOT contain any of these (e.g., it is a medical report, ID card, selfie, invoice), you must reject it.\n"
                "Return ONLY a JSON object with two keys: 'is_agriculture' (boolean) and 'reason' (string)."
            )

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_b64}"
                            },
                        },
                    ],
                }
            ]

            response = llm_service.client.chat.completions.create(
                model=llm_service.config.LLM_VISION_MODEL,
                messages=messages,
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            
            result_str = response.choices[0].message.content.strip()
            result = json.loads(result_str)
            
            is_agri = result.get('is_agriculture', False)
            
            if is_agri:
                return True, ""
            else:
                logger.warning(f"DomainGuard image validation failed: {result}")
                return False, self._get_image_refusal_message()
                
        except Exception as e:
            logger.error("DomainGuard image validation error: %s", e)
            return True, ""

    def _get_refusal_message(self) -> str:
        """Standard refusal message for text queries."""
        return (
            "I am an Agriculture AI Assistant and can only assist with farming-related topics such as "
            "crop diseases, soil health, fertilizers, irrigation, weather-based farming advice, "
            "pest management, and agricultural best practices."
        )

    def _get_image_refusal_message(self) -> str:
        """Standard refusal message for image queries."""
        return (
            "This assistant is designed exclusively for agriculture and farming. The uploaded image or document "
            "does not appear to be related to crops, plants, soil, livestock, or any agricultural activity. "
            "Please upload an agriculture-related image or document."
        )
