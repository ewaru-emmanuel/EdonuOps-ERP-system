import React, { useState, useMemo } from 'react';
import {
  Box,
  Typography,
  Chip,
  Checkbox,
  IconButton,
  Tooltip,
  Collapse,
  Paper,
  alpha,
  useTheme,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ChevronRight as ChevronRightIcon,
  AccountBalance as AssetIcon,
  CreditCard as LiabilityIcon,
  AccountBalanceWallet as EquityIcon,
  TrendingUp as RevenueIcon,
  TrendingDown as ExpenseIcon,
  Folder as FolderIcon,
  FolderOpen as FolderOpenIcon,
  Description as AccountIcon,
  MoreHoriz as MoreIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  FileCopy as CopyIcon
} from '@mui/icons-material';

import { useCoA } from '../context/CoAContext';

const CoATreeEnhanced = ({ onSelect, selectedAccounts = new Set(), onSelectAccount }) => {
  const theme = useTheme();
  const { accounts } = useCoA();
  const [expandedNodes, setExpandedNodes] = useState(new Set(['asset', 'liability', 'equity', 'revenue', 'expense']));
  const [hoveredNode, setHoveredNode] = useState(null);
  const [contextMenu, setContextMenu] = useState(null);

  // Use real account data from context
  const accountsData = useMemo(() => {
    return (accounts || []).map(acc => ({
      id: acc.id,
      code: acc.code,
      name: acc.account_name || acc.name,
      type: acc.account_type || acc.type,
      parent_id: acc.parent_id,
      balance: acc.balance || 0,
      is_active: acc.is_active !== false
    }));
  }, [accounts]);

  // Build tree structure
  const accountTree = useMemo(() => {
    const tree = {};
    const accountMap = {};
    
    // First pass: create account map
    accountsData.forEach(account => {
      accountMap[account.id] = { ...account, children: [] };
    });
    
    // Second pass: build tree structure
    accountsData.forEach(account => {
      if (account.parent_id === null) {
        tree[account.id] = accountMap[account.id];
      } else {
        const parent = accountMap[account.parent_id];
        if (parent) {
          parent.children.push(accountMap[account.id]);
        }
      }
    });
    
    return tree;
  }, [accountsData]);

  // Group accounts by type for organized display
  const groupedAccounts = useMemo(() => {
    const groups = {
      asset: { name: 'Assets', icon: <AssetIcon />, color: '#4caf50', accounts: [] },
      liability: { name: 'Liabilities', icon: <LiabilityIcon />, color: '#f44336', accounts: [] },
      equity: { name: 'Equity', icon: <EquityIcon />, color: '#2196f3', accounts: [] },
      revenue: { name: 'Revenue', icon: <RevenueIcon />, color: '#9c27b0', accounts: [] },
      expense: { name: 'Expenses', icon: <ExpenseIcon />, color: '#ff9800', accounts: [] }
    };
    
    Object.values(accountTree).forEach(account => {
      if (groups[account.type]) {
        groups[account.type].accounts.push(account);
      }
    });
    
    return groups;
  }, [accountTree]);

  const handleToggleExpand = (nodeId) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId);
    } else {
      newExpanded.add(nodeId);
    }
    setExpandedNodes(newExpanded);
  };

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

  const getAccountIcon = (account) => {
    const typeIcons = {
      asset: <AssetIcon />,
      liability: <LiabilityIcon />,
      equity: <EquityIcon />,
      revenue: <RevenueIcon />,
      expense: <ExpenseIcon />
    };
    return typeIcons[account.type] || <AccountIcon />;
  };

  const formatBalance = (balance) => {
    const formatted = Math.abs(balance).toLocaleString('en-US', {
      style: 'currency',
      currency: 'USD'
    });
    return balance < 0 ? `(${formatted})` : formatted;
  };

  const TreeNode = ({ account, level = 0, isLast = false, prefix = '' }) => {
    const isExpanded = expandedNodes.has(account.id);
    const hasChildren = account.children && account.children.length > 0;
    const isSelected = selectedAccounts.has(account.id);
    const isHovered = hoveredNode === account.id;

    const nodeIndent = level * 24;
    const lineHeight = '2.5rem';

    return (
      <Box key={account.id}>
        {/* Main node */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            height: lineHeight,
            pl: `${nodeIndent + 8}px`,
            pr: 1,
            cursor: 'pointer',
            backgroundColor: isSelected 
              ? alpha(theme.palette.primary.main, 0.08)
              : 'transparent',
            borderLeft: isSelected ? `3px solid ${theme.palette.primary.main}` : 'none',
            position: 'relative',
            transition: 'none', // Remove transition to eliminate lag
            '&:hover': {
              backgroundColor: alpha(theme.palette.action.hover, 0.02), // Extremely light hover
              '& .tree-actions': {
                opacity: 1
              }
            }
          }}
          onMouseEnter={() => setHoveredNode(account.id)}
          onMouseLeave={() => setHoveredNode(null)}
          onContextMenu={(e) => handleContextMenu(e, account)}
          onClick={() => onSelect && onSelect(account)}
        >
          {/* Tree structure lines */}
          {level > 0 && (
            <Box
              sx={{
                position: 'absolute',
                left: `${(level - 1) * 24 + 20}px`,
                top: 0,
                width: '1px',
                height: lineHeight,
                backgroundColor: alpha(theme.palette.divider, 0.3),
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: '50%',
                  left: 0,
                  width: '12px',
                  height: '1px',
                  backgroundColor: alpha(theme.palette.divider, 0.3),
                }
              }}
            />
          )}

          {/* Expand/collapse button */}
          <Box sx={{ width: 24, display: 'flex', justifyContent: 'center' }}>
            {hasChildren ? (
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  handleToggleExpand(account.id);
                }}
                sx={{ p: 0.5 }}
              >
                {isExpanded ? <ExpandMoreIcon fontSize="small" /> : <ChevronRightIcon fontSize="small" />}
              </IconButton>
            ) : (
              <Box sx={{ width: 24 }} />
            )}
          </Box>

          {/* Checkbox */}
          {onSelectAccount && (
            <Checkbox
              size="small"
              checked={isSelected}
              onChange={(e) => {
                e.stopPropagation();
                onSelectAccount(account.id, e.target.checked);
              }}
              sx={{ mr: 1, p: 0.5 }}
            />
          )}

          {/* Account icon */}
          <Box
            sx={{
              mr: 1,
              color: groupedAccounts[account.type]?.color || theme.palette.text.secondary,
              display: 'flex',
              alignItems: 'center'
            }}
          >
            {hasChildren ? (
              isExpanded ? <FolderOpenIcon fontSize="small" /> : <FolderIcon fontSize="small" />
            ) : (
              getAccountIcon(account)
            )}
          </Box>

          {/* Account code */}
          <Typography
            variant="body2"
            sx={{
              fontFamily: 'monospace',
              fontWeight: 600,
              color: theme.palette.text.primary,
              minWidth: 60,
              mr: 1
            }}
          >
            {account.code}
          </Typography>

          {/* Account name */}
          <Typography
            variant="body2"
            sx={{
              flex: 1,
              color: theme.palette.text.primary,
              fontWeight: isSelected ? 600 : 400
            }}
          >
            {account.name}
          </Typography>

          {/* Account type chip */}
          <Chip
            label={account.type}
            size="small"
            sx={{
              height: 20,
              fontSize: '0.7rem',
              backgroundColor: alpha(groupedAccounts[account.type]?.color || '#gray', 0.1),
              color: groupedAccounts[account.type]?.color || 'gray',
              border: `1px solid ${alpha(groupedAccounts[account.type]?.color || '#gray', 0.3)}`,
              mr: 1
            }}
          />

          {/* Balance */}
          <Typography
            variant="body2"
            sx={{
              fontFamily: 'monospace',
              fontWeight: 600,
              color: account.balance >= 0 ? theme.palette.success.main : theme.palette.error.main,
              minWidth: 80,
              textAlign: 'right',
              mr: 1
            }}
          >
            {formatBalance(account.balance)}
          </Typography>

          {/* Actions */}
          <Box
            className="tree-actions"
            sx={{
              opacity: 0,
              transition: 'opacity 0.2s',
              display: 'flex',
              gap: 0.5
            }}
          >
            <Tooltip title="More actions">
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  handleContextMenu(e, account);
                }}
              >
                <MoreIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Children */}
        {hasChildren && (
          <Collapse in={isExpanded} timeout={200}>
            <Box>
              {account.children.map((child, index) => (
                <TreeNode
                  key={child.id}
                  account={child}
                  level={level + 1}
                  isLast={index === account.children.length - 1}
                  prefix={prefix + (isLast ? '    ' : '│   ')}
                />
              ))}
            </Box>
          </Collapse>
        )}
      </Box>
    );
  };

  const CategoryHeader = ({ type, group }) => {
    const isExpanded = expandedNodes.has(type);
    const accountCount = group.accounts.length;
    const totalBalance = group.accounts.reduce((sum, acc) => sum + acc.balance, 0);

    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          p: 1.5,
          backgroundColor: alpha(group.color, 0.05),
          borderLeft: `4px solid ${group.color}`,
          cursor: 'pointer',
          transition: 'none', // Remove transition to eliminate lag
          '&:hover': {
            backgroundColor: alpha(group.color, 0.02) // Extremely light hover
          }
        }}
        onClick={() => handleToggleExpand(type)}
      >
        <IconButton size="small" sx={{ mr: 1 }}>
          {isExpanded ? <ExpandMoreIcon /> : <ChevronRightIcon />}
        </IconButton>
        
        <Box sx={{ color: group.color, mr: 1 }}>
          {group.icon}
        </Box>
        
        <Typography variant="h6" sx={{ flex: 1, fontWeight: 600 }}>
          {group.name}
        </Typography>
        
        <Chip
          label={`${accountCount} accounts`}
          size="small"
          sx={{ mr: 2 }}
        />
        
        <Typography
          variant="body2"
          sx={{
            fontFamily: 'monospace',
            fontWeight: 600,
            color: totalBalance >= 0 ? theme.palette.success.main : theme.palette.error.main
          }}
        >
          {formatBalance(totalBalance)}
        </Typography>
      </Box>
    );
  };

  return (
    <Paper sx={{ mt: 2, overflow: 'hidden' }}>
      <Box sx={{ maxHeight: '70vh', overflow: 'auto' }}>
        {Object.entries(groupedAccounts).map(([type, group]) => (
          <Box key={type}>
            <CategoryHeader type={type} group={group} />
            <Collapse in={expandedNodes.has(type)} timeout={300}>
              <Box sx={{ backgroundColor: alpha(theme.palette.background.paper, 0.5) }}>
                {group.accounts.map((account) => (
                  <TreeNode key={account.id} account={account} />
                ))}
              </Box>
            </Collapse>
          </Box>
        ))}
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
    </Paper>
  );
};

export default CoATreeEnhanced;
