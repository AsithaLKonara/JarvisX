/**
 * Push Notification Service for JarvisX Mobile App
 * Handles push notifications for approvals, alerts, and updates
 */

import { Platform, Alert } from 'react-native';
import PushNotification from 'react-native-push-notification';
import PushNotificationIOS from '@react-native-community/push-notification-ios';
import { PermissionsAndroid } from 'react-native';

export interface NotificationData {
  id: string;
  title: string;
  message: string;
  type: 'approval' | 'alert' | 'update' | 'reminder' | 'emergency';
  priority: 'low' | 'normal' | 'high' | 'critical';
  data?: any;
  actions?: NotificationAction[];
  sound?: string;
  badge?: number;
}

export interface NotificationAction {
  id: string;
  title: string;
  destructive?: boolean;
  authenticationRequired?: boolean;
}

export class PushNotificationService {
  private static instance: PushNotificationService;
  private isInitialized: boolean = false;
  private notificationHandlers: Map<string, (data: any) => void> = new Map();

  private constructor() {
    this.initialize();
  }

  public static getInstance(): PushNotificationService {
    if (!PushNotificationService.instance) {
      PushNotificationService.instance = new PushNotificationService();
    }
    return PushNotificationService.instance;
  }

  private async initialize(): Promise<void> {
    try {
      console.log('🔔 Initializing Push Notification Service...');

      // Request permissions
      await this.requestPermissions();

      // Configure push notifications
      this.configurePushNotifications();

      // Setup notification handlers
      this.setupNotificationHandlers();

      this.isInitialized = true;
      console.log('✅ Push Notification Service initialized');

    } catch (error) {
      console.error('❌ Failed to initialize Push Notification Service:', error);
    }
  }

