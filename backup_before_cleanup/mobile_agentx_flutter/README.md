# Mobile AgentX Flutter Demo

## Overview
This is the Flutter mobile UI for Mobile AgentX - a hackathon-ready mobile automation platform.

## Features
- **Chat Interface**: Natural language commands with chat bubbles
- **Suggested Commands**: Quick action chips for common workflows  
- **Workflow Timeline**: Visual execution logs showing agent coordination
- **Offline Mode**: Mock responses when backend is unavailable
- **Professional Design**: Material 3 theming with smooth animations

## Getting Started

### Prerequisites
- Flutter SDK (3.0+)
- Dart SDK (3.0+)
- Android Studio or VS Code with Flutter extension

### Installation
1. Navigate to the Flutter project directory:
```bash
cd mobile_agentx_flutter
```

2. Get dependencies:
```bash
flutter pub get
```

3. Run the app:
```bash
flutter run
```

### Demo Commands
Try these example commands in the chat:
- "Prepare for my 3 PM meeting"
- "Morning routine setup"  
- "Triage unread messages"
- "Schedule lunch with team"
- "Find nearby coffee shops"

## Architecture

### State Management
- **Provider**: Simple, reactive state management
- **ChatProvider**: Handles messages, workflows, and connection status
- **Mock API Service**: Simulates backend responses for demos

### Key Components
1. **ChatScreen**: Main interface with messages and input
2. **WorkflowTimelineWidget**: Shows agent execution steps
3. **SuggestedCommandsWidget**: Quick action chips
4. **MockApiService**: Offline demo capabilities

### Integration Points
- Backend API calls through `MockApiService`
- Workflow execution simulation with realistic delays
- Connection status monitoring with fallback modes

## File Structure
```
lib/
├── main.dart                 # App entry point
├── models/
│   └── chat_models.dart      # Data models
├── providers/
│   └── chat_provider.dart    # State management
├── screens/
│   └── chat_screen.dart      # Main UI screen
├── services/
│   └── mock_api_service.dart # Backend simulation
├── theme/
│   └── app_theme.dart        # Material 3 styling
└── widgets/
    ├── chat_message_widget.dart
    ├── chat_input_widget.dart
    ├── suggested_commands_widget.dart
    ├── workflow_timeline_widget.dart
    └── connection_status_banner.dart
```

## Hackathon Demo Tips
1. **Start in offline mode** - works without backend
2. **Use suggested commands** - pre-configured workflows
3. **Show workflow timeline** - tap to expand execution details
4. **Highlight parallel execution** - multiple agents working together

## Backend Integration
The Flutter app is designed to integrate with the Python backend in `../mobile-agentx/`:
- REST API calls for workflow execution
- WebSocket connection for real-time updates
- Graceful fallback to mock responses

## Customization
- **Themes**: Modify `app_theme.dart` for different color schemes
- **Commands**: Add new suggestions in `ChatProvider`
- **Workflows**: Extend mock responses in `MockApiService`
- **Animations**: Adjust timing and curves in widget files