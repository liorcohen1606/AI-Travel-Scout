import streamlit as st
import requests
from agent_logic import run_travel_scout
from context_manager import ContextManager

@st.cache_resource
def get_context_manager():
    return ContextManager()

def get_destination_image(destination):
    try:
        formatted_dest = destination.strip().title().replace(" ", "_")
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{formatted_dest}"
        
        headers = {'User-Agent': 'TravelScoutApp/1.0'}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if "originalimage" in data and "source" in data["originalimage"]:
                return data["originalimage"]["source"]
    except Exception as e:
        print(f"Image fetch error: {e}")
    return None

def display_conversation_history():
    """Show previous messages in current conversation."""
    ctx_manager = get_context_manager()
    history = ctx_manager.get_conversation_history()
    
    if history:
        with st.expander("📋 Conversation History", expanded=False):
            for msg in history:
                role = msg['role'].upper()
                icon = "🧑" if role == "USER" else "🤖"
                with st.chat_message(role.lower(), avatar=icon):
                    st.write(msg['content'])

def display_usage_stats():
    """Show API usage statistics."""
    ctx_manager = get_context_manager()
    stats = ctx_manager.get_usage_stats()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Messages", stats['num_messages'])
    col2.metric("Tokens Used", stats['total_tokens'])
    col3.metric("Est. Cost", f"${stats['estimated_cost']}")

def display_past_conversations():
    """Show user's past conversation sessions."""
    ctx_manager = get_context_manager()
    past_convs = ctx_manager.get_past_conversations(limit=5)
    
    if past_convs:
        with st.expander("🕐 Past Trips", expanded=False):
            for conv in past_convs:
                st.markdown(f"**{conv['destination']}** - {conv['month']}")
                st.caption(f"Vibes: {', '.join(conv['vibes']) if conv['vibes'] else 'N/A'}")

def main():
    st.set_page_config(page_title="AI Travel Scout", layout="wide")
    
    st.markdown("<h1 style='text-align: center; font-size: 4rem; color: #1E3A8A; font-weight: bold;'>AI Travel Scout</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #6B7280; margin-top: -15px; margin-bottom: 40px;'>Your Intelligent Trip Research Partner</h3>", unsafe_allow_html=True)
    
    ctx_manager = get_context_manager()
    
    with st.sidebar:
        st.header("Trip Details")
        
        # Show user preferences if available
        preferences = ctx_manager.get_preferences()
        default_vibes = preferences.get('favorite_vibes', []) if preferences else []
        
        destination = st.text_input("Destination", placeholder="e.g. Dubai, Tokyo, Paris")
        
        all_months = [
            "January", "February", "March", "April", "May", "June", 
            "July", "August", "September", "October", "November", "December"
        ]
        month = st.selectbox("When?", all_months)
        
        vibe = st.multiselect(
            "Travel Style",
            ["Street Food", "Hidden Gems", "Luxury", "Nature", "No Crowds", "Culture"],
            default=default_vibes[:3] if default_vibes else []
        )
        
        st.divider()
        include_hotels = st.checkbox("Include Hotel Recommendations?", value=True)
        
        submit_button = st.button("Start Scouting", use_container_width=True, type="primary")
        
        st.divider()
        st.subheader("Session Info")
        display_usage_stats()
        display_past_conversations()

    if submit_button:
        if destination:
            ctx_manager.start_conversation(destination, month, vibe)
            ctx_manager.add_user_message(f"Plan a trip to {destination} in {month}. Travel style: {', '.join(vibe) if vibe else 'varied'}")
            
            with st.spinner(f"Scouting the best spots in {destination}..."):
                try:
                    result = run_travel_scout(destination, month, vibe, include_hotels)
                    ctx_manager.add_agent_response(result)
                    image_url = get_destination_image(destination)
                    
                    st.success(f"Scouting complete for {destination}!")
                    
                    with st.container(border=True):
                        st.markdown("### Your Itinerary & Tips")
                        st.write(result)
                        
                        if image_url:
                            st.divider()
                            st.image(image_url, use_container_width=True)
                    
                    display_conversation_history()
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a destination in the sidebar to start.")

if __name__ == "__main__":
    main()