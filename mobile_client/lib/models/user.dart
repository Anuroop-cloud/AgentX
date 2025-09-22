import 'package:json_annotation/json_annotation.dart';

part 'user.g.dart';

@JsonSerializable()
class User {
  final String id;
  final String name;
  final String email;
  final String? avatarUrl;
  final DateTime createdAt;
  final DateTime updatedAt;
  final UserPreferences preferences;
  final UserStats stats;

  User({
    required this.id,
    required this.name,
    required this.email,
    this.avatarUrl,
    required this.createdAt,
    required this.updatedAt,
    required this.preferences,
    required this.stats,
  });

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
  Map<String, dynamic> toJson() => _$UserToJson(this);

  User copyWith({
    String? id,
    String? name,
    String? email,
    String? avatarUrl,
    DateTime? createdAt,
    DateTime? updatedAt,
    UserPreferences? preferences,
    UserStats? stats,
  }) {
    return User(
      id: id ?? this.id,
      name: name ?? this.name,
      email: email ?? this.email,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      preferences: preferences ?? this.preferences,
      stats: stats ?? this.stats,
    );
  }
}

@JsonSerializable()
class UserPreferences {
  final bool notificationsEnabled;
  final bool voiceFeedbackEnabled;
  final bool autoExecuteEnabled;
  final bool darkModeEnabled;
  final double automationSpeed;
  final String language;
  final String theme;

  UserPreferences({
    this.notificationsEnabled = true,
    this.voiceFeedbackEnabled = true,
    this.autoExecuteEnabled = false,
    this.darkModeEnabled = true,
    this.automationSpeed = 2.0,
    this.language = 'English',
    this.theme = 'dark',
  });

  factory UserPreferences.fromJson(Map<String, dynamic> json) => _$UserPreferencesFromJson(json);
  Map<String, dynamic> toJson() => _$UserPreferencesToJson(this);

  UserPreferences copyWith({
    bool? notificationsEnabled,
    bool? voiceFeedbackEnabled,
    bool? autoExecuteEnabled,
    bool? darkModeEnabled,
    double? automationSpeed,
    String? language,
    String? theme,
  }) {
    return UserPreferences(
      notificationsEnabled: notificationsEnabled ?? this.notificationsEnabled,
      voiceFeedbackEnabled: voiceFeedbackEnabled ?? this.voiceFeedbackEnabled,
      autoExecuteEnabled: autoExecuteEnabled ?? this.autoExecuteEnabled,
      darkModeEnabled: darkModeEnabled ?? this.darkModeEnabled,
      automationSpeed: automationSpeed ?? this.automationSpeed,
      language: language ?? this.language,
      theme: theme ?? this.theme,
    );
  }
}

@JsonSerializable()
class UserStats {
  final int activeAgents;
  final int tasksCompleted;
  final int daysActive;
  final int messagesExchanged;
  final double successRate;
  final int totalAutomations;

  UserStats({
    this.activeAgents = 0,
    this.tasksCompleted = 0,
    this.daysActive = 0,
    this.messagesExchanged = 0,
    this.successRate = 0.0,
    this.totalAutomations = 0,
  });

  factory UserStats.fromJson(Map<String, dynamic> json) => _$UserStatsFromJson(json);
  Map<String, dynamic> toJson() => _$UserStatsToJson(this);

  UserStats copyWith({
    int? activeAgents,
    int? tasksCompleted,
    int? daysActive,
    int? messagesExchanged,
    double? successRate,
    int? totalAutomations,
  }) {
    return UserStats(
      activeAgents: activeAgents ?? this.activeAgents,
      tasksCompleted: tasksCompleted ?? this.tasksCompleted,
      daysActive: daysActive ?? this.daysActive,
      messagesExchanged: messagesExchanged ?? this.messagesExchanged,
      successRate: successRate ?? this.successRate,
      totalAutomations: totalAutomations ?? this.totalAutomations,
    );
  }
}