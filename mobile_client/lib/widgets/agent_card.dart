import 'package:flutter/material.dart';
import 'package:glassmorphism/glassmorphism.dart';
import '../theme/app_theme.dart';

class AgentCard extends StatelessWidget {
  final Map<String, dynamic> agent;
  final VoidCallback onTap;

  const AgentCard({
    super.key,
    required this.agent,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isActive = agent['status'] == 'active';
    
    return GlassmorphicContainer(
      width: double.infinity,
      height: 100,
      borderRadius: 16,
      blur: 20,
      alignment: Alignment.bottomCenter,
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
                // Agent Icon
                Container(
                  width: 56,
                  height: 56,
                  decoration: BoxDecoration(
                    color: agent['color'].withOpacity(0.2),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(
                      color: agent['color'].withOpacity(0.3),
                      width: 1,
                    ),
                  ),
                  child: Icon(
                    agent['icon'],
                    color: agent['color'],
                    size: 28,
                  ),
                ),
                
                const SizedBox(width: 16),
                
                // Agent Info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              agent['name'],
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 4,
                            ),
                            decoration: BoxDecoration(
                              color: isActive 
                                  ? Colors.green.withOpacity(0.2)
                                  : Colors.orange.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(
                                color: isActive 
                                    ? Colors.green.withOpacity(0.3)
                                    : Colors.orange.withOpacity(0.3),
                                width: 1,
                              ),
                            ),
                            child: Text(
                              agent['status'].toUpperCase(),
                              style: TextStyle(
                                color: isActive ? Colors.green : Colors.orange,
                                fontSize: 10,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        agent['type'],
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.7),
                          fontSize: 14,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Icon(
                            Icons.access_time_rounded,
                            color: Colors.white.withOpacity(0.5),
                            size: 14,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            agent['lastActivity'],
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.5),
                              fontSize: 12,
                            ),
                          ),
                          const SizedBox(width: 16),
                          Icon(
                            Icons.check_circle_outline,
                            color: Colors.white.withOpacity(0.5),
                            size: 14,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            '${agent['tasksCompleted']} tasks',
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.5),
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                
                // Arrow
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
}