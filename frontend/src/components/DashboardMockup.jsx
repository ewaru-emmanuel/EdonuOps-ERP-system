import React from 'react';
import { Box, Paper, Typography, Grid, Chip, Avatar } from '@mui/material';
import {
  TrendingUp, TrendingDown, AccountBalance, Inventory,
  People, AttachMoney, ShoppingCart, Assessment
} from '@mui/icons-material';

const DashboardMockup = () => {
  return (
    <Box
      sx={{
        width: '100%',
        maxWidth: 500,
        height: 300,
        bgcolor: '#f8fafc',
        borderRadius: 3,
        p: 2,
        boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
        border: '1px solid #e2e8f0',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, pb: 1, borderBottom: '1px solid #e2e8f0' }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#1976d2', flexGrow: 1 }}>
          EdonuOps Dashboard
        </Typography>
        <Chip label="Live" color="success" size="small" />
      </Box>

      {/* Sidebar Mockup */}
      <Box sx={{ position: 'absolute', left: 0, top: 0, width: 60, height: '100%', bgcolor: '#1e293b', pt: 8 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, pt: 2 }}>
          <Box sx={{ width: 32, height: 32, bgcolor: '#1976d2', borderRadius: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <AccountBalance sx={{ fontSize: 18, color: 'white' }} />
          </Box>
          <Box sx={{ width: 32, height: 32, bgcolor: '#2e7d32', borderRadius: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Inventory sx={{ fontSize: 18, color: 'white' }} />
          </Box>
          <Box sx={{ width: 32, height: 32, bgcolor: '#0288d1', borderRadius: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <People sx={{ fontSize: 18, color: 'white' }} />
          </Box>
        </Box>
      </Box>

      {/* Main Content */}
      <Box sx={{ ml: 7 }}>
        <Grid container spacing={2}>
          {/* KPI Cards */}
          <Grid item xs={6} md={3}>
            <Paper sx={{ p: 1.5, textAlign: 'center', bgcolor: 'white', boxShadow: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                <TrendingUp sx={{ fontSize: 20, color: '#2e7d32', mr: 0.5 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#2e7d32' }}>
                  $124K
                </Typography>
              </Box>
              <Typography variant="caption" color="text.secondary">
                Monthly Revenue
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={6} md={3}>
            <Paper sx={{ p: 1.5, textAlign: 'center', bgcolor: 'white', boxShadow: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                <ShoppingCart sx={{ fontSize: 20, color: '#1976d2', mr: 0.5 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#1976d2' }}>
                  1,247
                </Typography>
              </Box>
              <Typography variant="caption" color="text.secondary">
                Orders
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={6} md={3}>
            <Paper sx={{ p: 1.5, textAlign: 'center', bgcolor: 'white', boxShadow: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                <Inventory sx={{ fontSize: 20, color: '#ed6c02', mr: 0.5 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#ed6c02' }}>
                  89%
                </Typography>
              </Box>
              <Typography variant="caption" color="text.secondary">
                Stock Level
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={6} md={3}>
            <Paper sx={{ p: 1.5, textAlign: 'center', bgcolor: 'white', boxShadow: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                <People sx={{ fontSize: 20, color: '#9c27b0', mr: 0.5 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#9c27b0' }}>
                  156
                </Typography>
              </Box>
              <Typography variant="caption" color="text.secondary">
                Customers
              </Typography>
            </Paper>
          </Grid>

          {/* Chart Area */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2, bgcolor: 'white', boxShadow: 1, height: 120 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Assessment sx={{ fontSize: 18, color: '#1976d2', mr: 1 }} />
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                  Revenue Trend
                </Typography>
              </Box>
              {/* Simple Bar Chart Mockup */}
              <Box sx={{ display: 'flex', alignItems: 'end', gap: 1, height: 60, mt: 1 }}>
                {[40, 60, 45, 80, 65, 90, 75].map((height, index) => (
                  <Box
                    key={index}
                    sx={{
                      width: 8,
                      height: `${height}%`,
                      bgcolor: index === 6 ? '#1976d2' : '#e3f2fd',
                      borderRadius: '2px 2px 0 0',
                      transition: 'all 0.3s ease'
                    }}
                  />
                ))}
              </Box>
            </Paper>
          </Grid>

          {/* Recent Activity */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, bgcolor: 'white', boxShadow: 1, height: 100 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                Recent Activity
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                <Avatar sx={{ width: 24, height: 24, fontSize: 12, bgcolor: '#1976d2', mr: 1 }}>
                  JD
                </Avatar>
                <Typography variant="caption">
                  New order #1234 received
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Avatar sx={{ width: 24, height: 24, fontSize: 12, bgcolor: '#2e7d32', mr: 1 }}>
                  SM
                </Avatar>
                <Typography variant="caption">
                  Inventory updated
                </Typography>
              </Box>
            </Paper>
          </Grid>

          {/* Quick Actions */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, bgcolor: 'white', boxShadow: 1, height: 100 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip label="New Order" size="small" color="primary" />
                <Chip label="Add Product" size="small" color="secondary" />
                <Chip label="Generate Report" size="small" />
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default DashboardMockup;
