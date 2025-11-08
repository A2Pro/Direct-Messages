#!/usr/bin/env python3
"""
Flask server to read and display consolidated chat logs.
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

# Global variable to store chat data
chat_data = None

def load_chat_data():
    """Load the consolidated chat CSV file."""
    global chat_data
    csv_file = "/home/a2/Downloads/Direct Messages/consolidated_chat.csv"
    
    if os.path.exists(csv_file):
        chat_data = pd.read_csv(csv_file)
        # Convert timestamp to datetime for better filtering
        chat_data['timestamp'] = pd.to_datetime(chat_data['timestamp'], format='mixed')
        return True
    return False

@app.route('/')
def index():
    """Main page showing chat statistics."""
    if chat_data is None:
        if not load_chat_data():
            return "Error: consolidated_chat.csv not found. Run consolidate_chat.py first."
    
    stats = {
        'total_messages': len(chat_data),
        'unique_authors': chat_data['author_username'].nunique(),
        'date_range': {
            'start': chat_data['timestamp'].min().strftime('%Y-%m-%d'),
            'end': chat_data['timestamp'].max().strftime('%Y-%m-%d')
        },
        'messages_with_attachments': chat_data['has_attachments'].sum(),
        'top_authors': chat_data['author_username'].value_counts().head(10).to_dict()
    }
    
    return f"""
    <html>
    <head>
        <title>Discord Chat Analytics</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #1a1a1a;
                color: #ffffff;
                margin: 0;
                padding: 20px;
            }}
            
            .header {{
                background: linear-gradient(135deg, #dc2626, #7f1d1d);
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 30px;
                box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
                text-align: center;
            }}
            
            .header h1 {{
                margin: 0;
                color: white;
                text-shadow: 0 2px 4px rgba(0,0,0,0.5);
                font-size: 2.5em;
            }}
            
            .stats-container {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .stat-card {{
                background: #262626;
                padding: 20px;
                border-radius: 12px;
                border: 1px solid #404040;
                border-left: 4px solid #dc2626;
            }}
            
            .stat-card h3 {{
                color: #dc2626;
                margin-top: 0;
                margin-bottom: 15px;
            }}
            
            .stat-list {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}
            
            .stat-list li {{
                padding: 8px 0;
                border-bottom: 1px solid #404040;
                display: flex;
                justify-content: space-between;
            }}
            
            .stat-list li:last-child {{
                border-bottom: none;
            }}
            
            .stat-value {{
                color: #dc2626;
                font-weight: bold;
            }}
            
            .nav-card {{
                background: #262626;
                padding: 25px;
                border-radius: 12px;
                border: 1px solid #404040;
                text-align: center;
            }}
            
            .nav-buttons {{
                display: flex;
                gap: 15px;
                justify-content: center;
                flex-wrap: wrap;
            }}
            
            .nav-button {{
                background: linear-gradient(135deg, #dc2626, #7f1d1d);
                color: white;
                text-decoration: none;
                padding: 15px 25px;
                border-radius: 8px;
                font-weight: bold;
                transition: all 0.3s ease;
                box-shadow: 0 2px 8px rgba(220, 38, 38, 0.3);
                border: none;
                cursor: pointer;
            }}
            
            .nav-button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 16px rgba(220, 38, 38, 0.4);
                background: linear-gradient(135deg, #ef4444, #dc2626);
            }}
            
            .emoji {{
                font-size: 1.2em;
                margin-right: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>💬 Discord Chat Analytics</h1>
        </div>
        
        <div class="stats-container">
            <div class="stat-card">
                <h3>📊 General Statistics</h3>
                <ul class="stat-list">
                    <li>
                        <span>Total Messages:</span>
                        <span class="stat-value">{stats['total_messages']:,}</span>
                    </li>
                    <li>
                        <span>Unique Authors:</span>
                        <span class="stat-value">{stats['unique_authors']}</span>
                    </li>
                    <li>
                        <span>Messages with Attachments:</span>
                        <span class="stat-value">{stats['messages_with_attachments']:,}</span>
                    </li>
                    <li>
                        <span>Date Range:</span>
                        <span class="stat-value">{stats['date_range']['start']} to {stats['date_range']['end']}</span>
                    </li>
                </ul>
            </div>
            
            <div class="stat-card">
                <h3>👥 Top Authors</h3>
                <ul class="stat-list">
                    {''.join([f"<li><span>{author}</span><span class='stat-value'>{count:,} messages</span></li>" for author, count in list(stats['top_authors'].items())[:8]])}
                </ul>
            </div>
        </div>
        
        <div class="nav-card">
            <h3 style="color: #dc2626; margin-bottom: 20px;">🚀 Explore the Chat</h3>
            <div class="nav-buttons">
                <a href="/messages" class="nav-button">
                    <span class="emoji">💬</span>View Messages
                </a>
                <a href="/search" class="nav-button">
                    <span class="emoji">🔍</span>Search Chat
                </a>
                <a href="/api/messages" class="nav-button">
                    <span class="emoji">📊</span>JSON API
                </a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/messages')
def messages():
    """Display paginated messages in chat interface style."""
    if chat_data is None:
        load_chat_data()
    
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    page_data = chat_data.iloc[start_idx:end_idx].copy()
    
    prev_page = max(1, page-1)
    next_page = page + 1
    
    # Group messages by consecutive user and time
    grouped_messages = []
    current_group = None
    
    for _, row in page_data.iterrows():
        timestamp = pd.to_datetime(row['timestamp'])
        
        # Skip messages with invalid usernames
        username = row['author_username']
        if not username or str(username).lower() == 'nan' or pd.isna(username):
            continue
            
        # Skip messages with no content and no valid attachments
        content = row['content']
        has_valid_attachment = (row['has_attachments'] and 
                               row['attachment_filename'] and 
                               str(row['attachment_filename']).lower() != 'nan' and
                               not pd.isna(row['attachment_filename']))
        
        if (not content or str(content).lower() == 'nan' or pd.isna(content)) and not has_valid_attachment:
            continue
        
        # Start new group if different user or more than 5 minutes apart
        if (current_group is None or 
            current_group['author'] != username or
            (timestamp - current_group['last_timestamp']).total_seconds() > 300):
            
            if current_group:
                grouped_messages.append(current_group)
            
            display_name = row['author_display_name']
            if not display_name or str(display_name).lower() == 'nan' or pd.isna(display_name):
                display_name = username
            
            current_group = {
                'author': username,
                'author_display': display_name,
                'first_timestamp': timestamp,
                'last_timestamp': timestamp,
                'messages': []
            }
        else:
            current_group['last_timestamp'] = timestamp
        
        current_group['messages'].append({
            'content': content if content and str(content).lower() != 'nan' and not pd.isna(content) else '',
            'timestamp': timestamp,
            'has_attachments': has_valid_attachment,
            'attachment_filename': row['attachment_filename'] if has_valid_attachment else '',
            'attachment_url': row['attachment_url'] if has_valid_attachment else ''
        })
    
    if current_group:
        grouped_messages.append(current_group)
    
    html = f"""
    <html>
    <head>
        <title>Chat Messages - Page {page}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #1a1a1a;
                color: #ffffff;
                margin: 0;
                padding: 20px;
            }}
            
            .header {{
                background: linear-gradient(135deg, #dc2626, #7f1d1d);
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 20px;
                box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
            }}
            
            .header h1 {{
                margin: 0;
                color: white;
                text-shadow: 0 2px 4px rgba(0,0,0,0.5);
            }}
            
            .nav-links {{
                margin: 10px 0;
            }}
            
            .nav-links a {{
                color: #fca5a5;
                text-decoration: none;
                margin-right: 15px;
                font-weight: 500;
            }}
            
            .nav-links a:hover {{
                color: white;
                text-decoration: underline;
            }}
            
            .pagination {{
                background: #262626;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                margin: 20px 0;
                border: 1px solid #404040;
            }}
            
            .pagination a {{
                color: #dc2626;
                text-decoration: none;
                font-weight: bold;
                padding: 8px 16px;
                margin: 0 5px;
                border-radius: 6px;
                background: #1a1a1a;
                border: 1px solid #404040;
                display: inline-block;
            }}
            
            .pagination a:hover {{
                background: #dc2626;
                color: white;
            }}
            
            .chat-container {{
                max-width: 800px;
                margin: 0 auto;
                background: #262626;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #404040;
            }}
            
            .message-group {{
                margin-bottom: 20px;
                padding: 15px;
                border-radius: 12px;
                background: #1f1f1f;
                border-left: 4px solid #dc2626;
            }}
            
            .message-header {{
                display: flex;
                align-items: center;
                margin-bottom: 8px;
                padding-bottom: 5px;
                border-bottom: 1px solid #404040;
            }}
            
            .username {{
                font-weight: bold;
                color: #dc2626;
                margin-right: 10px;
                font-size: 1.1em;
            }}
            
            .timestamp {{
                color: #888;
                font-size: 0.85em;
            }}
            
            .message {{
                margin: 8px 0;
                padding: 8px 0;
                line-height: 1.5;
            }}
            
            .message-content {{
                color: #e5e5e5;
                word-wrap: break-word;
                white-space: pre-wrap;
            }}
            
            .attachment {{
                margin-top: 8px;
                padding: 8px;
                background: #333;
                border-radius: 6px;
                border: 1px solid #555;
            }}
            
            .attachment a {{
                color: #fca5a5;
                text-decoration: none;
            }}
            
            .attachment a:hover {{
                color: #dc2626;
                text-decoration: underline;
            }}
            
            .message-time {{
                color: #666;
                font-size: 0.75em;
                margin-left: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>💬 Chat Messages - Page {page}</h1>
            <div class="nav-links">
                <a href="/">🏠 Home</a>
                <a href="/search">🔍 Search</a>
                <a href="/api/messages">📊 API</a>
            </div>
        </div>
        
        <div class="pagination">
            <a href="/messages?page={prev_page}&per_page={per_page}">← Previous</a>
            <span style="color: #dc2626; font-weight: bold; margin: 0 15px;">Page {page}</span>
            <a href="/messages?page={next_page}&per_page={per_page}">Next →</a>
        </div>
        
        <div class="chat-container">
    """
    
    for group in grouped_messages:
        # Format timestamp for display
        time_str = group['first_timestamp'].strftime('%Y-%m-%d %H:%M')
        
        html += f"""
            <div class="message-group">
                <div class="message-header">
                    <span class="username">{group['author_display']}</span>
                    <span class="timestamp">{time_str}</span>
                </div>
        """
        
        for msg in group['messages']:
            content = str(msg['content']) if msg['content'] else ''
            msg_time = msg['timestamp'].strftime('%H:%M')
            
            html += f"""
                <div class="message">
                    <div class="message-content">{content}</div>
            """
            
            if msg['has_attachments'] and msg['attachment_filename']:
                attachment_url = msg['attachment_url']
                if attachment_url and str(attachment_url).lower() != 'nan' and attachment_url.strip():
                    html += f"""
                        <div class="attachment">
                            📎 <a href="{attachment_url}" target="_blank">{msg['attachment_filename']}</a>
                        </div>
                    """
                else:
                    html += f"""
                        <div class="attachment">
                            📎 {msg['attachment_filename']}
                        </div>
                    """
            
            html += f'<span class="message-time">{msg_time}</span></div>'
        
        html += '</div>'
    
    html += f"""
        </div>
        
        <div class="pagination">
            <a href="/messages?page={prev_page}&per_page={per_page}">← Previous</a>
            <span style="color: #dc2626; font-weight: bold; margin: 0 15px;">Page {page}</span>
            <a href="/messages?page={next_page}&per_page={per_page}">Next →</a>
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/search')
def search():
    """Search interface."""
    query = request.args.get('q', '')
    author = request.args.get('author', '')
    
    if chat_data is None:
        load_chat_data()
    
    results = chat_data.copy()
    
    if query:
        results = results[results['content'].str.contains(query, case=False, na=False)]
    
    if author:
        results = results[results['author_username'].str.contains(author, case=False, na=False)]
    
    html = f"""
    <html>
    <head><title>Search Messages</title></head>
    <body>
        <h1>Search Messages</h1>
        <p><a href="/">← Back to Home</a></p>
        
        <form method="get">
            <input type="text" name="q" placeholder="Search content..." value="{query}">
            <input type="text" name="author" placeholder="Author username..." value="{author}">
            <input type="submit" value="Search">
        </form>
        
        <h2>Results ({len(results)} messages)</h2>
        
        <table border="1" style="width:100%; border-collapse: collapse;">
            <tr>
                <th>Timestamp</th>
                <th>Author</th>
                <th>Content</th>
            </tr>
    """
    
    for _, row in results.head(100).iterrows():  # Limit to 100 results
        content = str(row['content'])[:300] + ('...' if len(str(row['content'])) > 300 else '')
        html += f"""
            <tr>
                <td>{row['timestamp']}</td>
                <td>{row['author_username']}</td>
                <td>{content}</td>
            </tr>
        """
    
    html += """
        </table>
    </body>
    </html>
    """
    
    return html

@app.route('/api/messages')
def api_messages():
    """API endpoint returning messages as JSON."""
    if chat_data is None:
        load_chat_data()
    
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    result_data = chat_data.iloc[offset:offset+limit]
    
    # Convert to dict and handle datetime serialization
    messages = []
    for _, row in result_data.iterrows():
        message = row.to_dict()
        message['timestamp'] = message['timestamp'].isoformat()
        messages.append(message)
    
    return jsonify({
        'messages': messages,
        'total': len(chat_data),
        'offset': offset,
        'limit': limit
    })

if __name__ == '__main__':
    print("Starting Flask server...")
    print("Run consolidate_chat.py first if you haven't already!")
    print("Server will be available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)