  private async requestPermissions(): Promise<void> {
    if (Platform.OS === 'android') {
      try {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS,
          {
            title: 'JarvisX Notifications',
            message: 'JarvisX needs permission to send you notifications for approvals and alerts.',
            buttonNeutral: 'Ask Me Later',
            buttonNegative: 'Cancel',
            buttonPositive: 'OK',
          }
        );

        if (granted === PermissionsAndroid.RESULTS.GRANTED) {
          console.log('✅ Android notification permission granted');
        } else {
          console.log('❌ Android notification permission denied');
        }
      } catch (error) {
        console.error('❌ Error requesting Android notification permission:', error);
      }
    } else if (Platform.OS === 'ios') {
      // iOS permissions are handled automatically by the library
      console.log('✅ iOS notification permission handled by library');
    }
  }

  private configurePushNotifications(): void {
    PushNotification.configure({
      // Called when token is generated
      onRegister: (token) => {
        console.log('📱 Push notification token:', token);
        // Send token to server for targeting
        this.sendTokenToServer(token.token);
      },

      // Called when a remote or local notification is opened or received
      onNotification: (notification) => {
        console.log('📱 Notification received:', notification);
        this.handleNotification(notification);
      },

      // Called when the user fails to register for remote notifications
      onRegistrationError: (err) => {
        console.error('❌ Push notification registration error:', err);
      },

      // IOS only: Called when the user taps on a notification
      onRemoteNotification: (notification) => {
        console.log('📱 Remote notification tapped:', notification);
        this.handleNotification(notification);
      },

      // Should the initial notification be popped automatically
      popInitialNotification: true,

      // Request permissions on init
      requestPermissions: true,
    });

    // Create default channel for Android
    if (Platform.OS === 'android') {
      PushNotification.createChannel(
        {
          channelId: 'jarvisx-default',
          channelName: 'JarvisX Notifications',
          channelDescription: 'Default notifications from JarvisX',
          playSound: true,
          soundName: 'default',
          importance: 4,
          vibrate: true,
        },
        (created) => console.log(`📱 Channel created: ${created}`)
      );

      PushNotification.createChannel(
        {
          channelId: 'jarvisx-approval',
          channelName: 'JarvisX Approvals',
          channelDescription: 'Approval requests and decisions',
          playSound: true,
          soundName: 'default',
          importance: 5,
          vibrate: true,
        },
        (created) => console.log(`📱 Approval channel created: ${created}`)
      );

      PushNotification.createChannel(
        {
          channelId: 'jarvisx-emergency',
          channelName: 'JarvisX Emergency',
          channelDescription: 'Emergency alerts and critical notifications',
          playSound: true,
          soundName: 'default',
          importance: 5,
          vibrate: true,
        },
        (created) => console.log(`📱 Emergency channel created: ${created}`)
      );
    }
  }

  private setupNotificationHandlers(): void {
    // Handle approval notifications
    this.notificationHandlers.set('approval', (data) => {
      console.log('📋 Handling approval notification:', data);
      // Navigate to approval screen or show approval dialog
    });

    // Handle alert notifications
    this.notificationHandlers.set('alert', (data) => {
      console.log('⚠️ Handling alert notification:', data);
      // Show alert dialog
      Alert.alert(data.title, data.message);
    });

    // Handle update notifications
    this.notificationHandlers.set('update', (data) => {
      console.log('🔄 Handling update notification:', data);
      // Show update available dialog
    });

    // Handle emergency notifications
    this.notificationHandlers.set('emergency', (data) => {
      console.log('🚨 Handling emergency notification:', data);
      // Show emergency alert with high priority
      Alert.alert(
        '🚨 EMERGENCY',
        data.message,
        [
          { text: 'OK', style: 'destructive' }
        ]
      );
    });
  }

  private async sendTokenToServer(token: string): Promise<void> {
    try {
      // Send token to your server for push notification targeting
      const response = await fetch('http://localhost:3000/api/device-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          platform: Platform.OS,
          deviceType: 'mobile',
          timestamp: new Date().toISOString(),
        }),
      });

      if (response.ok) {
        console.log('✅ Device token sent to server');
      } else {
        console.error('❌ Failed to send device token to server');
      }
    } catch (error) {
      console.error('❌ Error sending device token to server:', error);
    }
  }

  private handleNotification(notification: any): void {
    const { type, data } = notification.userInfo || {};
    
    if (type && this.notificationHandlers.has(type)) {
      const handler = this.notificationHandlers.get(type);
      if (handler) {
        handler(data);
      }
    }

    // Handle notification actions
    if (notification.action) {
      this.handleNotificationAction(notification.action, data);
    }
  }

  private handleNotificationAction(action: string, data: any): void {
    console.log('📱 Notification action:', action, data);
    
    switch (action) {
      case 'approve':
        this.handleApprovalAction('approve', data);
        break;
      case 'reject':
        this.handleApprovalAction('reject', data);
        break;
      case 'view':
        this.handleViewAction(data);
        break;
      case 'dismiss':
        this.handleDismissAction(data);
        break;
    }
  }

  private async handleApprovalAction(action: 'approve' | 'reject', data: any): Promise<void> {
    try {
      const response = await fetch('http://localhost:8013/approval/decision', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          requestId: data.requestId,
          decision: action,
          reason: `Mobile ${action}`,
          userId: data.userId,
        }),
      });

      if (response.ok) {
        console.log(`✅ Approval ${action} successful`);
        this.showLocalNotification({
          title: 'Decision Sent',
          message: `Your ${action} decision has been sent to JarvisX`,
          type: 'update',
          priority: 'normal',
        });
      } else {
        console.error(`❌ Failed to ${action} request`);
      }
    } catch (error) {
      console.error(`❌ Error handling approval ${action}:`, error);
    }
  }

  private handleViewAction(data: any): void {
    // Navigate to relevant screen based on data
    console.log('📱 Navigate to view:', data);
  }

  private handleDismissAction(data: any): void {
    // Dismiss notification
    console.log('📱 Dismiss notification:', data);
  }

  public showLocalNotification(notification: NotificationData): void {
    if (!this.isInitialized) {
      console.warn('⚠️ Push Notification Service not initialized');
      return;
    }

    const channelId = this.getChannelId(notification.type);
    
    PushNotification.localNotification({
      id: notification.id,
      title: notification.title,
      message: notification.message,
      channelId,
      priority: notification.priority,
      soundName: notification.sound || 'default',
      badge: notification.badge,
      userInfo: {
        type: notification.type,
        data: notification.data,
      },
      actions: notification.actions?.map(action => action.title) || [],
    });
  }

  public showApprovalNotification(requestId: string, action: string, description: string): void {
    this.showLocalNotification({
      id: `approval_${requestId}`,
      title: 'Approval Required',
      message: `JarvisX wants to: ${description}`,
      type: 'approval',
      priority: 'high',
      data: { requestId, action, description },
      actions: [
        { id: 'approve', title: 'Approve' },
        { id: 'reject', title: 'Reject', destructive: true },
        { id: 'view', title: 'View Details' },
      ],
    });
  }

  public showEmergencyNotification(message: string, data?: any): void {
    this.showLocalNotification({
      id: `emergency_${Date.now()}`,
      title: '🚨 EMERGENCY',
      message,
      type: 'emergency',
      priority: 'critical',
      data,
      sound: 'default',
      badge: 1,
    });
  }

  public showAlertNotification(title: string, message: string, data?: any): void {
    this.showLocalNotification({
      id: `alert_${Date.now()}`,
      title,
      message,
      type: 'alert',
      priority: 'normal',
      data,
    });
  }

  public showUpdateNotification(version: string, data?: any): void {
    this.showLocalNotification({
      id: `update_${Date.now()}`,
      title: 'Update Available',
      message: `JarvisX ${version} is available`,
      type: 'update',
      priority: 'normal',
      data,
    });
  }

  public showReminderNotification(title: string, message: string, data?: any): void {
    this.showLocalNotification({
      id: `reminder_${Date.now()}`,
      title,
      message,
      type: 'reminder',
      priority: 'low',
      data,
    });
  }

  private getChannelId(type: string): string {
    switch (type) {
      case 'approval':
        return 'jarvisx-approval';
      case 'emergency':
        return 'jarvisx-emergency';
      default:
        return 'jarvisx-default';
    }
  }

  public cancelNotification(id: string): void {
    PushNotification.cancelLocalNotifications({ id });
  }

  public cancelAllNotifications(): void {
    PushNotification.cancelAllLocalNotifications();
  }

  public getBadgeCount(): Promise<number> {
    return new Promise((resolve) => {
      PushNotification.getApplicationIconBadgeNumber((badgeCount) => {
        resolve(badgeCount);
      });
    });
  }

  public setBadgeCount(count: number): void {
    PushNotification.setApplicationIconBadgeNumber(count);
  }

  public isInitialized(): boolean {
    return this.isInitialized;
  }
}

export default PushNotificationService;
