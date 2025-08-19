import React from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Button, Table, TableHead, TableBody,
  TableRow, TableCell, Typography
} from '@mui/material';
import { format } from 'date-fns';

const AuditTrailModal = ({ open, onClose, data = [] }) => {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Journal Entry History</DialogTitle>
      <DialogContent>
        {data.length === 0 ? (
          <Typography>No history available</Typography>
        ) : (
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>User</TableCell>
                <TableCell>Action</TableCell>
                <TableCell>Changes</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.map((item, idx) => (
                <TableRow key={idx}>
                  <TableCell>
                    {format(new Date(item.timestamp), 'PPpp')}
                  </TableCell>
                  <TableCell>{item.user}</TableCell>
                  <TableCell>{item.action}</TableCell>
                  <TableCell>
                    {Object.entries(item.changes).map(([field, values]) => (
                      <div key={field}>
                        <strong>{field}:</strong> {values.old} → {values.new}
                      </div>
                    ))}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default AuditTrailModal;