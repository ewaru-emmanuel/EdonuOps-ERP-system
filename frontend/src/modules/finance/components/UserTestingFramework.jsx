import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  RadioGroup,
  FormControlLabel,
  Radio,
  Checkbox,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Grid,
  Paper,
  Divider,
  IconButton,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Replay as ReplayIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Timer as TimerIcon,
  Person as PersonIcon,
  Business as BusinessIcon,
  Assessment as AssessmentIcon,
  VideoCall as VideoIcon,
  Mic as MicIcon,
  MicOff as MicOffIcon
} from '@mui/icons-material';

const UserTestingFramework = ({ onTestComplete }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [testSession, setTestSession] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [testData, setTestData] = useState({
    participant: {
      name: '',
      role: '',
      experience: '',
      business_type: '',
      accounting_knowledge: ''
    },
    tasks: [],
    observations: [],
    metrics: {
      task_completion_time: {},
      errors: {},
      satisfaction_scores: {},
      difficulty_ratings: {}
    }
  });

  const testScenarios = [
    {
      id: 'setup_business',
      title: 'Setup Your Business',
      description: 'Set up a new business in the system',
      tasks: [
        'Choose your business type (Retail, Services, Manufacturing, Freelancer)',
        'Select your country for compliance',
        'Review the Chart of Accounts template',
        'Activate required statutory modules'
      ],
      success_criteria: 'Business setup completed with appropriate CoA template',
      estimated_time: '5-10 minutes'
    },
    {
      id: 'record_sale',
      title: 'Record a Sale',
      description: 'Record a customer sale using the workflow system',
      tasks: [
        'Navigate to the workflow view',
        'Select "Record Sale" workflow',
        'Fill in customer details',
        'Add products/services sold',
        'Complete the transaction'
      ],
      success_criteria: 'Sale recorded with proper account tagging',
      estimated_time: '3-5 minutes'
    },
    {
      id: 'record_expense',
      title: 'Record an Expense',
      description: 'Record a business expense',
      tasks: [
        'Select "Record Expense" workflow',
        'Choose expense category',
        'Enter vendor information',
        'Add amount and description',
        'Complete the transaction'
      ],
      success_criteria: 'Expense recorded with proper categorization',
      estimated_time: '2-3 minutes'
    },
    {
      id: 'view_reports',
      title: 'View Financial Reports',
      description: 'Access and understand financial reports',
      tasks: [
        'Navigate to the dashboard',
        'View key financial metrics',
        'Access detailed reports',
        'Understand the data presented'
      ],
      success_criteria: 'User can access and understand reports',
      estimated_time: '3-5 minutes'
    },
    {
      id: 'manage_accounts',
      title: 'Manage Chart of Accounts',
      description: 'Add or modify accounts in the Chart of Accounts',
      tasks: [
        'Switch to progressive view',
        'Add a new account',
        'Modify an existing account',
        'Understand account types and relationships'
      ],
      success_criteria: 'Account management completed successfully',
      estimated_time: '5-7 minutes'
    }
  ];

  const handleNext = () => {
    setActiveStep(prev => prev + 1);
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
    setTestSession(null);
    setTestData({
      participant: {
        name: '',
        role: '',
        experience: '',
        business_type: '',
        accounting_knowledge: ''
      },
      tasks: [],
      observations: [],
      metrics: {
        task_completion_time: {},
        errors: {},
        satisfaction_scores: {},
        difficulty_ratings: {}
      }
    });
  };

  const startTestSession = () => {
    const sessionId = `test_${Date.now()}`;
    setTestSession({
      id: sessionId,
      startTime: new Date(),
      currentScenario: null,
      status: 'active'
    });
    setActiveStep(1);
  };

  const startRecording = () => {
    setIsRecording(true);
    // In a real implementation, this would start screen/audio recording
  };

  const stopRecording = () => {
    setIsRecording(false);
    // In a real implementation, this would stop recording
  };

  const recordObservation = (scenarioId, observation) => {
    setTestData(prev => ({
      ...prev,
      observations: [
        ...prev.observations,
        {
          id: Date.now(),
          scenarioId,
          timestamp: new Date(),
          observation,
          type: 'general'
        }
      ]
    }));
  };

  const recordError = (scenarioId, error) => {
    setTestData(prev => ({
      ...prev,
      observations: [
        ...prev.observations,
        {
          id: Date.now(),
          scenarioId,
          timestamp: new Date(),
          observation: error,
          type: 'error'
        }
      ],
      metrics: {
        ...prev.metrics,
        errors: {
          ...prev.metrics.errors,
          [scenarioId]: (prev.metrics.errors[scenarioId] || 0) + 1
        }
      }
    }));
  };

  const recordTaskCompletion = (scenarioId, timeSpent, difficulty, satisfaction) => {
    setTestData(prev => ({
      ...prev,
      tasks: [
        ...prev.tasks.filter(t => t.scenarioId !== scenarioId),
        {
          scenarioId,
          completed: true,
          timeSpent,
          difficulty,
          satisfaction,
          completedAt: new Date()
        }
      ],
      metrics: {
        ...prev.metrics,
        task_completion_time: {
          ...prev.metrics.task_completion_time,
          [scenarioId]: timeSpent
        },
        difficulty_ratings: {
          ...prev.metrics.difficulty_ratings,
          [scenarioId]: difficulty
        },
        satisfaction_scores: {
          ...prev.metrics.satisfaction_scores,
          [scenarioId]: satisfaction
        }
      }
    }));
  };

  const completeTest = () => {
    const endTime = new Date();
    const totalTime = endTime - testSession.startTime;
    
    const completedTasks = testData.tasks.filter(t => t.completed);
    const totalErrors = Object.values(testData.metrics.errors).reduce((sum, count) => sum + count, 0);
    const averageSatisfaction = Object.values(testData.metrics.satisfaction_scores).reduce((sum, score) => sum + score, 0) / completedTasks.length;
    const averageDifficulty = Object.values(testData.metrics.difficulty_ratings).reduce((sum, rating) => sum + rating, 0) / completedTasks.length;

    const testResults = {
      sessionId: testSession.id,
      participant: testData.participant,
      duration: totalTime,
      completedTasks: completedTasks.length,
      totalTasks: testScenarios.length,
      totalErrors,
      averageSatisfaction,
      averageDifficulty,
      observations: testData.observations,
      metrics: testData.metrics,
      recommendations: generateRecommendations(testData)
    };

    onTestComplete?.(testResults);
    setTestSession(null);
    setActiveStep(0);
  };

  const generateRecommendations = (data) => {
    const recommendations = [];
    
    // Analyze completion rates
    const completionRate = data.tasks.filter(t => t.completed).length / testScenarios.length;
    if (completionRate < 0.8) {
      recommendations.push({
        type: 'completion_rate',
        priority: 'high',
        message: 'Low task completion rate. Consider simplifying workflows or adding more guidance.'
      });
    }
    
    // Analyze error patterns
    const totalErrors = Object.values(data.metrics.errors).reduce((sum, count) => sum + count, 0);
    if (totalErrors > 5) {
      recommendations.push({
        type: 'error_rate',
        priority: 'high',
        message: 'High error rate. Review UI/UX for common pain points.'
      });
    }
    
    // Analyze satisfaction scores
    const avgSatisfaction = Object.values(data.metrics.satisfaction_scores).reduce((sum, score) => sum + score, 0) / data.tasks.length;
    if (avgSatisfaction < 3) {
      recommendations.push({
        type: 'satisfaction',
        priority: 'medium',
        message: 'Low satisfaction scores. Consider improving user experience.'
      });
    }
    
    // Analyze difficulty ratings
    const avgDifficulty = Object.values(data.metrics.difficulty_ratings).reduce((sum, rating) => sum + rating, 0) / data.tasks.length;
    if (avgDifficulty > 4) {
      recommendations.push({
        type: 'difficulty',
        priority: 'high',
        message: 'High difficulty ratings. Consider adding more guidance or simplifying processes.'
      });
    }
    
    return recommendations;
  };

  const renderParticipantInfo = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Participant Information
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Name (Optional)"
            value={testData.participant.name}
            onChange={(e) => setTestData(prev => ({
              ...prev,
              participant: { ...prev.participant, name: e.target.value }
            }))}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <InputLabel>Role</InputLabel>
            <Select
              value={testData.participant.role}
              onChange={(e) => setTestData(prev => ({
                ...prev,
                participant: { ...prev.participant, role: e.target.value }
              }))}
              label="Role"
            >
              <MenuItem value="business_owner">Business Owner</MenuItem>
              <MenuItem value="manager">Manager</MenuItem>
              <MenuItem value="employee">Employee</MenuItem>
              <MenuItem value="freelancer">Freelancer</MenuItem>
              <MenuItem value="other">Other</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <InputLabel>Business Type</InputLabel>
            <Select
              value={testData.participant.business_type}
              onChange={(e) => setTestData(prev => ({
                ...prev,
                participant: { ...prev.participant, business_type: e.target.value }
              }))}
              label="Business Type"
            >
              <MenuItem value="retail">Retail</MenuItem>
              <MenuItem value="services">Services</MenuItem>
              <MenuItem value="manufacturing">Manufacturing</MenuItem>
              <MenuItem value="freelancer">Freelancer</MenuItem>
              <MenuItem value="other">Other</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <InputLabel>Accounting Knowledge</InputLabel>
            <Select
              value={testData.participant.accounting_knowledge}
              onChange={(e) => setTestData(prev => ({
                ...prev,
                participant: { ...prev.participant, accounting_knowledge: e.target.value }
              }))}
              label="Accounting Knowledge"
            >
              <MenuItem value="none">No accounting knowledge</MenuItem>
              <MenuItem value="basic">Basic understanding</MenuItem>
              <MenuItem value="intermediate">Intermediate knowledge</MenuItem>
              <MenuItem value="advanced">Advanced knowledge</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>
    </Box>
  );

  const renderTestScenarios = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Test Scenarios
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        You will be asked to complete these tasks. Take your time and think aloud as you work.
      </Typography>
      
      <List>
        {testScenarios.map((scenario, index) => (
          <ListItem key={scenario.id}>
            <ListItemIcon>
              <CheckCircleIcon color={testData.tasks.find(t => t.scenarioId === scenario.id && t.completed) ? 'success' : 'disabled'} />
            </ListItemIcon>
            <ListItemText
              primary={`${index + 1}. ${scenario.title}`}
              secondary={
                <Box>
                  <Typography variant="body2">{scenario.description}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Estimated time: {scenario.estimated_time}
                  </Typography>
                </Box>
              }
            />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  const renderTestSession = () => (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">
          Test Session Active
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title={isRecording ? 'Stop Recording' : 'Start Recording'}>
            <IconButton
              onClick={isRecording ? stopRecording : startRecording}
              color={isRecording ? 'error' : 'primary'}
            >
              {isRecording ? <MicOffIcon /> : <MicIcon />}
            </IconButton>
          </Tooltip>
          <Button
            variant="outlined"
            onClick={completeTest}
            startIcon={<StopIcon />}
          >
            Complete Test
          </Button>
        </Box>
      </Box>

      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>Instructions:</strong> Complete each task as you would in real life. 
          Think aloud and don't worry about making mistakes. We're testing the system, not you.
        </Typography>
      </Alert>

      <Grid container spacing={3}>
        {testScenarios.map((scenario, index) => (
          <Grid item xs={12} md={6} key={scenario.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {index + 1}. {scenario.title}
                </Typography>
                <Typography variant="body2" paragraph>
                  {scenario.description}
                </Typography>
                
                <Typography variant="subtitle2" gutterBottom>
                  Tasks:
                </Typography>
                <List dense>
                  {scenario.tasks.map((task, taskIndex) => (
                    <ListItem key={taskIndex}>
                      <ListItemText primary={task} />
                    </ListItem>
                  ))}
                </List>
                
                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="contained"
                    startIcon={<PlayIcon />}
                    onClick={() => {
                      setTestSession(prev => ({ ...prev, currentScenario: scenario.id }));
                      // In a real implementation, this would navigate to the actual feature
                    }}
                  >
                    Start Task
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  const renderTestResults = () => {
    if (!testData.tasks.length) return null;

    const completedTasks = testData.tasks.filter(t => t.completed);
    const totalErrors = Object.values(testData.metrics.errors).reduce((sum, count) => sum + count, 0);
    const averageSatisfaction = Object.values(testData.metrics.satisfaction_scores).reduce((sum, score) => sum + score, 0) / completedTasks.length;
    const averageDifficulty = Object.values(testData.metrics.difficulty_ratings).reduce((sum, rating) => sum + rating, 0) / completedTasks.length;

    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          Test Results Summary
        </Typography>
        
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="primary">
                  {completedTasks.length}/{testScenarios.length}
                </Typography>
                <Typography variant="body2">Tasks Completed</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="error">
                  {totalErrors}
                </Typography>
                <Typography variant="body2">Total Errors</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="success">
                  {averageSatisfaction.toFixed(1)}/5
                </Typography>
                <Typography variant="body2">Avg Satisfaction</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="warning">
                  {averageDifficulty.toFixed(1)}/5
                </Typography>
                <Typography variant="body2">Avg Difficulty</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Typography variant="h6" gutterBottom>
          Observations
        </Typography>
        <List>
          {testData.observations.map(obs => (
            <ListItem key={obs.id}>
              <ListItemIcon>
                {obs.type === 'error' ? <ErrorIcon color="error" /> : <InfoIcon color="info" />}
              </ListItemIcon>
              <ListItemText
                primary={obs.observation}
                secondary={new Date(obs.timestamp).toLocaleTimeString()}
              />
            </ListItem>
          ))}
        </List>
      </Box>
    );
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        User Testing Framework
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        This framework helps you conduct user testing with non-accountants to validate 
        the simplicity and usability of the Chart of Accounts system.
      </Typography>

      <Stepper activeStep={activeStep} orientation="vertical">
        <Step>
          <StepLabel>Participant Information</StepLabel>
          <StepContent>
            {renderParticipantInfo()}
            <Box sx={{ mb: 2 }}>
              <Button
                variant="contained"
                onClick={handleNext}
                sx={{ mt: 1, mr: 1 }}
              >
                Continue
              </Button>
            </Box>
          </StepContent>
        </Step>

        <Step>
          <StepLabel>Test Scenarios</StepLabel>
          <StepContent>
            {renderTestScenarios()}
            <Box sx={{ mb: 2 }}>
              <Button
                variant="contained"
                onClick={startTestSession}
                sx={{ mt: 1, mr: 1 }}
                startIcon={<PlayIcon />}
              >
                Start Test Session
              </Button>
              <Button onClick={handleBack} sx={{ mt: 1, mr: 1 }}>
                Back
              </Button>
            </Box>
          </StepContent>
        </Step>

        <Step>
          <StepLabel>Conduct Test</StepLabel>
          <StepContent>
            {testSession ? renderTestSession() : (
              <Alert severity="info">
                Click "Start Test Session" to begin testing.
              </Alert>
            )}
            <Box sx={{ mb: 2 }}>
              <Button
                variant="contained"
                onClick={handleNext}
                sx={{ mt: 1, mr: 1 }}
                disabled={!testSession}
              >
                Complete Test
              </Button>
              <Button onClick={handleBack} sx={{ mt: 1, mr: 1 }}>
                Back
              </Button>
            </Box>
          </StepContent>
        </Step>

        <Step>
          <StepLabel>Results & Analysis</StepLabel>
          <StepContent>
            {renderTestResults()}
            <Box sx={{ mb: 2 }}>
              <Button
                variant="contained"
                onClick={handleReset}
                sx={{ mt: 1, mr: 1 }}
                startIcon={<ReplayIcon />}
              >
                Start New Test
              </Button>
            </Box>
          </StepContent>
        </Step>
      </Stepper>
    </Box>
  );
};

export default UserTestingFramework;
