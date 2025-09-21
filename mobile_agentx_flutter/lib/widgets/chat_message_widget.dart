/// Individual chat message widget with status indicators
/// Supports both user messages and agent responses

import 'package:flutter/material.dart';
import '../models/chat_models.dart';
import '../theme/app_theme.dart';
import 'workflow_timeline_widget.dart';

class ChatMessageWidget extends StatelessWidget {
  final ChatMessage message;
  final VoidCallback? onRetry;

  const ChatMessageWidget({
    super.key,
    required this.message,
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    final isUser = message.sender == MessageSender.user;
    
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment:
            isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUser) _buildAvatar(context, false),
          if (!isUser) const SizedBox(width: 12),
          Flexible(
            child: Container(
              constraints: BoxConstraints(
                maxWidth: MediaQuery.of(context).size.width * 0.8,
              ),
              decoration: BoxDecoration(
                color: isUser
                    ? AppTheme.primaryColor
                    : Theme.of(context).cardColor,
                borderRadius: BorderRadius.circular(16).copyWith(
                  bottomLeft: isUser ? const Radius.circular(16) : const Radius.circular(4),
                  bottomRight: isUser ? const Radius.circular(4) : const Radius.circular(16),
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          message.content,
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: isUser
                                ? Colors.white
                                : Theme.of(context).textTheme.bodyMedium?.color,
                          ),
                        ),
                        const SizedBox(height: 8),
                        _buildMessageFooter(context, isUser),
                      ],
                    ),
                  ),
                  
                  // Show workflow execution if available
                  if (message.workflowExecution != null)
                    WorkflowTimelineWidget(
                      execution: message.workflowExecution!,
                    ),
                ],
              ),
            ),
          ),
          if (isUser) const SizedBox(width: 12),
          if (isUser) _buildAvatar(context, true),
        ],
      ),
    );
  }

  Widget _buildAvatar(BuildContext context, bool isUser) {
    return Container(
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        color: isUser ? AppTheme.primaryColor : AppTheme.accentColor,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Icon(
        isUser ? Icons.person_rounded : Icons.smart_toy_rounded,
        color: Colors.white,
        size: 18,
      ),
    );
  }

  Widget _buildMessageFooter(BuildContext context, bool isUser) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          _formatTime(message.timestamp),
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: isUser
                ? Colors.white.withOpacity(0.7)
                : Theme.of(context).textTheme.bodySmall?.color?.withOpacity(0.7),
          ),
        ),
        if (!isUser) ...[
          const SizedBox(width: 8),
          _buildStatusIndicator(context),
        ],
      ],
    );
  }

  Widget _buildStatusIndicator(BuildContext context) {
    switch (message.status) {
      case MessageStatus.sending:
        return SizedBox(
          width: 12,
          height: 12,
          child: CircularProgressIndicator(
            strokeWidth: 2,
            valueColor: AlwaysStoppedAnimation<Color>(
              AppTheme.primaryColor.withOpacity(0.7),
            ),
          ),
        );
      
      case MessageStatus.sent:
        return Icon(
          Icons.check_circle_rounded,
          size: 12,
          color: AppTheme.accentColor,
        );
      
      case MessageStatus.failed:
        return GestureDetector(
          onTap: onRetry,
          child: Icon(
            Icons.error_rounded,
            size: 12,
            color: AppTheme.errorColor,
          ),
        );
      
      case MessageStatus.processing:
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              width: 12,
              height: 12,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(
                  AppTheme.accentColor,
                ),
              ),
            ),
            const SizedBox(width: 4),
            Text(
              'Processing...',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppTheme.accentColor,
                fontSize: 10,
              ),
            ),
          ],
        );
    }
  }

  String _formatTime(DateTime timestamp) {
    final now = DateTime.now();
    final diff = now.difference(timestamp);
    
    if (diff.inMinutes < 1) {
      return 'now';
    } else if (diff.inHours < 1) {
      return '${diff.inMinutes}m ago';
    } else if (diff.inDays < 1) {
      return '${diff.inHours}h ago';
    } else {
      return '${timestamp.day}/${timestamp.month}';
    }
  }
}