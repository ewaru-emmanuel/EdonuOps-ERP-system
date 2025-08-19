import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Palette as ThemeIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Preview as PreviewIcon,
  Save as SaveIcon
} from '@mui/icons-material';

const ThemeCustomization = () => {
  const [themes, setThemes] = useState([]);
  const [selectedTheme, setSelectedTheme] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [themeForm, setThemeForm] = useState({
    name: '',
    description: '',
    primaryColor: '#1976d2',
    secondaryColor: '#dc004e',
    mode: 'light',
    isActive: false
  });

  const colorPresets = [
    { name: 'Blue', primary: '#1976d2', secondary: '#dc004e' },
    { name: 'Green', primary: '#2e7d32', secondary: '#ff6f00' },
    { name: 'Purple', primary: '#7b1fa2', secondary: '#ff9800' },
    { name: 'Orange', primary: '#f57c00', secondary: '#1976d2' },
    { name: 'Teal', primary: '#00695c', secondary: '#ff6f00' },
    { name: 'Indigo', primary: '#3949ab', secondary: '#ff6f00' }
  ];

  useEffect(() => {
    fetchThemes();
  }, []);

  const fetchThemes = async () => {
    // Mock themes data
    const mockThemes = [
      {
        id: 1,
        name: 'Corporate Blue',
        description: 'Professional blue theme for corporate environments',
        primaryColor: '#1976d2',
        secondaryColor: '#dc004e',
        mode: 'light',
        isActive: true
      },
      {
        id: 2,
        name: 'Dark Professional',
        description: 'Dark theme for modern professional look',
        primaryColor: '#424242',
        secondaryColor: '#ff9800',
        mode: 'dark',
        isActive: false
      },
      {
        id: 3,
        name: 'Green Nature',
        description: 'Eco-friendly green theme',
        primaryColor: '#2e7d32',
        secondaryColor: '#ff6f00',
        mode: 'light',
        isActive: false
      }
    ];
    setThemes(mockThemes);
  };

  const handleOpenDialog = (theme = null) => {
    if (theme) {
      setThemeForm({
        name: theme.name,
        description: theme.description,
        primaryColor: theme.primaryColor,
        secondaryColor: theme.secondaryColor,
        mode: theme.mode,
        isActive: theme.isActive
      });
      setSelectedTheme(theme);
    } else {
      setThemeForm({
        name: '',
        description: '',
        primaryColor: '#1976d2',
        secondaryColor: '#dc004e',
        mode: 'light',
        isActive: false
      });
      setSelectedTheme(null);
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedTheme(null);
    setThemeForm({
      name: '',
      description: '',
      primaryColor: '#1976d2',
      secondaryColor: '#dc004e',
      mode: 'light',
      isActive: false
    });
  };

  const handleSaveTheme = async () => {
    try {
      if (selectedTheme) {
        // Update existing theme
        const updatedThemes = themes.map(theme =>
          theme.id === selectedTheme.id
            ? { ...theme, ...themeForm }
            : theme
        );
        setThemes(updatedThemes);
      } else {
        // Create new theme
        const newTheme = {
          id: Date.now(),
          ...themeForm
        };
        setThemes(prev => [...prev, newTheme]);
      }
      handleCloseDialog();
    } catch (error) {
      console.error('Error saving theme:', error);
    }
  };

  const handleDeleteTheme = async (id) => {
    try {
      setThemes(prev => prev.filter(theme => theme.id !== id));
    } catch (error) {
      console.error('Error deleting theme:', error);
    }
  };

  const handleActivateTheme = async (id) => {
    try {
      const updatedThemes = themes.map(theme => ({
        ...theme,
        isActive: theme.id === id
      }));
      setThemes(updatedThemes);
    } catch (error) {
      console.error('Error activating theme:', error);
    }
  };

  const applyColorPreset = (preset) => {
    setThemeForm(prev => ({
      ...prev,
      primaryColor: preset.primary,
      secondaryColor: preset.secondary
    }));
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2" sx={{ fontWeight: 'bold' }}>
          Theme Customization
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
          sx={{ borderRadius: 2 }}
        >
          Create Theme
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Theme List */}
        <Grid item xs={12} md={8}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Available Themes
              </Typography>
              
              <List>
                {themes.map((theme) => (
                  <ListItem
                    key={theme.id}
                    sx={{
                      border: 1,
                      borderColor: 'divider',
                      borderRadius: 1,
                      mb: 2,
                      '&:hover': {
                        bgcolor: 'action.hover'
                      }
                    }}
                  >
                    <ListItemIcon>
                      <ThemeIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                            {theme.name}
                          </Typography>
                          {theme.isActive && (
                            <Chip label="ACTIVE" color="success" size="small" />
                          )}
                          <Chip
                            label={theme.mode.toUpperCase()}
                            color="primary"
                            size="small"
                            variant="outlined"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                            {theme.description}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                            <Box
                              sx={{
                                width: 20,
                                height: 20,
                                bgcolor: theme.primaryColor,
                                borderRadius: 1,
                                border: '1px solid #ccc'
                              }}
                            />
                            <Box
                              sx={{
                                width: 20,
                                height: 20,
                                bgcolor: theme.secondaryColor,
                                borderRadius: 1,
                                border: '1px solid #ccc'
                              }}
                            />
                          </Box>
                        </Box>
                      }
                    />
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <IconButton
                        size="small"
                        onClick={() => handleOpenDialog(theme)}
                        sx={{ color: 'primary.main' }}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleActivateTheme(theme.id)}
                        sx={{ color: 'success.main' }}
                      >
                        <PreviewIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteTheme(theme.id)}
                        sx={{ color: 'error.main' }}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Color Presets */}
        <Grid item xs={12} md={4}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Color Presets
              </Typography>
              
              <Grid container spacing={2}>
                {colorPresets.map((preset) => (
                  <Grid item xs={6} key={preset.name}>
                    <Card
                      variant="outlined"
                      sx={{
                        cursor: 'pointer',
                        '&:hover': { bgcolor: 'action.hover' }
                      }}
                      onClick={() => applyColorPreset(preset)}
                    >
                      <CardContent sx={{ p: 2, textAlign: 'center' }}>
                        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mb: 1 }}>
                          <Box
                            sx={{
                              width: 24,
                              height: 24,
                              bgcolor: preset.primary,
                              borderRadius: 1,
                              border: '1px solid #ccc'
                            }}
                          />
                          <Box
                            sx={{
                              width: 24,
                              height: 24,
                              bgcolor: preset.secondary,
                              borderRadius: 1,
                              border: '1px solid #ccc'
                            }}
                          />
                        </Box>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {preset.name}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Create/Edit Theme Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedTheme ? 'Edit Theme' : 'Create New Theme'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Theme Name"
                value={themeForm.name}
                onChange={(e) => setThemeForm(prev => ({ ...prev, name: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={themeForm.description}
                onChange={(e) => setThemeForm(prev => ({ ...prev, description: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Primary Color"
                type="color"
                value={themeForm.primaryColor}
                onChange={(e) => setThemeForm(prev => ({ ...prev, primaryColor: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Secondary Color"
                type="color"
                value={themeForm.secondaryColor}
                onChange={(e) => setThemeForm(prev => ({ ...prev, secondaryColor: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Mode</InputLabel>
                <Select
                  value={themeForm.mode}
                  onChange={(e) => setThemeForm(prev => ({ ...prev, mode: e.target.value }))}
                  label="Mode"
                >
                  <MenuItem value="light">Light</MenuItem>
                  <MenuItem value="dark">Dark</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={themeForm.isActive}
                    onChange={(e) => setThemeForm(prev => ({ ...prev, isActive: e.target.checked }))}
                  />
                }
                label="Set as Active Theme"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>
            Cancel
          </Button>
          <Button
            onClick={handleSaveTheme}
            variant="contained"
            startIcon={<SaveIcon />}
            disabled={!themeForm.name}
          >
            {selectedTheme ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ThemeCustomization;
