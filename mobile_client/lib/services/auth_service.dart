import 'package:flutter/foundation.dart';

class AuthService extends ChangeNotifier {
  bool _isAuthenticated = false;
  String? _userEmail;
  String? _userName;

  bool get isAuthenticated => _isAuthenticated;
  String? get userEmail => _userEmail;
  String? get userName => _userName;

  Future<bool> signIn(String email, String password) async {
    try {
      // Simulate API call
      await Future.delayed(const Duration(seconds: 2));
      
      // For demo purposes, accept any valid email/password
      if (email.isNotEmpty && password.length >= 6) {
        _isAuthenticated = true;
        _userEmail = email;
        _userName = email.split('@')[0]; // Simple name extraction
        notifyListeners();
        return true;
      }
      
      return false;
    } catch (e) {
      debugPrint('Sign in error: $e');
      return false;
    }
  }

  Future<bool> signUp(String name, String email, String password) async {
    try {
      // Simulate API call
      await Future.delayed(const Duration(seconds: 2));
      
      // For demo purposes, accept any valid input
      if (name.isNotEmpty && email.isNotEmpty && password.length >= 8) {
        _isAuthenticated = true;
        _userEmail = email;
        _userName = name;
        notifyListeners();
        return true;
      }
      
      return false;
    } catch (e) {
      debugPrint('Sign up error: $e');
      return false;
    }
  }

  Future<void> signOut() async {
    _isAuthenticated = false;
    _userEmail = null;
    _userName = null;
    notifyListeners();
  }

  Future<bool> resetPassword(String email) async {
    try {
      // Simulate API call
      await Future.delayed(const Duration(seconds: 1));
      return true;
    } catch (e) {
      debugPrint('Reset password error: $e');
      return false;
    }
  }
}