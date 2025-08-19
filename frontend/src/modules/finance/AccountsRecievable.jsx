import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Chip,
  Stack,
  Alert,
  IconButton,
  Tooltip,
  Card,
  CardContent,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem
} from '@mui/material';
import {
  Add,
  Payment,
  Send,
  Edit,
  Visibility,
  Email,
  CheckCircle
} from '@mui/icons-material';
import { useFinanceData } from './context/FinanceDataContext';
import { useCurrency } from '../../contexts/CurrencyContext';
import { useCurrencyConversion } from '../../hooks/useCurrencyConversion';
import FinanceTable from '../../components/tables/FinanceTable';
import InvoiceForm from './forms/InvoiceForm';

const AccountsReceivable = () => {
  const { 
    invoices, 
    loading, 
    errors, 
    refreshInvoices: refresh,
    addInvoice,
    recordPayment
  } = useFinanceData();

  // Currency conversion
  const { selectedCurrency } = useCurrency();
  const { 
    data: convertedInvoices, 
    formatAmount 
  } = useCurrencyConversion(invoices, 'invoices');
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [showInvoiceForm, setShowInvoiceForm] = useState(false);
  const [showPaymentDialog, setShowPaymentDialog] = useState(false);
  const [paymentAmount, setPaymentAmount] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('bank_transfer');

  const handleCreateInvoice = () => {
    setSelectedInvoice(null);
    setShowInvoiceForm(true);
  };

  const handleEditInvoice = (invoice) => {
    setSelectedInvoice(invoice);
    setShowInvoiceForm(true);
  };

  const handleRecordPayment = (invoice) => {
    setSelectedInvoice(invoice);
    setPaymentAmount(invoice.amount?.toString() || '');
    setShowPaymentDialog(true);
  };

  // Use converted invoices for display
  const displayInvoices = convertedInvoices || invoices;

  const handleSendReminder = async (invoice) => {
    console.log('📧 Sending payment reminder for invoice:', invoice.invoice_number);
    // TODO: Implement email reminder functionality
    alert(`Payment reminder sent to ${invoice.customer_name} (${invoice.customer_email})`);
  };

  const handleProcessPayment = async () => {
    const paymentData = {
      amount: parseFloat(paymentAmount),
      method: paymentMethod,
      date: new Date().toISOString().slice(0, 10)
    };
    
    console.log('💰 Recording payment:', {
      invoice: selectedInvoice,
      payment: paymentData
    });
    
    // Record payment in centralized state
    recordPayment(selectedInvoice.id, paymentData);
    
    setShowPaymentDialog(false);
    setSelectedInvoice(null);
    setPaymentAmount('');
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
      header: 'Invoice #',
      accessor: 'invoice_number',
      width: '150px',
      sortable: true,
      cell: (invoiceNum) => (
        <Typography variant="body2" fontFamily="monospace" fontWeight="medium">
          {invoiceNum}
        </Typography>
      )
    },
    {
      header: 'Customer',
      accessor: 'customer_name',
      sortable: true,
      cell: (customer) => (
        <Typography variant="body2" fontWeight="medium">
          {customer}
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
      header: 'Invoice Date',
      accessor: 'invoice_date',
      width: '120px',
      sortable: true,
      cell: (date) => new Date(date).toLocaleDateString()
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
      width: '280px',
      cell: (id, row) => (
        <Stack direction="row" spacing={1}>
          {row.status !== 'paid' && (
            <>
              <Tooltip title="Record Payment">
                <Button
                  size="small"
                  variant="outlined"
                  color="success"
                  startIcon={<Payment />}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRecordPayment(row);
                  }}
                >
                  Pay
                </Button>
              </Tooltip>
              <Tooltip title="Send Reminder">
                <IconButton
                  size="small"
                  color="warning"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleSendReminder(row);
                  }}
                >
                  <Send fontSize="small" />
                </IconButton>
              </Tooltip>
            </>
          )}
          <Tooltip title="Edit Invoice">
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                handleEditInvoice(row);
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
                setSelectedInvoice(row);
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
  const totalOutstanding = invoices
    .filter(invoice => invoice.status !== 'paid')
    .reduce((sum, invoice) => sum + (invoice.amount || 0), 0);

  const totalOverdue = invoices
    .filter(invoice => invoice.status !== 'paid' && getDaysOverdue(invoice.due_date) > 0)
    .reduce((sum, invoice) => sum + (invoice.amount || 0), 0);

  const overdueCount = invoices
    .filter(invoice => invoice.status !== 'paid' && getDaysOverdue(invoice.due_date) > 0)
    .length;

  const avgDaysToPayment = 25; // TODO: Calculate actual average

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Accounts Receivable
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleCreateInvoice}
        >
          Create Invoice
        </Button>
      </Box>

      {/* Summary Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2, mb: 3 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" color="primary.main">
              ${totalOutstanding.toFixed(2)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Outstanding
            </Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography variant="h6" color="error.main">
              ${totalOverdue.toFixed(2)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Overdue ({overdueCount} invoices)
            </Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography variant="h6" color="success.main">
              {invoices.filter(i => i.status === 'paid').length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Paid This Month
            </Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography variant="h6" color="info.main">
              {avgDaysToPayment} days
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Avg Days to Payment
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Error handling */}
      {errors.invoices && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Failed to load invoices: {errors.invoices}
        </Alert>
      )}

      {/* Invoices Table */}
      <FinanceTable
        data={invoices}
        columns={columns}
        loading={loading.invoices}
        emptyMessage="No invoices found"
        pagination
        pageSize={25}
        title="Customer Invoices"
        exportable
        onExport={() => {
          console.log('📊 Exporting AR data...');
          // TODO: Implement export functionality
        }}
      />

      {/* Invoice Form Dialog */}
      <InvoiceForm
        open={showInvoiceForm}
        onClose={() => {
          setShowInvoiceForm(false);
          setSelectedInvoice(null);
        }}
        invoice={selectedInvoice}
        onSave={(invoiceData) => {
          console.log('✅ Invoice saved:', invoiceData);
          addInvoice(invoiceData);
        }}
      />

      {/* Payment Recording Dialog */}
      <Dialog
        open={showPaymentDialog}
        onClose={() => setShowPaymentDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Record Payment - {selectedInvoice?.customer_name}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
            <TextField
              label="Invoice Number"
              value={selectedInvoice?.invoice_number || ''}
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
              <MenuItem value="cash">Cash</MenuItem>
              <MenuItem value="wire">Wire Transfer</MenuItem>
            </TextField>
            <TextField
              label="Payment Date"
              type="date"
              defaultValue={new Date().toISOString().slice(0, 10)}
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
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
            startIcon={<CheckCircle />}
          >
            Record Payment
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AccountsReceivable;