# Phase 1: Conversation Memory & Context Management

## Overview

This phase implements a multi-turn conversation system that enables persistent context management and user preference tracking. The system maintains conversation history across sessions, learns user preferences, optimizes context windows for token efficiency, and provides cost tracking for API usage.

## Components

### 1. `conversation_manager.py`
Core persistence layer managing all conversation data with SQLite.

**Key Features:**
- Multi-turn History: Store and retrieve full conversation transcripts
- User Profiles: Track user preferences across sessions
- Context Optimization: Build token-efficient context windows for the agent
- Usage Tracking: Monitor API tokens and costs per user
- Data Hygiene: Auto-cleanup of old conversations

**Key Methods:**
```python
ConversationManager(db_path="travel_scout.db")

# Session management
create_conversation(user_id, conversation_id, destination, month, vibes)
add_message(conversation_id, role, content, tokens_used)
get_conversation_history(conversation_id, limit=None)

# Context optimization
get_context_window(conversation_id, max_tokens=6000)

# Preference learning
update_user_preferences(user_id, vibes, destinations, include_hotels)
get_user_preferences(user_id)

# Analytics
get_user_conversations(user_id, limit=10)
get_total_tokens_used(user_id)
cleanup_old_conversations(days=30)
```

### 2. `context_manager.py`
Streamlit-aware wrapper providing seamless multi-turn UI integration.

**Key Features:**
- Streamlit session state management
- Auto user ID generation
- Preference pre-population in UI
- Usage statistics display
- Past conversation retrieval

**Key Methods:**
```python
ContextManager()

start_conversation(destination, month, vibes)
add_user_message(content)
add_agent_response(content, tokens_used)
get_context(max_tokens=6000)
get_preferences()
get_past_conversations(limit=5)
get_usage_stats()
```

### 3. Enhanced `app.py`
Updated Streamlit UI with conversation awareness.

**New Features:**
- Pre-populate favorite vibes from past preferences
- Display conversation history with expandable view
- Show usage statistics (messages, tokens, cost)
- Browse past trips/conversations
- Automatic logging of queries and responses

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    created_at TIMESTAMP,
    last_active TIMESTAMP
)
```

### Conversations Table
```sql
CREATE TABLE conversations (
    conversation_id TEXT PRIMARY KEY,
    user_id TEXT,
    destination TEXT,
    month TEXT,
    vibes TEXT (JSON),
    created_at TIMESTAMP,
    last_updated TIMESTAMP
)
```

### Messages Table
```sql
CREATE TABLE messages (
    message_id INTEGER PRIMARY KEY,
    conversation_id TEXT,
    role TEXT ('user' | 'assistant'),
    content TEXT,
    tokens_used INTEGER,
    timestamp TIMESTAMP
)
```

### User Preferences Table
```sql
CREATE TABLE user_preferences (
    user_id TEXT PRIMARY KEY,
    favorite_vibes TEXT (JSON),
    favorite_destinations TEXT (JSON),
    include_hotels INTEGER (boolean),
    last_updated TIMESTAMP
)
```

## How It Works

### First Time User Flow
1. User visits app → `ContextManager` generates unique `user_id`
2. User enters destination, month, vibes → `start_conversation()` creates session
3. User query logged → `add_user_message()`
4. Agent responds → `add_agent_response()`
5. Preferences saved → `update_user_preferences()`

### Returning User Flow
1. `ContextManager` retrieves stored preferences
2. UI pre-populates favorite vibes
3. User sees past trips in sidebar
4. New conversation created with same logic
5. Context window intelligently includes relevant past context

### Context Window Optimization
- Recent messages are prioritized
- Token count tracked (word count × 1.3 multiplier)
- Stops adding older messages once token limit reached
- Allows agent to reference past context without exceeding limits

## Usage Examples

### Basic Usage (In app.py)
```python
from context_manager import ContextManager

ctx_manager = ContextManager()

# Start new conversation
ctx_manager.start_conversation("Paris", "June", ["Culture", "Hidden Gems"])

# Log messages
ctx_manager.add_user_message("What are hidden gems in Paris?")
ctx_manager.add_agent_response("Here are some hidden gems...")

# Retrieve context for agent
context = ctx_manager.get_context(max_tokens=6000)

# Get user preferences
preferences = ctx_manager.get_preferences()
```

### Advanced Usage
```python
# Track token usage
manager = ConversationManager()
manager.add_message(conv_id, "assistant", response, tokens_used=150)

# Get user stats
total_tokens = manager.get_total_tokens_used(user_id)
conversations = manager.get_user_conversations(user_id, limit=5)

# Cleanup old data
deleted = manager.cleanup_old_conversations(days=30)
```

## Testing

Run the test script to validate all components:
```bash
python test_conversation_manager.py
```

Expected output:
```
Testing ConversationManager...
ConversationManager initialized
User created: test_user_123
Conversation created: conv_001
Messages added to conversation
Retrieved 3 messages from history
Generated context window (286 chars)
User preferences stored
Retrieved preferences: ['Culture', 'Hidden Gems', 'Street Food']
Retrieved 1 conversation(s) for user
Total tokens tracked: 0
All tests passed! Database cleaned up.
```

## Next Steps

Phase 1 is complete. The foundation enables integration with advanced agent reasoning in Phase 2.
