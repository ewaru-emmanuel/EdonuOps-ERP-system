import React from 'react';
import { TreeView, TreeItem } from '@mui/x-tree-view';

import { 
  Typography,
  Chip,
  Stack,
  CircularProgress
} from '@mui/material';
import { useCoA } from '../context/CoAContext';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';

const CoATree = ({ onSelect }) => {
  const { accounts, loading, error, buildAccountTree } = useCoA();

  const renderTreeItems = (treeData) => {
    return treeData.map(account => (
      <TreeItem
        key={account.id}
        nodeId={account.id.toString()}
        label={
          <Stack direction="row" alignItems="center" spacing={1}>
            <Typography variant="body2">
              {account.code} - {account.name}
            </Typography>
            <Chip 
              label={account.type} 
              size="small" 
              variant="outlined"
              color={
                account.type === 'asset' ? 'primary' :
                account.type === 'liability' ? 'secondary' :
                account.type === 'equity' ? 'success' :
                account.type === 'revenue' ? 'info' :
                account.type === 'expense' ? 'warning' : 'default'
              }
            />
            <Typography variant="caption" color="text.secondary">
              ${account.balance?.toFixed(2) || '0.00'}
            </Typography>
          </Stack>
        }
        onClick={() => onSelect && onSelect(account)}
      >
        {account.children && account.children.length > 0 && renderTreeItems(account.children)}
      </TreeItem>
    ));
  };

  if (loading) return <CircularProgress size={24} />;
  
  if (error) return (
    <Typography color="error" variant="body2">
      Error loading accounts: {error}
    </Typography>
  );

  const treeData = buildAccountTree();

  return (
    <TreeView
      defaultCollapseIcon={<ExpandMoreIcon />}
      defaultExpandIcon={<ChevronRightIcon />}
      sx={{ minHeight: 400 }}
    >
      {renderTreeItems(treeData)}
    </TreeView>
  );
};

export default CoATree;
