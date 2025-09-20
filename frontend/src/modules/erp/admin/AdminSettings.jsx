import React, { useEffect, useState, useCallback } from 'react';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Card,
  CardContent,
  Grid,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Switch,
  FormControlLabel,
  Button,
  Divider,
  Alert,
  Snackbar
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import RefreshIcon from '@mui/icons-material/Refresh';
import CurrencyExchangeIcon from '@mui/icons-material/CurrencyExchange';
import SecurityIcon from '@mui/icons-material/Security';
import EmailIcon from '@mui/icons-material/Email';
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong';
import PublicIcon from '@mui/icons-material/Public';
import SettingsIcon from '@mui/icons-material/Settings';
import PeopleIcon from '@mui/icons-material/People';
import apiClient from '../../../services/apiClient';
import UserManagement from './UserManagement';
import PermissionTester from '../../../components/PermissionTester';
import AuditDashboard from './AuditDashboard';
import SecuritySettings from './SecuritySettings';

// Constants
const AVAILABLE_CURRENCIES = [
  'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'INR', 'BRL', 
  'KRW', 'SGD', 'HKD', 'MXN', 'NOK', 'SEK', 'DKK', 'PLN', 'CZK', 'HUF'
];

const SectionCard = ({ title, icon, children, onSave, onReset, saving }) => (
  <Card sx={{ mb: 3 }}>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {icon}
          <Typography variant="h6">{title}</Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<RefreshIcon />} onClick={onReset}>Reset</Button>
          <Button variant="contained" startIcon={<SaveIcon />} onClick={onSave} disabled={saving}>
            {saving ? 'Saving…' : 'Save'}
          </Button>
        </Box>
      </Box>
      {children}
    </CardContent>
  </Card>
);

