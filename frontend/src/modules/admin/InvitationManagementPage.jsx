import React, { useState } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Paper,
  Typography,
  Container
} from '@mui/material';
import {
  Email as EmailIcon,
  Analytics as AnalyticsIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import InvitationManagement from './components/InvitationManagement';
import InvitationAnalytics from './components/InvitationAnalytics';

const InvitationManagementPage = () => {
  const [currentTab, setCurrentTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  const tabContent = [
    {
      label: 'Manage Invitations',
      icon: <EmailIcon />,
      component: <InvitationManagement />
    },
    {
      label: 'Analytics',
      icon: <AnalyticsIcon />,
      component: <InvitationAnalytics />
    }
  ];

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Paper sx={{ mb: 3 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={currentTab} onChange={handleTabChange} aria-label="invitation management tabs">
            {tabContent.map((tab, index) => (
              <Tab
                key={index}
                icon={tab.icon}
                iconPosition="start"
                label={tab.label}
                sx={{ minHeight: 64 }}
              />
            ))}
          </Tabs>
        </Box>
      </Paper>

      <Box>
        {tabContent[currentTab].component}
      </Box>
    </Container>
  );
};

export default InvitationManagementPage;

