import 'package:json_annotation/json_annotation.dart';

part 'agent.g.dart';

@JsonSerializable()
class Agent {
  final String id;
  final String name;
  final String description;
  final String type;
  final AgentStatus status;
  final String? lastActivity;
  final int tasksCompleted;
  final Map<String, dynamic>? configuration;
  final List<String> capabilities;
  final DateTime createdAt;
  final DateTime updatedAt;

  Agent({
    required this.id,
    required this.name,
    required this.description,
    required this.type,
    required this.status,
    this.lastActivity,
    required this.tasksCompleted,
    this.configuration,
    required this.capabilities,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Agent.fromJson(Map<String, dynamic> json) => _$AgentFromJson(json);
  Map<String, dynamic> toJson() => _$AgentToJson(this);

  Agent copyWith({
    String? id,
    String? name,
    String? description,
    String? type,
    AgentStatus? status,
    String? lastActivity,
    int? tasksCompleted,
    Map<String, dynamic>? configuration,
    List<String>? capabilities,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Agent(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      type: type ?? this.type,
      status: status ?? this.status,
      lastActivity: lastActivity ?? this.lastActivity,
      tasksCompleted: tasksCompleted ?? this.tasksCompleted,
      configuration: configuration ?? this.configuration,
      capabilities: capabilities ?? this.capabilities,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

enum AgentStatus {
  @JsonValue('active')
  active,
  @JsonValue('idle')
  idle,
  @JsonValue('inactive')
  inactive,
  @JsonValue('error')
  error,
}