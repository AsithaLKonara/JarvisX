/**
 * JarvisX Mobile Settings Screen
 * App configuration and preferences
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Switch,
  Alert,
} from 'react-native';
import { Settings, Bell, Shield, Wifi, User, LogOut } from 'lucide-react-native';

export default function SettingsScreen() {
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [autoTradingEnabled, setAutoTradingEnabled] = useState(false);
  const [voiceCommandsEnabled, setVoiceCommandsEnabled] = useState(true);

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Logout', style: 'destructive', onPress: () => {
          // Logout logic
          console.log('Logging out...');
        }}
      ]
    );
  };

  const handleClearCache = () => {
    Alert.alert(
      'Clear Cache',
      'This will clear all cached data. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Clear', style: 'destructive', onPress: () => {
          // Clear cache logic
          console.log('Cache cleared');
        }}
      ]
    );
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <View style={styles.header}>
        <Settings size={24} color="#6366f1" />
        <Text style={styles.headerTitle}>Settings</Text>
      </View>

      {/* Notifications */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Notifications</Text>
        <View style={styles.settingItem}>
          <View style={styles.settingLeft}>
            <Bell size={20} color="#9CA3AF" />
            <Text style={styles.settingText}>Push Notifications</Text>
          </View>
          <Switch
            value={notificationsEnabled}
            onValueChange={setNotificationsEnabled}
            trackColor={{ false: '#374151', true: '#6366f1' }}
            thumbColor={notificationsEnabled ? '#FFFFFF' : '#9CA3AF'}
          />
        </View>
      </View>

      {/* Trading */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Trading</Text>
        <View style={styles.settingItem}>
          <View style={styles.settingLeft}>
            <Shield size={20} color="#9CA3AF" />
            <Text style={styles.settingText}>Auto Trading</Text>
          </View>
          <Switch
            value={autoTradingEnabled}
            onValueChange={setAutoTradingEnabled}
            trackColor={{ false: '#374151', true: '#6366f1' }}
            thumbColor={autoTradingEnabled ? '#FFFFFF' : '#9CA3AF'}
          />
        </View>
      </View>

      {/* Voice */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Voice Control</Text>
        <View style={styles.settingItem}>
          <View style={styles.settingLeft}>
            <Bell size={20} color="#9CA3AF" />
            <Text style={styles.settingText}>Voice Commands</Text>
          </View>
          <Switch
            value={voiceCommandsEnabled}
            onValueChange={setVoiceCommandsEnabled}
            trackColor={{ false: '#374151', true: '#6366f1' }}
            thumbColor={voiceCommandsEnabled ? '#FFFFFF' : '#9CA3AF'}
          />
        </View>
      </View>

      {/* Connection */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Connection</Text>
        <TouchableOpacity style={styles.settingButton}>
          <Wifi size={20} color="#9CA3AF" />
          <Text style={styles.settingButtonText}>WiFi Settings</Text>
        </TouchableOpacity>
      </View>

      {/* Account */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Account</Text>
        <TouchableOpacity style={styles.settingButton}>
          <User size={20} color="#9CA3AF" />
          <Text style={styles.settingButtonText}>Profile Settings</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.settingButton} onPress={handleClearCache}>
          <Settings size={20} color="#9CA3AF" />
          <Text style={styles.settingButtonText}>Clear Cache</Text>
        </TouchableOpacity>
      </View>

      {/* Logout */}
      <View style={styles.section}>
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <LogOut size={20} color="#EF4444" />
          <Text style={styles.logoutButtonText}>Logout</Text>
        </TouchableOpacity>
      </View>

      {/* App Info */}
      <View style={styles.section}>
        <Text style={styles.appInfo}>
          JarvisX Mobile v1.0.0
        </Text>
        <Text style={styles.appInfo}>
          © 2025 JarvisX. All rights reserved.
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#111827',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    paddingTop: 10,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginLeft: 12,
  },
  section: {
    paddingHorizontal: 20,
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
    marginBottom: 12,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#1F2937',
    padding: 16,
    borderRadius: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#374151',
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  settingText: {
    color: '#FFFFFF',
    fontSize: 16,
    marginLeft: 12,
  },
  settingButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1F2937',
    padding: 16,
    borderRadius: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#374151',
  },
  settingButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    marginLeft: 12,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1F2937',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#EF4444',
  },
  logoutButtonText: {
    color: '#EF4444',
    fontSize: 16,
    marginLeft: 12,
    fontWeight: '600',
  },
  appInfo: {
    color: '#9CA3AF',
    fontSize: 12,
    textAlign: 'center',
    marginBottom: 4,
  },
});
