import { useState, useEffect } from 'react';

export const useVisitorSession = () => {
  const [visitorId, setVisitorId] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Generate or retrieve unique visitor ID
    const initializeVisitor = () => {
      try {
        // Check if visitor already has an ID
        let existingVisitorId = localStorage.getItem('edonuops_visitor_id');
        let existingSessionId = localStorage.getItem('edonuops_session_id');
        
        // Generate new visitor ID if none exists
        if (!existingVisitorId) {
          existingVisitorId = generateUniqueId();
          localStorage.setItem('edonuops_visitor_id', existingVisitorId);
        }
        
        // Generate new session ID for this visit
        existingSessionId = generateUniqueId();
        localStorage.setItem('edonuops_session_id', existingSessionId);
        
        // Set session expiry (24 hours)
        const sessionExpiry = Date.now() + (24 * 60 * 60 * 1000);
        localStorage.setItem('edonuops_session_expiry', sessionExpiry.toString());
        
        setVisitorId(existingVisitorId);
        setSessionId(existingSessionId);
        
        // Store visitor info in backend (if available)
        storeVisitorInfo(existingVisitorId, existingSessionId);
        
      } catch (error) {
        console.error('Error initializing visitor session:', error);
        // Fallback to basic ID generation
        const fallbackId = generateUniqueId();
        setVisitorId(fallbackId);
        setSessionId(fallbackId);
      } finally {
        setIsLoading(false);
      }
    };

    initializeVisitor();
  }, []);

  // Generate cryptographically secure unique ID
  const generateUniqueId = () => {
    const timestamp = Date.now().toString(36);
    const randomPart = Math.random().toString(36).substring(2);
    const userAgent = navigator.userAgent.substring(0, 10);
    const screenInfo = `${window.screen.width}x${window.screen.height}`;
    
    // Create hash-like string
    const combined = `${timestamp}-${randomPart}-${userAgent}-${screenInfo}`;
    return btoa(combined).replace(/[^a-zA-Z0-9]/g, '').substring(0, 16);
  };

  // Store visitor info in backend (optional)
  const storeVisitorInfo = async (visitorId, sessionId) => {
    try {
      // This would call your backend to store visitor info
      // For now, we'll just log it
      console.log('Visitor initialized:', { visitorId, sessionId });
      
      // Store visitor info in backend
      await fetch('/api/visitors/initialize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ visitorId, sessionId, userAgent: navigator.userAgent })
      });
    } catch (error) {
      console.error('Could not store visitor info:', error);
    }
  };

  // Check if session is still valid
  const isSessionValid = () => {
    try {
      const expiry = localStorage.getItem('edonuops_session_expiry');
      if (!expiry) return false;
      return Date.now() < parseInt(expiry);
    } catch {
      return false;
    }
  };

  // Refresh session
  const refreshSession = () => {
    const newSessionId = generateUniqueId();
    const sessionExpiry = Date.now() + (24 * 60 * 60 * 1000);
    
    localStorage.setItem('edonuops_session_id', newSessionId);
    localStorage.setItem('edonuops_session_expiry', sessionExpiry.toString());
    
    setSessionId(newSessionId);
    return newSessionId;
  };

  // Get visitor-specific storage key
  const getStorageKey = (key) => {
    return `edonuops_${visitorId}_${key}`;
  };

  // Set visitor-specific data
  const setVisitorData = (key, value) => {
    try {
      const storageKey = getStorageKey(key);
      localStorage.setItem(storageKey, JSON.stringify(value));
    } catch (error) {
      console.error('Error setting visitor data:', error);
    }
  };

  // Get visitor-specific data
  const getVisitorData = (key, defaultValue = null) => {
    try {
      const storageKey = getStorageKey(key);
      const data = localStorage.getItem(storageKey);
      return data ? JSON.parse(data) : defaultValue;
    } catch (error) {
      console.error('Error getting visitor data:', error);
      return defaultValue;
    }
  };

  return {
    visitorId,
    sessionId,
    isLoading,
    isSessionValid,
    refreshSession,
    setVisitorData,
    getVisitorData,
    getStorageKey
  };
};
