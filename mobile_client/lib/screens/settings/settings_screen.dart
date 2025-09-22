import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:glassmorphism/glassmorphism.dart';
import 'package:go_router/go_router.dart';
import '../../theme/app_theme.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _notificationsEnabled = true;
  bool _autoExecuteEnabled = false;
  bool _voiceFeedbackEnabled = true;
  bool _darkModeEnabled = true;
  double _automationSpeed = 2.0;
  String _selectedLanguage = 'English';

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
                          'Settings',
                          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ],
                  ),
                ).animate().fadeIn(delay: 200.ms, duration: 800.ms),
              ),

              // General Settings
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'General',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 16),
                      
                      _buildSwitchSetting(
                        'Push Notifications',
                        'Receive notifications about agent activities',
                        Icons.notifications_outlined,
                        _notificationsEnabled,
                        (value) => setState(() => _notificationsEnabled = value),
                      ),
                      
                      const SizedBox(height: 16),
                      
                      _buildSwitchSetting(
                        'Voice Feedback',
                        'Hear audio confirmations during automation',
                        Icons.volume_up_outlined,
                        _voiceFeedbackEnabled,
                        (value) => setState(() => _voiceFeedbackEnabled = value),
                      ),
                      
                      const SizedBox(height: 16),
                      
                      _buildSwitchSetting(
                        'Dark Mode',
                        'Use dark theme throughout the app',
                        Icons.dark_mode_outlined,
                        _darkModeEnabled,
                        (value) => setState(() => _darkModeEnabled = value),
                      ),
                    ],
                  ),
                ).animate().slideY(
                  begin: 0.3,
                  delay: 400.ms,
                  duration: 800.ms,
                  curve: Curves.easeOutCubic,
                ),
              ),

              const SliverToBoxAdapter(child: SizedBox(height: 32)),

              // Automation Settings
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Automation',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 16),
                      
                      _buildSwitchSetting(
                        'Auto Execute',
                        'Automatically execute confirmed actions',
                        Icons.play_circle_outline,
                        _autoExecuteEnabled,
                        (value) => setState(() => _autoExecuteEnabled = value),
                      ),
                      
                      const SizedBox(height: 16),
                      
                      _buildSliderSetting(
                        'Automation Speed',
                        'Control how fast actions are performed',
                        Icons.speed_outlined,
                        _automationSpeed,
                        1.0,
                        5.0,
                        (value) => setState(() => _automationSpeed = value),
                      ),
                      
                      const SizedBox(height: 16),
                      
                      _buildSelectSetting(
                        'Language',
                        'Select your preferred language',
                        Icons.language_outlined,
                        _selectedLanguage,
                        ['English', 'Spanish', 'French', 'German', 'Chinese'],
                        (value) => setState(() => _selectedLanguage = value),
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

              // Advanced Settings
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Advanced',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 16),
                      
                      _buildActionSetting(
                        'Clear Cache',
                        'Free up storage space',
                        Icons.cleaning_services_outlined,
                        () {
                          // TODO: Implement clear cache
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Cache cleared successfully')),
                          );
                        },
                      ),
                      
                      const SizedBox(height: 16),
                      
                      _buildActionSetting(
                        'Export Data',
                        'Download your automation data',
                        Icons.download_outlined,
                        () {
                          // TODO: Implement export data
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Data export started')),
                          );
                        },
                      ),
                      
                      const SizedBox(height: 16),
                      
                      _buildActionSetting(
                        'Reset Settings',
                        'Restore all settings to default',
                        Icons.restore_outlined,
                        () {
                          _showResetDialog();
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

              // About Section
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'About',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 16),
                      
                      _buildInfoSetting(
                        'Version',
                        '1.0.0',
                        Icons.info_outline,
                      ),
                      
                      const SizedBox(height: 16),
                      
                      _buildActionSetting(
                        'Terms of Service',
                        'Read our terms and conditions',
                        Icons.description_outlined,
                        () {
                          // TODO: Show terms of service
                        },
                      ),
                      
                      const SizedBox(height: 16),
                      
                      _buildActionSetting(
                        'Privacy Policy',
                        'Learn about our privacy practices',
                        Icons.privacy_tip_outlined,
                        () {
                          // TODO: Show privacy policy
                        },
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

  Widget _buildSwitchSetting(
    String title,
    String subtitle,
    IconData icon,
    bool value,
    Function(bool) onChanged,
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
            
            Switch(
              value: value,
              onChanged: onChanged,
              activeColor: AppTheme.accentColor,
              trackColor: MaterialStateProperty.all(
                Colors.white.withOpacity(0.3),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSliderSetting(
    String title,
    String subtitle,
    IconData icon,
    double value,
    double min,
    double max,
    Function(double) onChanged,
  ) {
    return GlassmorphicContainer(
      width: double.infinity,
      height: 100,
      borderRadius: 16,
      blur: 20,
      alignment: Alignment.centerLeft,
      border: 2,
      linearGradient: AppTheme.glassmorphismGradient(opacity: 0.1),
      borderGradient: AppTheme.glassmorphismBorderGradient(opacity: 0.3),
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
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        title,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      Text(
                        '${value.toStringAsFixed(1)}x',
                        style: TextStyle(
                          color: AppTheme.accentColor,
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(
                    subtitle,
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.7),
                      fontSize: 12,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Slider(
                    value: value,
                    min: min,
                    max: max,
                    divisions: ((max - min) * 2).toInt(),
                    onChanged: onChanged,
                    activeColor: AppTheme.accentColor,
                    inactiveColor: Colors.white.withOpacity(0.3),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSelectSetting(
    String title,
    String subtitle,
    IconData icon,
    String value,
    List<String> options,
    Function(String) onChanged,
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
          onTap: () => _showSelectDialog(title, options, value, onChanged),
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
                
                Text(
                  value,
                  style: TextStyle(
                    color: AppTheme.accentColor,
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                
                const SizedBox(width: 8),
                
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
    );
  }

  Widget _buildActionSetting(
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
    );
  }

  Widget _buildInfoSetting(
    String title,
    String value,
    IconData icon,
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
              child: Text(
                title,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            
            Text(
              value,
              style: TextStyle(
                color: Colors.white.withOpacity(0.7),
                fontSize: 14,
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showSelectDialog(
    String title,
    List<String> options,
    String currentValue,
    Function(String) onChanged,
  ) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppTheme.surfaceColor,
        title: Text(
          title,
          style: const TextStyle(color: Colors.white),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: options.map((option) => ListTile(
            title: Text(
              option,
              style: const TextStyle(color: Colors.white),
            ),
            leading: Radio<String>(
              value: option,
              groupValue: currentValue,
              onChanged: (value) {
                if (value != null) {
                  onChanged(value);
                  Navigator.of(context).pop();
                }
              },
              activeColor: AppTheme.accentColor,
            ),
          )).toList(),
        ),
      ),
    );
  }

  void _showResetDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppTheme.surfaceColor,
        title: const Text(
          'Reset Settings',
          style: TextStyle(color: Colors.white),
        ),
        content: const Text(
          'Are you sure you want to reset all settings to default? This action cannot be undone.',
          style: TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              // TODO: Implement reset logic
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Settings reset to default')),
              );
            },
            child: const Text(
              'Reset',
              style: TextStyle(color: Colors.red),
            ),
          ),
        ],
      ),
    );
  }
}