import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:glassmorphism/glassmorphism.dart';
import 'package:go_router/go_router.dart';
import '../../theme/app_theme.dart';
import '../../widgets/message_bubble.dart';
import '../../widgets/glass_text_field.dart';

class ChatScreen extends StatefulWidget {
  final String agentId;

  const ChatScreen({
    super.key,
    required this.agentId,
  });

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<ChatMessage> _messages = [];
  bool _isTyping = false;

  // Mock agent data
  late Map<String, dynamic> _agent;

  @override
  void initState() {
    super.initState();
    _loadAgentData();
    _initializeChat();
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _loadAgentData() {
    final agents = {
      'whatsapp': {
        'name': 'WhatsApp Agent',
        'subtitle': 'Message automation assistant',
        'icon': Icons.message,
        'color': const Color(0xFF25D366),
      },
      'gmail': {
        'name': 'Gmail Agent',
        'subtitle': 'Email composition assistant',
        'icon': Icons.email,
        'color': const Color(0xFFEA4335),
      },
      'maps': {
        'name': 'Maps Agent',
        'subtitle': 'Navigation assistant',
        'icon': Icons.map,
        'color': const Color(0xFF34A853),
      },
      'general': {
        'name': 'AI Assistant',
        'subtitle': 'General automation helper',
        'icon': Icons.smart_toy,
        'color': AppTheme.primaryColor,
      },
    };

    _agent = agents[widget.agentId] ?? agents['general']!;
  }

  void _initializeChat() {
    // Add welcome message
    _messages.add(ChatMessage(
      text: _getWelcomeMessage(),
      isUser: false,
      timestamp: DateTime.now(),
      agentColor: _agent['color'],
    ));

    // Add some example messages
    if (widget.agentId == 'whatsapp') {
      _messages.addAll([
        ChatMessage(
          text: "Try saying something like:\n• Send a message to John\n• Text Mom 'I'll be late'\n• WhatsApp Sarah about the meeting",
          isUser: false,
          timestamp: DateTime.now().add(const Duration(seconds: 1)),
          agentColor: _agent['color'],
        ),
      ]);
    } else if (widget.agentId == 'gmail') {
      _messages.addAll([
        ChatMessage(
          text: "Here are some examples:\n• Send an email to manager about project update\n• Compose email to team@company.com\n• Email client about meeting reschedule",
          isUser: false,
          timestamp: DateTime.now().add(const Duration(seconds: 1)),
          agentColor: _agent['color'],
        ),
      ]);
    }
  }

  String _getWelcomeMessage() {
    switch (widget.agentId) {
      case 'whatsapp':
        return "Hi! I'm your WhatsApp automation assistant. I can help you send messages, find contacts, and automate your WhatsApp interactions. What would you like me to do?";
      case 'gmail':
        return "Hello! I'm your Gmail assistant. I can help you compose and send emails with smart templates and recipient detection. How can I assist you today?";
      case 'maps':
        return "Hey there! I'm your navigation assistant. I can help you get directions, find places, and navigate efficiently. Where would you like to go?";
      default:
        return "Hello! I'm your AI assistant. I can help you automate various tasks on your device using computer vision and natural language processing. What can I help you with?";
    }
  }

  void _sendMessage() {
    if (_messageController.text.trim().isEmpty) return;

    final message = ChatMessage(
      text: _messageController.text.trim(),
      isUser: true,
      timestamp: DateTime.now(),
    );

    setState(() {
      _messages.add(message);
      _isTyping = true;
    });

    _messageController.clear();
    _scrollToBottom();

    // Simulate agent response
    _simulateAgentResponse(message.text);
  }

  void _simulateAgentResponse(String userMessage) {
    Future.delayed(const Duration(seconds: 2), () {
      if (!mounted) return;

      setState(() {
        _isTyping = false;
        _messages.add(ChatMessage(
          text: _generateResponse(userMessage),
          isUser: false,
          timestamp: DateTime.now(),
          agentColor: _agent['color'],
        ));
      });

      _scrollToBottom();
    });
  }

  String _generateResponse(String userMessage) {
    final message = userMessage.toLowerCase();
    
    if (widget.agentId == 'whatsapp') {
      if (message.contains('send') || message.contains('message') || message.contains('text')) {
        return "I'll help you send that WhatsApp message! I'm analyzing your screen to detect the contact and compose the message. This may take a few seconds...";
      } else if (message.contains('contact') || message.contains('find')) {
        return "Searching for the contact in your WhatsApp. I'll use OCR to read the contact list and find the right person for you.";
      }
    } else if (widget.agentId == 'gmail') {
      if (message.contains('email') || message.contains('send') || message.contains('compose')) {
        return "I'll help you compose and send that email! I'm opening Gmail and will use smart templates to craft your message. Please wait...";
      } else if (message.contains('template') || message.contains('draft')) {
        return "I can suggest email templates based on your request. Let me analyze the context and provide the best template for your needs.";
      }
    } else if (widget.agentId == 'maps') {
      if (message.contains('directions') || message.contains('navigate') || message.contains('go to')) {
        return "I'll get directions for you! Opening Maps and searching for your destination. I'll provide turn-by-turn navigation once ready.";
      } else if (message.contains('find') || message.contains('search')) {
        return "Searching for nearby places that match your request. I'll show you the best options with ratings and reviews.";
      }
    }

    return "I understand your request! I'm using computer vision to analyze your screen and will automate the task for you. This may take a moment while I process the visual elements...";
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppTheme.backgroundGradient,
        ),
        child: SafeArea(
          child: Column(
            children: [
              // App Bar
              Padding(
                padding: const EdgeInsets.all(24),
                child: Row(
                  children: [
                    GestureDetector(
                      onTap: () => context.go('/dashboard'),
                      child: Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: Colors.white.withOpacity(0.2),
                            width: 1,
                          ),
                        ),
                        child: const Icon(
                          Icons.arrow_back_rounded,
                          color: Colors.white,
                          size: 20,
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        color: _agent['color'].withOpacity(0.2),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(
                          color: _agent['color'].withOpacity(0.3),
                          width: 2,
                        ),
                      ),
                      child: Icon(
                        _agent['icon'],
                        color: _agent['color'],
                        size: 24,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _agent['name'],
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            _agent['subtitle'],
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.7),
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: Colors.white.withOpacity(0.2),
                          width: 1,
                        ),
                      ),
                      child: const Icon(
                        Icons.more_vert_rounded,
                        color: Colors.white,
                        size: 20,
                      ),
                    ),
                  ],
                ),
              ).animate().fadeIn(delay: 200.ms, duration: 800.ms),

