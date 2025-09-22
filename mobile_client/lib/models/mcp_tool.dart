class MCPTool {
  final String id;
  final String name;
  final String description;
  final Map<String, dynamic> inputSchema;
  final bool isActive;

  MCPTool({
    required this.id,
    required this.name,
    required this.description,
    required this.inputSchema,
    this.isActive = false,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'inputSchema': inputSchema,
      'isActive': isActive,
    };
  }

  factory MCPTool.fromJson(Map<String, dynamic> json) {
    return MCPTool(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      inputSchema: json['inputSchema'] ?? {},
      isActive: json['isActive'] ?? false,
    );
  }
}