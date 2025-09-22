#!/usr/bin/env python3
import json
import time
import sqlite3
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

class AgentXServer:
    def __init__(self):
        self.conn = sqlite3.connect(':memory:')
        self.init_data()
        
    def init_data(self):
        self.conn.execute('CREATE TABLE tools (id TEXT PRIMARY KEY, name TEXT, description TEXT)')
        
        tools = [
            ('time.now', 'Time', 'Get current time'),
            ('whatsapp.send', 'WhatsApp', 'Send message'),
            ('gmail.send', 'Gmail', 'Send email'),
            ('calendar.create', 'Calendar', 'Create event')
        ]
        
        for tool_id, name, desc in tools:
            self.conn.execute('INSERT INTO tools VALUES (?, ?, ?)', (tool_id, name, desc))
        self.conn.commit()
        
    def get_tools(self):
        cursor = self.conn.execute('SELECT * FROM tools')
        return [{'id': r[0], 'name': r[1], 'description': r[2]} for r in cursor.fetchall()]
        
    def invoke_tool(self, tool_id, inputs):
        ts = datetime.now().isoformat()
        results = {
            'time.now': {'current_time': ts},
            'whatsapp.send': {'message_id': f'msg_{int(time.time())}', 'status': 'sent'},
            'gmail.send': {'email_id': f'email_{int(time.time())}', 'status': 'sent'},
            'calendar.create': {'event_id': f'event_{int(time.time())}', 'status': 'created'}
        }
        return results.get(tool_id, {'status': 'unknown'})

server = AgentXServer()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == '/':
            resp = {'message': '🤖 AgentX MCP Orchestrator', 'status': 'running', 'tools': len(server.get_tools())}
        elif self.path == '/tools':
            resp = {'tools': server.get_tools()}
        elif self.path == '/health':
            resp = {'status': 'healthy', 'uptime': int(time.time())}
        else:
            resp = {'status': 'not_found'}
            
        self.wfile.write(json.dumps(resp, indent=2).encode())
        
    def do_POST(self):
        if self.path == '/invoke':
            length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(length))
            result = server.invoke_tool(data.get('tool_id'), data.get('inputs', {}))
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps({'status': 'success', 'result': result}, indent=2).encode())
        
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

def main():
    httpd = HTTPServer(('0.0.0.0', 5000), Handler)
    print("🚀 AgentX MCP Orchestrator starting on http://0.0.0.0:5000")
    print("📊 Available endpoints:")
    print("   • GET  / - Status and info")
    print("   • GET  /tools - List available tools") 
    print("   • POST /invoke - Invoke a tool")
    print("   • GET  /health - Health check")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server shutting down...")
        httpd.server_close()

if __name__ == '__main__':
    main()
