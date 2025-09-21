/// Suggested commands widget for quick action buttons
/// Shows contextual suggestions based on chat state

import 'package:flutter/material.dart';
import '../models/chat_models.dart';
import '../theme/app_theme.dart';

class SuggestedCommandsWidget extends StatelessWidget {
  final List<SuggestedCommand> commands;
  final Function(SuggestedCommand) onCommandTap;

  const SuggestedCommandsWidget({
    super.key,
    required this.commands,
    required this.onCommandTap,
  });

  @override
  Widget build(BuildContext context) {
    if (commands.isEmpty) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Text(
              'Suggested commands:',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).textTheme.bodySmall?.color?.withOpacity(0.7),
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: commands.map((command) => _buildCommandChip(context, command)).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildCommandChip(BuildContext context, SuggestedCommand command) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => onCommandTap(command),
        borderRadius: BorderRadius.circular(20),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          decoration: BoxDecoration(
            border: Border.all(
              color: _getCategoryColor(command.category).withOpacity(0.3),
              width: 1,
            ),
            borderRadius: BorderRadius.circular(20),
            color: _getCategoryColor(command.category).withOpacity(0.1),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                _getCategoryIcon(command.category),
                size: 16,
                color: _getCategoryColor(command.category),
              ),
              const SizedBox(width: 8),
              Flexible(
                child: Text(
                  command.title,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: _getCategoryColor(command.category),
                    fontWeight: FontWeight.w500,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  IconData _getCategoryIcon(CommandCategory category) {
    switch (category) {
      case CommandCategory.email:
        return Icons.email_rounded;
      case CommandCategory.messaging:
        return Icons.message_rounded;
      case CommandCategory.calendar:
        return Icons.calendar_today_rounded;
      case CommandCategory.automation:
        return Icons.auto_fix_high_rounded;
      case CommandCategory.workflow:
        return Icons.account_tree_rounded;
    }
  }

  Color _getCategoryColor(CommandCategory category) {
    switch (category) {
      case CommandCategory.email:
        return Colors.blue;
      case CommandCategory.messaging:
        return Colors.green;
      case CommandCategory.calendar:
        return Colors.orange;
      case CommandCategory.automation:
        return AppTheme.primaryColor;
      case CommandCategory.workflow:
        return AppTheme.accentColor;
    }
  }
}