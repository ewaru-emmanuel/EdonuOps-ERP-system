import { useEffect, useState } from 'react';
import { useAuth } from '../../../App';

export const useWebSocket = (channel, callback) => {
  const { apiClient } = useAuth();
  const [lastMessage, setLastMessage] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('Disconnected');

  useEffect(() => {
    // For now, we'll mock the WebSocket functionality
    // In a real implementation, this would connect to an actual WebSocket
    setConnectionStatus('Connected');

    // Simulate receiving messages periodically (for testing)
    const interval = setInterval(() => {
      const mockMessage = {
        data: JSON.stringify({
          type: 'heartbeat',
          timestamp: new Date().toISOString(),
          channel: channel
        })
      };
      setLastMessage(mockMessage);
      
      if (callback) {
        try {
          const parsedData = JSON.parse(mockMessage.data);
          callback(parsedData);
        } catch (e) {
          console.warn('Failed to parse WebSocket message:', e);
        }
      }
    }, 30000); // Send heartbeat every 30 seconds

    // Connect to WebSocket if available
    let socket;
    try {
      socket = apiClient.connectWebSocket?.(channel, (data) => {
        const message = { data: JSON.stringify(data) };
        setLastMessage(message);
        if (callback) callback(data);
      });
    } catch (error) {
      console.warn('WebSocket connection failed, using mock mode:', error);
    }

    // Cleanup function
    return () => {
      clearInterval(interval);
      if (socket && typeof socket.close === 'function') {
        socket.close();
      }
      setConnectionStatus('Disconnected');
    };
  }, [channel, callback, apiClient]);

  return {
    lastMessage,
    connectionStatus,
    sendMessage: (message) => {
      // In a real implementation, this would send the message through the WebSocket
    }
  };
};
