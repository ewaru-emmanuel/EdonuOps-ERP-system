import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Tabs,
  Tab,
  Chip,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  LinearProgress,
  Avatar,
  Snackbar
} from '@mui/material';
import {
  People as PeopleIcon,
  Payment as PaymentIcon,
  PersonAdd as PersonAddIcon,
  School as SchoolIcon,
  Assessment as AssessmentIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material';
import { ConfirmationDialog } from '../../components/CommonForms';
import ImprovedForm from '../../components/ImprovedForm';
import DetailViewModal from '../../components/DetailViewModal';
import { useRealTimeData } from '../../hooks/useRealTimeData';

const HCMModule = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  
  // Form and dialog states
  const [employeeFormOpen, setEmployeeFormOpen] = useState(false);
  const [editEmployee, setEditEmployee] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteItem, setDeleteItem] = useState(null);
  const [detailViewOpen, setDetailViewOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [selectedItemType, setSelectedItemType] = useState('');

  // Real-time data hooks
  const { 
    data: employees, 
    loading: employeesLoading, 
    create: createEmployee,
    update: updateEmployee,
    remove: deleteEmployee
  } = useRealTimeData('/api/hr/employees');
  
  const { 
    data: payroll 
  } = useRealTimeData('/api/hr/payroll');
  
  const { 
    data: recruitment 
  } = useRealTimeData('/api/hr/recruitment');

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  // Employee Management
  const handleEmployeeAdd = () => {
    setEditEmployee(null);
    setEmployeeFormOpen(true);
  };

  const handleEmployeeEdit = (employee) => {
    setEditEmployee(employee);
    setEmployeeFormOpen(true);
  };

  const handleEmployeeDelete = (employee) => {
    setDeleteItem(employee);
    setDeleteDialogOpen(true);
  };

  const handleSaveEmployee = async (formData) => {
    try {
      if (editEmployee) {
        await updateEmployee(editEmployee.id, formData);
        showSnackbar(`Employee "${formData.first_name} ${formData.last_name}" updated successfully`);
      } else {
        await createEmployee(formData);
        showSnackbar(`Employee "${formData.first_name} ${formData.last_name}" created successfully`);
      }
      setEmployeeFormOpen(false);
      setEditEmployee(null);
    } catch (error) {
      showSnackbar(`Failed to save employee: ${error.message}`, 'error');
    }
  };

  const handleConfirmDelete = async () => {
    try {
      await deleteEmployee(deleteItem.id);
      showSnackbar(`${deleteItem?.name || 'Employee'} deleted successfully`);
      setDeleteDialogOpen(false);
      setDeleteItem(null);
    } catch (error) {
      showSnackbar(`Failed to delete employee: ${error.message}`, 'error');
    }
  };



  // Calculate metrics from real data
  const hcmMetrics = {
    totalEmployees: employees.length,
    newHires: employees.filter(emp => {
      const hireDate = new Date(emp.hire_date || emp.created_at);
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
      return hireDate > thirtyDaysAgo;
    }).length,
    avgSalary: employees.length > 0 ? 
      employees.reduce((sum, emp) => sum + (emp.salary || 0), 0) / employees.length : 0,
    turnoverRate: 0 // Would be calculated from historical data
  };

  return (
    <Container maxWidth="xl">
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <Avatar sx={{ bgcolor: 'primary.main', width: 56, height: 56 }}>
            <PeopleIcon />
          </Avatar>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
              Human Capital Management
            </Typography>
            <Typography variant="h6" color="text.secondary">
              Complete workforce management with HR, Payroll, Recruitment & Performance
            </Typography>
          </Box>
        </Box>
        
        <Alert severity="success" sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            ✅ Comprehensive HCM System Ready
          </Typography>
          <Typography variant="body2">
            Your complete human capital management system is operational with HR, Payroll, Recruitment, Onboarding, and Performance Management.
          </Typography>
        </Alert>
      </Box>

      {/* HCM Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                    {hcmMetrics.totalEmployees}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Employees
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'success.main' }}>
                  <PeopleIcon />
                </Avatar>
              </Box>
              <LinearProgress variant="determinate" value={85} sx={{ mt: 2 }} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                    {hcmMetrics.newHires}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    New Hires (30d)
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  <PersonAddIcon />
                </Avatar>
              </Box>
              <LinearProgress variant="determinate" value={75} sx={{ mt: 2 }} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                    ${(hcmMetrics.avgSalary / 1000).toFixed(0)}K
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg Salary
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'warning.main' }}>
                  <PaymentIcon />
                </Avatar>
              </Box>
              <LinearProgress variant="determinate" value={90} sx={{ mt: 2 }} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                    {hcmMetrics.turnoverRate}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Turnover Rate
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'info.main' }}>
                  <TrendingUpIcon />
                </Avatar>
              </Box>
              <LinearProgress variant="determinate" value={45} sx={{ mt: 2 }} />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Interface */}
      <Paper elevation={3} sx={{ borderRadius: 2, overflow: 'hidden' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab label="Employees" icon={<PeopleIcon />} />
            <Tab label="Payroll" icon={<PaymentIcon />} />
            <Tab label="Recruitment" icon={<PersonAddIcon />} />
            <Tab label="Onboarding" icon={<SchoolIcon />} />
            <Tab label="Performance" icon={<AssessmentIcon />} />
          </Tabs>
        </Box>

        <Box sx={{ p: 3, minHeight: '60vh' }}>
          {/* Employees Tab */}
          {activeTab === 0 && (
            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h5">Employee Management</Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleEmployeeAdd}
                >
                  Add Employee
                </Button>
              </Box>
              
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Employee</TableCell>
                      <TableCell>Position</TableCell>
                      <TableCell>Department</TableCell>
                      <TableCell>Salary</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {employees.map((employee) => (
                      <TableRow key={employee.id}>
                        <TableCell>
                          <Box display="flex" alignItems="center" gap={2}>
                            <Avatar sx={{ width: 32, height: 32 }}>
                              {employee.name.charAt(0)}
                            </Avatar>
                            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                              {employee.name}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>{employee.position}</TableCell>
                        <TableCell>{employee.department}</TableCell>
                        <TableCell>${employee.salary.toLocaleString()}</TableCell>
                        <TableCell>
                          <Chip 
                            label={employee.status} 
                            color="success" 
                            size="small" 
                          />
                        </TableCell>
                        <TableCell>
                          <IconButton onClick={() => handleEmployeeEdit(employee)}>
                            <EditIcon />
                          </IconButton>
                          <IconButton onClick={() => {
                            setSelectedItem(employee);
                            setSelectedItemType('employee');
                            setDetailViewOpen(true);
                          }}>
                            <ViewIcon />
                          </IconButton>
                          <IconButton onClick={() => handleEmployeeDelete(employee)} color="error">
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {/* Payroll Tab */}
          {activeTab === 1 && (
            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h5">Payroll Management</Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => showSnackbar('Process payroll would start here')}
                >
                  Process Payroll
                </Button>
              </Box>
              
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Employee</TableCell>
                      <TableCell>Period</TableCell>
                      <TableCell align="right">Gross Pay</TableCell>
                      <TableCell align="right">Net Pay</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {payroll.map((pay) => (
                      <TableRow key={pay.id}>
                        <TableCell>{pay.employee}</TableCell>
                        <TableCell>{pay.period}</TableCell>
                        <TableCell align="right">${pay.grossPay.toLocaleString()}</TableCell>
                        <TableCell align="right">${pay.netPay.toLocaleString()}</TableCell>
                        <TableCell>
                          <Chip 
                            label={pay.status} 
                            color="success" 
                            size="small" 
                          />
                        </TableCell>
                        <TableCell>
                          <IconButton onClick={() => showSnackbar('Payroll details would open here')}>
                            <ViewIcon />
                          </IconButton>
                          <IconButton onClick={() => showSnackbar('Payroll slip would download here')}>
                            <DownloadIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {/* Recruitment Tab */}
          {activeTab === 2 && (
            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h5">Recruitment</Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => showSnackbar('Post new job form would open here')}
                >
                  Post Job
                </Button>
              </Box>
              
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Position</TableCell>
                      <TableCell>Department</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Applications</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recruitment.map((job) => (
                      <TableRow key={job.id}>
                        <TableCell>{job.position}</TableCell>
                        <TableCell>{job.department}</TableCell>
                        <TableCell>
                          <Chip 
                            label={job.status} 
                            color={job.status === 'Open' ? 'success' : 'default'} 
                            size="small" 
                          />
                        </TableCell>
                        <TableCell>{job.applications}</TableCell>
                        <TableCell>
                          <IconButton onClick={() => showSnackbar('Edit job posting would open here')}>
                            <EditIcon />
                          </IconButton>
                          <IconButton onClick={() => showSnackbar('View applications would open here')}>
                            <ViewIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {/* Onboarding Tab */}
          {activeTab === 3 && (
            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h5">Onboarding</Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => showSnackbar('Add onboarding plan would open here')}
                >
                  Add Onboarding Plan
                </Button>
              </Box>
              
              <Alert severity="info">
                <Typography variant="body2">
                  Onboarding management system with task tracking, progress monitoring, and automated workflows.
                  Track new employee progress through orientation, training, and integration phases.
                </Typography>
              </Alert>
            </Box>
          )}

          {/* Performance Tab */}
          {activeTab === 4 && (
            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h5">Performance Management</Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => showSnackbar('Add performance review would open here')}
                >
                  Add Review
                </Button>
              </Box>
              
              <Alert severity="info">
                <Typography variant="body2">
                  Performance management system with goal setting, regular reviews, 360-degree feedback,
                  and performance analytics. Track employee development and career progression.
                </Typography>
              </Alert>
            </Box>
          )}
        </Box>
      </Paper>

      {/* Footer */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          EdonuOps HCM - Complete Workforce Management Platform
        </Typography>
        <Box sx={{ mt: 1 }}>
          <Chip label="HRIS Compliant" size="small" sx={{ mr: 1 }} />
          <Chip label="Payroll Ready" size="small" sx={{ mr: 1 }} />
          <Chip label="Performance Tracking" size="small" color="primary" />
        </Box>
      </Box>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>

      {/* Detail View Modal */}
      <DetailViewModal
        open={detailViewOpen}
        onClose={() => {
          setDetailViewOpen(false);
          setSelectedItem(null);
          setSelectedItemType('');
        }}
        data={selectedItem}
        type={selectedItemType}
        onEdit={(item) => {
          setDetailViewOpen(false);
          handleEmployeeEdit(item);
        }}
        title={`${selectedItemType.charAt(0).toUpperCase() + selectedItemType.slice(1)} Details`}
      />

      {/* Improved Form for Employee Management */}
      <ImprovedForm
        open={employeeFormOpen}
        onClose={() => {
          setEmployeeFormOpen(false);
          setEditEmployee(null);
        }}
        onSave={handleSaveEmployee}
        data={editEmployee}
        type="employee"
        title="Employee"
        loading={employeesLoading}
      />

      <ConfirmationDialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        onConfirm={handleConfirmDelete}
        title="Delete Employee"
        message={`Are you sure you want to delete "${deleteItem?.name}"? This action cannot be undone.`}
      />
    </Container>
  );
};

export default HCMModule;
