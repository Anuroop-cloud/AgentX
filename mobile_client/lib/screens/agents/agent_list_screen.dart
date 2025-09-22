import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:glassmorphism/glassmorphism.dart';
import 'package:go_router/go_router.dart';
import '../../theme/app_theme.dart';
import '../../widgets/agent_card.dart';

class AgentListScreen extends StatefulWidget {
  const AgentListScreen({super.key});

  @override
  State<AgentListScreen> createState() => _AgentListScreenState();
}

class _AgentListScreenState extends State<AgentListScreen> with TickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';

  final List<Map<String, dynamic>> _allAgents = [
    {
      'id': 'whatsapp_agent',
      'name': 'WhatsApp Agent',
      'description': 'Automate WhatsApp messaging with intelligent contact detection',
      'type': 'Communication',
      'category': 'active',
      'status': 'active',
      'lastActivity': '2 mins ago',
      'tasksCompleted': 15,
      'icon': Icons.message,
      'color': const Color(0xFF25D366),
      'features': ['Send Messages', 'Contact Search', 'Smart Reply'],
    },
    {
      'id': 'email_agent',
      'name': 'Email Assistant',
      'description': 'Compose and send emails with AI-powered content generation',
      'type': 'Productivity',
      'category': 'active',
      'status': 'idle',
      'lastActivity': '1 hour ago',
      'tasksCompleted': 8,
      'icon': Icons.email,
      'color': const Color(0xFFEA4335),
      'features': ['Compose Email', 'Smart Templates', 'Auto Send'],
    },
    {
      'id': 'automation_agent',
      'name': 'Smart Automation',
      'description': 'Advanced screen automation with computer vision',
      'type': 'Automation',
      'category': 'active',
      'status': 'active',
      'lastActivity': '5 mins ago',
      'tasksCompleted': 23,
      'icon': Icons.auto_awesome,
      'color': AppTheme.accentColor,
      'features': ['Screen Detection', 'OCR Reading', 'Smart Tapping'],
    },
    {
      'id': 'calendar_agent',
      'name': 'Calendar Manager',
      'description': 'Schedule meetings and manage your calendar efficiently',
      'type': 'Productivity',
      'category': 'available',
      'status': 'inactive',
      'lastActivity': 'Never used',
      'tasksCompleted': 0,
      'icon': Icons.calendar_today,
      'color': const Color(0xFF4285F4),
      'features': ['Create Events', 'Schedule Meetings', 'Reminders'],
    },
    {
      'id': 'maps_agent',
      'name': 'Navigation Assistant',
      'description': 'Get directions and navigate with voice commands',
      'type': 'Navigation',
      'category': 'available',
      'status': 'inactive',
      'lastActivity': 'Never used',
      'tasksCompleted': 0,
      'icon': Icons.map,
      'color': const Color(0xFF34A853),
      'features': ['Get Directions', 'Find Places', 'Traffic Updates'],
    },
    {
      'id': 'spotify_agent',
      'name': 'Music Controller',
      'description': 'Control music playback and discover new songs',
      'type': 'Entertainment',
      'category': 'available',
      'status': 'inactive',
      'lastActivity': 'Never used',
      'tasksCompleted': 0,
      'icon': Icons.music_note,
      'color': const Color(0xFF1DB954),
      'features': ['Play Music', 'Create Playlists', 'Discover Songs'],
    },
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  List<Map<String, dynamic>> get _filteredAgents {
    return _allAgents.where((agent) {
      final matchesSearch = _searchQuery.isEmpty ||
          agent['name'].toLowerCase().contains(_searchQuery.toLowerCase()) ||
          agent['type'].toLowerCase().contains(_searchQuery.toLowerCase());
      
      final category = _getSelectedCategory();
      final matchesCategory = category == 'all' || agent['category'] == category;
      
      return matchesSearch && matchesCategory;
    }).toList();
  }

  String _getSelectedCategory() {
    switch (_tabController.index) {
      case 0: return 'all';
      case 1: return 'active';
      case 2: return 'available';
      default: return 'all';
    }
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
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'AI Agents',
                            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                          Text(
                            'Manage your automation assistants',
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: Colors.white70,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        gradient: AppTheme.primaryGradient,
                        borderRadius: BorderRadius.circular(12),
                        boxShadow: [
                          BoxShadow(
                            color: AppTheme.primaryColor.withOpacity(0.3),
                            blurRadius: 15,
                            offset: const Offset(0, 5),
                          ),
                        ],
                      ),
                      child: const Icon(
                        Icons.add_rounded,
                        color: Colors.white,
                        size: 20,
                      ),
                    ),
                  ],
                ),
              ).animate().fadeIn(delay: 200.ms, duration: 800.ms),

              // Search Bar
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: GlassmorphicContainer(
                  width: double.infinity,
                  height: 56,
                  borderRadius: 16,
                  blur: 20,
                  alignment: Alignment.centerLeft,
                  border: 2,
                  linearGradient: AppTheme.glassmorphismGradient(opacity: 0.1),
                  borderGradient: AppTheme.glassmorphismBorderGradient(opacity: 0.3),
                  child: TextField(
                    controller: _searchController,
                    onChanged: (value) {
                      setState(() {
                        _searchQuery = value;
                      });
                    },
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                    ),
                    decoration: InputDecoration(
                      hintText: 'Search agents...',
                      hintStyle: TextStyle(
                        color: Colors.white.withOpacity(0.5),
                        fontSize: 16,
                      ),
                      prefixIcon: Icon(
                        Icons.search_rounded,
                        color: Colors.white.withOpacity(0.7),
                        size: 22,
                      ),
                      suffixIcon: _searchQuery.isNotEmpty
                          ? IconButton(
                              icon: Icon(
                                Icons.clear_rounded,
                                color: Colors.white.withOpacity(0.7),
                                size: 20,
                              ),
                              onPressed: () {
                                _searchController.clear();
                                setState(() {
                                  _searchQuery = '';
                                });
                              },
                            )
                          : null,
                      border: InputBorder.none,
                      enabledBorder: InputBorder.none,
                      focusedBorder: InputBorder.none,
                      contentPadding: EdgeInsets.zero,
                    ),
                  ),
                ),
              ).animate().slideY(
                begin: 0.3,
                delay: 400.ms,
                duration: 800.ms,
                curve: Curves.easeOutCubic,
              ),

              const SizedBox(height: 24),

              // Tab Bar
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: Container(
                  height: 50,
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: Colors.white.withOpacity(0.2),
                      width: 1,
                    ),
                  ),
                  child: TabBar(
                    controller: _tabController,
                    onTap: (_) => setState(() {}),
                    indicator: BoxDecoration(
                      gradient: AppTheme.primaryGradient,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    labelColor: Colors.white,
                    unselectedLabelColor: Colors.white70,
                    labelStyle: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                    unselectedLabelStyle: const TextStyle(
                      fontWeight: FontWeight.w400,
                      fontSize: 14,
                    ),
                    tabs: const [
                      Tab(text: 'All'),
                      Tab(text: 'Active'),
                      Tab(text: 'Available'),
                    ],
                  ),
                ),
              ).animate().slideY(
                begin: 0.3,
                delay: 600.ms,
                duration: 800.ms,
                curve: Curves.easeOutCubic,
              ),

              const SizedBox(height: 24),

              // Agents List
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  child: _filteredAgents.isEmpty
                      ? _buildEmptyState()
                      : ListView.builder(
                          itemCount: _filteredAgents.length,
                          itemBuilder: (context, index) {
                            final agent = _filteredAgents[index];
                            return Padding(
                              padding: EdgeInsets.only(
                                bottom: index < _filteredAgents.length - 1 ? 16 : 100,
                              ),
                              child: AgentCard(
                                agent: agent,
                                onTap: () => context.go('/agents/${agent['id']}'),
                              ).animate().slideX(
                                begin: 0.3,
                                delay: (800 + index * 100).ms,
                                duration: 800.ms,
                                curve: Curves.easeOutCubic,
                              ),
                            );
                          },
                        ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.1),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(
                color: Colors.white.withOpacity(0.2),
                width: 1,
              ),
            ),
            child: Icon(
              Icons.search_off_rounded,
              color: Colors.white.withOpacity(0.5),
              size: 40,
            ),
          ),
          const SizedBox(height: 24),
          Text(
            'No agents found',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Try adjusting your search or filters',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Colors.white70,
            ),
          ),
        ],
      ),
    );
  }
}