/// Data models for Mobile AgentX chat system
/// Handles chat messages, workflow steps, and agent responses

import 'package:json_annotation/json_annotation.dart';

part 'chat_models.g.dart';

/// Represents a single chat message in the conversation
@JsonSerializable()
class ChatMessage {
  final String id;
  final String content;
  final MessageType type;
  final DateTime timestamp;
  final WorkflowExecution? workflow;
  final MessageStatus status;

  const ChatMessage({
    required this.id,
    required this.content,
    required this.type,
    required this.timestamp,
    this.workflow,
    this.status = MessageStatus.sent,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) =>
      _$ChatMessageFromJson(json);
  Map<String, dynamic> toJson() => _$ChatMessageToJson(this);

  ChatMessage copyWith({
    String? id,
    String? content,
    MessageType? type,
    DateTime? timestamp,
    WorkflowExecution? workflow,
    MessageStatus? status,
  }) {
    return ChatMessage(
      id: id ?? this.id,
      content: content ?? this.content,
      type: type ?? this.type,
      timestamp: timestamp ?? this.timestamp,
      workflow: workflow ?? this.workflow,
      status: status ?? this.status,
    );
  }
}

/// Type of message (user input or agent response)
enum MessageType {
  user,
  agent,
  system,
}

/// Status of message delivery/processing
enum MessageStatus {
  sending,
  sent,
  processing,
  completed,
  error,
}

/// Represents the execution of a workflow with multiple agents
@JsonSerializable()
class WorkflowExecution {
  final String id;
  final String name;
  final String description;
  final WorkflowType type;
  final List<AgentStep> steps;
  final DateTime startTime;
  final DateTime? endTime;
  final WorkflowStatus status;
  final String? errorMessage;

  const WorkflowExecution({
    required this.id,
    required this.name,
    required this.description,
    required this.type,
    required this.steps,
    required this.startTime,
    this.endTime,
    this.status = WorkflowStatus.running,
    this.errorMessage,
  });

  factory WorkflowExecution.fromJson(Map<String, dynamic> json) =>
      _$WorkflowExecutionFromJson(json);
  Map<String, dynamic> toJson() => _$WorkflowExecutionToJson(this);

  WorkflowExecution copyWith({
    String? id,
    String? name,
    String? description,
    WorkflowType? type,
    List<AgentStep>? steps,
    DateTime? startTime,
    DateTime? endTime,
    WorkflowStatus? status,
    String? errorMessage,
  }) {
    return WorkflowExecution(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      type: type ?? this.type,
      steps: steps ?? this.steps,
      startTime: startTime ?? this.startTime,
      endTime: endTime ?? this.endTime,
      status: status ?? this.status,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }

  /// Get duration of workflow execution
  Duration get duration {
    final end = endTime ?? DateTime.now();
    return end.difference(startTime);
  }

  /// Get progress percentage (0.0 to 1.0)
  double get progress {
    if (steps.isEmpty) return 0.0;
    final completedSteps = steps.where((s) => s.status == StepStatus.completed).length;
    return completedSteps / steps.length;
  }
}

/// Type of workflow execution pattern
enum WorkflowType {
  sequential,
  parallel,
  hybrid,
}

/// Status of workflow execution
enum WorkflowStatus {
  pending,
  running,
  completed,
  error,
}

/// Represents a single step in a workflow (agent execution)
@JsonSerializable()
class AgentStep {
  final String id;
  final String agentName;
  final String description;
  final String? result;
  final DateTime startTime;
  final DateTime? endTime;
  final StepStatus status;
  final String? errorMessage;
  final Map<String, dynamic>? metadata;

  const AgentStep({
    required this.id,
    required this.agentName,
    required this.description,
    this.result,
    required this.startTime,
    this.endTime,
    this.status = StepStatus.pending,
    this.errorMessage,
    this.metadata,
  });

  factory AgentStep.fromJson(Map<String, dynamic> json) =>
      _$AgentStepFromJson(json);
  Map<String, dynamic> toJson() => _$AgentStepToJson(this);

  AgentStep copyWith({
    String? id,
    String? agentName,
    String? description,
    String? result,
    DateTime? startTime,
    DateTime? endTime,
    StepStatus? status,
    String? errorMessage,
    Map<String, dynamic>? metadata,
  }) {
    return AgentStep(
      id: id ?? this.id,
      agentName: agentName ?? this.agentName,
      description: description ?? this.description,
      result: result ?? this.result,
      startTime: startTime ?? this.startTime,
      endTime: endTime ?? this.endTime,
      status: status ?? this.status,
      errorMessage: errorMessage ?? this.errorMessage,
      metadata: metadata ?? this.metadata,
    );
  }

  /// Get duration of step execution
  Duration get duration {
    final end = endTime ?? DateTime.now();
    return end.difference(startTime);
  }

  /// Get agent icon based on agent name
  String get agentIcon {
    switch (agentName.toLowerCase()) {
      case 'gmail':
      case 'mobile_gmail_agent':
        return '📧';
      case 'whatsapp':
      case 'mobile_whatsapp_agent':
        return '💬';
      case 'calendar':
      case 'mobile_calendar_agent':
        return '📅';
      case 'maps':
      case 'mobile_maps_agent':
        return '🗺️';
      case 'spotify':
      case 'mobile_spotify_agent':
        return '🎵';
      case 'summary':
      case 'mobile_summary_agent':
        return '📝';
      default:
        return '🤖';
    }
  }

  /// Get friendly agent name
  String get friendlyName {
    switch (agentName.toLowerCase()) {
      case 'gmail':
      case 'mobile_gmail_agent':
        return 'Gmail';
      case 'whatsapp':
      case 'mobile_whatsapp_agent':
        return 'WhatsApp';
      case 'calendar':  
      case 'mobile_calendar_agent':
        return 'Calendar';
      case 'maps':
      case 'mobile_maps_agent':
        return 'Maps';
      case 'spotify':
      case 'mobile_spotify_agent':
        return 'Spotify';
      case 'summary':
      case 'mobile_summary_agent':
        return 'Summary';
      default:
        return agentName;
    }
  }
}

/// Status of individual agent step
enum StepStatus {
  pending,
  running,
  completed,
  error,
}

/// Suggested command for quick user input
@JsonSerializable()
class SuggestedCommand {
  final String id;
  final String title;
  final String command;
  final String description;
  final String icon;
  final String category;

  const SuggestedCommand({
    required this.id,
    required this.title,
    required this.command,
    required this.description,
    required this.icon,
    required this.category,
  });

  factory SuggestedCommand.fromJson(Map<String, dynamic> json) =>
      _$SuggestedCommandFromJson(json);
  Map<String, dynamic> toJson() => _$SuggestedCommandToJson(this);
}

/// App connection status
@JsonSerializable()
class ConnectionStatus {
  final bool isOnline;
  final bool backendConnected;
  final DateTime lastSync;
  final String? errorMessage;

  const ConnectionStatus({
    required this.isOnline,
    required this.backendConnected,
    required this.lastSync,
    this.errorMessage,
  });

  factory ConnectionStatus.fromJson(Map<String, dynamic> json) =>
      _$ConnectionStatusFromJson(json);
  Map<String, dynamic> toJson() => _$ConnectionStatusToJson(this);

  /// Get display message for connection status
  String get displayMessage {
    if (!isOnline) return 'No internet connection';
    if (!backendConnected) return 'Backend offline - using mock mode';
    return 'All systems online';
  }

  /// Get status color
  String get statusColor {
    if (!isOnline || !backendConnected) return 'warning';
    return 'success';
  }
}