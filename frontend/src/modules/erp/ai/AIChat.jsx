import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Chip,
  IconButton,
  Divider
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as AIIcon,
  Person as PersonIcon,
  Refresh as RefreshIcon,
  Clear as ClearIcon
} from '@mui/icons-material';

const AIChat = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Initialize with welcome message
    setMessages([
      {
        id: 1,
        type: 'ai',
        content: 'Hello! I\'m your AI Co-Pilot. I can help you with business insights, automation suggestions, and answer questions about your ERP system. How can I assist you today?',
        timestamp: new Date().toISOString()
      }
    ]);
  }, []);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = generateAIResponse(inputMessage);
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: aiResponse,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsLoading(false);
    }, 1000);
  };

  const generateAIResponse = (userInput) => {
    const input = userInput.toLowerCase();
    
    if (input.includes('inventory') || input.includes('stock')) {
      return 'I can help you with inventory management! I can analyze stock levels, suggest reorder points, and identify slow-moving items. Would you like me to generate an inventory report or check for low stock alerts?';
    } else if (input.includes('finance') || input.includes('financial')) {
      return 'I can assist with financial analysis and reporting. I can help you with cash flow analysis, budget tracking, financial forecasting, and generating financial reports. What specific financial information do you need?';
    } else if (input.includes('automation') || input.includes('workflow')) {
      return 'I can help you create and optimize workflows! I can suggest automation opportunities, create workflow templates, and analyze process efficiency. Would you like me to review your current processes?';
    } else if (input.includes('report') || input.includes('analytics')) {
      return 'I can generate various reports and analytics for you. I can create sales reports, financial statements, performance dashboards, and custom analytics. What type of report would you like?';
    } else if (input.includes('help') || input.includes('support')) {
      return 'I\'m here to help! I can assist with:\n• Business insights and analytics\n• Process automation suggestions\n• Financial analysis and reporting\n• Inventory management\n• Workflow optimization\n\nWhat would you like to know more about?';
    } else {
      return 'I understand you\'re asking about "' + userInput + '". I can help you with business insights, automation, financial analysis, inventory management, and more. Could you please provide more specific details about what you need assistance with?';
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: Date.now(),
        type: 'ai',
        content: 'Chat cleared. How can I help you today?',
        timestamp: new Date().toISOString()
      }
    ]);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2" sx={{ fontWeight: 'bold' }}>
          AI Chat Assistant
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={clearChat}
            size="small"
          >
            Clear Chat
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Chat Interface */}
        <Grid item xs={12} md={8}>
          <Card elevation={2} sx={{ height: '60vh', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
              {/* Messages */}
              <Box sx={{ flexGrow: 1, overflowY: 'auto', mb: 2 }}>
                <List>
                  {messages.map((message) => (
                    <ListItem
                      key={message.id}
                      sx={{
                        flexDirection: message.type === 'user' ? 'row-reverse' : 'row',
                        alignItems: 'flex-start',
                        mb: 2
                      }}
                    >
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: message.type === 'ai' ? 'primary.main' : 'secondary.main' }}>
                          {message.type === 'ai' ? <AIIcon /> : <PersonIcon />}
                        </Avatar>
                      </ListItemAvatar>
                      <Box
                        sx={{
                          maxWidth: '70%',
                          bgcolor: message.type === 'user' ? 'primary.main' : 'grey.100',
                          color: message.type === 'user' ? 'white' : 'text.primary',
                          borderRadius: 2,
                          p: 2,
                          ml: message.type === 'user' ? 0 : 1,
                          mr: message.type === 'user' ? 1 : 0
                        }}
                      >
                        <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
                          {message.content}
                        </Typography>
                        <Typography variant="caption" sx={{ opacity: 0.7, mt: 1, display: 'block' }}>
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </Typography>
                      </Box>
                    </ListItem>
                  ))}
                  {isLoading && (
                    <ListItem sx={{ alignItems: 'flex-start' }}>
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: 'primary.main' }}>
                          <AIIcon />
                        </Avatar>
                      </ListItemAvatar>
                      <Box sx={{ bgcolor: 'grey.100', borderRadius: 2, p: 2, ml: 1 }}>
                        <Typography variant="body1">
                          Thinking...
                        </Typography>
                      </Box>
                    </ListItem>
                  )}
                </List>
                <div ref={messagesEndRef} />
              </Box>

              {/* Input */}
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  multiline
                  maxRows={4}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me anything about your business..."
                  disabled={isLoading}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                />
                <Button
                  variant="contained"
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || isLoading}
                  sx={{ borderRadius: 2, minWidth: 56 }}
                >
                  <SendIcon />
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Quick Actions
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => setInputMessage('Generate a financial report for this month')}
                  sx={{ justifyContent: 'flex-start', textAlign: 'left' }}
                >
                  📊 Generate Financial Report
                </Button>
                
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => setInputMessage('Check inventory levels and suggest reorder items')}
                  sx={{ justifyContent: 'flex-start', textAlign: 'left' }}
                >
                  📦 Check Inventory Levels
                </Button>
                
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => setInputMessage('Analyze sales performance and suggest improvements')}
                  sx={{ justifyContent: 'flex-start', textAlign: 'left' }}
                >
                  📈 Analyze Sales Performance
                </Button>
                
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => setInputMessage('Create an automated workflow for invoice processing')}
                  sx={{ justifyContent: 'flex-start', textAlign: 'left' }}
                >
                  ⚡ Create Automation Workflow
                </Button>
                
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => setInputMessage('What are the best practices for ERP implementation?')}
                  sx={{ justifyContent: 'flex-start', textAlign: 'left' }}
                >
                  💡 Get Best Practices
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AIChat;
