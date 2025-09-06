import React, { useEffect, useState } from 'react';
import {
  Box, Typography, Card, CardContent, Grid, TextField, Button, Table, TableBody, TableCell, TableHead, TableRow, Dialog, DialogTitle, DialogContent, DialogActions, Snackbar, Alert
} from '@mui/material';
import apiClient from '../../../services/apiClient';

const SmartTransfers = () => {
  const [transfers, setTransfers] = useState([]);
  const [valuation, setValuation] = useState([]);
  const [createOpen, setCreateOpen] = useState(false);
  const [shipOpen, setShipOpen] = useState(false);
  const [receiveOpen, setReceiveOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [draft, setDraft] = useState({ from_warehouse_id: '', to_warehouse_id: '', lines: [{ product_id: '', quantity: '' }] });
  const [selectedTransfer, setSelectedTransfer] = useState(null);
  const [lineOps, setLineOps] = useState([{ line_id: '', quantity: '' }]);

  const loadData = async () => {
    try { setTransfers(await apiClient.get('/api/inventory/warehouse/transfers')); } catch {}
    try { const v = await apiClient.get('/api/inventory/warehouse/valuation/warehouse'); setValuation(v.warehouses || []); } catch {}
  };

  useEffect(() => { loadData(); }, []);

  const addDraftLine = () => setDraft({ ...draft, lines: [...draft.lines, { product_id: '', quantity: '' }] });
  const updateDraftLine = (idx, field, value) => {
    const lines = draft.lines.map((l, i) => (i === idx ? { ...l, [field]: value } : l));
    setDraft({ ...draft, lines });
  };

  const createTransfer = async () => {
    try {
      const payload = {
        from_warehouse_id: Number(draft.from_warehouse_id),
        to_warehouse_id: Number(draft.to_warehouse_id),
        lines: draft.lines.map(l => ({ product_id: Number(l.product_id), quantity: Number(l.quantity) }))
      };
      await apiClient.post('/api/inventory/warehouse/transfers', payload);
      setCreateOpen(false);
      setDraft({ from_warehouse_id: '', to_warehouse_id: '', lines: [{ product_id: '', quantity: '' }] });
      setSnackbar({ open: true, message: 'Transfer created', severity: 'success' });
      loadData();
    } catch {
      setSnackbar({ open: true, message: 'Failed to create transfer', severity: 'error' });
    }
  };

  const doShip = async () => {
    try {
      const payload = { lines: lineOps.map(l => ({ line_id: Number(l.line_id), quantity: Number(l.quantity) })) };
      await apiClient.post(`/api/inventory/warehouse/transfers/${selectedTransfer.id}/ship`, payload);
      setShipOpen(false); setLineOps([{ line_id: '', quantity: '' }]); setSelectedTransfer(null);
      setSnackbar({ open: true, message: 'Shipped', severity: 'success' });
      loadData();
    } catch { setSnackbar({ open: true, message: 'Ship failed', severity: 'error' }); }
  };

  const doReceive = async () => {
    try {
      const payload = { lines: lineOps.map(l => ({ line_id: Number(l.line_id), quantity: Number(l.quantity) })), warehouse_id: selectedTransfer?.to_warehouse_id };
      await apiClient.post(`/api/inventory/warehouse/transfers/${selectedTransfer.id}/receive`, payload);
      setReceiveOpen(false); setLineOps([{ line_id: '', quantity: '' }]); setSelectedTransfer(null);
      setSnackbar({ open: true, message: 'Received', severity: 'success' });
      loadData();
    } catch { setSnackbar({ open: true, message: 'Receive failed', severity: 'error' }); }
  };

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box>
          <Typography variant="h6" gutterBottom>Transfers</Typography>
          <Typography variant="body2" color="text.secondary">Create, ship, and receive inter‑warehouse transfers</Typography>
        </Box>
        <Button variant="contained" onClick={() => setCreateOpen(true)}>New Transfer</Button>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} md={7}>
          <Card>
            <CardContent>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Number</TableCell>
                    <TableCell>From</TableCell>
                    <TableCell>To</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {transfers.map(tr => (
                    <TableRow key={tr.id}>
                      <TableCell>{tr.number}</TableCell>
                      <TableCell>{tr.from_warehouse_id}</TableCell>
                      <TableCell>{tr.to_warehouse_id}</TableCell>
                      <TableCell>{tr.status}</TableCell>
                      <TableCell>
                        <Button size="small" onClick={() => { setSelectedTransfer(tr); setShipOpen(true); }}>Ship</Button>
                        <Button size="small" onClick={() => { setSelectedTransfer(tr); setReceiveOpen(true); }}>Receive</Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={5}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>Warehouse Valuation</Typography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Warehouse</TableCell>
                    <TableCell align="right">On Hand</TableCell>
                    <TableCell align="right">Avg Cost</TableCell>
                    <TableCell align="right">Valuation</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {valuation.map(v => (
                    <TableRow key={v.warehouse_id}>
                      <TableCell>{v.warehouse_name}</TableCell>
                      <TableCell align="right">{v.on_hand}</TableCell>
                      <TableCell align="right">{v.avg_cost}</TableCell>
                      <TableCell align="right">{v.valuation_base}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Create Transfer Dialog */}
      <Dialog open={createOpen} onClose={() => setCreateOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New Transfer</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="From Warehouse ID" value={draft.from_warehouse_id} onChange={(e) => setDraft({ ...draft, from_warehouse_id: e.target.value })} sx={{ mb: 2 }} />
          <TextField fullWidth label="To Warehouse ID" value={draft.to_warehouse_id} onChange={(e) => setDraft({ ...draft, to_warehouse_id: e.target.value })} sx={{ mb: 2 }} />
          {draft.lines.map((ln, idx) => (
            <Box key={idx} sx={{ display: 'flex', gap: 1, mb: 1 }}>
              <TextField label="Product ID" value={ln.product_id} onChange={(e) => updateDraftLine(idx, 'product_id', e.target.value)} />
              <TextField label="Qty" type="number" value={ln.quantity} onChange={(e) => updateDraftLine(idx, 'quantity', e.target.value)} />
            </Box>
          ))}
          <Button onClick={addDraftLine}>Add Line</Button>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={createTransfer}>Create</Button>
        </DialogActions>
      </Dialog>

      {/* Ship Dialog */}
      <Dialog open={shipOpen} onClose={() => setShipOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Ship Transfer</DialogTitle>
        <DialogContent>
          {lineOps.map((op, idx) => (
            <Box key={idx} sx={{ display: 'flex', gap: 1, mb: 1 }}>
              <TextField label="Line ID" value={op.line_id} onChange={(e) => setLineOps(lineOps.map((o, i) => i === idx ? { ...o, line_id: e.target.value } : o))} />
              <TextField label="Qty" type="number" value={op.quantity} onChange={(e) => setLineOps(lineOps.map((o, i) => i === idx ? { ...o, quantity: e.target.value } : o))} />
            </Box>
          ))}
          <Button onClick={() => setLineOps([...lineOps, { line_id: '', quantity: '' }])}>Add</Button>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShipOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={doShip}>Ship</Button>
        </DialogActions>
      </Dialog>

      {/* Receive Dialog */}
      <Dialog open={receiveOpen} onClose={() => setReceiveOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Receive Transfer</DialogTitle>
        <DialogContent>
          {lineOps.map((op, idx) => (
            <Box key={idx} sx={{ display: 'flex', gap: 1, mb: 1 }}>
              <TextField label="Line ID" value={op.line_id} onChange={(e) => setLineOps(lineOps.map((o, i) => i === idx ? { ...o, line_id: e.target.value } : o))} />
              <TextField label="Qty" type="number" value={op.quantity} onChange={(e) => setLineOps(lineOps.map((o, i) => i === idx ? { ...o, quantity: e.target.value } : o))} />
            </Box>
          ))}
          <Button onClick={() => setLineOps([...lineOps, { line_id: '', quantity: '' }])}>Add</Button>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReceiveOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={doReceive}>Receive</Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={snackbar.open} autoHideDuration={4000} onClose={() => setSnackbar({ ...snackbar, open: false })}>
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default SmartTransfers;