              // Messages
              Expanded(
                child: ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  itemCount: _messages.length + (_isTyping ? 1 : 0),
                  itemBuilder: (context, index) {
                    if (index == _messages.length && _isTyping) {
                      return _buildTypingIndicator();
                    }
                    
                    final message = _messages[index];
                    return Padding(
                      padding: EdgeInsets.only(
                        bottom: index < _messages.length - 1 ? 16 : 24,
                      ),
                      child: MessageBubble(
                        message: message,
                      ).animate().slideX(
                        begin: message.isUser ? 0.3 : -0.3,
                        delay: (index * 100).ms,
                        duration: 600.ms,
                        curve: Curves.easeOutCubic,
                      ),
                    );
                  },
                ),
              ),

              // Message Input
              Padding(
                padding: const EdgeInsets.all(24),
                child: Row(
                  children: [
                    Expanded(
                      child: GlassmorphicContainer(
                        width: double.infinity,
                        height: null,
                        borderRadius: 20,
                        blur: 20,
                        alignment: Alignment.centerLeft,
                        border: 2,
                        linearGradient: AppTheme.glassmorphismGradient(opacity: 0.1),
                        borderGradient: AppTheme.glassmorphismBorderGradient(opacity: 0.3),
                        child: TextField(
                          controller: _messageController,
                          maxLines: null,
                          textCapitalization: TextCapitalization.sentences,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                          ),
                          decoration: InputDecoration(
                            hintText: 'Type your message...',
                            hintStyle: TextStyle(
                              color: Colors.white.withOpacity(0.5),
                              fontSize: 16,
                            ),
                            border: InputBorder.none,
                            enabledBorder: InputBorder.none,
                            focusedBorder: InputBorder.none,
                            contentPadding: const EdgeInsets.symmetric(
                              horizontal: 20,
                              vertical: 16,
                            ),
                          ),
                          onSubmitted: (_) => _sendMessage(),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Container(
                      width: 56,
                      height: 56,
                      decoration: BoxDecoration(
                        gradient: AppTheme.primaryGradient,
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: [
                          BoxShadow(
                            color: AppTheme.primaryColor.withOpacity(0.3),
                            blurRadius: 15,
                            offset: const Offset(0, 5),
                          ),
                        ],
                      ),
                      child: Material(
                        color: Colors.transparent,
                        child: InkWell(
                          borderRadius: BorderRadius.circular(16),
                          onTap: _sendMessage,
                          child: const Icon(
                            Icons.send_rounded,
                            color: Colors.white,
                            size: 24,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ).animate().slideY(
                begin: 0.3,
                delay: 400.ms,
                duration: 800.ms,
                curve: Curves.easeOutCubic,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Padding(
      padding: const EdgeInsets.only(bottom: 24),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: _agent['color'].withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: _agent['color'].withOpacity(0.3),
                width: 1,
              ),
            ),
            child: Icon(
              _agent['icon'],
              color: _agent['color'],
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          GlassmorphicContainer(
            width: null,
            height: 56,
            borderRadius: 16,
            blur: 20,
            alignment: Alignment.centerLeft,
            border: 2,
            linearGradient: AppTheme.glassmorphismGradient(opacity: 0.1),
            borderGradient: AppTheme.glassmorphismBorderGradient(opacity: 0.3),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'AI is thinking',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.7),
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(width: 8),
                  SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(_agent['color']),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final Color? agentColor;

  ChatMessage({
    required this.text,
    required this.isUser,
    required this.timestamp,
    this.agentColor,
  });
}