/// Mock API service for Mobile AgentX
/// Simulates backend responses for offline/demo mode

import 'dart:async';
import 'dart:math';
import '../models/chat_models.dart';

class MockApiService {
  static const Duration _responseDelay = Duration(milliseconds: 800);
  static const Duration _stepDelay = Duration(milliseconds: 600);
  
  /// Simulate processing a user command and return workflow execution
  static Future<WorkflowExecution> processCommand(String command) async {
    await Future.delayed(_responseDelay);
    
    // Determine workflow type based on command
    final workflowData = _getWorkflowForCommand(command);
    
    // Create workflow execution
    final workflow = WorkflowExecution(
      id: _generateId(),
      name: workflowData['name'],
      description: workflowData['description'],
      type: workflowData['type'],
      steps: workflowData['steps'],
      startTime: DateTime.now(),
      status: WorkflowStatus.running,
    );
    
    return workflow;
  }
  
  /// Simulate step-by-step execution of workflow
  static Stream<WorkflowExecution> executeWorkflow(WorkflowExecution workflow) async* {
    var currentWorkflow = workflow;
    
    if (workflow.type == WorkflowType.parallel) {
      // Parallel execution - all steps start simultaneously
      final updatedSteps = workflow.steps.map((step) => 
        step.copyWith(status: StepStatus.running)
      ).toList();
      
      currentWorkflow = workflow.copyWith(steps: updatedSteps);
      yield currentWorkflow;
      
      // Complete all steps with slight delays
      for (int i = 0; i < workflow.steps.length; i++) {
        await Future.delayed(Duration(milliseconds: 400 + Random().nextInt(800)));
        
        final completedStep = updatedSteps[i].copyWith(
          status: StepStatus.completed,
          endTime: DateTime.now(),
          result: _getStepResult(updatedSteps[i].agentName),
        );
        
        updatedSteps[i] = completedStep;
        currentWorkflow = currentWorkflow.copyWith(steps: List.from(updatedSteps));
        yield currentWorkflow;
      }
    } else {
      // Sequential execution - one step at a time
      final updatedSteps = List<AgentStep>.from(workflow.steps);
      
      for (int i = 0; i < updatedSteps.length; i++) {
        // Start current step
        updatedSteps[i] = updatedSteps[i].copyWith(status: StepStatus.running);
        currentWorkflow = currentWorkflow.copyWith(steps: List.from(updatedSteps));
        yield currentWorkflow;
        
        await Future.delayed(_stepDelay);
        
        // Complete current step
        updatedSteps[i] = updatedSteps[i].copyWith(
          status: StepStatus.completed,
          endTime: DateTime.now(),
          result: _getStepResult(updatedSteps[i].agentName),
        );
        
        currentWorkflow = currentWorkflow.copyWith(steps: List.from(updatedSteps));
        yield currentWorkflow;
      }
    }
    
    // Mark workflow as completed
    yield currentWorkflow.copyWith(
      status: WorkflowStatus.completed,
      endTime: DateTime.now(),
    );
  }
  
