import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../models/mcp_tool.dart';
import '../models/conversation.dart';

class AgentXService extends ChangeNotifier {
  static const String baseUrl = 'http://0.0.0.0:5000';
  
  List<MCPTool> _tools = [];
  List<Conversation> _conversations = [];
  bool _isLoading = false;
  String? _error;
  bool _isConnected = false;

  List<MCPTool> get tools => _tools;
  List<Conversation> get conversations => _conversations;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isConnected => _isConnected;

  Future<void> loadTools() async {
    _setLoading(true);
    try {
      final response = await http.get(Uri.parse('$baseUrl/tools'));
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _tools = (data['tools'] as List)
            .map((tool) => MCPTool.fromJson(tool))
            .toList();
        _isConnected = true;
        _error = null;
        
        // Add demo tools if none are available
        if (_tools.isEmpty) {
          _addDemoTools();
        }
      } else {
        _error = 'Failed to load tools: ${response.statusCode}';
        _isConnected = false;
      }
    } catch (e) {
      _error = 'Network error: $e';
      _isConnected = false;
      // Load demo tools in offline mode
      _addDemoTools();
    } finally {
      _setLoading(false);
    }
  }

  void _addDemoTools() {
    _tools = [
      MCPTool(
        id: 'gmail.send',
        name: 'Gmail Send',
        description: 'Send emails via Gmail',
        inputSchema: {
          'to': {'type': 'string', 'description': 'Recipient email'},
          'subject': {'type': 'string', 'description': 'Email subject'},
          'body': {'type': 'string', 'description': 'Email body'},
        },
      ),
      MCPTool(
        id: 'whatsapp.send',
        name: 'WhatsApp Send',
        description: 'Send WhatsApp messages',
        inputSchema: {
          'chat_id': {'type': 'string', 'description': 'Chat or contact ID'},
          'message': {'type': 'string', 'description': 'Message to send'},
        },
      ),
      MCPTool(
        id: 'calendar.create',
        name: 'Calendar Create',
        description: 'Create calendar events',
        inputSchema: {
          'title': {'type': 'string', 'description': 'Event title'},
          'start': {'type': 'string', 'description': 'Start datetime'},
          'end': {'type': 'string', 'description': 'End datetime'},
        },
      ),
      MCPTool(
        id: 'time.now',
        name: 'Current Time',
        description: 'Get current time and date',
        inputSchema: {},
      ),
    ];
    notifyListeners();
  }

  Future<Map<String, dynamic>> invokeTool(String toolId, Map<String, dynamic> inputs) async {
    _setLoading(true);
    try {
      Map<String, dynamic> result;
      
      if (!_isConnected) {
        // Use demo mode
        result = await _invokeDemoTool(toolId, inputs);
      } else {
        final response = await http.post(
          Uri.parse('$baseUrl/invoke'),
          headers: {'Content-Type': 'application/json'},
          body: json.encode({
            'tool_id': toolId,
            'inputs': inputs,
          }),
        );

        if (response.statusCode == 200) {
          result = json.decode(response.body);
        } else {
          throw Exception('Failed to invoke tool: ${response.statusCode}');
        }
      }
      
      // Add to conversation history
      _conversations.add(Conversation(
        message: 'Invoked ${toolId}',
        sender: 'assistant',
        timestamp: DateTime.now(),
        result: json.encode(result),
        toolUsed: toolId,
      ));
      
      notifyListeners();
      return result;
    } catch (e) {
      if (!_isConnected) {
        // Fallback to demo mode on error
        final result = await _invokeDemoTool(toolId, inputs);
        _conversations.add(Conversation(
          message: 'Invoked ${toolId} (Demo Mode)',
          sender: 'assistant',
          timestamp: DateTime.now(),
          result: json.encode(result),
          toolUsed: toolId,
        ));
        notifyListeners();
        return result;
      }
      _error = 'Failed to invoke tool: $e';
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  Future<Map<String, dynamic>> runWorkflow(String workflowName, Map<String, dynamic> params) async {
    _setLoading(true);
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/workflow'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'workflow': workflowName,
          ...params,
        }),
      );

      if (response.statusCode == 200) {
        final result = json.decode(response.body);
        
        _conversations.add(Conversation(
          message: 'Executed workflow: $workflowName',
          sender: 'assistant',
          timestamp: DateTime.now(),
          result: json.encode(result),
        ));
        
        notifyListeners();
        return result;
      } else {
        throw Exception('Failed to run workflow: ${response.statusCode}');
      }
    } catch (e) {
      _error = 'Failed to run workflow: $e';
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  void addMessage(String message, String sender) {
    _conversations.add(Conversation(
      message: message,
      sender: sender,
      timestamp: DateTime.now(),
    ));
    notifyListeners();
  }

  // Demo mode tool invocation for offline usage
  Future<Map<String, dynamic>> _invokeDemoTool(String toolId, Map<String, dynamic> inputs) async {
    await Future.delayed(const Duration(milliseconds: 800)); // Simulate network delay
    
    switch (toolId) {
      case 'gmail.send':
        return {
          'status': 'success',
          'message_id': 'demo_${DateTime.now().millisecondsSinceEpoch}',
          'result': 'Email sent to ${inputs['to']} with subject "${inputs['subject']}"'
        };
      case 'whatsapp.send':
        return {
          'status': 'success',
          'message_id': 'wa_${DateTime.now().millisecondsSinceEpoch}',
          'result': 'WhatsApp message sent to ${inputs['chat_id']}'
        };
      case 'calendar.create':
        return {
          'status': 'success',
          'event_id': 'cal_${DateTime.now().millisecondsSinceEpoch}',
          'result': 'Calendar event "${inputs['title']}" created'
        };
      case 'time.now':
        return {
          'status': 'success',
          'current_time': DateTime.now().toIso8601String(),
          'formatted': DateTime.now().toString(),
        };
      default:
        return {
          'status': 'error',
          'message': 'Unknown tool: $toolId'
        };
    }
  }

  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
