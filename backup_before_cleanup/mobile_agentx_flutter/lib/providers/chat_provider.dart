/// Chat Provider - State management for Mobile AgentX chat interface
/// Handles chat messages, workflow execution, and app state

import 'package:flutter/foundation.dart';
import '../models/chat_models.dart';
import '../services/mock_api_service.dart';
import 'dart:async';

class ChatProvider extends ChangeNotifier {
  // Chat state
  final List<ChatMessage> _messages = [];
  final List<SuggestedCommand> _suggestedCommands = [];
  ConnectionStatus _connectionStatus = ConnectionStatus(
    isOnline: true,
    backendConnected: false,
    lastSync: DateTime.now(),
  );
  
  bool _isProcessing = false;
  StreamSubscription<WorkflowExecution>? _workflowSubscription;
  
  // Getters
  List<ChatMessage> get messages => List.unmodifiable(_messages);
  List<SuggestedCommand> get suggestedCommands => List.unmodifiable(_suggestedCommands);
  ConnectionStatus get connectionStatus => _connectionStatus;
  bool get isProcessing => _isProcessing;
  bool get isOfflineMode => !_connectionStatus.backendConnected;
  
  ChatProvider() {
    _initialize();
  }
  
  /// Initialize the chat provider
  void _initialize() {
    _loadSuggestedCommands();
    _checkConnectionStatus();
    _addWelcomeMessage();
  }
  
  /// Load suggested commands
  void _loadSuggestedCommands() {
    _suggestedCommands.clear();
    _suggestedCommands.addAll(MockApiService.getSuggestedCommands());
    notifyListeners();
  }
  
  /// Check connection status
  Future<void> _checkConnectionStatus() async {
    try {
      _connectionStatus = await MockApiService.checkConnection();
      notifyListeners();
    } catch (e) {
      debugPrint('Error checking connection: $e');
    }
  }
  
  /// Add welcome message
  void _addWelcomeMessage() {
    final welcomeMessage = ChatMessage(
      id: 'welcome',
      content: '👋 Welcome to Mobile AgentX! I can help you automate tasks across your mobile apps.\n\nTry asking me to "Prepare for my meeting" or tap one of the suggestions below.',
      type: MessageType.agent,
      timestamp: DateTime.now(),
      status: MessageStatus.completed,
    );
    
    _messages.add(welcomeMessage);
    notifyListeners();
  }
  
  /// Send a user message and process it
  Future<void> sendMessage(String content) async {
    if (content.trim().isEmpty || _isProcessing) return;
    
    // Add user message
    final userMessage = ChatMessage(
      id: _generateMessageId(),
      content: content.trim(),
      type: MessageType.user,
      timestamp: DateTime.now(),
      status: MessageStatus.sent,
    );
    
    _messages.add(userMessage);
    _isProcessing = true;
    notifyListeners();
    
    try {
      // Process command and get workflow
      final workflow = await MockApiService.processCommand(content);
      
      // Add agent response with workflow
      final agentMessage = ChatMessage(
        id: _generateMessageId(),
        content: _getAgentResponse(workflow),
        type: MessageType.agent,
        timestamp: DateTime.now(),
        workflow: workflow,
        status: MessageStatus.processing,
      );
      
      _messages.add(agentMessage);
      notifyListeners();
      
      // Execute workflow and update in real-time
      await _executeWorkflow(agentMessage, workflow);
      
    } catch (e) {
      // Add error message
      final errorMessage = ChatMessage(
        id: _generateMessageId(),
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        type: MessageType.agent,
        timestamp: DateTime.now(),
        status: MessageStatus.error,
      );
      
      _messages.add(errorMessage);
      debugPrint('Error processing message: $e');
    } finally {
      _isProcessing = false;
      notifyListeners();
    }
  }
  
  /// Execute workflow and update message in real-time
  Future<void> _executeWorkflow(ChatMessage message, WorkflowExecution workflow) async {
    _workflowSubscription?.cancel();
    
    _workflowSubscription = MockApiService.executeWorkflow(workflow).listen(
      (updatedWorkflow) {
        // Find and update the message with new workflow state
        final messageIndex = _messages.indexWhere((m) => m.id == message.id);
        if (messageIndex != -1) {
          _messages[messageIndex] = message.copyWith(
            workflow: updatedWorkflow,
            status: updatedWorkflow.status == WorkflowStatus.completed 
                ? MessageStatus.completed 
                : MessageStatus.processing,
          );
          notifyListeners();
        }
      },
      onError: (error) {
        // Update message with error state
        final messageIndex = _messages.indexWhere((m) => m.id == message.id);
        if (messageIndex != -1) {
          _messages[messageIndex] = message.copyWith(
            status: MessageStatus.error,
            workflow: workflow.copyWith(
              status: WorkflowStatus.error,
              errorMessage: error.toString(),
            ),
          );
          notifyListeners();
        }
        debugPrint('Workflow execution error: $error');
      },
      onDone: () {
        _workflowSubscription = null;
      },
    );
  }
  
  /// Generate agent response based on workflow
  String _getAgentResponse(WorkflowExecution workflow) {
    switch (workflow.name) {
      case 'Meeting Preparation':
        return '📅 I\'ll help you prepare for your meeting! Let me coordinate across your apps to gather everything you need.';
      case 'Morning Routine':
        return '🌅 Good morning! Let me check your schedule, emails, and messages to create your daily briefing.';
      case 'Communication Triage':
        return '💬 I\'ll analyze all your messages and emails to help you prioritize what needs your attention first.';
      default:
        return '🤖 I\'m processing your request and coordinating with the appropriate agents.';
    }
  }
  
  /// Send a suggested command
  Future<void> sendSuggestedCommand(SuggestedCommand command) async {
    await sendMessage(command.command);
  }
  
  /// Clear chat history
  void clearChat() {
    _messages.clear();
    _addWelcomeMessage();
    notifyListeners();
  }
  
  /// Retry failed message
  Future<void> retryMessage(String messageId) async {
    final messageIndex = _messages.indexWhere((m) => m.id == messageId);
    if (messageIndex == -1) return;
    
    final message = _messages[messageIndex];
    if (message.type == MessageType.user) {
      // Find and remove the corresponding agent response
      _messages.removeWhere((m) => 
        m.timestamp.isAfter(message.timestamp) && 
        m.type == MessageType.agent
      );
      
      // Resend the message
      await sendMessage(message.content);
    }
  }
  
  /// Generate unique message ID
  String _generateMessageId() {
    return 'msg_${DateTime.now().millisecondsSinceEpoch}_${_messages.length}';
  }
  
  /// Get workflow by message ID
  WorkflowExecution? getWorkflowForMessage(String messageId) {
    final message = _messages.firstWhere(
      (m) => m.id == messageId,
      orElse: () => const ChatMessage(
        id: '',
        content: '',
        type: MessageType.system,
        timestamp: null,
      ) as ChatMessage,
    );
    return message.workflow;
  }
  
  /// Update connection status manually
  Future<void> refreshConnectionStatus() async {
    await _checkConnectionStatus();
  }
  
  @override
  void dispose() {
    _workflowSubscription?.cancel();
    super.dispose();
  }
}