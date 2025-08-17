import streamlit as st
import json
import os
from datetime import datetime
import uuid

class ChatHistoryManager:
    def __init__(self):
        self.history_file = "chat_history.json"
        self.ensure_history_file()
    
    def ensure_history_file(self):
        """Ensure the history file exists"""
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w') as f:
                json.dump({"conversations": {}}, f)
    
    def save_conversation(self, chat_id, messages, title=None):
        """Save a conversation to JSON file"""
        try:
            # Load existing data
            with open(self.history_file, 'r') as f:
                data = json.load(f)
            
            # Generate title if not provided
            if not title and messages:
                title = self.generate_title(messages[0]['content'])
            
            # Create conversation data
            conversation_data = {
                "chat_id": chat_id,
                "title": title or "Untitled Chat",
                "messages": messages,
                "timestamp": datetime.now().isoformat(),
                "message_count": len(messages),
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "created_time": datetime.now().strftime("%H:%M")
            }
            
            # Save conversation
            data["conversations"][chat_id] = conversation_data
            
            # Write back to file
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            st.error(f"Error saving conversation: {e}")
            return False
    
    def load_conversation(self, chat_id):
        """Load a conversation by chat_id"""
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
            
            if chat_id in data["conversations"]:
                conv_data = data["conversations"][chat_id]
                return conv_data["messages"], {
                    "title": conv_data.get("title", "Untitled"),
                    "timestamp": conv_data.get("timestamp", ""),
                    "created_date": conv_data.get("created_date", ""),
                    "created_time": conv_data.get("created_time", "")
                }
            return None, None
        except Exception as e:
            st.error(f"Error loading conversation: {e}")
            return None, None
    
    def get_all_conversations(self):
        """Get all conversations metadata"""
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
            
            conversations = []
            for chat_id, conv_data in data["conversations"].items():
                conversations.append({
                    'chat_id': chat_id,
                    'title': conv_data.get('title', 'Untitled'),
                    'timestamp': conv_data.get('timestamp', ''),
                    'message_count': conv_data.get('message_count', 0),
                    'date': conv_data.get('created_date', ''),
                    'time': conv_data.get('created_time', '')
                })
            
            # Sort by timestamp (newest first)
            conversations.sort(key=lambda x: x['timestamp'], reverse=True)
            return conversations
        except Exception as e:
            st.error(f"Error getting conversations: {e}")
            return []
    
    def delete_conversation(self, chat_id):
        """Delete a conversation"""
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
            
            if chat_id in data["conversations"]:
                del data["conversations"][chat_id]
                
                with open(self.history_file, 'w') as f:
                    json.dump(data, f, indent=2)
                return True
            return False
        except Exception as e:
            st.error(f"Error deleting conversation: {e}")
            return False
    
    def search_conversations(self, query, n_results=10):
        """Search conversations by content"""
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
            
            conversations = []
            query_lower = query.lower()
            
            for chat_id, conv_data in data["conversations"].items():
                # Search in title and messages
                title_match = query_lower in conv_data.get('title', '').lower()
                
                message_match = False
                for msg in conv_data.get('messages', []):
                    if query_lower in msg.get('content', '').lower():
                        message_match = True
                        break
                
                if title_match or message_match:
                    conversations.append({
                        'chat_id': chat_id,
                        'title': conv_data.get('title', 'Untitled'),
                        'timestamp': conv_data.get('timestamp', ''),
                        'message_count': conv_data.get('message_count', 0),
                        'date': conv_data.get('created_date', ''),
                        'time': conv_data.get('created_time', '')
                    })
            
            # Sort by timestamp and limit results
            conversations.sort(key=lambda x: x['timestamp'], reverse=True)
            return conversations[:n_results]
        except Exception as e:
            st.error(f"Error searching conversations: {e}")
            return []
    
    def generate_title(self, first_message):
        """Generate a title from the first message"""
        # Simple title generation - take first 50 characters
        title = first_message[:50].strip()
        if len(first_message) > 50:
            title += "..."
        return title
    
    def export_conversation(self, chat_id):
        """Export conversation as JSON"""
        try:
            messages, metadata = self.load_conversation(chat_id)
            if messages:
                export_data = {
                    "chat_id": chat_id,
                    "metadata": metadata,
                    "messages": messages,
                    "exported_at": datetime.now().isoformat()
                }
                return json.dumps(export_data, indent=2)
            return None
        except Exception as e:
            st.error(f"Error exporting conversation: {e}")
            return None
