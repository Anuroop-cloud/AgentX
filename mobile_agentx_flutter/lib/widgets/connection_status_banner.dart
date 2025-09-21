/// Connection status banner widget
/// Shows offline mode notification

import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class ConnectionStatusBanner extends StatelessWidget {
  const ConnectionStatusBanner({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: AppTheme.warningColor.withOpacity(0.1),
        border: Border(
          bottom: BorderSide(
            color: AppTheme.warningColor.withOpacity(0.2),
            width: 1,
          ),
        ),
      ),
      child: Row(
        children: [
          Icon(
            Icons.wifi_off_rounded,
            color: AppTheme.warningColor,
            size: 16,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              'Demo Mode - Using mock responses',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppTheme.warningColor,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Icon(
            Icons.info_outline_rounded,
            color: AppTheme.warningColor,
            size: 16,
          ),
        ],
      ),
    );
  }
}