const AdminSettings = () => {
  const [tab, setTab] = useState(0);
  const [saving, setSaving] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  // Sections state - Initialize with empty/neutral defaults
  const [currency, setCurrency] = useState({ base_currency: '', allowed_currencies: [], rate_source: '', rounding: 2 });
  const [tax, setTax] = useState({ default_rate: 0, tax_inclusive: false, jurisdiction: '' });
  const [documents, setDocuments] = useState({ invoice_prefix: '', po_prefix: '', so_prefix: '', default_terms_days: 0 });
  const [email, setEmail] = useState({ from_name: '', from_email: '', provider: '' });
  const [security, setSecurity] = useState({ session_timeout_minutes: 0, password_policy: '' });
  const [localization, setLocalization] = useState({ timezone: '', locale: '', fiscal_year_start: '' });
  const [features, setFeatures] = useState({ enable_ai: false, enable_kb: false });
  const [userPermissions, setUserPermissions] = useState({ 
    defaultUserRole: '', 
    restrictionLevel: '', 
    allowRoleOverride: false, 
    requireApprovalForAdjustments: false,
    enableAuditTrail: false
  });

  const loadSection = useCallback(async (section, setter, transform) => {
    try {
      const res = await apiClient.getSettingsSection(section);
      const data = res?.data || res;
      if (data && Object.keys(data).length > 0) {
        setter(prevState => ({ ...prevState, ...(transform ? transform(data) : data) }));
      }
      // If no data, keep existing defaults
    } catch (e) {
      // Keep defaults - don't overwrite state
    }
  }, []);

  const loadAll = useCallback(async () => {
    await Promise.all([
      loadSection('currency', setCurrency),
      loadSection('tax', setTax),
      loadSection('documents', setDocuments),
      loadSection('email', setEmail),
      loadSection('security', setSecurity),
      loadSection('localization', setLocalization),
      loadSection('features', setFeatures),
      loadSection('userPermissions', setUserPermissions)
    ]);
  }, [loadSection]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  const saveSection = async (section, data) => {
    try {
      setSaving(true);
      await apiClient.putSettingsSection(section, { data });
      
      // Also save to localStorage for immediate access by other components
      if (section === 'userPermissions') {
        localStorage.setItem('adminSettings_userPermissions', JSON.stringify(data));
      }
      
      setSnackbar({ open: true, message: 'Settings saved', severity: 'success' });
    } catch (e) {
      setSnackbar({ open: true, message: 'Failed to save', severity: 'error' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <SettingsIcon color="primary" /> Admin Settings
      </Typography>

      <Tabs value={tab} onChange={(e, v) => setTab(v)} sx={{ mb: 2 }}>
        <Tab label="User Management" />
        <Tab label="Audit Dashboard" />
        <Tab label="Security Settings" />
        <Tab label="Permission Testing" />
        <Tab label="User Permissions" />
        <Tab label="Currency & FX" />
        <Tab label="Tax" />
        <Tab label="Documents" />
        <Tab label="Email" />
        <Tab label="Security" />
        <Tab label="Localization" />
        <Tab label="Features" />
      </Tabs>

      {tab === 0 && (
        <UserManagement />
      )}

      {tab === 1 && (
        <AuditDashboard />
      )}

      {tab === 2 && (
        <SecuritySettings />
      )}

      {tab === 3 && (
        <PermissionTester />
      )}

      {tab === 4 && (
        <SectionCard
          title="User Permissions & Smart Entry Settings"
          icon={<SecurityIcon color="primary" />}
          onSave={() => saveSection('userPermissions', userPermissions)}
          onReset={loadAll}
          saving={saving}
        >
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
              <strong>Enterprise Configuration:</strong> Configure how your organization handles user permissions 
              and access control. These settings apply to all users in your system.
            </Typography>
          </Alert>

          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Default User Role</InputLabel>
                <Select
                  value={userPermissions.defaultUserRole || ''}
                  onChange={(e) => setUserPermissions({ ...userPermissions, defaultUserRole: e.target.value })}
                  label="Default User Role"
                  displayEmpty
                >
                  <MenuItem value="">
                    <em>Select Default Role</em>
                  </MenuItem>
                  <MenuItem value="user">Regular User</MenuItem>
                  <MenuItem value="accountant">Accountant</MenuItem>
                  <MenuItem value="admin">Administrator</MenuItem>
                  <MenuItem value="manager">Manager</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Access Control Level</InputLabel>
                <Select
                  value={userPermissions.restrictionLevel || ''}
                  onChange={(e) => setUserPermissions({ ...userPermissions, restrictionLevel: e.target.value })}
                  label="Access Control Level"
                  displayEmpty
                >
                  <MenuItem value="">
                    <em>Select Access Level</em>
                  </MenuItem>
                  <MenuItem value="none">Open - Full access for all users</MenuItem>
                  <MenuItem value="flexible">Flexible - Role-based with overrides</MenuItem>
                  <MenuItem value="strict">Strict - Enforce role restrictions</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          <Box sx={{ mt: 2 }}>
            <FormControlLabel 
              control={
                <Switch 
                  checked={Boolean(userPermissions.allowRoleOverride)} 
                  onChange={(e) => setUserPermissions({ ...userPermissions, allowRoleOverride: e.target.checked })} 
                />
              } 
              label="Allow users to temporarily override their role permissions" 
            />
          </Box>

          <Box sx={{ mt: 1 }}>
            <FormControlLabel 
              control={
                <Switch 
                  checked={Boolean(userPermissions.requireApprovalForAdjustments)} 
                  onChange={(e) => setUserPermissions({ ...userPermissions, requireApprovalForAdjustments: e.target.checked })} 
                />
              } 
              label="Require approval for adjustment entries and reversals" 
            />
          </Box>

          <Box sx={{ mt: 1 }}>
            <FormControlLabel 
              control={
                <Switch 
                  checked={Boolean(userPermissions.enableAuditTrail)} 
                  onChange={(e) => setUserPermissions({ ...userPermissions, enableAuditTrail: e.target.checked })} 
                />
              } 
              label="Enable detailed audit trail for permission overrides" 
            />
          </Box>

          <Divider sx={{ my: 2 }} />

          <Typography variant="body2" color="textSecondary">
            <strong>Current Configuration:</strong>
            <br />
            • Default Role: <strong>{userPermissions.defaultUserRole}</strong>
            <br />
            • Restriction Level: <strong>{userPermissions.restrictionLevel}</strong>
            <br />
            • Role Override: <strong>{userPermissions.allowRoleOverride ? 'Enabled' : 'Disabled'}</strong>
            <br />
            • Approval Required: <strong>{userPermissions.requireApprovalForAdjustments ? 'Yes' : 'No'}</strong>
          </Typography>
        </SectionCard>
      )}

      {tab === 5 && (
        <SectionCard
          title="Currency & FX"
          icon={<CurrencyExchangeIcon color="primary" />}
          onSave={() => saveSection('currency', currency)}
          onReset={loadAll}
          saving={saving}
        >
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Base Currency</InputLabel>
                <Select
                  label="Base Currency"
                  value={currency.base_currency || ''}
                  onChange={(e) => setCurrency({ ...currency, base_currency: e.target.value })}
                  displayEmpty
                >
                  <MenuItem value="">
                    <em>Select Currency</em>
                  </MenuItem>
                  {AVAILABLE_CURRENCIES.map(c => (
                    <MenuItem key={c} value={c}>{c}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Rate Source</InputLabel>
                <Select
                  label="Rate Source"
                  value={currency.rate_source || ''}
                  onChange={(e) => setCurrency({ ...currency, rate_source: e.target.value })}
                  displayEmpty
                >
                  <MenuItem value="">
                    <em>Select Rate Source</em>
                  </MenuItem>
                  <MenuItem value="manual">Manual</MenuItem>
                  <MenuItem value="provider">Provider</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Rounding (decimals)"
                type="number"
                value={currency.rounding ?? 2}
                onChange={(e) => setCurrency({ ...currency, rounding: parseInt(e.target.value || '0', 10) })}
              />
            </Grid>
          </Grid>
          <Divider sx={{ my: 2 }} />
          <Alert severity="info">Changing base currency affects new documents; historical documents keep their locked values.</Alert>
        </SectionCard>
      )}

      {tab === 6 && (
        <SectionCard
          title="Tax Settings"
          icon={<ReceiptLongIcon color="primary" />}
          onSave={() => saveSection('tax', tax)}
          onReset={loadAll}
          saving={saving}
        >
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Default Tax Rate (%)"
                type="number"
                value={tax.default_rate ?? 0}
                onChange={(e) => setTax({ ...tax, default_rate: parseFloat(e.target.value || '0') })}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={<Switch checked={!!tax.tax_inclusive} onChange={(e) => setTax({ ...tax, tax_inclusive: e.target.checked })} />}
                label="Tax Inclusive Pricing"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Jurisdiction"
                value={tax.jurisdiction || ''}
                onChange={(e) => setTax({ ...tax, jurisdiction: e.target.value })}
              />
            </Grid>
          </Grid>
        </SectionCard>
      )}

      {tab === 7 && (
        <SectionCard
          title="Document Settings"
          icon={<ReceiptLongIcon color="primary" />}
          onSave={() => saveSection('documents', documents)}
          onReset={loadAll}
          saving={saving}
        >
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}><TextField fullWidth label="Invoice Prefix" value={documents.invoice_prefix || ''} onChange={(e) => setDocuments({ ...documents, invoice_prefix: e.target.value })} /></Grid>
            <Grid item xs={12} md={3}><TextField fullWidth label="PO Prefix" value={documents.po_prefix || ''} onChange={(e) => setDocuments({ ...documents, po_prefix: e.target.value })} /></Grid>
            <Grid item xs={12} md={3}><TextField fullWidth label="SO Prefix" value={documents.so_prefix || ''} onChange={(e) => setDocuments({ ...documents, so_prefix: e.target.value })} /></Grid>
            <Grid item xs={12} md={3}><TextField fullWidth label="Default Terms (days)" type="number" value={documents.default_terms_days ?? 30} onChange={(e) => setDocuments({ ...documents, default_terms_days: parseInt(e.target.value || '0', 10) })} /></Grid>
          </Grid>
        </SectionCard>
      )}

      {tab === 8 && (
        <SectionCard
          title="Email Settings"
          icon={<EmailIcon color="primary" />}
          onSave={() => saveSection('email', email)}
          onReset={loadAll}
          saving={saving}
        >
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}><TextField fullWidth label="From Name" value={email.from_name || ''} onChange={(e) => setEmail({ ...email, from_name: e.target.value })} /></Grid>
            <Grid item xs={12} md={4}><TextField fullWidth label="From Email" value={email.from_email || ''} onChange={(e) => setEmail({ ...email, from_email: e.target.value })} /></Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Provider</InputLabel>
                <Select label="Provider" value={email.provider || ''} onChange={(e) => setEmail({ ...email, provider: e.target.value })} displayEmpty>
                  <MenuItem value="">
                    <em>Select Provider</em>
                  </MenuItem>
                  <MenuItem value="smtp">SMTP</MenuItem>
                  <MenuItem value="sendgrid">SendGrid</MenuItem>
                  <MenuItem value="postmark">Postmark</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
          <Divider sx={{ my: 2 }} />
          <Alert severity="info">Verify your domain with your provider to improve deliverability.</Alert>
        </SectionCard>
      )}

      {tab === 9 && (
        <SectionCard
          title="Security Settings"
          icon={<SecurityIcon color="primary" />}
          onSave={() => saveSection('security', security)}
          onReset={loadAll}
          saving={saving}
        >
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}><TextField fullWidth label="Session Timeout (minutes)" type="number" value={security.session_timeout_minutes || ''} onChange={(e) => setSecurity({ ...security, session_timeout_minutes: parseInt(e.target.value || '0', 10) })} /></Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Password Policy</InputLabel>
                <Select label="Password Policy" value={security.password_policy || ''} onChange={(e) => setSecurity({ ...security, password_policy: e.target.value })} displayEmpty>
                  <MenuItem value="">
                    <em>Select Policy</em>
                  </MenuItem>
                  <MenuItem value="standard">Standard</MenuItem>
                  <MenuItem value="strict">Strict</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </SectionCard>
      )}

      {tab === 10 && (
        <SectionCard
          title="Localization"
          icon={<PublicIcon color="primary" />}
          onSave={() => saveSection('localization', localization)}
          onReset={loadAll}
          saving={saving}
        >
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}><TextField fullWidth label="Timezone" value={localization.timezone || ''} onChange={(e) => setLocalization({ ...localization, timezone: e.target.value })} /></Grid>
            <Grid item xs={12} md={4}><TextField fullWidth label="Locale" value={localization.locale || ''} onChange={(e) => setLocalization({ ...localization, locale: e.target.value })} /></Grid>
            <Grid item xs={12} md={4}><TextField fullWidth label="Fiscal Year Start (MM-DD)" value={localization.fiscal_year_start || ''} onChange={(e) => setLocalization({ ...localization, fiscal_year_start: e.target.value })} /></Grid>
          </Grid>
        </SectionCard>
      )}

      {tab === 11 && (
        <SectionCard
          title="Features"
          icon={<SettingsIcon color="primary" />}
          onSave={() => saveSection('features', features)}
          onReset={loadAll}
          saving={saving}
        >
          <FormControlLabel control={<Switch checked={!!features.enable_ai} onChange={(e) => setFeatures({ ...features, enable_ai: e.target.checked })} />} label="Enable AI" />
          <FormControlLabel control={<Switch checked={!!features.enable_kb} onChange={(e) => setFeatures({ ...features, enable_kb: e.target.checked })} />} label="Enable Knowledge Base" />
        </SectionCard>
      )}


      <Snackbar open={snackbar.open} autoHideDuration={4000} onClose={() => setSnackbar({ ...snackbar, open: false })}>
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default AdminSettings;


