import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:liquid_swipe/liquid_swipe.dart';
import '../../theme/app_theme.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final LiquidController _liquidController = LiquidController();
  int _currentPage = 0;

  final List<OnboardingPage> _pages = [
    OnboardingPage(
      icon: Icons.smart_toy_rounded,
      title: 'Meet AgentX',
      subtitle: 'Your AI-Powered Mobile Assistant',
      description: 'Experience the future of mobile automation with intelligent AI agents that understand and execute your commands.',
      gradient: AppTheme.primaryGradient,
    ),
    OnboardingPage(
      icon: Icons.auto_awesome,
      title: 'Intelligent Automation',
      subtitle: 'Smart Screen Understanding',
      description: 'Advanced computer vision and OCR technology to understand your screen content and automate tasks across apps.',
      gradient: AppTheme.accentGradient,
    ),
    OnboardingPage(
      icon: Icons.hub_rounded,
      title: 'Multi-App Control',
      subtitle: 'WhatsApp, Gmail, Maps & More',
      description: 'Control multiple applications seamlessly with natural language commands and smart contact detection.',
      gradient: const LinearGradient(
        colors: [Color(0xFFE17055), Color(0xFFFD79A8)],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      ),
    ),
    OnboardingPage(
      icon: Icons.security,
      title: 'Secure & Private',
      subtitle: 'Your Data, Your Control',
      description: 'Enterprise-grade security with local processing and encrypted communications. Your privacy is our priority.',
      gradient: const LinearGradient(
        colors: [Color(0xFF00B894), Color(0xFF55A3FF)],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      ),
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          LiquidSwipe(
            pages: _pages.map((page) => _buildPage(page)).toList(),
            onPageChangeCallback: (activePageIndex) {
              setState(() {
                _currentPage = activePageIndex;
              });
            },
            waveType: WaveType.liquidReveal,
            liquidController: _liquidController,
            enableSideReveal: true,
            ignoreUserGestureWhileAnimating: true,
          ),
          
          // Skip button
          Positioned(
            top: MediaQuery.of(context).padding.top + 16,
            right: 24,
            child: TextButton(
              onPressed: _finishOnboarding,
              child: Text(
                'Skip',
                style: TextStyle(
                  color: Colors.white.withOpacity(0.8),
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ),
          
          // Page indicator and next button
          Positioned(
            bottom: MediaQuery.of(context).padding.bottom + 40,
            left: 24,
            right: 24,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                // Page indicators
                Row(
                  children: List.generate(
                    _pages.length,
                    (index) => Container(
                      margin: const EdgeInsets.only(right: 8),
                      width: _currentPage == index ? 24 : 8,
                      height: 8,
                      decoration: BoxDecoration(
                        color: _currentPage == index 
                            ? Colors.white 
                            : Colors.white.withOpacity(0.3),
                        borderRadius: BorderRadius.circular(4),
                      ),
                    ).animate().scale(
                      duration: 300.ms,
                      curve: Curves.easeInOut,
                    ),
                  ),
                ),
                
                // Next/Get Started button
                Container(
                  decoration: BoxDecoration(
                    gradient: AppTheme.glassmorphismGradient(opacity: 0.2),
                    borderRadius: BorderRadius.circular(25),
                    border: Border.all(
                      color: Colors.white.withOpacity(0.3),
                      width: 1,
                    ),
                  ),
                  child: Material(
                    color: Colors.transparent,
                    child: InkWell(
                      borderRadius: BorderRadius.circular(25),
                      onTap: _currentPage == _pages.length - 1 
                          ? _finishOnboarding 
                          : _nextPage,
                      child: Padding(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 24,
                          vertical: 16,
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              _currentPage == _pages.length - 1 
                                  ? 'Get Started' 
                                  : 'Next',
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const SizedBox(width: 8),
                            const Icon(
                              Icons.arrow_forward_rounded,
                              color: Colors.white,
                              size: 20,
                            ),
                          ],
                        ),
                      ),
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

  Widget _buildPage(OnboardingPage page) {
    return Container(
      decoration: BoxDecoration(gradient: page.gradient),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Spacer(flex: 2),
              
              // Icon
              Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(30),
                  border: Border.all(
                    color: Colors.white.withOpacity(0.3),
                    width: 2,
                  ),
                ),
                child: Icon(
                  page.icon,
                  size: 60,
                  color: Colors.white,
                ),
              ).animate().scale(
                delay: 300.ms,
                duration: 800.ms,
                curve: Curves.elasticOut,
              ),
              
              const SizedBox(height: 48),
              
              // Title
              Text(
                page.title,
                style: const TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                  letterSpacing: -0.5,
                ),
                textAlign: TextAlign.center,
              ).animate().fadeIn(delay: 600.ms, duration: 800.ms),
              
              const SizedBox(height: 16),
              
              // Subtitle
              Text(
                page.subtitle,
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w500,
                  color: Colors.white.withOpacity(0.9),
                  letterSpacing: 0.5,
                ),
                textAlign: TextAlign.center,
              ).animate().fadeIn(delay: 900.ms, duration: 800.ms),
              
              const SizedBox(height: 32),
              
              // Description
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Text(
                  page.description,
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.white.withOpacity(0.8),
                    height: 1.6,
                  ),
                  textAlign: TextAlign.center,
                ),
              ).animate().fadeIn(delay: 1200.ms, duration: 800.ms),
              
              const Spacer(flex: 3),
            ],
          ),
        ),
      ),
    );
  }

  void _nextPage() {
    _liquidController.animateToPage(page: _currentPage + 1);
  }

  Future<void> _finishOnboarding() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('hasSeenOnboarding', true);
    
    if (mounted) {
      context.go('/login');
    }
  }
}

class OnboardingPage {
  final IconData icon;
  final String title;
  final String subtitle;
  final String description;
  final Gradient gradient;

  OnboardingPage({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.description,
    required this.gradient,
  });
}