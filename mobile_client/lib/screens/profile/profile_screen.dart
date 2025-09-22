import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:glassmorphism/glassmorphism.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../theme/app_theme.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  String _userName = 'Agent User';
  String _userEmail = 'agent@agentx.ai';

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  Future<void> _loadUserData() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _userName = prefs.getString('userName') ?? 'Agent User';
      _userEmail = prefs.getString('userEmail') ?? 'agent@agentx.ai';
    });
  }

  Future<void> _logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('isLoggedIn', false);
    await prefs.remove('userName');
    await prefs.remove('userEmail');
    
    if (mounted) {
      context.go('/login');
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
          child: CustomScrollView(
            slivers: [
              // App Bar
              SliverToBoxAdapter(
                child: Padding(
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
                        child: Text(
                          'Profile',
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
                          Icons.edit_outlined,
                          color: Colors.white,
                          size: 20,
                        ),
                      ),
                    ],
                  ),
                ).animate().fadeIn(delay: 200.ms, duration: 800.ms),
              ),

              // Profile Header
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
                          // Avatar
                          Container(
                            width: 80,
                            height: 80,
                            decoration: BoxDecoration(
                              gradient: AppTheme.primaryGradient,
                              borderRadius: BorderRadius.circular(20),
                              boxShadow: [
                                BoxShadow(
                                  color: AppTheme.primaryColor.withOpacity(0.3),
                                  blurRadius: 20,
                                  offset: const Offset(0, 10),
                                ),
                              ],
                            ),
                            child: const Icon(
                              Icons.person_rounded,
                              color: Colors.white,
                              size: 40,
                            ),
                          ),
                          
                          const SizedBox(height: 16),
                          
                          // Name
                          Text(
                            _userName,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          
                          const SizedBox(height: 4),
                          
                          // Email
                          Text(
                            _userEmail,
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.7),
                              fontSize: 16,
                            ),
                          ),
                          
                          const SizedBox(height: 20),
                          
                          // Stats Row
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                            children: [
                              _buildStatItem('Active Agents', '3'),
                              Container(
                                width: 1,
                                height: 40,
                                color: Colors.white.withOpacity(0.2),
                              ),
                              _buildStatItem('Tasks Completed', '46'),
                              Container(
                                width: 1,
                                height: 40,
                                color: Colors.white.withOpacity(0.2),
                              ),
                              _buildStatItem('Days Active', '12'),
                            ],
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

              const SliverToBoxAdapter(child: SizedBox(height: 32)),

              // Menu Items
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  child: Column(
                    children: [
                      _buildMenuItem(
                        'Account Settings',
                        'Manage your account and preferences',
                        Icons.settings_outlined,
                        () => context.go('/settings'),
                      ),
                      
                      const SizedBox(height: 16),
                      
                      _buildMenuItem(
                        'Agent History',
                        'View your automation history',
                        Icons.history_outlined,
                        () {
                          // TODO: Navigate to history
                        },
                      ),
                      
                      const SizedBox(height: 16),
                      
                      _buildMenuItem(
                        'Usage Analytics',
                        'See your usage statistics',
                        Icons.analytics_outlined,
                        () {
                          // TODO: Navigate to analytics
                        },
                      ),
                      
                      const SizedBox(height: 16),
                      
                      _buildMenuItem(
                        'Privacy & Security',
                        'Control your privacy settings',
                        Icons.security_outlined,
                        () {
                          // TODO: Navigate to privacy settings
                        },
                      ),
                      
                      const SizedBox(height: 16),
                      
                      _buildMenuItem(
                        'Help & Support',
                        'Get help and contact support',
                        Icons.help_outline,
                        () {
                          // TODO: Navigate to help
                        },
                      ),
                      
                      const SizedBox(height: 32),
                      
                      // Logout Button
                      Container(
                        width: double.infinity,
                        height: 56,
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [Color(0xFFE74C3C), Color(0xFFC0392B)],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: [
                            BoxShadow(
                              color: const Color(0xFFE74C3C).withOpacity(0.3),
                              blurRadius: 15,
                              offset: const Offset(0, 5),
                            ),
                          ],
                        ),
                        child: Material(
                          color: Colors.transparent,
                          child: InkWell(
                            borderRadius: BorderRadius.circular(16),
                            onTap: _logout,
                            child: const Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(
                                  Icons.logout_rounded,
                                  color: Colors.white,
                                  size: 20,
                                ),
                                SizedBox(width: 8),
                                Text(
                                  'Logout',
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 16,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ).animate().slideY(
                        begin: 0.3,
                        delay: 1000.ms,
                        duration: 800.ms,
                        curve: Curves.easeOutCubic,
                      ),
                    ],
                  ),
                ),
              ),

              const SliverToBoxAdapter(child: SizedBox(height: 100)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            color: Colors.white.withOpacity(0.7),
            fontSize: 12,
          ),
        ),
      ],
    );
  }

  Widget _buildMenuItem(
    String title,
    String subtitle,
    IconData icon,
    VoidCallback onTap,
  ) {
    return GlassmorphicContainer(
      width: double.infinity,
      height: 80,
      borderRadius: 16,
      blur: 20,
      alignment: Alignment.centerLeft,
      border: 2,
      linearGradient: AppTheme.glassmorphismGradient(opacity: 0.1),
      borderGradient: AppTheme.glassmorphismBorderGradient(opacity: 0.3),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: Colors.white.withOpacity(0.2),
                      width: 1,
                    ),
                  ),
                  child: Icon(
                    icon,
                    color: Colors.white,
                    size: 24,
                  ),
                ),
                
                const SizedBox(width: 16),
                
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        title,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        subtitle,
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.7),
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
                
                Icon(
                  Icons.arrow_forward_ios_rounded,
                  color: Colors.white.withOpacity(0.3),
                  size: 16,
                ),
              ],
            ),
          ),
        ),
      ),
    ).animate().slideX(
      begin: 0.3,
      delay: (600 + (_getMenuItemIndex(title) * 100)).ms,
      duration: 800.ms,
      curve: Curves.easeOutCubic,
    );
  }

  int _getMenuItemIndex(String title) {
    const items = [
      'Account Settings',
      'Agent History',
      'Usage Analytics',
      'Privacy & Security',
      'Help & Support',
    ];
    return items.indexOf(title);
  }
}