/**
 * UI Language Service
 * Adapts terminology based on inventory complexity tier
 */

class UILanguageService {
  constructor() {
    this.complexityLevel = 'tier1'; // Default to simple inventory
  }

  setComplexityLevel(level) {
    this.complexityLevel = level;
  }

  // Navigation & Menu Items
  getMenuItems() {
    const items = {
      tier1: {
        dashboard: 'Dashboard',
        inventory: 'Inventory Management',
        products: 'Products',
        stockLevels: 'Stock Levels',
        reports: 'Reports',
        settings: 'Settings'
      },
      tier2: {
        dashboard: 'Dashboard',
        inventory: 'Warehouse Management',
        products: 'Products',
        stockLevels: 'Stock by Location',
        locations: 'Locations',
        reports: 'Reports',
        settings: 'Settings'
      },
      tier3: {
        dashboard: 'Dashboard',
        inventory: 'Warehouse Operations',
        products: 'Products',
        stockLevels: 'Advanced Stock Management',
        locations: 'Advanced Locations',
        operations: 'Operations',
        mobileWMS: 'Mobile WMS',
        reports: 'Reports',
        settings: 'Settings'
      }
    };
    return items[this.complexityLevel] || items.tier1;
  }

  // Page Titles
  getPageTitles() {
    const titles = {
      tier1: {
        inventory: 'Inventory Management',
        addStock: 'Add Stock',
        stockTake: 'Stock Count',
        transfers: 'Stock Transfers',
        reports: 'Inventory Reports'
      },
      tier2: {
        inventory: 'Warehouse Management',
        addStock: 'Receive Stock',
        stockTake: 'Location Stock Count',
        transfers: 'Location Transfers',
        reports: 'Warehouse Reports'
      },
      tier3: {
        inventory: 'Warehouse Operations',
        addStock: 'Advanced Receiving',
        stockTake: 'Cycle Counting',
        transfers: 'Advanced Transfers',
        reports: 'WMS Reports'
      }
    };
    return titles[this.complexityLevel] || titles.tier1;
  }

  // Form Labels
  getFormLabels() {
    const labels = {
      tier1: {
        warehouse: 'Storage Location',
        location: 'General Area',
        quantity: 'Quantity',
        product: 'Product',
        stockLevel: 'Current Stock',
        addStock: 'Add Stock',
        transfer: 'Move Stock'
      },
      tier2: {
        warehouse: 'Warehouse',
        location: 'Location',
        quantity: 'Quantity',
        product: 'Product',
        stockLevel: 'Stock by Location',
        addStock: 'Receive Stock',
        transfer: 'Transfer Stock'
      },
      tier3: {
        warehouse: 'Warehouse',
        location: 'Exact Location',
        quantity: 'Quantity',
        product: 'Product',
        stockLevel: 'Bin-Level Stock',
        addStock: 'Advanced Receiving',
        transfer: 'Advanced Transfer'
      }
    };
    return labels[this.complexityLevel] || labels.tier1;
  }

  // Button Text
  getButtonText() {
    const buttons = {
      tier1: {
        addStock: 'Add Stock',
        countStock: 'Count Stock',
        moveStock: 'Move Stock',
        viewStock: 'View Stock Levels',
        generateReport: 'Generate Report'
      },
      tier2: {
        addStock: 'Receive Stock',
        countStock: 'Count by Location',
        moveStock: 'Transfer Stock',
        viewStock: 'View by Location',
        generateReport: 'Generate Report'
      },
      tier3: {
        addStock: 'Advanced Receiving',
        countStock: 'Cycle Count',
        moveStock: 'Advanced Transfer',
        viewStock: 'View Bin Details',
        generateReport: 'Generate WMS Report'
      }
    };
    return buttons[this.complexityLevel] || buttons.tier1;
  }

