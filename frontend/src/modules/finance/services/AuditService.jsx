// src/services/AuditService.jsx

import { collection, addDoc, getDocs, query, where, orderBy } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

/**
 * AuditService provides a client for interacting with a backend audit trail.
 * This service is designed to be used with a Firestore instance.
 */
class AuditService {
  /**
   * Logs a change to a document in Firestore.
   *
   * @param {object} db The Firestore database instance.
   * @param {string} user The user ID or name.
   * @param {string} docId The unique identifier of the document (e.g., a journal entry ID).
   * @param {object} changes The changes being made to the document.
   */
  static async logChange(db, user, docId, changes) {
    if (!db) {
      console.error('AuditService requires a db instance to be provided.');
      return;
    }
    
    // In a real application, you might also want to fetch the 'before' state
    // and log it, as well as handle device/location on the backend.
    
    try {
      await addDoc(collection(db, "audit_trail"), {
        timestamp: new Date().toISOString(),
        user,
        docId,
        changes,
        // The following fields are better handled on a trusted server-side process
        // to prevent client-side manipulation.
        // device_fingerprint: window.navigator.userAgent,
        // location: await fetch('https://ipapi.co/json/').then(res => res.json())
      });
    } catch (error) {
      console.error(`Failed to log audit change for document ${docId}:`, error);
    }
  }

  /**
   * Fetches the audit trail for a specific document from Firestore.
   *
   * @param {object} db The Firestore database instance.
   * @param {string} docId The unique identifier of the document.
   * @returns {Promise<Array<object>>} A promise that resolves to an array of audit log entries.
   */
  static async getAuditTrail(db, docId) {
    if (!db) {
      console.error('AuditService requires a db instance to be provided.');
      return [];
    }

    try {
      const q = query(
        collection(db, "audit_trail"),
        where("docId", "==", docId),
        // orderBy("timestamp", "desc") // Ordering can be slow without an index.
      );
      const querySnapshot = await getDocs(q);
      const trail = [];
      querySnapshot.forEach((doc) => {
        trail.push({ id: doc.id, ...doc.data() });
      });
      return trail;
    } catch (error) {
      console.error(`Failed to fetch audit trail for document ${docId}:`, error);
      return [];
    }
  }
}

export default AuditService;
