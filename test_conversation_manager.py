#!/usr/bin/env python
"""Test script for conversation_manager.py"""

import os
from conversation_manager import ConversationManager

def test_conversation_manager():
    """Test all core functionality of ConversationManager."""
    
    # Remove existing test DB if present
    test_db = "test_travel_scout.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    print("🧪 Testing ConversationManager...\n")
    
    # Initialize
    manager = ConversationManager(db_path=test_db)
    print("✅ ConversationManager initialized")
    
    # Test user creation
    user_id = "test_user_123"
    manager.create_user(user_id)
    print(f"✅ User created: {user_id}")
    
    # Test conversation creation
    conv_id = "conv_001"
    manager.create_conversation(
        user_id=user_id,
        conversation_id=conv_id,
        destination="Paris",
        month="June",
        vibes=["Culture", "Hidden Gems"]
    )
    print(f"✅ Conversation created: {conv_id}")
    
    # Test adding messages
    manager.add_message(conv_id, "user", "Tell me about Paris in June")
    manager.add_message(conv_id, "assistant", "Paris in June is beautiful! Here are some hidden gems...")
    manager.add_message(conv_id, "user", "What about affordable hotels?")
    print("✅ Messages added to conversation")
    
    # Test retrieving history
    history = manager.get_conversation_history(conv_id)
    print(f"✅ Retrieved {len(history)} messages from history")
    
    # Test context window
    context = manager.get_context_window(conv_id, max_tokens=1000)
    print(f"✅ Generated context window ({len(context)} chars)")
    
    # Test user preferences
    manager.update_user_preferences(
        user_id=user_id,
        vibes=["Culture", "Hidden Gems", "Street Food"],
        destinations=["Paris", "Tokyo"],
        include_hotels=True
    )
    print("✅ User preferences stored")
    
    # Test retrieving preferences
    prefs = manager.get_user_preferences(user_id)
    print(f"✅ Retrieved preferences: {prefs['favorite_vibes']}")
    
    # Test conversation list
    user_convs = manager.get_user_conversations(user_id)
    print(f"✅ Retrieved {len(user_convs)} conversation(s) for user")
    
    # Test token counting
    tokens = manager.get_total_tokens_used(user_id)
    print(f"✅ Total tokens tracked: {tokens}")
    
    # Cleanup
    os.remove(test_db)
    print("\n✅ All tests passed! Database cleaned up.")

if __name__ == "__main__":
    test_conversation_manager()
