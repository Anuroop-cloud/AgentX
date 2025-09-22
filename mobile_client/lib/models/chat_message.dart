import 'package:json_annotation/json_annotation.dart';

part 'chat_message.g.dart';

@JsonSerializable()
class ChatMessage {
  final String id;
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final String? agentId;
  final MessageType type;
  final MessageStatus status;
  final Map<String, dynamic>? metadata;

  ChatMessage({
    required this.id,
    required this.text,
    required this.isUser,
    required this.timestamp,
    this.agentId,
    this.type = MessageType.text,
    this.status = MessageStatus.sent,
    this.metadata,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) => _$ChatMessageFromJson(json);
  Map<String, dynamic> toJson() => _$ChatMessageToJson(this);

  ChatMessage copyWith({
    String? id,
    String? text,
    bool? isUser,
    DateTime? timestamp,
    String? agentId,
    MessageType? type,
    MessageStatus? status,
    Map<String, dynamic>? metadata,
  }) {
    return ChatMessage(
      id: id ?? this.id,
      text: text ?? this.text,
      isUser: isUser ?? this.isUser,
      timestamp: timestamp ?? this.timestamp,
      agentId: agentId ?? this.agentId,
      type: type ?? this.type,
      status: status ?? this.status,
      metadata: metadata ?? this.metadata,
    );
  }
}

enum MessageType {
  @JsonValue('text')
  text,
  @JsonValue('action')
  action,
  @JsonValue('system')
  system,
  @JsonValue('error')
  error,
}

enum MessageStatus {
  @JsonValue('sending')
  sending,
  @JsonValue('sent')
  sent,
  @JsonValue('delivered')
  delivered,
  @JsonValue('failed')
  failed,
}