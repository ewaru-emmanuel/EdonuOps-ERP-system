import React, { useState, useCallback, useEffect } from 'react';
import {
  TextField, MenuItem, Button, Box, Typography,
  Tabs, Tab, Alert, Chip, Stack, Tooltip, IconButton
} from '@mui/material';
import { Refresh, Download, Add } from '@mui/icons-material';
import { useFinanceData } from './context/FinanceDataContext';
import { useWebSocket } from './hooks/useWebSocket';
import { useCurrency } from '../../contexts/CurrencyContext';
import { useCurrencyConversion } from '../../hooks/useCurrencyConversion';
import FinanceTable from '../../components/tables/FinanceTable';
import JournalEntryForm from './forms/JournalEntryForm';
import SourceDocumentModal from './modals/SourceDocumentModal';

const GeneralLedger = () => {
  // Data fetching from centralized context
  const { 
    glEntries: entries, 
    loading, 
    errors, 
    refreshGLEntries: refresh, 
    addJournalEntry,
    updateJournalEntry 
  } = useFinanceData();

  // Currency conversion
  const { selectedCurrency } = useCurrency();
  const { 
    data: convertedEntries, 
    formatAmount 
  } = useCurrencyConversion(entries, 'gl_entries');
  
  // State
  const [activeTab, setActiveTab] = useState('all');
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [showJournalForm, setShowJournalForm] = useState(false);
  const [filters, setFilters] = useState({
    period: '',
    entity: '',
    status: '',
    book_type: '',
  });
  const [sourceDoc, setSourceDoc] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [selectedBooks, setSelectedBooks] = useState([]);

  // WebSocket for real-time updates
  const { lastMessage } = useWebSocket('gl_updates');
  
  useEffect(() => {
    if (lastMessage) {
      const update = JSON.parse(lastMessage.data);
      if (update.type === 'new_entry' || update.type === 'updated_entry') {
        refresh();
        setLastUpdate(new Date());
      }
    }
  }, [lastMessage, refresh]);

  // Available book types
  const availableBooks = ['primary', 'tax', 'ifrs', 'consolidation', 'management'];

  // Handlers
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleTabChange = (_, newValue) => {
    setActiveTab(newValue);
  };

  const handleBookToggle = (book) => {
    setSelectedBooks(prev =>
      prev.includes(book)
        ? prev.filter(b => b !== book)
        : [...prev, book]
    );
  };

  // Calculations
  const isBalanced = (entry) => {
    const totalDebits = entry.lines?.reduce((sum, line) => sum + parseFloat(line.debit_amount || 0), 0);
    const totalCredits = entry.lines?.reduce((sum, line) => sum + parseFloat(line.credit_amount || 0), 0);
    return Math.abs(totalDebits - totalCredits) < 0.01;
  };

  // Filtering logic
  const filteredEntries = useCallback(() => {
    let result = Array.isArray(convertedEntries) ? [...convertedEntries] : [];

    // Tab filtering
    if (activeTab === 'debits') {
      result = result.filter(e => e.lines?.some(l => l.debit_amount > 0));
    } else if (activeTab === 'credits') {
      result = result.filter(e => e.lines?.some(l => l.credit_amount > 0));
    }

    // Additional filters
    if (filters.period) result = result.filter(e => e.period === filters.period);
    if (filters.entity) result = result.filter(e => e.entity === filters.entity);
    if (filters.status) result = result.filter(e => e.status === filters.status);
    
    // Multi-book filtering
    if (selectedBooks.length > 0) {
      result = result.filter(e => selectedBooks.includes(e.book_type));
    } else if (filters.book_type) {
      result = result.filter(e => e.book_type === filters.book_type);
    }

    return result;
  }, [entries, activeTab, filters, selectedBooks]);

  // Export to CSV
  const handleExport = () => {
    const headers = [
      'Date', 'Period', 'Reference', 'Status', 'Book Type',
      'Account', 'Description', 'Debit', 'Credit', 'Entity', 'Balance Check'
    ];

    const rows = filteredEntries().flatMap(entry => 
      entry.lines?.map(line => ([
        entry.docDate,
        entry.period,
        entry.reference,
        entry.status,
        entry.book_type,
        line.account_name,
        line.description,
        line.debit_amount,
        line.credit_amount,
        entry.entity,
        isBalanced(entry) ? 'Balanced' : 'Unbalanced'
      ])) || []
    );

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(item => `"${String(item || '')}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.setAttribute('download', `gl_export_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Table columns
  const columns = [
    {
      header: 'Date',
      accessor: 'docDate',
      width: '120px',
      cell: (date) => new Date(date).toLocaleDateString(),
      sortable: true,
    },
    {
      header: 'Reference',
      accessor: 'reference',
      cell: (ref) => <Typography variant="body2" noWrap>{ref}</Typography>,
      sortable: true,
    },
    {
      header: 'Status',
      accessor: 'status',
      width: '100px',
      cell: (status) => (
        <Chip 
          label={status.toUpperCase()} 
          size="small"
          color={
            status === 'posted' ? 'success' :
            status === 'approved' ? 'primary' :
            status === 'pending' ? 'warning' : 'default'
          }
        />
      ),
    },
    {
      header: 'Book',
      accessor: 'book_type',
      width: '100px',
      cell: (book) => (
        <Tooltip title={book}>
          <Chip label={book.toUpperCase().slice(0,3)} size="small" />
        </Tooltip>
      ),
    },
    {
      header: 'Amounts',
      accessor: 'lines',
      cell: (lines) => {
        const totalDebit = lines.reduce((sum, l) => sum + (+l.debit_amount || 0), 0);
        const totalCredit = lines.reduce((sum, l) => sum + (+l.credit_amount || 0), 0);
        return (
          <Stack direction="row" spacing={1}>
            <Typography color="green" variant="body2">${totalDebit.toFixed(2)}</Typography>
            <Typography color="red" variant="body2">(${totalCredit.toFixed(2)})</Typography>
          </Stack>
        );
      },
      align: 'right',
    },
    {
      header: 'Balanced',
      accessor: 'lines',
      width: '100px',
      cell: (lines) => (
        isBalanced({ lines }) ? (
          <Tooltip title="Balanced">
            <Chip label="✔" color="success" size="small" />
          </Tooltip>
        ) : (
          <Tooltip title="Unbalanced">
            <Chip label="✘" color="error" size="small" />
          </Tooltip>
        )
      ),
      align: 'center',
    },
    {
      header: 'Source',
      accessor: 'lines',
      width: '120px',
      cell: (lines) => {
        const sourceLine = lines.find(l => l.source_doc);
        return sourceLine ? (
          <Button
            size="small"
            variant="outlined"
            onClick={(e) => {
              e.stopPropagation();
              setSourceDoc(sourceLine.source_doc);
            }}
          >
            View
          </Button>
        ) : null;
      },
    },
    {
      header: 'Actions',
      accessor: 'id',
      width: '180px',
      cell: (id, row) => (
        <Stack direction="row" spacing={1}>
          <Button
            size="small"
            variant="outlined"
            onClick={(e) => {
              e.stopPropagation();
              setSelectedEntry(row);
            }}
            disabled={row.status === 'posted'}
          >
            Edit
          </Button>
          <Tooltip title="View Details">
            <Button
              size="small"
              variant="text"
              onClick={(e) => {
                e.stopPropagation();
                setSelectedEntry(row);
              }}
            >
              View
            </Button>
          </Tooltip>
        </Stack>
      ),
    },
  ];

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1">
          General Ledger
          {lastUpdate && (
            <Typography variant="caption" color="text.secondary" sx={{ ml: 2 }}>
              Last updated: {lastUpdate.toLocaleTimeString()}
            </Typography>
          )}
        </Typography>
        <Stack direction="row" spacing={2}>
          <Tooltip title="Refresh Data">
            <IconButton onClick={refresh} disabled={loading}>
              <Refresh />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setShowJournalForm(true)}
            disabled={loading}
          >
            New Journal Entry
          </Button>
        </Stack>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="All Entries" value="all" />
          <Tab label="Debits" value="debits" />
          <Tab label="Credits" value="credits" />
        </Tabs>
      </Box>

      {/* Filters */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap', alignItems: 'center' }}>
        <TextField
          select
          label="Period"
          name="period"
          value={filters.period}
          onChange={handleFilterChange}
          size="small"
          sx={{ minWidth: 120 }}
        >
          <MenuItem value="">All Periods</MenuItem>
          {[...new Set(entries.map(e => e.period))].map(p => (
            <MenuItem key={p} value={p}>{p}</MenuItem>
          ))}
        </TextField>

        <TextField
          select
          label="Entity"
          name="entity"
          value={filters.entity}
          onChange={handleFilterChange}
          size="small"
          sx={{ minWidth: 120 }}
        >
          <MenuItem value="">All Entities</MenuItem>
          {[...new Set(entries.map(e => e.entity))].map(ent => (
            <MenuItem key={ent} value={ent}>{ent}</MenuItem>
          ))}
        </TextField>

        <TextField
          select
          label="Status"
          name="status"
          value={filters.status}
          onChange={handleFilterChange}
          size="small"
          sx={{ minWidth: 120 }}
        >
          <MenuItem value="">All Statuses</MenuItem>
          {['draft', 'pending', 'approved', 'posted'].map(s => (
            <MenuItem key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</MenuItem>
          ))}
        </TextField>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="body2">Books:</Typography>
          {availableBooks.map(book => (
            <Chip
              key={book}
              label={book.toUpperCase()}
              size="small"
              variant={selectedBooks.includes(book) ? 'filled' : 'outlined'}
              color={selectedBooks.includes(book) ? 'primary' : 'default'}
              onClick={() => handleBookToggle(book)}
              sx={{ cursor: 'pointer' }}
            />
          ))}
        </Box>

        <Tooltip title="Export to CSV">
          <IconButton
            onClick={handleExport}
            disabled={filteredEntries().length === 0}
            color="primary"
          >
            <Download />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Error handling */}
      {errors.gl_entries && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Failed to load data: {errors.gl_entries}
        </Alert>
      )}

      {/* Journal Entry Form */}
      <JournalEntryForm
        open={showJournalForm || !!selectedEntry}
        onClose={() => {
          setShowJournalForm(false);
          setSelectedEntry(null);
        }}
        entry={selectedEntry}
        onSave={(journalData) => {
          console.log('✅ Journal entry saved:', journalData);
          if (selectedEntry) {
            updateJournalEntry(selectedEntry.id, journalData);
          } else {
            addJournalEntry(journalData);
          }
        }}
      />

      {/* Main table */}
      <FinanceTable
        data={filteredEntries()}
        columns={columns}
        loading={loading.gl_entries}
        emptyMessage="No journal entries found"
        onRowClick={(row) => {
          if (row.status !== 'posted') {
            setSelectedEntry(row);
          }
        }}
        pagination
        pageSize={10}
        rowStyle={(row) => ({
          cursor: row.status !== 'posted' ? 'pointer' : 'default',
          backgroundColor: row.status === 'posted' ? '#f5f5f5' : 'inherit'
        })}
      />

      {/* Source document modal */}
      <SourceDocumentModal
        open={!!sourceDoc}
        onClose={() => setSourceDoc(null)}
        document={sourceDoc}
      />
    </Box>
  );
};

export default GeneralLedger;