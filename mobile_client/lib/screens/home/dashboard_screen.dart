import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:glassmorphism/glassmorphism.dart';
import 'package:go_router/go_router.dart';
import '../../theme/app_theme.dart';
import '../../widgets/agent_card.dart';
import '../../widgets/quick_action_button.dart';
import '../../widgets/stats_card.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _selectedIndex = 0;

  final List<Map<String, dynamic>> _quickActions = [
    {
      'icon': Icons.chat_bubble_outline,
      'title': 'Chat',
      'subtitle': 'Talk to AI',
      'gradient': AppTheme.primaryGradient,
      'route': '/chat/general',
    },
    {
      'icon': Icons.message_outlined,
      'title': 'WhatsApp',
      'subtitle': 'Send Messages',
      'gradient': const LinearGradient(
        colors: [Color(0xFF25D366), Color(0xFF128C7E)],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      ),
      'route': '/chat/whatsapp',
    },
    {
      'icon': Icons.email_outlined,
      'title': 'Gmail',
      'subtitle': 'Compose Email',
      'gradient': const LinearGradient(
        colors: [Color(0xFFEA4335), Color(0xFFFBBC04)],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      ),
      'route': '/chat/gmail',
    },
    {
      'icon': Icons.map_outlined,
      'title': 'Maps',
      'subtitle': 'Navigation',
      'gradient': const LinearGradient(
        colors: [Color(0xFF4285F4), Color(0xFF34A853)],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      ),
      'route': '/chat/maps',
    },
  ];

  final List<Map<String, dynamic>> _activeAgents = [
    {
      'id': 'whatsapp_agent',
      'name': 'WhatsApp Agent',
      'type': 'Communication',
      'status': 'active',
      'lastActivity': '2 mins ago',
      'tasksCompleted': 15,
      'icon': Icons.message,
      'color': const Color(0xFF25D366),
    },
    {
      'id': 'email_agent',
      'name': 'Email Assistant',
      'type': 'Productivity',
      'status': 'idle',
      'lastActivity': '1 hour ago',
      'tasksCompleted': 8,
      'icon': Icons.email,
      'color': const Color(0xFFEA4335),
    },
    {
      'id': 'automation_agent',
      'name': 'Smart Automation',
      'type': 'Automation',
      'status': 'active',
      'lastActivity': '5 mins ago',
      'tasksCompleted': 23,
      'icon': Icons.auto_awesome,
      'color': AppTheme.accentColor,
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppTheme.backgroundGradient,
        ),
        child: SafeArea(
          child: _selectedIndex == 0 ? _buildHomeTab() : _buildOtherTab(),
        ),
      ),
      bottomNavigationBar: _buildBottomNavigationBar(),
    );
  }

  Widget _buildHomeTab() {
    return CustomScrollView(
      slivers: [
        // App Bar
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Row(
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Hello, Agent',
                      style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ).animate().fadeIn(delay: 200.ms, duration: 800.ms),
                    const SizedBox(height: 4),
                    Text(
                      'Ready to automate your world?',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        color: Colors.white70,
                      ),
                    ).animate().fadeIn(delay: 400.ms, duration: 800.ms),
                  ],
                ),
                const Spacer(),
                GestureDetector(
                  onTap: () => context.go('/profile'),
                  child: Container(
                    width: 48,
                    height: 48,
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
                    child: const Icon(
                      Icons.person_outline,
                      color: Colors.white,
                      size: 24,
                    ),
                  ),
                ).animate().scale(delay: 600.ms, duration: 600.ms),
              ],
            ),
          ),
        ),

        // Stats Cards
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Row(
              children: [
                Expanded(
                  child: StatsCard(
                    title: 'Active Agents',
                    value: '3',
                    subtitle: '+2 from yesterday',
                    icon: Icons.smart_toy,
                    gradient: AppTheme.primaryGradient,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: StatsCard(
                    title: 'Tasks Completed',
                    value: '46',
                    subtitle: '+12 today',
                    icon: Icons.check_circle_outline,
                    gradient: AppTheme.accentGradient,
                  ),
                ),
              ],
            ).animate().slideY(
              begin: 0.3,
              delay: 800.ms,
              duration: 800.ms,
              curve: Curves.easeOutCubic,
            ),
          ),
        ),

        const SliverToBoxAdapter(child: SizedBox(height: 32)),

        // Quick Actions
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Quick Actions',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ).animate().fadeIn(delay: 1000.ms, duration: 800.ms),
                const SizedBox(height: 16),
                GridView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    crossAxisSpacing: 16,
                    mainAxisSpacing: 16,
                    childAspectRatio: 1.2,
                  ),
                  itemCount: _quickActions.length,
                  itemBuilder: (context, index) {
                    final action = _quickActions[index];
                    return QuickActionButton(
                      icon: action['icon'],
                      title: action['title'],
                      subtitle: action['subtitle'],
                      gradient: action['gradient'],
                      onTap: () => context.go(action['route']),
                    ).animate().scale(
                      delay: (1200 + index * 100).ms,
                      duration: 600.ms,
                      curve: Curves.easeOutBack,
                    );
                  },
                ),
              ],
            ),
          ),
        ),

        const SliverToBoxAdapter(child: SizedBox(height: 32)),

        // Active Agents
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Active Agents',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    TextButton(
                      onPressed: () => context.go('/agents'),
                      child: Text(
                        'View All',
                        style: TextStyle(
                          color: AppTheme.accentColor,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ],
                ).animate().fadeIn(delay: 1600.ms, duration: 800.ms),
                const SizedBox(height: 16),
                ...List.generate(
                  _activeAgents.length,
                  (index) => Padding(
                    padding: EdgeInsets.only(bottom: index < _activeAgents.length - 1 ? 16 : 0),
                    child: AgentCard(
                      agent: _activeAgents[index],
                      onTap: () => context.go('/agents/${_activeAgents[index]['id']}'),
                    ).animate().slideX(
                      begin: 0.3,
                      delay: (1800 + index * 150).ms,
                      duration: 800.ms,
                      curve: Curves.easeOutCubic,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),

        const SliverToBoxAdapter(child: SizedBox(height: 100)),
      ],
    );
  }

  Widget _buildOtherTab() {
    return Center(
      child: Text(
        'Coming Soon',
        style: Theme.of(context).textTheme.headlineMedium?.copyWith(
          color: Colors.white,
        ),
      ),
    );
  }

  Widget _buildBottomNavigationBar() {
    return Container(
      margin: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(25),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: GlassmorphicContainer(
        width: double.infinity,
        height: 70,
        borderRadius: 25,
        blur: 20,
        alignment: Alignment.center,
        border: 2,
        linearGradient: AppTheme.glassmorphismGradient(opacity: 0.15),
        borderGradient: AppTheme.glassmorphismBorderGradient(opacity: 0.3),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            _buildNavItem(Icons.home_rounded, 'Home', 0),
            _buildNavItem(Icons.smart_toy_rounded, 'Agents', 1),
            _buildNavItem(Icons.chat_bubble_rounded, 'Chat', 2),
            _buildNavItem(Icons.settings_rounded, 'Settings', 3),
          ],
        ),
      ),
    );
  }

  Widget _buildNavItem(IconData icon, String label, int index) {
    final isSelected = _selectedIndex == index;
    return GestureDetector(
      onTap: () {
        setState(() => _selectedIndex = index);
        if (index == 1) context.go('/agents');
        if (index == 2) context.go('/chat/general');
        if (index == 3) context.go('/settings');
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          gradient: isSelected ? AppTheme.primaryGradient : null,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              color: isSelected ? Colors.white : Colors.white70,
              size: 24,
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                color: isSelected ? Colors.white : Colors.white70,
                fontSize: 12,
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
              ),
            ),
          ],
        ),
      ),
    );
  }
}