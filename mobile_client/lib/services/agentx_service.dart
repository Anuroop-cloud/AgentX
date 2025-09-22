import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class AgentXService extends ChangeNotifier {
  static const String baseUrl = 'http://0.0.0.0:5000';
  
  List<Map<String, dynamic>> _tools = [];
  List<Map<String, dynamic>> _conversations = [];
  bool _isLoading = false;
  String? _error;

  List<Map<String, dynamic>> get tools => _tools;
  List<Map<String, dynamic>> get conversations => _conversations;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadTools() async {
    _setLoading(true);
    try {
      final response = await http.get(Uri.parse('$baseUrl/tools'));
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _tools = List<Map<String, dynamic>>.from(data['tools']);
        _error = null;
      } else {
        _error = 'Failed to load tools: ${response.statusCode}';
      }
    } catch (e) {
      _error = 'Network error: $e';
    } finally {
      _setLoading(false);
    }
  }

  Future<Map<String, dynamic>> invokeTool(String toolId, Map<String, dynamic> inputs) async {
    _setLoading(true);
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/invoke'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'tool_id': toolId,
          'inputs': inputs,
        }),
      );

      if (response.statusCode == 200) {
        final result = json.decode(response.body);
        
        // Add to conversation history
        _conversations.add({
          'timestamp': DateTime.now().toIso8601String(),
          'type': 'tool_invocation',
          'tool_id': toolId,
          'inputs': inputs,
          'result': result,
        });
        
        notifyListeners();
        return result;
      } else {
        throw Exception('Failed to invoke tool: ${response.statusCode}');
      }
    } catch (e) {
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
        
        _conversations.add({
          'timestamp': DateTime.now().toIso8601String(),
          'type': 'workflow',
          'workflow': workflowName,
          'params': params,
          'result': result,
        });
        
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

  void addMessage(String message, String type) {
    _conversations.add({
      'timestamp': DateTime.now().toIso8601String(),
      'type': type,
      'message': message,
    });
    notifyListeners();
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