  // Dashboard Cards
  getDashboardCards() {
    const cards = {
      tier1: {
        totalStock: 'Total Stock',
        lowStock: 'Low Stock Items',
        recentActivity: 'Recent Stock Changes',
        stockValue: 'Total Stock Value'
      },
      tier2: {
        totalStock: 'Warehouse Stock',
        lowStock: 'Low Stock by Location',
        recentActivity: 'Recent Warehouse Activity',
        stockValue: 'Warehouse Stock Value'
      },
      tier3: {
        totalStock: 'WMS Stock Overview',
        lowStock: 'ABC Analysis',
        recentActivity: 'Live Operations Feed',
        stockValue: 'WMS Stock Valuation'
      }
    };
    return cards[this.complexityLevel] || cards.tier1;
  }

  // Table Headers
  getTableHeaders() {
    const headers = {
      tier1: {
        product: 'Product',
        warehouse: 'Storage Location',
        quantity: 'Quantity',
        value: 'Value',
        status: 'Status'
      },
      tier2: {
        product: 'Product',
        warehouse: 'Warehouse',
        location: 'Location',
        quantity: 'Quantity',
        value: 'Value',
        status: 'Status'
      },
      tier3: {
        product: 'Product',
        warehouse: 'Warehouse',
        location: 'Exact Location',
        quantity: 'Quantity',
        value: 'Value',
        status: 'Status',
        lastActivity: 'Last Activity'
      }
    };
    return headers[this.complexityLevel] || headers.tier1;
  }

  // Messages & Notifications
  getMessages() {
    const messages = {
      tier1: {
        stockAdded: 'Stock added successfully',
        stockMoved: 'Stock moved successfully',
        stockCounted: 'Stock count completed',
        lowStockAlert: 'Low stock alert',
        noStock: 'No stock available'
      },
      tier2: {
        stockAdded: 'Stock received successfully',
        stockMoved: 'Stock transferred successfully',
        stockCounted: 'Location stock count completed',
        lowStockAlert: 'Low stock by location',
        noStock: 'No stock in this location'
      },
      tier3: {
        stockAdded: 'Advanced receiving completed',
        stockMoved: 'Advanced transfer completed',
        stockCounted: 'Cycle count completed',
        lowStockAlert: 'ABC analysis alert',
        noStock: 'No stock in this bin'
      }
    };
    return messages[this.complexityLevel] || messages.tier1;
  }

  // Help Text & Descriptions
  getHelpText() {
    const help = {
      tier1: {
        inventory: 'Manage your product inventory and stock levels',
        addStock: 'Add new stock to your storage location',
        stockTake: 'Count your current stock levels',
        transfers: 'Move stock between storage locations'
      },
      tier2: {
        inventory: 'Manage your warehouse and location-based stock',
        addStock: 'Receive stock into specific warehouse locations',
        stockTake: 'Count stock by specific locations',
        transfers: 'Transfer stock between warehouse locations'
      },
      tier3: {
        inventory: 'Advanced warehouse operations and management',
        addStock: 'Advanced receiving with putaway rules',
        stockTake: 'Automated cycle counting and ABC analysis',
        transfers: 'Advanced transfers with transit tracking'
      }
    };
    return help[this.complexityLevel] || help.tier1;
  }

  // Feature Names
  getFeatureNames() {
    const features = {
      tier1: {
        inventory: 'Inventory Management',
        stockTracking: 'Stock Tracking',
        basicReports: 'Basic Reports',
        simpleTransfers: 'Simple Transfers'
      },
      tier2: {
        inventory: 'Warehouse Management',
        stockTracking: 'Location-Based Tracking',
        basicReports: 'Warehouse Reports',
        simpleTransfers: 'Location Transfers'
      },
      tier3: {
        inventory: 'Warehouse Operations',
        stockTracking: 'Advanced WMS',
        basicReports: 'WMS Reports',
        simpleTransfers: 'Advanced Transfers'
      }
    };
    return features[this.complexityLevel] || features.tier1;
  }
}

// Create singleton instance
const uiLanguageService = new UILanguageService();

export default uiLanguageService;

