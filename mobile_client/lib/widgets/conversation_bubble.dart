import 'package:flutter/material.dart';
import 'package:glassmorphism/glassmorphism.dart';
import '../models/conversation.dart';
import '../theme/app_theme.dart';

class ConversationBubble extends StatelessWidget {
  final Conversation conversation;

  const ConversationBubble({
    super.key,
    required this.conversation,
  });

  double _calculateBubbleHeight(String message) {
    // Base height for padding and minimum content
    double baseHeight = 60.0;
    
    // Calculate additional height based on text length
    int lineCount = (message.length / 35).ceil();
    if (lineCount > 1) {
      baseHeight += (lineCount - 1) * 20.0;
    }
    
    // Account for line breaks in text
    int actualLineBreaks = '\n'.allMatches(message).length;
    baseHeight += actualLineBreaks * 20.0;
    
    return baseHeight.clamp(60.0, 200.0); // Min 60, Max 200
  }

  @override
  Widget build(BuildContext context) {
    final isUser = conversation.sender == 'user';
    
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUser) _buildAvatar(false),
          if (!isUser) const SizedBox(width: 12),
          Flexible(
            child: Container(
              constraints: BoxConstraints(
                maxWidth: MediaQuery.of(context).size.width * 0.75,
              ),
              child: GlassmorphicContainer(
                width: MediaQuery.of(context).size.width * 0.75,
                height: _calculateBubbleHeight(conversation.message),
                borderRadius: isUser ? 20 : 20,
                blur: 15,
                alignment: Alignment.center,
                border: 1.5,
                linearGradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: isUser 
                      ? [
                          AppTheme.primaryColor.withOpacity(0.3),
                          AppTheme.primaryColor.withOpacity(0.1),
                        ]
                      : [
                          Colors.white.withOpacity(0.15),
                          Colors.white.withOpacity(0.05),
                        ],
                ),
                borderGradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: isUser
                      ? [
                          AppTheme.primaryColor.withOpacity(0.6),
                          AppTheme.primaryColor.withOpacity(0.3),
                        ]
                      : [
                          Colors.white.withOpacity(0.3),
                          Colors.white.withOpacity(0.1),
                        ],
                ),
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        conversation.message,
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: isUser ? FontWeight.w500 : FontWeight.w400,
                        ),
                      ),
                      if (conversation.result != null) ...[
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: Colors.black.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            conversation.result!,
                            style: const TextStyle(
                              color: Colors.white70,
                              fontSize: 14,
                              fontFamily: 'monospace',
                            ),
                          ),
                        ),
                      ],
                      const SizedBox(height: 4),
                      Text(
                        _formatTime(conversation.timestamp),
                        style: const TextStyle(
                          color: Colors.white54,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
          if (isUser) const SizedBox(width: 12),
          if (isUser) _buildAvatar(true),
        ],
      ),
    );
  }

  Widget _buildAvatar(bool isUser) {
    return Container(
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        gradient: isUser ? AppTheme.primaryGradient : AppTheme.accentGradient,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.white.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Icon(
        isUser ? Icons.person : Icons.psychology,
        color: Colors.white,
        size: 18,
      ),
    );
  }

  String _formatTime(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);
    
    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}h ago';
    } else {
      return '${timestamp.day}/${timestamp.month}';
    }
  }
}