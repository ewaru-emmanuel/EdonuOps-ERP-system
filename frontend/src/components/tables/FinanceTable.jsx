import React, { useState, useMemo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Paper,
  Box,
  Typography,
  Skeleton,
  Checkbox,
  Toolbar,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import { FilterList, GetApp } from '@mui/icons-material';

const FinanceTable = ({
  data = [],
  columns = [],
  loading = false,
  emptyMessage = "No data available",
  onRowClick,
  pagination = true,
  pageSize = 25,
  selectable = false,
  onSelectionChange,
  rowStyle,
  title,
  dense = false,
  exportable = false,
  onExport,
  stickyHeader = true
}) => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(pageSize);
  const [sortBy, setSortBy] = useState('');
  const [sortDirection, setSortDirection] = useState('asc');
  const [selected, setSelected] = useState(new Set());

  // Sorting logic
  const sortedData = useMemo(() => {
    if (!sortBy) return data;
    
    return [...data].sort((a, b) => {
      const aValue = a[sortBy];
      const bValue = b[sortBy];
      
      if (aValue === null || aValue === undefined) return 1;
      if (bValue === null || bValue === undefined) return -1;
      
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
      }
      
      const aStr = String(aValue).toLowerCase();
      const bStr = String(bValue).toLowerCase();
      
      if (aStr < bStr) return sortDirection === 'asc' ? -1 : 1;
      if (aStr > bStr) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }, [data, sortBy, sortDirection]);

  // Pagination logic
  const paginatedData = useMemo(() => {
    if (!pagination) return sortedData;
    
    const start = page * rowsPerPage;
    return sortedData.slice(start, start + rowsPerPage);
  }, [sortedData, page, rowsPerPage, pagination]);

  const handleSort = (columnKey) => {
    const isCurrentSort = sortBy === columnKey;
    setSortDirection(isCurrentSort && sortDirection === 'asc' ? 'desc' : 'asc');
    setSortBy(columnKey);
  };

  const handlePageChange = (event, newPage) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSelectAll = (event) => {
    if (event.target.checked) {
      const newSelected = new Set(paginatedData.map(row => row.id || row.key));
      setSelected(newSelected);
      onSelectionChange?.(Array.from(newSelected));
    } else {
      setSelected(new Set());
      onSelectionChange?.([]);
    }
  };

  const handleRowSelect = (event, id) => {
    event.stopPropagation();
    const newSelected = new Set(selected);
    
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    
    setSelected(newSelected);
    onSelectionChange?.(Array.from(newSelected));
  };

  const isSelected = (id) => selected.has(id);

  const renderCell = (column, row, value) => {
    if (column.cell) {
      return column.cell(value, row);
    }
    
    if (value === null || value === undefined) {
      return <Typography color="textSecondary">—</Typography>;
    }
    
    if (typeof value === 'number') {
      return value.toLocaleString();
    }
    
    if (typeof value === 'boolean') {
      return (
        <Chip
          label={value ? 'Yes' : 'No'}
          color={value ? 'success' : 'default'}
          size="small"
        />
      );
    }
    
    return String(value);
  };

  if (loading) {
    return (
      <TableContainer component={Paper}>
        <Table size={dense ? 'small' : 'medium'}>
          <TableHead>
            <TableRow>
              {columns.map((column, index) => (
                <TableCell key={index}>
                  <Skeleton variant="text" width="80%" />
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {Array.from({ length: rowsPerPage }).map((_, index) => (
              <TableRow key={index}>
                {columns.map((_, colIndex) => (
                  <TableCell key={colIndex}>
                    <Skeleton variant="text" />
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  }

  const numSelected = selected.size;
  const numRows = paginatedData.length;

  return (
    <Paper sx={{ width: '100%', overflow: 'hidden' }}>
      {/* Toolbar */}
      {(title || selectable || exportable) && (
        <Toolbar
          sx={{
            pl: { sm: 2 },
            pr: { xs: 1, sm: 1 },
            ...(numSelected > 0 && {
              bgcolor: (theme) => theme.palette.action.selected,
            }),
          }}
        >
          {numSelected > 0 ? (
            <Typography
              sx={{ flex: '1 1 100%' }}
              color="inherit"
              variant="subtitle1"
              component="div"
            >
              {numSelected} selected
            </Typography>
          ) : (
            <Typography
              sx={{ flex: '1 1 100%' }}
              variant="h6"
              id="tableTitle"
              component="div"
            >
              {title}
            </Typography>
          )}

          {exportable && (
            <Tooltip title="Export data">
              <IconButton onClick={onExport}>
                <GetApp />
              </IconButton>
            </Tooltip>
          )}
        </Toolbar>
      )}

      {/* Table */}
      <TableContainer sx={{ maxHeight: 440 }}>
        <Table
          stickyHeader={stickyHeader}
          size={dense ? 'small' : 'medium'}
          aria-labelledby="tableTitle"
        >
          <TableHead>
            <TableRow>
              {selectable && (
                <TableCell padding="checkbox">
                  <Checkbox
                    color="primary"
                    indeterminate={numSelected > 0 && numSelected < numRows}
                    checked={numRows > 0 && numSelected === numRows}
                    onChange={handleSelectAll}
                    inputProps={{
                      'aria-label': 'select all items',
                    }}
                  />
                </TableCell>
              )}
              {columns.map((column) => (
                <TableCell
                  key={column.accessor}
                  align={column.align || 'left'}
                  style={{ 
                    width: column.width,
                    minWidth: column.minWidth || column.width
                  }}
                  sortDirection={sortBy === column.accessor ? sortDirection : false}
                >
                  {column.sortable ? (
                    <TableSortLabel
                      active={sortBy === column.accessor}
                      direction={sortBy === column.accessor ? sortDirection : 'asc'}
                      onClick={() => handleSort(column.accessor)}
                    >
                      {column.header}
                    </TableSortLabel>
                  ) : (
                    column.header
                  )}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedData.length === 0 ? (
              <TableRow>
                <TableCell 
                  colSpan={columns.length + (selectable ? 1 : 0)} 
                  align="center"
                  sx={{ py: 8 }}
                >
                  <Typography color="textSecondary" variant="body1">
                    {emptyMessage}
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              paginatedData.map((row, index) => {
                const rowId = row.id || row.key || index;
                const isItemSelected = isSelected(rowId);
                const labelId = `enhanced-table-checkbox-${index}`;

                return (
                  <TableRow
                    hover
                    role={onRowClick ? "button" : undefined}
                    aria-checked={isItemSelected}
                    tabIndex={-1}
                    key={rowId}
                    selected={isItemSelected}
                    onClick={onRowClick ? () => onRowClick(row) : undefined}
                    sx={{
                      cursor: onRowClick ? 'pointer' : 'default',
                      ...(rowStyle && rowStyle(row))
                    }}
                  >
                    {selectable && (
                      <TableCell padding="checkbox">
                        <Checkbox
                          color="primary"
                          checked={isItemSelected}
                          onChange={(event) => handleRowSelect(event, rowId)}
                          inputProps={{
                            'aria-labelledby': labelId,
                          }}
                        />
                      </TableCell>
                    )}
                    {columns.map((column) => {
                      const value = row[column.accessor];
                      return (
                        <TableCell
                          key={column.accessor}
                          align={column.align || 'left'}
                          component={index === 0 && !selectable ? "th" : undefined}
                          id={index === 0 && !selectable ? labelId : undefined}
                          scope={index === 0 && !selectable ? "row" : undefined}
                        >
                          {renderCell(column, row, value)}
                        </TableCell>
                      );
                    })}
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      {pagination && (
        <TablePagination
          rowsPerPageOptions={[10, 25, 50, 100]}
          component="div"
          count={sortedData.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handlePageChange}
          onRowsPerPageChange={handleRowsPerPageChange}
          showFirstButton
          showLastButton
        />
      )}
    </Paper>
  );
};

export default FinanceTable;