import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:glassmorphism/glassmorphism.dart';
import 'package:go_router/go_router.dart';
import '../../theme/app_theme.dart';

class AgentDetailScreen extends StatefulWidget {
  final String agentId;

  const AgentDetailScreen({
    super.key,
    required this.agentId,
  });

  @override
  State<AgentDetailScreen> createState() => _AgentDetailScreenState();
}

class _AgentDetailScreenState extends State<AgentDetailScreen> {
  bool _isAgentEnabled = true;
  
  // Mock agent data - in real app, this would come from a service
  late Map<String, dynamic> _agent;

  @override
  void initState() {
    super.initState();
    _loadAgentData();
  }

  void _loadAgentData() {
    // Mock data - replace with actual service call
    final agents = {
      'whatsapp_agent': {
        'id': 'whatsapp_agent',
        'name': 'WhatsApp Agent',
        'description': 'Automate WhatsApp messaging with intelligent contact detection and smart reply suggestions.',
        'type': 'Communication',
        'status': 'active',
        'lastActivity': '2 mins ago',
        'tasksCompleted': 15,
        'icon': Icons.message,
        'color': const Color(0xFF25D366),
        'features': ['Send Messages', 'Contact Search', 'Smart Reply', 'Auto Detection'],
        'stats': {
          'Messages Sent': 127,
          'Contacts Found': 45,
          'Success Rate': '94%',
          'Avg Response Time': '2.3s',
        },
        'capabilities': [
          'Natural language message composition',
          'Intelligent contact detection',
          'Screen reading with OCR',
          'Automated message sending',
          'Real-time status monitoring',
        ],
      },
      'email_agent': {
        'id': 'email_agent',
        'name': 'Email Assistant',
        'description': 'Compose and send emails with AI-powered content generation and smart templates.',
        'type': 'Productivity',
        'status': 'idle',
        'lastActivity': '1 hour ago',
        'tasksCompleted': 8,
        'icon': Icons.email,
        'color': const Color(0xFFEA4335),
        'features': ['Compose Email', 'Smart Templates', 'Auto Send', 'Recipient Detection'],
        'stats': {
          'Emails Sent': 34,
          'Templates Used': 12,
          'Success Rate': '97%',
          'Avg Compose Time': '1.2s',
        },
        'capabilities': [
          'AI-powered email composition',
          'Smart template suggestions',
          'Recipient auto-detection',
          'Subject line optimization',
          'Automated sending workflows',
        ],
      },
    };

    _agent = agents[widget.agentId] ?? agents['whatsapp_agent']!;
    _isAgentEnabled = _agent['status'] == 'active';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppTheme.backgroundGradient,
        ),
        child: SafeArea(
          child: CustomScrollView(
            slivers: [
              // App Bar
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Row(
                    children: [
                      GestureDetector(
                        onTap: () => context.go('/agents'),
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
                      Expanded(
                        child: Text(
                          'Agent Details',
                          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
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
              ),

              // Agent Header
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  child: GlassmorphicContainer(
                    width: double.infinity,
                    height: null,
                    borderRadius: 20,
                    blur: 20,
                    alignment: Alignment.bottomCenter,
                    border: 2,
                    linearGradient: AppTheme.glassmorphismGradient(opacity: 0.1),
                    borderGradient: AppTheme.glassmorphismBorderGradient(opacity: 0.3),
                    child: Padding(
                      padding: const EdgeInsets.all(24),
                      child: Column(
                        children: [
                          // Agent Icon and Status
                          Row(
                            children: [
                              Container(
                                width: 64,
                                height: 64,
                                decoration: BoxDecoration(
                                  color: _agent['color'].withOpacity(0.2),
                                  borderRadius: BorderRadius.circular(16),
                                  border: Border.all(
                                    color: _agent['color'].withOpacity(0.3),
                                    width: 2,
                                  ),
                                ),
                                child: Icon(
                                  _agent['icon'],
                                  color: _agent['color'],
                                  size: 32,
                                ),
                              ),
                              const SizedBox(width: 16),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      _agent['name'],
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontSize: 20,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      _agent['type'],
                                      style: TextStyle(
                                        color: Colors.white.withOpacity(0.7),
                                        fontSize: 14,
                                      ),
                                    ),
                                    const SizedBox(height: 8),
                                    Container(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 12,
                                        vertical: 6,
                                      ),
                                      decoration: BoxDecoration(
                                        color: _isAgentEnabled 
                                            ? Colors.green.withOpacity(0.2)
                                            : Colors.orange.withOpacity(0.2),
                                        borderRadius: BorderRadius.circular(12),
                                        border: Border.all(
                                          color: _isAgentEnabled 
                                              ? Colors.green.withOpacity(0.3)
                                              : Colors.orange.withOpacity(0.3),
                                          width: 1,
                                        ),
                                      ),
                                      child: Text(
                                        _isAgentEnabled ? 'ACTIVE' : 'INACTIVE',
                                        style: TextStyle(
                                          color: _isAgentEnabled ? Colors.green : Colors.orange,
                                          fontSize: 12,
                                          fontWeight: FontWeight.w600,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              Switch(
                                value: _isAgentEnabled,
                                onChanged: (value) {
                                  setState(() {
                                    _isAgentEnabled = value;
                                  });
                                },
                                activeColor: _agent['color'],
                                trackColor: MaterialStateProperty.all(
                                  Colors.white.withOpacity(0.3),
                                ),
                              ),
                            ],
                          ),
                          
                          const SizedBox(height: 20),
                          
                          // Description
                          Text(
                            _agent['description'],
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.8),
                              fontSize: 14,
                              height: 1.5,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ).animate().slideY(
                  begin: 0.3,
                  delay: 400.ms,
                  duration: 800.ms,
                  curve: Curves.easeOutCubic,
                ),
              ),

              const SliverToBoxAdapter(child: SizedBox(height: 24)),

              // Quick Actions
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  child: Row(
                    children: [
                      Expanded(
                        child: _buildActionButton(
                          'Chat Now',
                          Icons.chat_bubble_outline,
                          AppTheme.primaryGradient,
                          () => context.go('/chat/${widget.agentId}'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _buildActionButton(
                          'Settings',
                          Icons.settings_outlined,
                          AppTheme.accentGradient,
                          () {
                            // TODO: Navigate to agent settings
                          },
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _buildActionButton(
                          'Logs',
                          Icons.history_outlined,
                          const LinearGradient(
                            colors: [Color(0xFFE17055), Color(0xFFFD79A8)],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          () {
                            // TODO: Navigate to agent logs
                          },
                        ),
                      ),
                    ],
                  ),
                ).animate().slideY(
                  begin: 0.3,
                  delay: 600.ms,
                  duration: 800.ms,
                  curve: Curves.easeOutCubic,
                ),
              ),

              const SliverToBoxAdapter(child: SizedBox(height: 32)),

              // Statistics
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Performance Stats',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 16),
                      GridView.builder(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 2,
                          crossAxisSpacing: 16,
                          mainAxisSpacing: 16,
                          childAspectRatio: 1.3,
                        ),
                        itemCount: _agent['stats'].length,
                        itemBuilder: (context, index) {
                          final entry = _agent['stats'].entries.elementAt(index);
                          return _buildStatCard(entry.key, entry.value.toString());
                        },
                      ),
                    ],
                  ),
                ).animate().slideY(
                  begin: 0.3,
                  delay: 800.ms,
                  duration: 800.ms,
                  curve: Curves.easeOutCubic,
                ),
              ),

              const SliverToBoxAdapter(child: SizedBox(height: 32)),

              // Capabilities
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Capabilities',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 16),
                      ...List.generate(
                        _agent['capabilities'].length,
                        (index) => Padding(
                          padding: EdgeInsets.only(
                            bottom: index < _agent['capabilities'].length - 1 ? 12 : 0,
                          ),
                          child: _buildCapabilityItem(_agent['capabilities'][index]),
                        ),
                      ),
                    ],
                  ),
                ).animate().slideY(
                  begin: 0.3,
                  delay: 1000.ms,
                  duration: 800.ms,
                  curve: Curves.easeOutCubic,
                ),
              ),

              const SliverToBoxAdapter(child: SizedBox(height: 100)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildActionButton(
    String title,
    IconData icon,
    Gradient gradient,
    VoidCallback onTap,
  ) {
    return Container(
      height: 56,
      decoration: BoxDecoration(
        gradient: gradient,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: gradient.colors.first.withOpacity(0.3),
            blurRadius: 15,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: onTap,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                color: Colors.white,
                size: 20,
              ),
              const SizedBox(height: 4),
              Text(
                title,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatCard(String title, String value) {
    return GlassmorphicContainer(
      width: double.infinity,
      height: double.infinity,
      borderRadius: 16,
      blur: 20,
      alignment: Alignment.bottomCenter,
      border: 2,
      linearGradient: AppTheme.glassmorphismGradient(opacity: 0.1),
      borderGradient: AppTheme.glassmorphismBorderGradient(opacity: 0.3),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              value,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              title,
              style: TextStyle(
                color: Colors.white.withOpacity(0.7),
                fontSize: 12,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCapabilityItem(String capability) {
    return Row(
      children: [
        Container(
          width: 6,
          height: 6,
          decoration: BoxDecoration(
            color: _agent['color'],
            borderRadius: BorderRadius.circular(3),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            capability,
            style: TextStyle(
              color: Colors.white.withOpacity(0.8),
              fontSize: 14,
              height: 1.5,
            ),
          ),
        ),
      ],
    );
  }
}