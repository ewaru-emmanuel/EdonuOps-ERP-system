import React from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Button, Typography, Stack, Divider, Chip
} from '@mui/material';

const SourceDocumentModal = ({ open, onClose, document }) => {
  if (!document) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        Source Document: {document.type.toUpperCase()} #{document.number}
      </DialogTitle>
      <DialogContent>
        <Stack spacing={2}>
          <Typography variant="h6">{document.vendor || document.customer}</Typography>
          <Typography>Date: {document.date}</Typography>
          <Typography>Amount: ${document.amount?.toFixed(2)}</Typography>
          <Typography>Status: {document.status}</Typography>
          
          <Divider />
          
          <Typography variant="subtitle1">Line Items</Typography>
          {document.items?.map((item, idx) => (
            <Stack key={idx} direction="row" spacing={2}>
              <Typography>{item.description}</Typography>
              <Typography flexGrow={1}>{item.quantity} × ${item.unit_price}</Typography>
              <Typography>${item.amount}</Typography>
            </Stack>
          ))}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
        <Button 
          variant="contained" 
          onClick={() => window.open(`/${document.type}/${document.id}`)}
        >
          Open Full Document
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default SourceDocumentModal;