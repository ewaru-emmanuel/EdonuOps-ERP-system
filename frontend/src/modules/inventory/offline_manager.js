// Offline-First Mobile WMS Manager
class OfflineWMSManager {
    constructor() {
        this.isOnline = navigator.onLine;
        this.syncQueue = [];
        this.syncInProgress = false;
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.syncPendingTransactions();
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showOfflineIndicator();
        });
    }
    
    showOfflineIndicator() {
        let indicator = document.getElementById('offline-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'offline-indicator';
            indicator.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: #f44336;
                color: white;
                text-align: center;
                padding: 8px;
                z-index: 9999;
                font-weight: bold;
            `;
            document.body.appendChild(indicator);
        }
        indicator.textContent = '🔄 OFFLINE MODE - Data will sync when connection is restored';
    }
    
    hideOfflineIndicator() {
        const indicator = document.getElementById('offline-indicator');
        if (indicator) indicator.remove();
    }
    
    async processBarcodeScan(scanData) {
        const transaction = {
            id: Date.now() + Math.random(),
            type: 'barcode_scan',
            data: scanData,
            timestamp: new Date().toISOString(),
            status: 'pending'
        };
        
        // Store locally
        this.syncQueue.push(transaction);
        localStorage.setItem('wms_sync_queue', JSON.stringify(this.syncQueue));
        
        if (this.isOnline) {
            return await this.syncTransaction(transaction);
        } else {
            return {
                success: true,
                message: 'Scan stored offline - will sync when online',
                offline: true,
                transactionId: transaction.id
            };
        }
    }
    
    async syncPendingTransactions() {
        if (this.syncInProgress) return;
        
        this.syncInProgress = true;
        
        try {
            const queue = JSON.parse(localStorage.getItem('wms_sync_queue') || '[]');
            
            for (const transaction of queue) {
                try {
                    const result = await this.syncTransaction(transaction);
                    if (result.success) {
                        this.syncQueue = this.syncQueue.filter(t => t.id !== transaction.id);
                        localStorage.setItem('wms_sync_queue', JSON.stringify(this.syncQueue));
                    }
                } catch (error) {
                    console.error('Sync error:', error);
                }
            }
            
            if (this.syncQueue.length === 0) {
                this.hideOfflineIndicator();
            }
            
        } finally {
            this.syncInProgress = false;
        }
    }
    
    async syncTransaction(transaction) {
        const apiEndpoints = {
            'barcode_scan': '/api/inventory/scan',
            'inventory_count': '/api/inventory/taking/counts',
            'pick_list_operation': '/api/inventory/pick-lists/process'
        };
        
        const endpoint = apiEndpoints[transaction.type];
        
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(transaction.data)
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            return { success: true, data: await response.json() };
            
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
    
    getSyncStatus() {
        return {
            isOnline: this.isOnline,
            syncInProgress: this.syncInProgress,
            pendingTransactions: this.syncQueue.length,
            lastSyncAttempt: new Date().toISOString()
        };
    }
}

export default OfflineWMSManager;
const offlineWMS = new OfflineWMSManager();
export { offlineWMS };
