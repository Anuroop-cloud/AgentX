/// Workflow timeline widget showing agent execution steps
/// Displays sequential and parallel agent operations with visual indicators

import 'package:flutter/material.dart';
import '../models/chat_models.dart';
import '../theme/app_theme.dart';

class WorkflowTimelineWidget extends StatefulWidget {
  final WorkflowExecution execution;

  const WorkflowTimelineWidget({
    super.key,
    required this.execution,
  });

  @override
  State<WorkflowTimelineWidget> createState() => _WorkflowTimelineWidgetState();
}

class _WorkflowTimelineWidgetState extends State<WorkflowTimelineWidget>
    with TickerProviderStateMixin {
  bool _isExpanded = false;
  late AnimationController _expandController;
  late Animation<double> _expandAnimation;

  @override
  void initState() {
    super.initState();
    _expandController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _expandAnimation = CurvedAnimation(
      parent: _expandController,
      curve: Curves.easeInOut,
    );
  }

  @override
  void dispose() {
    _expandController.dispose();
    super.dispose();
  }

  void _toggleExpanded() {
    setState(() {
      _isExpanded = !_isExpanded;
      if (_isExpanded) {
        _expandController.forward();
      } else {
        _expandController.reverse();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: 8),
      decoration: BoxDecoration(
        color: Theme.of(context).scaffoldBackgroundColor.withOpacity(0.5),
        borderRadius: const BorderRadius.only(
          bottomLeft: Radius.circular(16),
          bottomRight: Radius.circular(16),
        ),
      ),
      child: Column(
        children: [
          // Header with workflow status and expand button
          Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: _toggleExpanded,
              borderRadius: const BorderRadius.only(
                bottomLeft: Radius.circular(16),
                bottomRight: Radius.circular(16),
              ),
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Row(
                  children: [
                    _buildStatusIcon(),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            widget.execution.workflowType,
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            _getStatusText(),
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: _getStatusColor(),
                            ),
                          ),
                        ],
                      ),
                    ),
                    Text(
                      '${widget.execution.completedSteps}/${widget.execution.totalSteps}',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Theme.of(context).textTheme.bodySmall?.color?.withOpacity(0.7),
                      ),
                    ),
                    const SizedBox(width: 8),
                    AnimatedRotation(
                      turns: _isExpanded ? 0.5 : 0.0,
                      duration: const Duration(milliseconds: 300),
                      child: Icon(
                        Icons.keyboard_arrow_down_rounded,
                        color: Theme.of(context).textTheme.bodySmall?.color?.withOpacity(0.7),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          
          // Expandable timeline content
          SizeTransition(
            sizeFactor: _expandAnimation,
            child: Container(
              padding: const EdgeInsets.only(left: 12, right: 12, bottom: 16),
              child: Column(
                children: [
                  const Divider(height: 1),
                  const SizedBox(height: 16),
                  ...widget.execution.steps.asMap().entries.map(
                    (entry) => _buildTimelineStep(entry.key, entry.value),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusIcon() {
    switch (widget.execution.status) {
      case WorkflowStatus.running:
        return SizedBox(
          width: 20,
          height: 20,
          child: CircularProgressIndicator(
            strokeWidth: 2,
            valueColor: AlwaysStoppedAnimation<Color>(AppTheme.accentColor),
          ),
        );
      case WorkflowStatus.completed:
        return Icon(
          Icons.check_circle_rounded,
          color: AppTheme.accentColor,
          size: 20,
        );
      case WorkflowStatus.failed:
        return Icon(
          Icons.error_rounded,
          color: AppTheme.errorColor,
          size: 20,
        );
      case WorkflowStatus.pending:
        return Icon(
          Icons.schedule_rounded,
          color: AppTheme.warningColor,
          size: 20,
        );
    }
  }

  String _getStatusText() {
    switch (widget.execution.status) {
      case WorkflowStatus.running:
        return 'Executing workflow...';
      case WorkflowStatus.completed:
        return 'Workflow completed successfully';
      case WorkflowStatus.failed:
        return 'Workflow failed';
      case WorkflowStatus.pending:
        return 'Workflow pending';
    }
  }

  Color _getStatusColor() {
    switch (widget.execution.status) {
      case WorkflowStatus.running:
        return AppTheme.accentColor;
      case WorkflowStatus.completed:
        return AppTheme.accentColor;
      case WorkflowStatus.failed:
        return AppTheme.errorColor;
      case WorkflowStatus.pending:
        return AppTheme.warningColor;
    }
  }

  Widget _buildTimelineStep(int index, AgentStep step) {
    final isLast = index == widget.execution.steps.length - 1;
    final isParallel = step.executionType == ExecutionType.parallel;
    
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Timeline indicator
        Column(
          children: [
            Container(
              width: 24,
              height: 24,
              decoration: BoxDecoration(
                color: _getStepStatusColor(step.status),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: _getStepStatusColor(step.status).withOpacity(0.3),
                  width: 2,
                ),
              ),
              child: _getStepStatusIcon(step.status),
            ),
            if (!isLast)
              Container(
                width: 2,
                height: 32,
                decoration: BoxDecoration(
                  color: Theme.of(context).dividerColor.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(1),
                ),
              ),
          ],
        ),
        
        const SizedBox(width: 12),
        
        // Step content
        Expanded(
          child: Container(
            padding: const EdgeInsets.only(bottom: 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        step.agentName,
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    if (isParallel)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: AppTheme.accentColor.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          'PARALLEL',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: AppTheme.accentColor,
                            fontSize: 10,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  step.description,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).textTheme.bodySmall?.color?.withOpacity(0.8),
                  ),
                ),
                if (step.duration != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    'Completed in ${step.duration!.inMilliseconds}ms',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Theme.of(context).textTheme.bodySmall?.color?.withOpacity(0.6),
                      fontSize: 11,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ],
    );
  }

  Color _getStepStatusColor(StepStatus status) {
    switch (status) {
      case StepStatus.pending:
        return Theme.of(context).disabledColor;
      case StepStatus.running:
        return AppTheme.accentColor;
      case StepStatus.completed:
        return AppTheme.accentColor;
      case StepStatus.failed:
        return AppTheme.errorColor;
    }
  }

  Widget _getStepStatusIcon(StepStatus status) {
    switch (status) {
      case StepStatus.pending:
        return Icon(
          Icons.schedule_rounded,
          color: Colors.white,
          size: 12,
        );
      case StepStatus.running:
        return SizedBox(
          width: 12,
          height: 12,
          child: CircularProgressIndicator(
            strokeWidth: 2,
            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
          ),
        );
      case StepStatus.completed:
        return Icon(
          Icons.check_rounded,
          color: Colors.white,
          size: 12,
        );
      case StepStatus.failed:
        return Icon(
          Icons.close_rounded,
          color: Colors.white,
          size: 12,
        );
    }
  }
}