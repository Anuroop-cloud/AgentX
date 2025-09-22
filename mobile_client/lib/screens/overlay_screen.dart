import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:glassmorphism/glassmorphism.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../services/agentx_service.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_card.dart';
import '../widgets/conversation_bubble.dart';

class OverlayScreen extends StatefulWidget {
  const OverlayScreen({super.key});

  @override
  State<OverlayScreen> createState() => _OverlayScreenState();
}

class _OverlayScreenState extends State<OverlayScreen> with TickerProviderStateMixin {
  late AnimationController _slideController;
  late AnimationController _pulseController;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _pulseAnimation;
  
  final TextEditingController _messageController = TextEditingController();
  bool _isExpanded = false;
  bool _isMinimized = true;

  @override
  void initState() {
    super.initState();
    
    _slideController = AnimationController(
      duration: const Duration(milliseconds: 400),
      vsync: this,
    );
    
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    
    _slideAnimation = Tween<Offset>(
      begin: const Offset(1.0, 0.0),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _slideController,
      curve: Curves.easeOutCubic,
    ));
    
    _pulseAnimation = Tween<double>(
      begin: 1.0,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _pulseController,
      curve: Curves.easeInOut,
    ));
    
    _pulseController.repeat(reverse: true);
    
    // Auto-show after 2 seconds
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) {
        _toggleOverlay();
      }
    });
  }

  @override
  void dispose() {
    _slideController.dispose();
    _pulseController.dispose();
    _messageController.dispose();
    super.dispose();
  }

  void _toggleOverlay() {
    setState(() {
      _isMinimized = !_isMinimized;
    });
    
    if (_isMinimized) {
      _slideController.reverse();
    } else {
      _slideController.forward();
    }
  }

  void _toggleExpanded() {
    setState(() {
      _isExpanded = !_isExpanded;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Stack(
        children: [
          // Floating Action Button - Always visible
          Positioned(
            right: 20,
            top: MediaQuery.of(context).size.height * 0.3,
            child: _buildFloatingButton(),
          ),
          
          // Overlay Panel - Slides in from right
          SlideTransition(
            position: _slideAnimation,
            child: _buildOverlayPanel(),
          ),
        ],
      ),
    );
  }

  Widget _buildFloatingButton() {
    return ScaleTransition(
      scale: _pulseAnimation,
      child: GestureDetector(
        onTap: _toggleOverlay,
        child: Container(
          width: 60,
          height: 60,
          decoration: BoxDecoration(
            gradient: AppTheme.primaryGradient,
            borderRadius: BorderRadius.circular(30),
            boxShadow: [
              BoxShadow(
                color: AppTheme.primaryColor.withOpacity(0.4),
                blurRadius: 20,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: const Icon(
            Icons.psychology,
            color: Colors.white,
            size: 28,
          ),
        ).animate().scale(
          duration: 600.ms,
          curve: Curves.elasticOut,
        ),
      ),
    );
  }

  Widget _buildOverlayPanel() {
    return Positioned(
      right: 0,
      top: 0,
      bottom: 0,
      child: Container(
        width: _isExpanded ? MediaQuery.of(context).size.width : 300,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              AppTheme.backgroundGradientStart.withOpacity(0.95),
              AppTheme.backgroundGradientEnd.withOpacity(0.90),
            ],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.3),
              blurRadius: 20,
              offset: const Offset(-5, 0),
            ),
          ],
        ),
        child: SafeArea(
          child: Column(
            children: [
              _buildHeader(),
              Expanded(child: _buildContent()),
              _buildInputArea(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              gradient: AppTheme.primaryGradient,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(Icons.psychology, color: Colors.white, size: 18),
          ),
          const SizedBox(width: 12),
          const Expanded(
            child: Text(
              'AgentX Assistant',
              style: TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          IconButton(
            icon: Icon(
              _isExpanded ? Icons.fullscreen_exit : Icons.fullscreen,
              color: Colors.white70,
            ),
            onPressed: _toggleExpanded,
          ),
          IconButton(
            icon: const Icon(Icons.close, color: Colors.white70),
            onPressed: _toggleOverlay,
          ),
        ],
      ),
    );
  }

  Widget _buildContent() {
    return Consumer<AgentXService>(
      builder: (context, service, _) {
        if (service.conversations.isEmpty) {
          return Center(
            child: GlassCard(
              padding: const EdgeInsets.all(20),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.psychology,
                    size: 48,
                    color: AppTheme.primaryColor.withOpacity(0.7),
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'AgentX Ready',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'I can help you with emails, messages, calendar, and more!',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
          );
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: service.conversations.length,
          itemBuilder: (context, index) {
            final conversation = service.conversations[index];
            return ConversationBubble(conversation: conversation)
                .animate()
                .slideInFromRight(
                  delay: (50 * index).ms,
                  duration: 400.ms,
                );
          },
        );
      },
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // Quick Actions
          _buildQuickActions(),
          const SizedBox(height: 12),
          
          // Text Input
          GlassCard(
            padding: const EdgeInsets.all(4),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    decoration: const InputDecoration(
                      hintText: 'Ask AgentX...',
                      hintStyle: TextStyle(color: Colors.white60),
                      border: InputBorder.none,
                      contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    ),
                    style: const TextStyle(color: Colors.white),
                    onSubmitted: (_) => _sendMessage(),
                  ),
                ),
                const SizedBox(width: 8),
                Consumer<AgentXService>(
                  builder: (context, service, _) => Container(
                    decoration: BoxDecoration(
                      gradient: AppTheme.primaryGradient,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: IconButton(
                      icon: service.isLoading 
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                color: Colors.white,
                                strokeWidth: 2,
                              ),
                            )
                          : const Icon(Icons.send, color: Colors.white),
                      onPressed: service.isLoading ? null : _sendMessage,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions() {
    return Row(
      children: [
        _buildQuickActionChip('📧 Email', () => _quickAction('gmail.send')),
        const SizedBox(width: 8),
        _buildQuickActionChip('💬 Chat', () => _quickAction('whatsapp.send')),
        const SizedBox(width: 8),
        _buildQuickActionChip('📅 Calendar', () => _quickAction('calendar.create')),
        const SizedBox(width: 8),
        _buildQuickActionChip('⏰ Time', () => _quickAction('time.now')),
      ],
    );
  }

  Widget _buildQuickActionChip(String label, VoidCallback onTap) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: Colors.white.withOpacity(0.2),
              width: 1,
            ),
          ),
          child: Text(
            label,
            textAlign: TextAlign.center,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
      ),
    );
  }

  void _sendMessage() {
    final message = _messageController.text.trim();
    if (message.isEmpty) return;

    final service = context.read<AgentXService>();
    service.addMessage(message, 'user');
    _messageController.clear();

    // Simple command parsing
    if (message.toLowerCase().contains('time')) {
      _quickAction('time.now');
    } else if (message.toLowerCase().contains('email')) {
      _quickAction('gmail.send');
    } else if (message.toLowerCase().contains('whatsapp') || message.toLowerCase().contains('message')) {
      _quickAction('whatsapp.send');
    } else if (message.toLowerCase().contains('calendar') || message.toLowerCase().contains('meeting')) {
      _quickAction('calendar.create');
    } else {
      service.addMessage(
        'I understand you want help with: "$message". Try using the quick actions below!',
        'assistant',
      );
    }
  }

  void _quickAction(String toolId) {
    final service = context.read<AgentXService>();
    
    Map<String, dynamic> inputs = {};
    
    switch (toolId) {
      case 'gmail.send':
        inputs = {
          'to': 'colleague@company.com',
          'subject': 'Quick Update from AgentX',
          'body': 'This is a demo email sent via AgentX overlay!'
        };
        break;
      case 'whatsapp.send':
        inputs = {
          'chat_id': 'team',
          'message': 'Hello from AgentX overlay! 🤖✨'
        };
        break;
      case 'calendar.create':
        inputs = {
          'title': 'AgentX Demo Meeting',
          'start': DateTime.now().add(const Duration(hours: 1)).toIso8601String(),
          'end': DateTime.now().add(const Duration(hours: 2)).toIso8601String()
        };
        break;
      case 'time.now':
        // No inputs needed
        break;
    }

    service.invokeTool(toolId, inputs);
  }
}