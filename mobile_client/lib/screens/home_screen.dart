import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:glassmorphism/glassmorphism.dart';
import '../services/agentx_service.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_card.dart';
import '../widgets/tool_card.dart';
import '../widgets/conversation_bubble.dart';
import '../widgets/gradient_background.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with TickerProviderStateMixin {
  late AnimationController _animationController;
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );
    
    // Load tools on startup
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AgentXService>().loadTools();
    });
    
    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                gradient: AppTheme.primaryGradient,
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.psychology, color: Colors.white, size: 20),
            ),
            const SizedBox(width: 12),
            const Text(
              'AgentX',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
          ],
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white70),
            onPressed: () {
              context.read<AgentXService>().loadTools();
            },
          ),
        ],
      ),
      body: GradientBackground(
        child: SafeArea(
          child: Consumer<AgentXService>(
            builder: (context, service, _) {
              return Column(
                children: [
                  // Header Stats
                  _buildHeaderStats(service).animate().slideInFromTop(
                    duration: 600.ms,
                    curve: Curves.easeOutQuart,
                  ),
                  
                  // Quick Actions
                  _buildQuickActions().animate().slideInFromLeft(
                    delay: 200.ms,
                    duration: 600.ms,
                    curve: Curves.easeOutQuart,
                  ),
                  
                  // Conversation Area
                  Expanded(
                    child: _buildConversationArea(service).animate().fadeIn(
                      delay: 400.ms,
                      duration: 800.ms,
                    ),
                  ),
                  
                  // Input Area
                  _buildInputArea(service).animate().slideInFromBottom(
                    delay: 600.ms,
                    duration: 600.ms,
                    curve: Curves.easeOutQuart,
                  ),
                ],
              );
            },
          ),
        ),
      ),
    );
  }

  Widget _buildHeaderStats(AgentXService service) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: GlassCard(
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _buildStatItem('Tools', '${service.tools.length}', Icons.build),
            _buildStatItem('Messages', '${service.conversations.length}', Icons.chat_bubble),
            _buildStatItem('Status', service.isLoading ? 'Active' : 'Ready', Icons.circle),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, color: AppTheme.accentColor, size: 24),
        const SizedBox(height: 8),
        Text(
          value,
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            fontSize: 12,
            color: Colors.white60,
          ),
        ),
      ],
    );
  }

  Widget _buildQuickActions() {
    return SizedBox(
      height: 120,
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        children: [
          _buildActionCard('📧 Send Email', 'gmail.send', Colors.red),
          _buildActionCard('💬 WhatsApp', 'whatsapp.send', Colors.green),
          _buildActionCard('📅 Calendar', 'calendar.create', Colors.blue),
          _buildActionCard('⏰ Time', 'time.now', Colors.orange),
        ],
      ),
    );
  }

  Widget _buildActionCard(String title, String toolId, Color color) {
    return Container(
      width: 140,
      margin: const EdgeInsets.only(right: 12),
      child: GlassCard(
        onTap: () => _quickInvoke(toolId),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: color.withOpacity(0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(Icons.flash_on, color: color, size: 20),
            ),
            const SizedBox(height: 8),
            Text(
              title,
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 12,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildConversationArea(AgentXService service) {
    if (service.conversations.isEmpty) {
      return Center(
        child: GlassCard(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.psychology,
                size: 64,
                color: AppTheme.primaryColor.withOpacity(0.7),
              ),
              const SizedBox(height: 16),
              const Text(
                'Welcome to AgentX',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Your AI-powered task automation assistant.\nTap a quick action or type a message to get started.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Colors.white70,
                  fontSize: 16,
                ),
              ),
            ],
          ),
        ),
      );
    }

    return ListView.builder(
      controller: _scrollController,
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
  }

  Widget _buildInputArea(AgentXService service) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: GlassCard(
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: _messageController,
                decoration: const InputDecoration(
                  hintText: 'Ask AgentX to help you...',
                  hintStyle: TextStyle(color: Colors.white60),
                  border: InputBorder.none,
                  contentPadding: EdgeInsets.symmetric(horizontal: 16),
                ),
                style: const TextStyle(color: Colors.white),
                onSubmitted: (_) => _sendMessage(service),
              ),
            ),
            const SizedBox(width: 8),
            Container(
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
                onPressed: service.isLoading ? null : () => _sendMessage(service),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _sendMessage(AgentXService service) {
    final message = _messageController.text.trim();
    if (message.isEmpty) return;

    service.addMessage(message, 'user');
    _messageController.clear();

    // Simple command parsing
    if (message.toLowerCase().contains('time')) {
      _quickInvoke('time.now');
    } else if (message.toLowerCase().contains('email')) {
      _quickInvoke('gmail.send');
    } else if (message.toLowerCase().contains('whatsapp')) {
      _quickInvoke('whatsapp.send');
    } else if (message.toLowerCase().contains('calendar')) {
      _quickInvoke('calendar.create');
    } else {
      service.addMessage('I understand you want help with: "$message". Try using one of the quick actions above!', 'assistant');
    }

    // Scroll to bottom
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    });
  }

  void _quickInvoke(String toolId) {
    final service = context.read<AgentXService>();
    
    Map<String, dynamic> inputs = {};
    
    if (toolId == 'gmail.send') {
      inputs = {
        'to': 'colleague@company.com',
        'subject': 'Quick Update',
        'body': 'This is a demo email sent via AgentX!'
      };
    } else if (toolId == 'whatsapp.send') {
      inputs = {
        'chat_id': 'team',
        'message': 'Hello from AgentX! 🤖'
      };
    } else if (toolId == 'calendar.create') {
      inputs = {
        'title': 'AgentX Demo Meeting',
        'start': DateTime.now().add(const Duration(hours: 1)).toIso8601String(),
        'end': DateTime.now().add(const Duration(hours: 2)).toIso8601String()
      };
    }

    service.invokeTool(toolId, inputs);
  }
}
