import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  Divider
} from '@mui/material';
import {
  Calculate as CalculateIcon,
  Receipt as ReceiptIcon,
  TrendingUp as TrendingIcon,
  Save as SaveIcon
} from '@mui/icons-material';

const TaxCalculations = () => {
  const [calculationData, setCalculationData] = useState({
    amount: '',
    taxType: 'sales',
    jurisdiction: 'State',
    includeTax: true
  });
  const [calculationResult, setCalculationResult] = useState(null);
  const [recentCalculations, setRecentCalculations] = useState([]);

  const taxRates = {
    sales: {
      State: 7.25,
      City: 8.875,
      County: 2.5
    },
    vat: {
      Federal: 20,
      State: 10
    },
    corporate: {
      Federal: 21
    }
  };

  useEffect(() => {
    // Load recent calculations
    const recent = JSON.parse(localStorage.getItem('recentTaxCalculations') || '[]');
    setRecentCalculations(recent);
  }, []);

  const handleCalculate = () => {
    if (!calculationData.amount || !calculationData.taxType || !calculationData.jurisdiction) {
      return;
    }

    const amount = parseFloat(calculationData.amount);
    const rate = taxRates[calculationData.taxType]?.[calculationData.jurisdiction] || 0;
    
    let taxAmount, totalAmount, baseAmount;
    
    if (calculationData.includeTax) {
      // Amount includes tax, calculate backwards
      totalAmount = amount;
      baseAmount = amount / (1 + rate / 100);
      taxAmount = totalAmount - baseAmount;
    } else {
      // Amount is base, add tax
      baseAmount = amount;
      taxAmount = amount * (rate / 100);
      totalAmount = baseAmount + taxAmount;
    }

    const result = {
      baseAmount: baseAmount.toFixed(2),
      taxAmount: taxAmount.toFixed(2),
      totalAmount: totalAmount.toFixed(2),
      rate: rate,
      type: calculationData.taxType,
      jurisdiction: calculationData.jurisdiction,
      timestamp: new Date().toISOString()
    };

    setCalculationResult(result);
    
    // Save to recent calculations
    const updated = [result, ...recentCalculations.slice(0, 9)];
    setRecentCalculations(updated);
    localStorage.setItem('recentTaxCalculations', JSON.stringify(updated));
  };

  const handleInputChange = (field, value) => {
    setCalculationData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <Box>
      <Typography variant="h5" component="h2" sx={{ fontWeight: 'bold', mb: 3 }}>
        Tax Calculator
      </Typography>

      <Grid container spacing={3}>
        {/* Calculator Form */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Calculate Tax
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Amount"
                    type="number"
                    value={calculationData.amount}
                    onChange={(e) => handleInputChange('amount', e.target.value)}
                    InputProps={{
                      startAdornment: <Typography sx={{ mr: 1 }}>$</Typography>
                    }}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Tax Type</InputLabel>
                    <Select
                      value={calculationData.taxType}
                      onChange={(e) => handleInputChange('taxType', e.target.value)}
                      label="Tax Type"
                    >
                      <MenuItem value="sales">Sales Tax</MenuItem>
                      <MenuItem value="vat">VAT</MenuItem>
                      <MenuItem value="corporate">Corporate Tax</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Jurisdiction</InputLabel>
                    <Select
                      value={calculationData.jurisdiction}
                      onChange={(e) => handleInputChange('jurisdiction', e.target.value)}
                      label="Jurisdiction"
                    >
                      <MenuItem value="State">State</MenuItem>
                      <MenuItem value="City">City</MenuItem>
                      <MenuItem value="County">County</MenuItem>
                      <MenuItem value="Federal">Federal</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Calculation Type</InputLabel>
                    <Select
                      value={calculationData.includeTax ? 'include' : 'exclude'}
                      onChange={(e) => handleInputChange('includeTax', e.target.value === 'include')}
                      label="Calculation Type"
                    >
                      <MenuItem value="include">Amount includes tax</MenuItem>
                      <MenuItem value="exclude">Amount excludes tax</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12}>
                  <Button
                    fullWidth
                    variant="contained"
                    startIcon={<CalculateIcon />}
                    onClick={handleCalculate}
                    disabled={!calculationData.amount}
                    size="large"
                    sx={{ mt: 2 }}
                  >
                    Calculate Tax
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Results */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Calculation Results
              </Typography>
              
              {calculationResult ? (
                <Box>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography color="textSecondary" gutterBottom>
                        Base Amount
                      </Typography>
                      <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                        ${calculationResult.baseAmount}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography color="textSecondary" gutterBottom>
                        Tax Amount
                      </Typography>
                      <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'error.main' }}>
                        ${calculationResult.taxAmount}
                      </Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Divider sx={{ my: 2 }} />
                      <Typography color="textSecondary" gutterBottom>
                        Total Amount
                      </Typography>
                      <Typography variant="h3" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                        ${calculationResult.totalAmount}
                      </Typography>
                    </Grid>
                  </Grid>
                  
                  <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                    <Typography variant="body2" color="textSecondary">
                      <strong>Tax Rate:</strong> {calculationResult.rate}% ({calculationResult.type} - {calculationResult.jurisdiction})
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      <strong>Calculation:</strong> {calculationData.includeTax ? 'Amount includes tax' : 'Amount excludes tax'}
                    </Typography>
                  </Box>
                </Box>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <CalculateIcon sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
                  <Typography color="textSecondary">
                    Enter amount and tax details to calculate
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Calculations */}
        <Grid item xs={12}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Recent Calculations
              </Typography>
              
              {recentCalculations.length > 0 ? (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Date</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Base Amount</TableCell>
                        <TableCell>Tax Amount</TableCell>
                        <TableCell>Total Amount</TableCell>
                        <TableCell>Rate</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {recentCalculations.map((calc, index) => (
                        <TableRow key={index} hover>
                          <TableCell>
                            {new Date(calc.timestamp).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={`${calc.type} - ${calc.jurisdiction}`}
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography sx={{ fontWeight: 'bold' }}>
                              ${calc.baseAmount}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography sx={{ fontWeight: 'bold', color: 'error.main' }}>
                              ${calc.taxAmount}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography sx={{ fontWeight: 'bold', color: 'success.main' }}>
                              ${calc.totalAmount}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" color="textSecondary">
                              {calc.rate}%
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <ReceiptIcon sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
                  <Typography color="textSecondary">
                    No recent calculations
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default TaxCalculations;




