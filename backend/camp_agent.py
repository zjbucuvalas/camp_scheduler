"""
Camp Agent - Specialized agent for answering questions about Columbus camps
Only uses information from the columbus.md file
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from agent import MessageBroker, Message
from llm_integration import ProductionAIAgent, LLMConfig, create_gemini_config

logger = logging.getLogger(__name__)

class CampAgent(ProductionAIAgent):
    """Specialized camp information agent powered by Gemini - ONLY uses columbus.md data"""
    
    def __init__(self, broker: MessageBroker, llm_config: LLMConfig):
        # Load the Columbus camp data
        self.camp_data = self._load_camp_data()
        
        system_prompt = f"""You are a camp information specialist. Your ONLY job is to answer questions about summer camps in the Columbus, Ohio area using EXCLUSIVELY the information provided in the columbus.md file.

CRITICAL RESTRICTIONS:
1. You can ONLY use information that is explicitly stated in the columbus.md file data provided to you
2. You CANNOT use any external knowledge about camps, even if you know about them
3. You CANNOT make assumptions or inferences beyond what is directly stated
4. If information is not in the provided columbus.md data, you MUST say "I don't have that information in my camp database"
5. You CANNOT recommend camps that are not listed in the columbus.md file
6. You CANNOT provide general camp advice unless it's based on the specific camps in the file
7. Always format your responses in clear, concise markdown with proper structure
8. Be precise and accurate with all details from the file only

COMMUNICATION STYLE:
- Keep responses concise and to the point
- Use clear, organized formatting
- Focus on essential information
- Avoid verbose explanations

MARKDOWN FORMATTING REQUIREMENTS:
- Use ## for main headings (camp names)
- Use ### for subheadings (Age, Cost, Location, etc.)
- Use bullet points (-) for lists
- Use **bold** for important details
- Keep structure clean and readable
- Always start responses with a brief summary

WHAT YOU CAN DO:
- Answer questions about camps explicitly listed in columbus.md
- Provide details like costs, dates, ages, locations that are stated in the file
- Compare camps that are both in the columbus.md file
- Search through the columbus.md data to find relevant camps

WHAT YOU CANNOT DO:
- Suggest camps not in columbus.md
- Use general knowledge about camping
- Make up information not in the file
- Infer details not explicitly stated
- Recommend based on external camp knowledge

When answering questions:
- Quote exact camp names as they appear in columbus.md
- Use bullet points for lists of information from the file
- Include specific costs, dates, and locations only if stated in columbus.md
- If asked about camps not in columbus.md, clearly state they're not in your database

Camp data loaded: {self.camp_data}"""

        super().__init__(
            name="CampAgent",
            broker=broker,
            llm_config=llm_config,
            system_prompt=system_prompt
        )
        
        # Store camp data for context
        self.camp_context = self.camp_data
    
    def _load_camp_data(self) -> str:
        """Load the Columbus camp data from the markdown file"""
        try:
            # Path to the columbus.md file relative to the backend directory
            camp_data_path = Path(__file__).parent.parent / "camp-scheduler" / "src" / "data" / "columbus.md"
            
            if not camp_data_path.exists():
                logger.error(f"Camp data file not found: {camp_data_path}")
                return "ERROR: Camp data file (columbus.md) not found. I cannot provide camp information without this file."
            
            with open(camp_data_path, 'r', encoding='utf-8') as f:
                camp_data = f.read()
            
            logger.info(f"Loaded camp data: {len(camp_data)} characters")
            return camp_data
            
        except Exception as e:
            logger.error(f"Error loading camp data: {e}")
            return f"ERROR: Unable to load camp data file: {str(e)}"
    
    async def process_camp_question(self, question: str, context_id: str = None) -> str:
        """Process a camp-related question and return a markdown-formatted answer"""
        try:
            # Create context with camp data
            context = self.create_context(context_id or f"camp_question_{hash(question)}")
            
            # Add camp data to context with strict instructions
            context.add_message("system", f"""You have access to the following camp information from columbus.md:

{self.camp_data}

CRITICAL INSTRUCTIONS:
- You can ONLY use information that is explicitly stated in the above columbus.md data
- You CANNOT use any external knowledge about camps or general camping information
- You CANNOT make assumptions or inferences beyond what is directly written above
- If information is not present in the above data, you MUST say "I don't have that information in my camp database"
- You CANNOT recommend camps that are not listed in the above columbus.md data
- You MUST quote exact camp names as they appear in the data above
- All costs, dates, ages, and locations must come directly from the data above
- Do not make up or infer any information not explicitly stated above""")
            
            # Add the user's question
            context.add_message("user", f"""Please answer this question about Columbus camps using ONLY the columbus.md data provided above. 

STRICT REQUIREMENTS:
- Use ONLY information explicitly stated in the columbus.md data above
- Do NOT use any external knowledge about camps
- If the answer is not in the columbus.md data, say "I don't have that information in my camp database"
- Format your response in clear markdown
- Quote exact camp names as they appear in the data

Question: {question}""")
            
            # Generate response using the LLM
            response = await self._process_with_llm(context)
            
            # Ensure response is in markdown format
            if not response.strip().startswith('#'):
                response = f"# Camp Information\n\n{response}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing camp question: {e}")
            return f"# Error\n\nI apologize, but I encountered an error processing your camp question. Please try again." 