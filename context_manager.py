import uuid
import streamlit as st
from conversation_manager import ConversationManager
from typing import List, Optional, Dict, Any

class ContextManager:
    """Bridges ConversationManager with Streamlit session state for seamless multi-turn interactions."""
    
    def __init__(self):
        self.conv_manager = ConversationManager()
        self._ensure_session_state()
    
    def _ensure_session_state(self):
        """Initialize Streamlit session state for conversation tracking."""
        if "user_id" not in st.session_state:
            st.session_state.user_id = str(uuid.uuid4())
        
        if "conversation_id" not in st.session_state:
            st.session_state.conversation_id = str(uuid.uuid4())
        
        if "conversation_created" not in st.session_state:
            st.session_state.conversation_created = False
    
    def start_conversation(self, destination: str, month: str, vibes: List[str]) -> str:
        """Initialize a new conversation session."""
        self._ensure_session_state()
        
        conversation_id = st.session_state.conversation_id
        user_id = st.session_state.user_id
        
        self.conv_manager.create_conversation(
            user_id=user_id,
            conversation_id=conversation_id,
            destination=destination,
            month=month,
            vibes=vibes
        )
        
        self.conv_manager.update_user_preferences(
            user_id=user_id,
            vibes=vibes,
            destinations=[destination]
        )
        
        st.session_state.conversation_created = True
        return conversation_id
    
    def add_user_message(self, content: str) -> bool:
        """Log user query to history."""
        return self.conv_manager.add_message(
            conversation_id=st.session_state.conversation_id,
            role="user",
            content=content
        )
    
    def add_agent_response(self, content: str, tokens_used: int = 0) -> bool:
        """Log agent response to history."""
        return self.conv_manager.add_message(
            conversation_id=st.session_state.conversation_id,
            role="assistant",
            content=content,
            tokens_used=tokens_used
        )
    
    def get_context(self, max_tokens: int = 6000) -> str:
        """Get optimized context window for agent."""
        return self.conv_manager.get_context_window(
            conversation_id=st.session_state.conversation_id,
            max_tokens=max_tokens
        )
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Retrieve full conversation history."""
        return self.conv_manager.get_conversation_history(
            conversation_id=st.session_state.conversation_id
        )
    
    def get_preferences(self) -> Dict[str, Any]:
        """Get user's learned preferences."""
        return self.conv_manager.get_user_preferences(
            user_id=st.session_state.user_id
        )
    
    def get_past_conversations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve user's past conversation sessions."""
        return self.conv_manager.get_user_conversations(
            user_id=st.session_state.user_id,
            limit=limit
        )
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get user's API usage statistics."""
        total_tokens = self.conv_manager.get_total_tokens_used(
            user_id=st.session_state.user_id
        )
        
        history = self.get_conversation_history()
        num_messages = len(history)
        
        return {
            "total_tokens": total_tokens,
            "num_messages": num_messages,
            "estimated_cost": round(total_tokens * 0.0001, 4)
        }
