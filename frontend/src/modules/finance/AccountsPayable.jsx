import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Chip,
  Stack,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Tooltip,
  IconButton
} from '@mui/material';
import { Add, Payment, Send, Edit, Visibility } from '@mui/icons-material';
import { useFinanceData } from './hooks/useFinanceData';
import { useCurrency } from '../../components/GlobalCurrencySettings';
import { useCurrencyConversion } from '../../hooks/useCurrencyConversion';
import FinanceTable from '../../components/tables/FinanceTable';

const AccountsPayable = () => {
  const { data: bills, loading, error, refresh } = useFinanceData('ap');

  // Currency conversion
  const { selectedCurrency } = useCurrency();
  const { 
    data: convertedBills, 
    formatAmount 
  } = useCurrencyConversion(bills, 'bills');
  const [selectedBill, setSelectedBill] = useState(null);
  const [showPaymentDialog, setShowPaymentDialog] = useState(false);
  const [showBillDialog, setShowBillDialog] = useState(false);
  const [paymentAmount, setPaymentAmount] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('bank_transfer');

  const handlePayBill = (bill) => {
    setSelectedBill(bill);
    setPaymentAmount(bill.amount?.toString() || '');
    setShowPaymentDialog(true);
  };

  const handleProcessPayment = async () => {
    // TODO: Implement payment processing
      amount: paymentAmount,
      method: paymentMethod
    });
    
    setShowPaymentDialog(false);
    setSelectedBill(null);
    setPaymentAmount('');
    // refresh(); // Refresh data after payment
  };

  const handleEditBill = (bill) => {
    setSelectedBill(bill);
    setShowBillDialog(true);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'paid': return 'success';
      case 'pending': return 'warning';
      case 'overdue': return 'error';
      case 'draft': return 'default';
      default: return 'default';
    }
  };

  const getDaysOverdue = (dueDate) => {
    const due = new Date(dueDate);
    const today = new Date();
    const diffTime = today - due;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 0;
  };

  const columns = [
    {
      header: 'Vendor',
      accessor: 'vendor_name',
      sortable: true,
      cell: (vendor) => (
        <Typography variant="body2" fontWeight="medium">
          {vendor}
        </Typography>
      )
    },
    {
      header: 'Invoice #',
      accessor: 'invoice_number',
      width: '150px',
      cell: (invoiceNum) => (
        <Typography variant="body2" fontFamily="monospace">
          {invoiceNum}
        </Typography>
      )
    },
    {
      header: 'Amount',
      accessor: 'amount',
      width: '120px',
      align: 'right',
      sortable: true,
      cell: (amount) => (
        <Typography variant="body2" fontWeight="medium">
          ${amount?.toFixed(2) || '0.00'}
        </Typography>
      )
    },
    {
      header: 'Due Date',
      accessor: 'due_date',
      width: '120px',
      sortable: true,
      cell: (dueDate, row) => {
        const overdueDays = getDaysOverdue(dueDate);
        return (
          <Box>
            <Typography variant="body2">
              {new Date(dueDate).toLocaleDateString()}
            </Typography>
            {overdueDays > 0 && row.status !== 'paid' && (
              <Typography variant="caption" color="error">
                {overdueDays} days overdue
              </Typography>
            )}
          </Box>
        );
      }
    },
    {
      header: 'Status',
      accessor: 'status',
      width: '120px',
      cell: (status) => (
        <Chip
          label={status.charAt(0).toUpperCase() + status.slice(1)}
          color={getStatusColor(status)}
          size="small"
          variant="outlined"
        />
      )
    },
    {
      header: 'Actions',
      accessor: 'id',
      width: '200px',
      cell: (id, row) => (
        <Stack direction="row" spacing={1}>
          {row.status !== 'paid' && (
            <Tooltip title="Process Payment">
              <Button
                size="small"
                variant="outlined"
                color="primary"
                startIcon={<Payment />}
                onClick={(e) => {
                  e.stopPropagation();
                  handlePayBill(row);
                }}
              >
                Pay
              </Button>
            </Tooltip>
          )}
          <Tooltip title="Edit Bill">
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                handleEditBill(row);
              }}
            >
              <Edit fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="View Details">
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                setSelectedBill(row);
              }}
            >
              <Visibility fontSize="small" />
            </IconButton>
          </Tooltip>
        </Stack>
      )
    }
  ];

  // Summary calculations
  const totalPending = bills
    .filter(bill => bill.status === 'pending')
    .reduce((sum, bill) => sum + (bill.amount || 0), 0);

  const totalOverdue = bills
    .filter(bill => bill.status !== 'paid' && getDaysOverdue(bill.due_date) > 0)
    .reduce((sum, bill) => sum + (bill.amount || 0), 0);

  const overdueCount = bills
    .filter(bill => bill.status !== 'paid' && getDaysOverdue(bill.due_date) > 0)
    .length;

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Accounts Payable
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setShowBillDialog(true)}
        >
          New Bill
        </Button>
      </Box>

      {/* Summary Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2, mb: 3 }}>
        <Box sx={{ p: 2, bgcolor: 'primary.50', borderRadius: 1, border: 1, borderColor: 'primary.200' }}>
          <Typography variant="h6" color="primary.main">
            ${totalPending.toFixed(2)}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Total Pending
          </Typography>
        </Box>
        <Box sx={{ p: 2, bgcolor: 'error.50', borderRadius: 1, border: 1, borderColor: 'error.200' }}>
          <Typography variant="h6" color="error.main">
            ${totalOverdue.toFixed(2)}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Overdue ({overdueCount} bills)
          </Typography>
        </Box>
        <Box sx={{ p: 2, bgcolor: 'success.50', borderRadius: 1, border: 1, borderColor: 'success.200' }}>
          <Typography variant="h6" color="success.main">
            {bills.filter(b => b.status === 'paid').length}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Paid This Month
          </Typography>
        </Box>
      </Box>

      {/* Error handling */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Failed to load bills: {error}
        </Alert>
      )}

      {/* Bills Table */}
      <FinanceTable
        data={bills}
        columns={columns}
        loading={loading}
        emptyMessage="No bills found"
        pagination
        pageSize={25}
        title="Vendor Bills"
        exportable
        onExport={() => {
          // TODO: Implement export functionality
        }}
      />

      {/* Payment Dialog */}
      <Dialog
        open={showPaymentDialog}
        onClose={() => setShowPaymentDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Process Payment - {selectedBill?.vendor_name}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
            <TextField
              label="Invoice Number"
              value={selectedBill?.invoice_number || ''}
              disabled
              fullWidth
            />
            <TextField
              label="Payment Amount"
              type="number"
              value={paymentAmount}
              onChange={(e) => setPaymentAmount(e.target.value)}
              fullWidth
              InputProps={{
                startAdornment: <Typography sx={{ mr: 1 }}>$</Typography>,
              }}
            />
            <TextField
              select
              label="Payment Method"
              value={paymentMethod}
              onChange={(e) => setPaymentMethod(e.target.value)}
              fullWidth
            >
              <MenuItem value="bank_transfer">Bank Transfer</MenuItem>
              <MenuItem value="check">Check</MenuItem>
              <MenuItem value="credit_card">Credit Card</MenuItem>
              <MenuItem value="wire">Wire Transfer</MenuItem>
              <MenuItem value="ach">ACH</MenuItem>
            </TextField>
            <TextField
              label="Reference/Notes"
              multiline
              rows={3}
              placeholder="Payment reference or notes..."
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowPaymentDialog(false)}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleProcessPayment}
            startIcon={<Payment />}
          >
            Process Payment
          </Button>
        </DialogActions>
      </Dialog>

      {/* Bill Details/Edit Dialog */}
      <Dialog
        open={showBillDialog}
        onClose={() => setShowBillDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedBill ? 'Edit Bill' : 'New Bill'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
            <TextField
              label="Vendor Name"
              defaultValue={selectedBill?.vendor_name || ''}
              fullWidth
            />
            <TextField
              label="Invoice Number"
              defaultValue={selectedBill?.invoice_number || ''}
              fullWidth
            />
            <TextField
              label="Amount"
              type="number"
              defaultValue={selectedBill?.amount || ''}
              fullWidth
              InputProps={{
                startAdornment: <Typography sx={{ mr: 1 }}>$</Typography>,
              }}
            />
            <TextField
              label="Due Date"
              type="date"
              defaultValue={selectedBill?.due_date || ''}
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              select
              label="Status"
              defaultValue={selectedBill?.status || 'pending'}
              fullWidth
            >
              <MenuItem value="draft">Draft</MenuItem>
              <MenuItem value="pending">Pending</MenuItem>
              <MenuItem value="paid">Paid</MenuItem>
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowBillDialog(false)}>
            Cancel
          </Button>
          <Button variant="contained">
            {selectedBill ? 'Update' : 'Create'} Bill
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AccountsPayable;