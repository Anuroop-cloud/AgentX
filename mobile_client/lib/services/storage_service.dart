import 'package:hive_flutter/hive_flutter.dart';
import 'package:shared_preferences/shared_preferences.dart';

class StorageService {
  static const String _boxName = 'agentx_data';
  static Box? _box;

  // Initialize storage
  static Future<void> init() async {
    await Hive.initFlutter();
    _box = await Hive.openBox(_boxName);
  }

  // Shared Preferences methods
  static Future<void> setBool(String key, bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(key, value);
  }

  static Future<bool?> getBool(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(key);
  }

  static Future<void> setString(String key, String value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(key, value);
  }

  static Future<String?> getString(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(key);
  }

  static Future<void> setInt(String key, int value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(key, value);
  }

  static Future<int?> getInt(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt(key);
  }

  static Future<void> remove(String key) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(key);
  }

  // Hive methods for complex data
  static Future<void> storeData(String key, dynamic value) async {
    await _box?.put(key, value);
  }

  static T? getData<T>(String key) {
    return _box?.get(key) as T?;
  }

  static Future<void> removeData(String key) async {
    await _box?.delete(key);
  }

  static Future<void> clearAll() async {
    await _box?.clear();
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }

  // Agent-specific storage
  static Future<void> saveAgentConfig(String agentId, Map<String, dynamic> config) async {
    await storeData('agent_config_$agentId', config);
  }

  static Map<String, dynamic>? getAgentConfig(String agentId) {
    return getData<Map<String, dynamic>>('agent_config_$agentId');
  }

  // Chat history storage
  static Future<void> saveChatHistory(String agentId, List<Map<String, dynamic>> messages) async {
    await storeData('chat_history_$agentId', messages);
  }

  static List<Map<String, dynamic>>? getChatHistory(String agentId) {
    final data = getData<List<dynamic>>('chat_history_$agentId');
    return data?.map((e) => e as Map<String, dynamic>).toList();
  }

  // User preferences
  static Future<void> saveUserPreferences(Map<String, dynamic> preferences) async {
    await storeData('user_preferences', preferences);
  }

  static Map<String, dynamic>? getUserPreferences() {
    return getData<Map<String, dynamic>>('user_preferences');
  }
}