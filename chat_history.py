import streamlit as st
import chromadb
import json
from datetime import datetime
import uuid

class ChatHistoryManager:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chat_history")
        self.collection = self.client.get_or_create_collection(
            name="conversations",
            metadata={"hnsw:space": "cosine"}
        )
    
    def save_conversation(self, chat_id, messages, title=None):
        """Save a conversation to the vector database"""
        try:
            # Create conversation text for embedding
            conversation_text = ""
            for msg in messages:
                conversation_text += f"{msg['role']}: {msg['content']}\n"
            
            # Generate title if not provided
            if not title and messages:
                title = self.generate_title(messages[0]['content'])
            
            # Create metadata
            metadata = {
                "chat_id": chat_id,
                "title": title or "Untitled Chat",
                "timestamp": datetime.now().isoformat(),
                "message_count": len(messages),
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "created_time": datetime.now().strftime("%H:%M")
            }
            
            # Convert messages to JSON string for storage
            messages_json = json.dumps(messages)
            
            # Save to vector database
            self.collection.upsert(
                documents=[conversation_text],
                metadatas=[metadata],
                ids=[chat_id]
            )
            
            return True
        except Exception as e:
            st.error(f"Error saving conversation: {e}")
            return False
    
    def load_conversation(self, chat_id):
        """Load a conversation by chat_id"""
        try:
            results = self.collection.get(ids=[chat_id])
            if results['ids']:
                # Extract messages from document
                document = results['documents'][0]
                messages = []
                for line in document.split('\n'):
                    if line.strip():
                        if line.startswith('user: '):
                            messages.append({"role": "user", "content": line[6:]})
                        elif line.startswith('assistant: '):
                            messages.append({"role": "assistant", "content": line[11:]})
                return messages, results['metadatas'][0]
            return None, None
        except Exception as e:
            st.error(f"Error loading conversation: {e}")
            return None, None
    
    def get_all_conversations(self):
        """Get all conversations metadata"""
        try:
            results = self.collection.get()
            conversations = []
            for i, chat_id in enumerate(results['ids']):
                metadata = results['metadatas'][i]
                conversations.append({
                    'chat_id': chat_id,
                    'title': metadata.get('title', 'Untitled'),
                    'timestamp': metadata.get('timestamp', ''),
                    'message_count': metadata.get('message_count', 0),
                    'date': metadata.get('created_date', ''),
                    'time': metadata.get('created_time', '')
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
            self.collection.delete(ids=[chat_id])
            return True
        except Exception as e:
            st.error(f"Error deleting conversation: {e}")
            return False
    
    def search_conversations(self, query, n_results=10):
        """Search conversations by content"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            conversations = []
            for i, chat_id in enumerate(results['ids'][0]):
                metadata = results['metadatas'][0][i]
                conversations.append({
                    'chat_id': chat_id,
                    'title': metadata.get('title', 'Untitled'),
                    'timestamp': metadata.get('timestamp', ''),
                    'relevance': results['distances'][0][i],
                    'date': metadata.get('created_date', ''),
                    'time': metadata.get('created_time', '')
                })
            
            return conversations
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