  /// Get workflow configuration based on user command
  static Map<String, dynamic> _getWorkflowForCommand(String command) {
    final commandLower = command.toLowerCase();
    
    if (commandLower.contains('meeting') || commandLower.contains('prepare')) {
      return {
        'name': 'Meeting Preparation',
        'description': 'Coordinating across apps to prepare for your meeting',
        'type': WorkflowType.sequential,
        'steps': [
          AgentStep(
            id: _generateId(),
            agentName: 'mobile_calendar_agent',
            description: 'Checking calendar for meeting details',
            startTime: DateTime.now(),
          ),
          AgentStep(
            id: _generateId(),
            agentName: 'mobile_gmail_agent', 
            description: 'Finding relevant emails with attendees',
            startTime: DateTime.now(),
          ),
          AgentStep(
            id: _generateId(),
            agentName: 'mobile_maps_agent',
            description: 'Getting directions and traffic info',
            startTime: DateTime.now(),
          ),
          AgentStep(
            id: _generateId(),
            agentName: 'mobile_whatsapp_agent',
            description: 'Sending timing updates to team',
            startTime: DateTime.now(),
          ),
          AgentStep(
            id: _generateId(),
            agentName: 'mobile_summary_agent',
            description: 'Creating meeting preparation summary',
            startTime: DateTime.now(),
          ),
        ],
      };
    } else if (commandLower.contains('morning') || commandLower.contains('day')) {
      return {
        'name': 'Morning Routine',
        'description': 'Gathering information across apps simultaneously',
        'type': WorkflowType.parallel,
        'steps': [
          AgentStep(
            id: _generateId(),
            agentName: 'mobile_calendar_agent',
            description: 'Checking today\'s schedule',
            startTime: DateTime.now(),
          ),
          AgentStep(
            id: _generateId(),
            agentName: 'mobile_gmail_agent',
            description: 'Reviewing overnight emails',
            startTime: DateTime.now(),
          ),
          AgentStep(
            id: _generateId(),
            agentName: 'mobile_whatsapp_agent',
            description: 'Checking personal messages',
            startTime: DateTime.now(),
          ),
          AgentStep(
            id: _generateId(),
            agentName: 'mobile_summary_agent',
            description: 'Creating daily briefing',
            startTime: DateTime.now(),
          ),
        ],
      };
    } else if (commandLower.contains('message') || commandLower.contains('triage')) {
      return {
        'name': 'Communication Triage',
        'description': 'Analyzing and prioritizing all communications',
        'type': WorkflowType.sequential,
        'steps': [
          AgentStep(
            id: _generateId(),
            agentName: 'mobile_gmail_agent',
            description: 'Analyzing recent emails for urgency',
            startTime: DateTime.now(),
          ),
          AgentStep(
            id: _generateId(),
            agentName: 'mobile_whatsapp_agent',
            description: 'Reviewing WhatsApp conversations',
            startTime: DateTime.now(),
          ),
          AgentStep(
            id: _generateId(),
            agentName: 'mobile_summary_agent',
            description: 'Creating priority matrix with responses',
            startTime: DateTime.now(),
          ),
        ],
      };
    } else {
      // Default workflow
      return {
        'name': 'Smart Assistant',
        'description': 'Processing your request intelligently',
        'type': WorkflowType.sequential,
        'steps': [
          AgentStep(
            id: _generateId(),
            agentName: 'mobile_summary_agent',
            description: 'Understanding your request',
            startTime: DateTime.now(),
          ),
          AgentStep(
            id: _generateId(),
            agentName: 'mobile_gmail_agent',
            description: 'Checking relevant information',
            startTime: DateTime.now(),
          ),
        ],
      };
    }
  }
  
  /// Get mock result for completed agent step
  static String _getStepResult(String agentName) {
    switch (agentName.toLowerCase()) {
      case 'mobile_calendar_agent':
        return 'Found meeting: Client Call at 3:00 PM in Conference Room A';
      case 'mobile_gmail_agent':
        return 'Found 3 relevant emails with client correspondence';
      case 'mobile_maps_agent':
        return '12 minutes drive, light traffic conditions';
      case 'mobile_whatsapp_agent':
        return 'Sent updates to 2 team members about timing';
      case 'mobile_summary_agent':
        return 'Created comprehensive brief with key talking points';
      case 'mobile_spotify_agent':
        return 'Queued focus playlist for productivity';
      default:
        return 'Task completed successfully';
    }
  }
  
  /// Generate random ID
  static String _generateId() {
    return DateTime.now().millisecondsSinceEpoch.toString() + 
           Random().nextInt(1000).toString();
  }
  
  /// Get suggested commands for quick access
  static List<SuggestedCommand> getSuggestedCommands() {
    return [
      const SuggestedCommand(
        id: '1',
        title: 'Meeting Prep',
        command: 'Prepare for my 3 PM client meeting',
        description: 'Get ready for upcoming meetings',
        icon: '📅',
        category: 'Productivity',
      ),
      const SuggestedCommand(
        id: '2',
        title: 'Morning Routine',
        command: 'Plan my productive morning',
        description: 'Daily briefing and schedule',
        icon: '🌅',
        category: 'Daily',
      ),
      const SuggestedCommand(
        id: '3',
        title: 'Triage Messages',
        command: 'Summarize and prioritize my messages',
        description: 'Organize communications',
        icon: '💬',
        category: 'Communication',
      ),
      const SuggestedCommand(
        id: '4',
        title: 'Smart Scheduling',
        command: 'Find time for a 1-hour meeting tomorrow',
        description: 'Intelligent calendar management',
        icon: '🗓️',
        category: 'Scheduling',
      ),
      const SuggestedCommand(
        id: '5',
        title: 'Travel Update',
        command: 'Check traffic to downtown office',
        description: 'Navigation and travel planning',
        icon: '🚗',
        category: 'Travel',
      ),
      const SuggestedCommand(
        id: '6',
        title: 'Focus Mode',
        command: 'Set up focus environment for deep work',
        description: 'Productivity optimization',
        icon: '🎯',
        category: 'Productivity',
      ),
    ];
  }
  
  /// Simulate connection status check
  static Future<ConnectionStatus> checkConnection() async {
    await Future.delayed(const Duration(milliseconds: 200));
    
    // Simulate offline mode for demo
    return ConnectionStatus(
      isOnline: true,
      backendConnected: false, // Always false for demo
      lastSync: DateTime.now(),
    );
  }
}