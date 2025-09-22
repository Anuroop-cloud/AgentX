import 'package:flutter/material.dart';
import 'package:glassmorphism/glassmorphism.dart';
import 'package:intl/intl.dart';
import '../theme/app_theme.dart';
import '../screens/chat/chat_screen.dart';

class MessageBubble extends StatelessWidget {
  final ChatMessage message;

  const MessageBubble({
    super.key,
    required this.message,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: message.isUser 
          ? MainAxisAlignment.end 
          : MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (!message.isUser) ...[
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: message.agentColor?.withOpacity(0.2) ?? AppTheme.primaryColor.withOpacity(0.2),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(
                color: message.agentColor?.withOpacity(0.3) ?? AppTheme.primaryColor.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: Icon(
              Icons.smart_toy,
              color: message.agentColor ?? AppTheme.primaryColor,
              size: 16,
            ),
          ),
          const SizedBox(width: 12),
        ],
        
        Flexible(
          child: Column(
            crossAxisAlignment: message.isUser 
                ? CrossAxisAlignment.end 
                : CrossAxisAlignment.start,
            children: [
              GlassmorphicContainer(
                width: null,
                height: null,
                borderRadius: 20,
                blur: 20,
                alignment: Alignment.centerLeft,
                border: 2,
                linearGradient: message.isUser
                    ? const LinearGradient(
                        colors: [
                          Color(0x206C5CE7),
                          Color(0x10A29BFE),
                        ],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      )
                    : AppTheme.glassmorphismGradient(opacity: 0.05),
                borderGradient: message.isUser
                    ? const LinearGradient(
                        colors: [
                          Color(0x406C5CE7),
                          Color(0x20A29BFE),
                        ],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      )
                    : AppTheme.glassmorphismBorderGradient(opacity: 0.2),
                child: Container(
                  constraints: BoxConstraints(
                    maxWidth: MediaQuery.of(context).size.width * 0.75,
                  ),
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 12,
                  ),
                  child: Text(
                    message.text,
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.9),
                      fontSize: 15,
                      height: 1.4,
                    ),
                  ),
                ),
              ),
              
              const SizedBox(height: 4),
              
              Text(
                DateFormat('HH:mm').format(message.timestamp),
                style: TextStyle(
                  color: Colors.white.withOpacity(0.4),
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
        
        if (message.isUser) ...[
          const SizedBox(width: 12),
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              gradient: AppTheme.primaryGradient,
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Icon(
              Icons.person,
              color: Colors.white,
              size: 16,
            ),
          ),
        ],
      ],
    );
  }
}