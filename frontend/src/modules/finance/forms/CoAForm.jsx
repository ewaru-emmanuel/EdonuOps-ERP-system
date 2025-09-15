import React, { useState, useEffect } from 'react';
import {
  Box, TextField, Button, MenuItem, Stack, Alert, Chip, FormControl, InputLabel, Select, Checkbox, ListItemText
} from '@mui/material';
import { useCoA } from '../context/CoAContext';

const accountTypes = ['asset', 'liability', 'equity', 'revenue', 'expense'];

const CoAForm = ({ selectedAccount, onDone }) => {
  const { addAccount, updateAccount } = useCoA();
  
  // Default values for missing context properties
  const dimensions = [];
  const isAccountCodeUnique = () => true;
  const getAccountHierarchy = () => [];
  const [form, setForm] = useState({
    name: '',
    category: '',
    type: '',
    description: '',
    isActive: true,
  });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (selectedAccount) {
      setForm({
        name: selectedAccount.name || '',
        category: selectedAccount.category || '',
        type: selectedAccount.type || '',
        description: selectedAccount.description || '',
        isActive: selectedAccount.isActive !== false,
      });
    } else {
      setForm({ 
        name: '', 
        category: '', 
        type: '', 
        description: '',
        isActive: true
      });
    }
    setError(null);
    setSuccess(null);
  }, [selectedAccount]);

  const handleSubmit = async () => {
    if (submitting) return;
    
    setError(null);
    setSubmitting(true);
    
    try {
      // Basic validation
      if (!form.name.trim()) {
        throw new Error('Account name is required');
      }
      if (!form.category) {
        throw new Error('Account category is required');
      }
      if (!form.type) {
        throw new Error('Account type is required');
      }

      // Save
      if (selectedAccount) {
        await updateAccount(selectedAccount.id, form);
        setSuccess('Account updated successfully!');
      } else {
        await addAccount(form);
        setSuccess('Account created successfully!');
        setForm({ 
          name: '', 
          category: '', 
          type: '', 
          description: '',
          isActive: true
        });
      }
      
      // Close form after short delay
      setTimeout(() => {
        onDone?.();
      }, 1500);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box mt={2}>
      <Stack spacing={2}>
        {error && <Alert severity="error">{error}</Alert>}
        {success && <Alert severity="success">{success}</Alert>}

        <TextField 
          select 
          label="Account Category*" 
          name="category" 
          value={form.category} 
          onChange={(e) => setForm({ ...form, category: e.target.value })}
          error={!!error && error.includes('category')}
          disabled={submitting}
        >
          {accountTypes.map((type) => (
            <MenuItem key={type} value={type}>
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </MenuItem>
          ))}
        </TextField>

        <TextField 
          label="Account Name*" 
          name="name" 
          value={form.name} 
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          error={!!error && error.includes('name')}
          disabled={submitting}
        />

        <TextField 
          label="Account Type*" 
          name="type" 
          value={form.type} 
          onChange={(e) => setForm({ ...form, type: e.target.value })}
          error={!!error && error.includes('type')}
          placeholder="e.g., Current Asset, Fixed Asset, etc."
          disabled={submitting}
        />

        <TextField 
          label="Description" 
          name="description" 
          value={form.description} 
          onChange={(e) => setForm({ ...form, description: e.target.value })}
          multiline
          rows={2}
          placeholder="Optional description for this account"
          disabled={submitting}
        />


        <Button 
          variant="contained" 
          onClick={handleSubmit}
          disabled={submitting}
        >
          {submitting ? 'Saving...' : (selectedAccount ? 'Update Account' : 'Create Account')}
        </Button>
      </Stack>
    </Box>
  );
};

export default CoAForm;