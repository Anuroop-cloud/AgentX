import 'package:json_annotation/json_annotation.dart';

part 'automation_task.g.dart';

@JsonSerializable()
class AutomationTask {
  final String id;
  final String title;
  final String description;
  final String agentId;
  final TaskStatus status;
  final TaskPriority priority;
  final DateTime createdAt;
  final DateTime? startedAt;
  final DateTime? completedAt;
  final Map<String, dynamic>? parameters;
  final List<TaskStep> steps;
  final String? errorMessage;
  final double progress;

  AutomationTask({
    required this.id,
    required this.title,
    required this.description,
    required this.agentId,
    required this.status,
    required this.priority,
    required this.createdAt,
    this.startedAt,
    this.completedAt,
    this.parameters,
    required this.steps,
    this.errorMessage,
    this.progress = 0.0,
  });

  factory AutomationTask.fromJson(Map<String, dynamic> json) => _$AutomationTaskFromJson(json);
  Map<String, dynamic> toJson() => _$AutomationTaskToJson(this);

  AutomationTask copyWith({
    String? id,
    String? title,
    String? description,
    String? agentId,
    TaskStatus? status,
    TaskPriority? priority,
    DateTime? createdAt,
    DateTime? startedAt,
    DateTime? completedAt,
    Map<String, dynamic>? parameters,
    List<TaskStep>? steps,
    String? errorMessage,
    double? progress,
  }) {
    return AutomationTask(
      id: id ?? this.id,
      title: title ?? this.title,
      description: description ?? this.description,
      agentId: agentId ?? this.agentId,
      status: status ?? this.status,
      priority: priority ?? this.priority,
      createdAt: createdAt ?? this.createdAt,
      startedAt: startedAt ?? this.startedAt,
      completedAt: completedAt ?? this.completedAt,
      parameters: parameters ?? this.parameters,
      steps: steps ?? this.steps,
      errorMessage: errorMessage ?? this.errorMessage,
      progress: progress ?? this.progress,
    );
  }
}

@JsonSerializable()
class TaskStep {
  final String id;
  final String name;
  final String description;
  final StepStatus status;
  final DateTime? startedAt;
  final DateTime? completedAt;
  final Map<String, dynamic>? result;
  final String? errorMessage;

  TaskStep({
    required this.id,
    required this.name,
    required this.description,
    required this.status,
    this.startedAt,
    this.completedAt,
    this.result,
    this.errorMessage,
  });

  factory TaskStep.fromJson(Map<String, dynamic> json) => _$TaskStepFromJson(json);
  Map<String, dynamic> toJson() => _$TaskStepToJson(this);
}

enum TaskStatus {
  @JsonValue('pending')
  pending,
  @JsonValue('running')
  running,
  @JsonValue('completed')
  completed,
  @JsonValue('failed')
  failed,
  @JsonValue('cancelled')
  cancelled,
}

enum TaskPriority {
  @JsonValue('low')
  low,
  @JsonValue('medium')
  medium,
  @JsonValue('high')
  high,
  @JsonValue('urgent')
  urgent,
}

enum StepStatus {
  @JsonValue('pending')
  pending,
  @JsonValue('running')
  running,
  @JsonValue('completed')
  completed,
  @JsonValue('failed')
  failed,
  @JsonValue('skipped')
  skipped,
}