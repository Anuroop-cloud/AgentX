/// Main chat screen for Mobile AgentX
/// Provides chat interface with workflow visualization

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/chat_provider.dart';
import '../widgets/chat_message_widget.dart';
import '../widgets/suggested_commands_widget.dart';
import '../widgets/chat_input_widget.dart';
import '../widgets/connection_status_banner.dart';
import '../theme/app_theme.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> with TickerProviderStateMixin {
  final ScrollController _scrollController = ScrollController();
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );
    _animationController.forward();
  }

  @override
  void dispose() {
    _scrollController.dispose();
    _animationController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
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
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: _buildAppBar(context),
      body: FadeTransition(
        opacity: _fadeAnimation,
        child: Column(
          children: [
            // Connection status banner
            Consumer<ChatProvider>(
              builder: (context, chatProvider, child) {
                if (chatProvider.isOfflineMode) {
                  return const ConnectionStatusBanner();
                }
                return const SizedBox.shrink();
              },
            ),
            
            // Chat messages
            Expanded(
              child: Consumer<ChatProvider>(
                builder: (context, chatProvider, child) {
                  // Auto-scroll when new messages arrive
                  WidgetsBinding.instance.addPostFrameCallback((_) {
                    _scrollToBottom();
                  });

                  return ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 8,
                    ),
                    itemCount: chatProvider.messages.length,
                    itemBuilder: (context, index) {
                      final message = chatProvider.messages[index];
                      return ChatMessageWidget(
                        message: message,
                        onRetry: () => chatProvider.retryMessage(message.id),
                      );
                    },
                  );
                },
              ),
            ),
            
            // Suggested commands (show when no messages or at start)
            Consumer<ChatProvider>(
              builder: (context, chatProvider, child) {
                final showSuggestions = chatProvider.messages.length <= 1 ||
                    !chatProvider.isProcessing;
                
                if (showSuggestions) {
                  return SuggestedCommandsWidget(
                    commands: chatProvider.suggestedCommands,
                    onCommandTap: (command) {
                      chatProvider.sendSuggestedCommand(command);
                    },
                  );
                }
                return const SizedBox.shrink();
              },
            ),
            
            // Chat input
            Consumer<ChatProvider>(
              builder: (context, chatProvider, child) {
                return ChatInputWidget(
                  onSendMessage: (message) {
                    chatProvider.sendMessage(message);
                    _scrollToBottom();
                  },
                  isProcessing: chatProvider.isProcessing,
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  PreferredSizeWidget _buildAppBar(BuildContext context) {
    return AppBar(
      title: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [AppTheme.primaryColor, AppTheme.secondaryColor],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(
              Icons.smart_toy_rounded,
              color: Colors.white,
              size: 18,
            ),
          ),
          const SizedBox(width: 12),
          const Text('Mobile AgentX'),
        ],
      ),
      actions: [
        Consumer<ChatProvider>(
          builder: (context, chatProvider, child) {
            return IconButton(
              icon: Icon(
                chatProvider.isOfflineMode
                    ? Icons.wifi_off_rounded
                    : Icons.wifi_rounded,
                color: chatProvider.isOfflineMode
                    ? AppTheme.warningColor
                    : AppTheme.accentColor,
              ),
              onPressed: () {
                chatProvider.refreshConnectionStatus();
                _showConnectionDialog(context, chatProvider);
              },
              tooltip: 'Connection Status',
            );
          },
        ),
        PopupMenuButton<String>(
          icon: const Icon(Icons.more_vert_rounded),
          onSelected: (value) {
            switch (value) {
              case 'clear':
                _showClearChatDialog(context);
                break;
              case 'about':
                _showAboutDialog(context);
                break;
            }
          },
          itemBuilder: (context) => [
            const PopupMenuItem(
              value: 'clear',
              child: Row(
                children: [
                  Icon(Icons.clear_all_rounded),
                  SizedBox(width: 12),
                  Text('Clear Chat'),
                ],
              ),
            ),
            const PopupMenuItem(
              value: 'about',
              child: Row(
                children: [
                  Icon(Icons.info_outline_rounded),
                  SizedBox(width: 12),
                  Text('About'),
                ],
              ),
            ),
          ],
        ),
      ],
    );
  }

  void _showConnectionDialog(BuildContext context, ChatProvider chatProvider) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.wifi_rounded),
            SizedBox(width: 12),
            Text('Connection Status'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildStatusRow(
              'Internet',
              chatProvider.connectionStatus.isOnline,
            ),
            const SizedBox(height: 8),
            _buildStatusRow(
              'Backend Server',
              chatProvider.connectionStatus.backendConnected,
            ),
            const SizedBox(height: 16),
            Text(
              chatProvider.connectionStatus.displayMessage,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: chatProvider.isOfflineMode
                    ? AppTheme.warningColor
                    : AppTheme.accentColor,
              ),
            ),
            if (chatProvider.isOfflineMode) ...[
              const SizedBox(height: 8),
              Text(
                'Demo mode is active with mock responses.',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusRow(String label, bool isConnected) {
    return Row(
      children: [
        Icon(
          isConnected ? Icons.check_circle : Icons.error,
          color: isConnected ? AppTheme.accentColor : AppTheme.errorColor,
          size: 20,
        ),
        const SizedBox(width: 8),
        Text(label),
      ],
    );
  }

  void _showClearChatDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear Chat'),
        content: const Text('Are you sure you want to clear all messages?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              context.read<ChatProvider>().clearChat();
              Navigator.of(context).pop();
            },
            child: const Text('Clear'),
          ),
        ],
      ),
    );
  }

  void _showAboutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.smart_toy_rounded),
            SizedBox(width: 12),
            Text('Mobile AgentX'),
          ],
        ),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Mobile-first AI agent platform for smartphone automation.',
              style: TextStyle(fontWeight: FontWeight.w500),
            ),
            SizedBox(height: 16),
            Text('Features:'),
            SizedBox(height: 8),
            Text('• Multi-agent workflow coordination'),
            Text('• Natural language processing'),
            Text('• Cross-app automation'),
            Text('• Real-time execution tracking'),
            SizedBox(height: 16),
            Text('Built for hackathon demo with mock API integration.'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }
}