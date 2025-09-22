import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class GradientBackground extends StatelessWidget {
  final Widget child;

  const GradientBackground({
    super.key,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            AppTheme.backgroundGradientStart,
            AppTheme.backgroundGradientMiddle,
            AppTheme.backgroundGradientEnd,
          ],
          stops: const [0.0, 0.5, 1.0],
        ),
      ),
      child: Container(
        decoration: BoxDecoration(
          // Add subtle noise/texture overlay
          image: DecorationImage(
            image: const AssetImage('assets/images/noise_texture.png'),
            fit: BoxFit.cover,
            opacity: 0.03,
            colorFilter: ColorFilter.mode(
              Colors.white.withOpacity(0.03),
              BlendMode.overlay,
            ),
          ),
        ),
        child: child,
      ),
    );
  }
}

class AnimatedGradientBackground extends StatefulWidget {
  final Widget child;

  const AnimatedGradientBackground({
    super.key,
    required this.child,
  });

  @override
  State<AnimatedGradientBackground> createState() => _AnimatedGradientBackgroundState();
}

class _AnimatedGradientBackgroundState extends State<AnimatedGradientBackground>
    with TickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(seconds: 8),
      vsync: this,
    );
    _animation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
    _controller.repeat(reverse: true);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Color.lerp(
                  AppTheme.backgroundGradientStart,
                  AppTheme.backgroundGradientStart.withOpacity(0.8),
                  _animation.value,
                )!,
                Color.lerp(
                  AppTheme.backgroundGradientMiddle,
                  AppTheme.backgroundGradientMiddle.withOpacity(0.9),
                  _animation.value,
                )!,
                Color.lerp(
                  AppTheme.backgroundGradientEnd,
                  AppTheme.backgroundGradientEnd.withOpacity(0.7),
                  _animation.value,
                )!,
              ],
              stops: const [0.0, 0.5, 1.0],
            ),
          ),
          child: widget.child,
        );
      },
    );
  }
}