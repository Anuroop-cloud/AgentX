class Conversation {
  final String message;
  final String sender; // 'user' or 'assistant'
  final DateTime timestamp;
  final String? result;
  final String? toolUsed;

  Conversation({
    required this.message,
    required this.sender,
    required this.timestamp,
    this.result,
    this.toolUsed,
  });

  Map<String, dynamic> toJson() {
    return {
      'message': message,
      'sender': sender,
      'timestamp': timestamp.toIso8601String(),
      'result': result,
      'toolUsed': toolUsed,
    };
  }

  factory Conversation.fromJson(Map<String, dynamic> json) {
    return Conversation(
      message: json['message'],
      sender: json['sender'],
      timestamp: DateTime.parse(json['timestamp']),
      result: json['result'],
      toolUsed: json['toolUsed'],
    );
  }
}