import React, { useState, useMemo } from 'react';
import {
  Box,
  Typography,
  Chip,
  Checkbox,
  useTheme,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  VisibilityOff as VisibilityOffIcon,
  FileCopy as CopyIcon,
  Add as AddIcon
} from '@mui/icons-material';

import { useCoA } from '../context/CoAContext';

const CoATreeEnhanced = ({ onSelect, selectedAccounts = new Set(), onSelectAccount, accounts: accountsProp }) => {
  const theme = useTheme();
  const { accounts: contextAccounts } = useCoA();
  const [contextMenu, setContextMenu] = useState(null);

  // Use accounts from prop (API accounts) if provided, otherwise fall back to context
  const accounts = accountsProp || contextAccounts || [];

  // Use real account data from accounts
  const accountsData = useMemo(() => {
    return (accounts || []).map(acc => ({
      id: acc.id,
      code: acc.code,
      name: acc.account_name || acc.name,
      type: acc.account_type || acc.type,
      balance: acc.balance || 0,
      is_active: acc.is_active !== false
    }));
  }, [accounts]);

  // Build hierarchical tree structure based on parent-child relationships
  const buildAccountTree = useMemo(() => {
    const accountMap = new Map();
    const rootAccounts = [];

    // Create a map of all accounts with children array
    accountsData.forEach(account => {
      accountMap.set(account.id, { ...account, children: [] });
    });

    // Build the tree structure
    accountsData.forEach(account => {
      const node = accountMap.get(account.id);
      // Check if account has a parent_id (from the original account object)
      const originalAccount = accounts.find(acc => acc.id === account.id);
      const parentId = originalAccount?.parent_id;
      
      if (parentId) {
        const parent = accountMap.get(parentId);
        if (parent) {
          parent.children.push(node);
        } else {
          // Parent not found, add to root
          rootAccounts.push(node);
        }
      } else {
        // No parent, add to root
        rootAccounts.push(node);
      }
    });

    return rootAccounts;
  }, [accountsData, accounts]);

  // Group root accounts by type for organized display (when no parent-child relationships exist)
  const groupedAccounts = useMemo(() => {
    const groups = {
      asset: { accounts: [] },
      liability: { accounts: [] },
      equity: { accounts: [] },
      revenue: { accounts: [] },
      expense: { accounts: [] }
    };
    
    buildAccountTree.forEach(account => {
      if (groups[account.type]) {
        groups[account.type].accounts.push(account);
      }
    });
    
    return groups;
  }, [buildAccountTree]);

  const handleContextMenu = (event, account) => {
    event.preventDefault();
    setContextMenu({
      mouseX: event.clientX - 2,
      mouseY: event.clientY - 4,
      account
    });
  };

  const handleCloseContextMenu = () => {
    setContextMenu(null);
  };

  const formatAmount = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount || 0);
  };

  const renderAccountItem = (account, depth = 0) => {
    const accountName = account.name || 'Unnamed Account';
    const accountType = account.type || '';
    const balance = account.balance || 0;
    const isActive = account.is_active !== false;
    const isSelected = selectedAccounts.has(account.id);
    const hasChildren = account.children && account.children.length > 0;
    const indent = depth * 24; // 24px per level

    return (
      <Box key={account.id}>
      <Box
        onClick={() => onSelect && onSelect(account)}
          onContextMenu={(e) => handleContextMenu(e, account)}
        sx={{
          display: 'flex',
          alignItems: 'center',
          py: 1.5,
          px: 2,
            pl: 2 + indent,
          borderLeft: `3px solid ${
            accountType === 'asset' ? '#4caf50' :
            accountType === 'liability' ? '#f44336' :
            accountType === 'equity' ? '#2196f3' :
            accountType === 'revenue' ? '#9c27b0' :
            '#ff9800'
          }`,
          cursor: 'pointer',
          backgroundColor: isSelected ? 'rgba(25, 118, 210, 0.08)' : 'transparent',
          '&:hover': {
            backgroundColor: accountType === 'asset' ? 'rgba(46, 125, 50, 0.04)' :
                           accountType === 'liability' ? 'rgba(198, 40, 40, 0.04)' :
                           accountType === 'equity' ? 'rgba(21, 101, 192, 0.04)' :
                           accountType === 'revenue' ? 'rgba(123, 31, 162, 0.04)' :
                           'rgba(230, 81, 0, 0.04)',
            transform: 'translateX(2px)'
          },
          transition: 'all 0.2s ease',
          opacity: isActive ? 1 : 0.6
        }}
      >
        {onSelectAccount && (
          <Checkbox
            size="small"
            checked={isSelected}
            onChange={(e) => {
              e.stopPropagation();
              onSelectAccount(account.id, e.target.checked);
            }}
            onClick={(e) => e.stopPropagation()}
            sx={{ mr: 1 }}
          />
        )}
          {/* Indent indicator for child accounts */}
          {depth > 0 && (
            <Box
              sx={{
                width: 16,
                height: 1,
                bgcolor: 'divider',
                mr: 1
              }}
            />
          )}
        <Typography 
          variant="body2" 
          sx={{ 
            fontFamily: 'monospace',
            fontWeight: 500,
            color: 'text.secondary',
            minWidth: 80,
            mr: 2
          }}
        >
          {account.code}
        </Typography>
        <Typography 
          variant="body2" 
          sx={{ 
            flexGrow: 1,
            fontWeight: 'medium',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}
        >
          {accountName}
            {hasChildren && (
              <Typography component="span" variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                ({account.children.length} child{account.children.length !== 1 ? 'ren' : ''})
              </Typography>
            )}
        </Typography>
        <Chip 
          label={accountType} 
          size="small"
          sx={{
            minWidth: 80,
            bgcolor: 
              accountType === 'asset' ? '#e8f5e9' :
              accountType === 'liability' ? '#ffebee' :
              accountType === 'equity' ? '#e3f2fd' :
              accountType === 'revenue' ? '#f3e5f5' :
              '#fff3e0',
            color:
              accountType === 'asset' ? '#2e7d32' :
              accountType === 'liability' ? '#c62828' :
              accountType === 'equity' ? '#1565c0' :
              accountType === 'revenue' ? '#7b1fa2' :
              '#e65100',
            fontWeight: 600,
            border: 'none',
            mr: 2
          }}
        />
        <Typography 
          variant="body2" 
          color={balance >= 0 ? 'text.primary' : 'error.main'}
          fontWeight="medium"
          sx={{ minWidth: 100, textAlign: 'right', mr: 2 }}
        >
          {formatAmount(balance)}
        </Typography>
        <Chip
          label={isActive ? 'Active' : 'Inactive'}
          size="small"
          color={isActive ? 'success' : 'error'}
          variant="outlined"
          sx={{ height: 24, fontSize: '0.7rem', minWidth: 70 }}
        />
        </Box>
        {/* Recursively render children */}
        {hasChildren && (
          <Box>
            {account.children
              .sort((a, b) => (a.code || '').localeCompare(b.code || ''))
              .map(child => renderAccountItem(child, depth + 1))}
          </Box>
        )}
      </Box>
    );
  };

  // Check if we have any accounts
  const hasAccounts = accountsData.length > 0;
  const hasTreeAccounts = buildAccountTree.length > 0;
  
  // Check if any accounts have parent-child relationships
  const hasHierarchy = buildAccountTree.some(account => account.children && account.children.length > 0);

  return (
    <>
      <Box>
        {!hasAccounts ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="body1" color="text.secondary">
              No accounts found. Create your first account to get started.
            </Typography>
          </Box>
        ) : !hasTreeAccounts ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="body1" color="text.secondary">
              No accounts to display. Check your filters.
            </Typography>
          </Box>
        ) : hasHierarchy ? (
          // Show hierarchical tree structure when parent-child relationships exist
          <>
            <Box sx={{ mb: 2, px: 2, py: 1, bgcolor: 'info.light', borderRadius: 1 }}>
              <Typography variant="caption" color="text.secondary">
                💡 Tree View: Shows parent-child account relationships. Child accounts are indented under their parents.
              </Typography>
            </Box>
            {Object.entries(groupedAccounts)
              .filter(([_, group]) => group.accounts.length > 0)
              .map(([type, group]) => (
                <Box key={type} sx={{ mb: 3 }}>
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      mb: 1, 
                      px: 2,
                      textTransform: 'capitalize',
                      fontWeight: 600,
                      color: 'text.primary'
                    }}
                  >
                    {type} ({group.accounts.length})
                  </Typography>
                  {group.accounts
                    .sort((a, b) => (a.code || '').localeCompare(b.code || ''))
                    .map((account) => renderAccountItem(account, 0))}
                </Box>
              ))}
          </>
        ) : (
          // Show grouped by type when no hierarchy exists (fallback)
          <>
            <Box sx={{ mb: 2, px: 2, py: 1, bgcolor: 'grey.100', borderRadius: 1 }}>
              <Typography variant="caption" color="text.secondary">
                ℹ️ No parent-child relationships found. Accounts are grouped by type. Create child accounts to see the tree structure.
              </Typography>
            </Box>
            {Object.entries(groupedAccounts)
              .filter(([_, group]) => group.accounts.length > 0)
              .map(([type, group]) => (
                <Box key={type} sx={{ mb: 3 }}>
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      mb: 1, 
                      px: 2,
                      textTransform: 'capitalize',
                      fontWeight: 600,
                      color: 'text.primary'
                    }}
                  >
                    {type} ({group.accounts.length})
                  </Typography>
                  {group.accounts
                    .sort((a, b) => (a.code || '').localeCompare(b.code || ''))
                    .map((account) => renderAccountItem(account, 0))}
          </Box>
        ))}
          </>
        )}
      </Box>

      {/* Context Menu */}
      <Menu
        open={contextMenu !== null}
        onClose={handleCloseContextMenu}
        anchorReference="anchorPosition"
        anchorPosition={
          contextMenu !== null
            ? { top: contextMenu.mouseY, left: contextMenu.mouseX }
            : undefined
        }
      >
        <MenuItem onClick={() => { onSelect && onSelect(contextMenu?.account); handleCloseContextMenu(); }}>
          <ListItemIcon><EditIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Edit Account</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleCloseContextMenu}>
          <ListItemIcon><CopyIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Duplicate Account</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleCloseContextMenu}>
          <ListItemIcon><AddIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Add Child Account</ListItemText>
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleCloseContextMenu}>
          <ListItemIcon><VisibilityOffIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Deactivate Account</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleCloseContextMenu} sx={{ color: 'error.main' }}>
          <ListItemIcon><DeleteIcon fontSize="small" color="error" /></ListItemIcon>
          <ListItemText>Delete Account</ListItemText>
        </MenuItem>
      </Menu>
    </>
  );
};

export default CoATreeEnhanced;
