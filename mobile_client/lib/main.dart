import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'theme/app_theme.dart';
import 'screens/splash_screen.dart';
import 'screens/onboarding/onboarding_screen.dart';
import 'screens/auth/login_screen.dart';
import 'screens/auth/signup_screen.dart';
import 'screens/home/dashboard_screen.dart';
import 'screens/agents/agent_list_screen.dart';
import 'screens/agents/agent_detail_screen.dart';
import 'screens/chat/chat_screen.dart';
import 'screens/profile/profile_screen.dart';
import 'screens/settings/settings_screen.dart';
import 'services/auth_service.dart';
import 'services/storage_service.dart';

// Global navigation key
final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Hive
  await Hive.initFlutter();
  
  // Initialize Firebase
  try {
    await Firebase.initializeApp();
  } catch (e) {
    debugPrint('Firebase initialization failed: $e');
  }
  
  // Set preferred orientations
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);
  
  // Set system UI overlay style
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
      statusBarBrightness: Brightness.dark,
      systemNavigationBarColor: Colors.transparent,
      systemNavigationBarIconBrightness: Brightness.light,
    ),
  );
  
  runApp(const ProviderScope(child: AgentXApp()));
}

class AgentXApp extends ConsumerStatefulWidget {
  const AgentXApp({super.key});

  @override
  ConsumerState<AgentXApp> createState() => _AgentXAppState();
}

class _AgentXAppState extends ConsumerState<AgentXApp> {
  late final GoRouter _router;
  
  @override
  void initState() {
    super.initState();
    _initializeRouter();
  }
  
  void _initializeRouter() {
    _router = GoRouter(
      navigatorKey: navigatorKey,
      initialLocation: '/splash',
      routes: [
        // Splash Screen
        GoRoute(
          path: '/splash',
          builder: (context, state) => const SplashScreen(),
        ),
        
        // Onboarding
        GoRoute(
          path: '/onboarding',
          builder: (context, state) => const OnboardingScreen(),
        ),
        
        // Authentication
        GoRoute(
          path: '/login',
          builder: (context, state) => const LoginScreen(),
        ),
        GoRoute(
          path: '/signup',
          builder: (context, state) => const SignUpScreen(),
        ),
        
        // Main App
        GoRoute(
          path: '/dashboard',
          builder: (context, state) => const DashboardScreen(),
        ),
        
        // Agents
        GoRoute(
          path: '/agents',
          builder: (context, state) => const AgentListScreen(),
        ),
        GoRoute(
          path: '/agents/:id',
          builder: (context, state) => AgentDetailScreen(
            agentId: state.pathParameters['id']!,
          ),
        ),
        
        // Chat
        GoRoute(
          path: '/chat/:agentId',
          builder: (context, state) => ChatScreen(
            agentId: state.pathParameters['agentId']!,
          ),
        ),
        
        // Profile & Settings
        GoRoute(
          path: '/profile',
          builder: (context, state) => const ProfileScreen(),
        ),
        GoRoute(
          path: '/settings',
          builder: (context, state) => const SettingsScreen(),
        ),
      ],
      redirect: (context, state) async {
        final prefs = await SharedPreferences.getInstance();
        final hasSeenOnboarding = prefs.getBool('hasSeenOnboarding') ?? false;
        final isLoggedIn = prefs.getBool('isLoggedIn') ?? false;
        
        // Handle splash screen
        if (state.fullPath == '/splash') {
          return null; // Allow splash screen
        }
        
        // Redirect to onboarding if not seen
        if (!hasSeenOnboarding && !state.fullPath!.startsWith('/onboarding')) {
          return '/onboarding';
        }
        
        // Redirect to login if not authenticated
        if (hasSeenOnboarding && !isLoggedIn && 
            !state.fullPath!.startsWith('/login') && 
            !state.fullPath!.startsWith('/signup')) {
          return '/login';
        }
        
        // Redirect to dashboard if authenticated and on auth screens
        if (isLoggedIn && (state.fullPath!.startsWith('/login') || 
            state.fullPath!.startsWith('/signup') ||
            state.fullPath!.startsWith('/onboarding'))) {
          return '/dashboard';
        }
        
        return null;
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'AgentX - AI Mobile Assistant',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system,
      routerConfig: _router,
      builder: (context, child) {
        return MediaQuery(
          data: MediaQuery.of(context).copyWith(textScaleFactor: 1.0),
          child: child!,
        );
      },
    );
  }
}
