/**
 * Floating chat widget component for mobile
 */
import React, { useState } from 'react'
import {
  View,
  Text,
  TouchableOpacity,
  Modal,
  StyleSheet,
  Dimensions,
  Animated,
} from 'react-native'
import GlassView from '../ui/GlassView'
import ChatContainer from './ChatContainer'

const { width, height } = Dimensions.get('window')

export default function ChatWidget() {
  const [isExpanded, setIsExpanded] = useState(false)
  const [scaleAnim] = useState(new Animated.Value(1))
  
  const toggleWidget = () => {
    setIsExpanded(!isExpanded)
    Animated.spring(scaleAnim, {
      toValue: isExpanded ? 1 : 0.95,
      useNativeDriver: true,
    }).start()
  }
  
  if (!isExpanded) {
    // Minimized widget button
    return (
      <TouchableOpacity
        style={styles.minimizedWidget}
        onPress={toggleWidget}
        activeOpacity={0.8}
      >
        <GlassView variant="button" style={styles.widgetButton}>
          <Text style={styles.widgetIcon}>💬</Text>
        </GlassView>
      </TouchableOpacity>
    )
  }
  
  // Expanded widget
  return (
    <Modal
      visible={isExpanded}
      transparent
      animationType="fade"
      onRequestClose={toggleWidget}
    >
      <View style={styles.widgetOverlay}>
        <Animated.View
          style={[
            styles.widgetContainer,
            { transform: [{ scale: scaleAnim }] },
          ]}
        >
          <GlassView variant="panel" style={styles.widgetContent}>
            <View style={styles.widgetHeader}>
              <Text style={styles.widgetTitle}>JarvisX</Text>
              <TouchableOpacity onPress={toggleWidget}>
                <Text style={styles.closeButton}>✕</Text>
              </TouchableOpacity>
            </View>
            <ChatContainer />
          </GlassView>
        </Animated.View>
      </View>
    </Modal>
  )
}

const styles = StyleSheet.create({
  minimizedWidget: {
    position: 'absolute',
    bottom: 20,
    right: 20,
    zIndex: 1000,
  },
  widgetButton: {
    width: 60,
    height: 60,
    borderRadius: 30,
  },
  widgetIcon: {
    fontSize: 24,
  },
  widgetOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  widgetContainer: {
    width: width * 0.9,
    maxWidth: 400,
    height: height * 0.8,
    maxHeight: 600,
  },
  widgetContent: {
    flex: 1,
    padding: 16,
  },
  widgetHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  widgetTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  closeButton: {
    fontSize: 24,
    color: '#FFFFFF',
  },
})

