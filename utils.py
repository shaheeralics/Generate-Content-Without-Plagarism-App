import streamlit as st
import json
from datetime import datetime, timedelta
import re

class AIResponseHandler:
    """Enhanced AI response handling with multiple capabilities"""
    
    @staticmethod
    def detect_content_type(text):
        """Detect what type of content the user is asking for"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['rewrite', 'paraphrase', 'rephrase', 'reword']):
            return 'rewrite'
        elif any(word in text_lower for word in ['summarize', 'summary', 'tldr']):
            return 'summarize'
        elif any(word in text_lower for word in ['explain', 'what is', 'define']):
            return 'explain'
        elif any(word in text_lower for word in ['translate', 'translation']):
            return 'translate'
        elif any(word in text_lower for word in ['improve', 'enhance', 'better']):
            return 'improve'
        else:
            return 'general'
    
    @staticmethod
    def get_specialized_prompt(content_type, text):
        """Get specialized prompts based on content type"""
        prompts = {
            'rewrite': f"""
            You are an expert content rewriter. Completely rewrite the following text while:
            1. Maintaining the original meaning and key information
            2. Using different vocabulary and sentence structures
            3. Making it sound natural and human-like
            4. Avoiding plagiarism detection completely
            5. Improving clarity and readability
            6. Keeping the same tone and style intention
            
            Original text: {text}
            
            Provide a completely rewritten version:
            """,
            
            'summarize': f"""
            Create a clear, concise summary of the following text:
            1. Capture the main points and key information
            2. Use your own words and structure
            3. Make it about 30% of the original length
            4. Maintain logical flow
            
            Text to summarize: {text}
            
            Summary:
            """,
            
            'explain': f"""
            Provide a clear, detailed explanation of the following:
            1. Break down complex concepts into simple terms
            2. Use examples where helpful
            3. Structure your explanation logically
            4. Make it easy to understand
            
            Topic/Question: {text}
            
            Explanation:
            """,
            
            'improve': f"""
            Improve and enhance the following text by:
            1. Fixing any grammar or spelling issues
            2. Improving clarity and readability
            3. Enhancing flow and structure
            4. Making it more engaging
            5. Maintaining the original intent
            
            Text to improve: {text}
            
            Improved version:
            """,
            
            'general': f"""
            Please help me with the following request. Provide a helpful, accurate, and detailed response:
            
            Request: {text}
            
            Response:
            """
        }
        
        return prompts.get(content_type, prompts['general'])

class ChatUtils:
    """Utility functions for chat management"""
    
    @staticmethod
    def format_timestamp(timestamp_str):
        """Format timestamp for display"""
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            now = datetime.now()
            
            if dt.date() == now.date():
                return f"Today {dt.strftime('%H:%M')}"
            elif dt.date() == (now - timedelta(days=1)).date():
                return f"Yesterday {dt.strftime('%H:%M')}"
            elif dt.year == now.year:
                return dt.strftime('%m/%d %H:%M')
            else:
                return dt.strftime('%m/%d/%y')
        except:
            return "Unknown"
    
    @staticmethod
    def clean_text(text):
        """Clean and sanitize text for display"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Basic HTML escaping for safety
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#x27;')
        
        return text
    
    @staticmethod
    def estimate_reading_time(text):
        """Estimate reading time for text"""
        words = len(text.split())
        minutes = max(1, round(words / 200))  # Average reading speed
        return f"{minutes} min read"
    
    @staticmethod
    def extract_keywords(text):
        """Extract keywords from text"""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        # Remove common words
        stop_words = {'that', 'this', 'with', 'from', 'they', 'have', 'were', 'been', 'their', 'said', 'each', 'which', 'what', 'will', 'there', 'more', 'than', 'many', 'some', 'time', 'very', 'when', 'much', 'just', 'like', 'over', 'also', 'back', 'after', 'first', 'well', 'year', 'work', 'such', 'make', 'even', 'most', 'take', 'only', 'think', 'know', 'come', 'good', 'give', 'other'}
        keywords = [word for word in set(words) if word not in stop_words]
        return keywords[:10]  # Return top 10 keywords

class ExportManager:
    """Handle various export formats"""
    
    @staticmethod
    def export_to_json(messages, metadata):
        """Export conversation to JSON"""
        export_data = {
            "metadata": metadata,
            "messages": messages,
            "exported_at": datetime.now().isoformat(),
            "total_messages": len(messages)
        }
        return json.dumps(export_data, indent=2)
    
    @staticmethod
    def export_to_markdown(messages, metadata):
        """Export conversation to Markdown"""
        md_content = f"# {metadata.get('title', 'Conversation')}\n\n"
        md_content += f"**Date:** {metadata.get('created_date', 'Unknown')}\n"
        md_content += f"**Time:** {metadata.get('created_time', 'Unknown')}\n"
        md_content += f"**Messages:** {len(messages)}\n\n---\n\n"
        
        for i, msg in enumerate(messages, 1):
            role = "🧑 **You**" if msg['role'] == 'user' else "🤖 **Assistant**"
            md_content += f"## {role}\n\n{msg['content']}\n\n"
        
        return md_content
    
    @staticmethod
    def export_to_text(messages, metadata):
        """Export conversation to plain text"""
        txt_content = f"Conversation: {metadata.get('title', 'Untitled')}\n"
        txt_content += f"Date: {metadata.get('created_date', 'Unknown')}\n"
        txt_content += f"Time: {metadata.get('created_time', 'Unknown')}\n"
        txt_content += f"Messages: {len(messages)}\n"
        txt_content += "=" * 50 + "\n\n"
        
        for i, msg in enumerate(messages, 1):
            role = "You" if msg['role'] == 'user' else "Assistant"
            txt_content += f"[{i}] {role}:\n{msg['content']}\n\n"
        
        return txt_content

class AdvancedSearch:
    """Advanced search functionality"""
    
    @staticmethod
    def search_by_date_range(chat_manager, start_date, end_date):
        """Search conversations by date range"""
        all_conversations = chat_manager.get_all_conversations()
        filtered = []
        
        for conv in all_conversations:
            try:
                conv_date = datetime.fromisoformat(conv['timestamp']).date()
                if start_date <= conv_date <= end_date:
                    filtered.append(conv)
            except:
                continue
        
        return filtered
    
    @staticmethod
    def search_by_message_count(chat_manager, min_messages=0, max_messages=1000):
        """Search conversations by message count"""
        all_conversations = chat_manager.get_all_conversations()
        return [conv for conv in all_conversations 
                if min_messages <= conv.get('message_count', 0) <= max_messages]
    
    @staticmethod
    def search_by_keywords(chat_manager, keywords):
        """Search conversations by specific keywords"""
        results = []
        for keyword in keywords:
            keyword_results = chat_manager.search_conversations(keyword, n_results=50)
            results.extend(keyword_results)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_results = []
        for item in results:
            if item['chat_id'] not in seen:
                seen.add(item['chat_id'])
                unique_results.append(item)
        
        return unique_results

def get_response_stats(text):
    """Get statistics about the response"""
    return {
        'word_count': len(text.split()),
        'character_count': len(text),
        'reading_time': ChatUtils.estimate_reading_time(text),
        'keywords': ChatUtils.extract_keywords(text)
    }
