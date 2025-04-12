import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Container,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Paper,
  Divider,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  ChatBubble as ChatIcon,
} from '@mui/icons-material';
import { chatService } from '../services';
import { useAuth } from '../contexts';
import { ChatMessage as ChatMessageType } from '../types';

const HistoryPage: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [chatSessions, setChatSessions] = useState<Record<string, ChatMessageType[]>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [sessionToDelete, setSessionToDelete] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    loadChatHistory();
  }, [isAuthenticated, navigate]);

  const loadChatHistory = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Get current session ID
      const currentSessionId = chatService.getSessionId();
      
      // Load chat history for current session
      const response = await chatService.getChatHistory(currentSessionId);
      
      if (response.history && response.history.length > 0) {
        // Group messages by session ID
        const sessions: Record<string, ChatMessageType[]> = {};
        sessions[currentSessionId] = response.history;
        
        setChatSessions(sessions);
      }
    } catch (error) {
      console.error('Failed to load chat history:', error);
      setError(t('chat.history.error'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSessionClick = (sessionId: string) => {
    chatService.setSessionId(sessionId);
    navigate('/');
  };

  const handleDeleteClick = (sessionId: string) => {
    setSessionToDelete(sessionId);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (sessionToDelete) {
      // Remove session from state
      const newSessions = { ...chatSessions };
      delete newSessions[sessionToDelete];
      setChatSessions(newSessions);
      
      // If current session was deleted, create a new one
      if (chatService.getSessionId() === sessionToDelete) {
        const newSessionId = chatService.generateSessionId();
        chatService.setSessionId(newSessionId);
      }
      
      setDeleteDialogOpen(false);
      setSessionToDelete(null);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setSessionToDelete(null);
  };

  const getSessionTitle = (sessionId: string, messages: ChatMessageType[]) => {
    // Find first user message
    const firstUserMessage = messages.find(msg => msg.type === 'query');
    if (firstUserMessage) {
      // Truncate message if too long
      const maxLength = 30;
      const content = firstUserMessage.content;
      return content.length > maxLength
        ? `${content.substring(0, maxLength)}...`
        : content;
    }
    
    // Fallback to session ID
    return `${t('app.chat')} ${sessionId.substring(sessionId.length - 6)}`;
  };

  const getSessionDate = (messages: ChatMessageType[]) => {
    if (messages.length > 0) {
      const latestMessage = messages.reduce((latest, current) => {
        return new Date(latest.created_at) > new Date(current.created_at)
          ? latest
          : current;
      });
      
      return new Date(latestMessage.created_at).toLocaleString();
    }
    return '';
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {t('app.history')}
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        ) : Object.keys(chatSessions).length === 0 ? (
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="body1" color="text.secondary">
              {t('chat.history.empty')}
            </Typography>
          </Paper>
        ) : (
          <Paper elevation={2}>
            <List>
              {Object.entries(chatSessions).map(([sessionId, messages], index) => (
                <React.Fragment key={sessionId}>
                  {index > 0 && <Divider />}
                  <ListItem
                    secondaryAction={
                      <IconButton
                        edge="end"
                        aria-label="delete"
                        onClick={() => handleDeleteClick(sessionId)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    }
                    disablePadding
                  >
                    <ListItemButton onClick={() => handleSessionClick(sessionId)}>
                      <ChatIcon sx={{ mr: 2, color: 'primary.main' }} />
                      <ListItemText
                        primary={getSessionTitle(sessionId, messages)}
                        secondary={getSessionDate(messages)}
                      />
                    </ListItemButton>
                  </ListItem>
                </React.Fragment>
              ))}
            </List>
          </Paper>
        )}
      </Box>

      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          {t('chat.history.confirmation')}
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            {t('app.confirmation')}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel}>{t('app.no')}</Button>
          <Button onClick={handleDeleteConfirm} autoFocus>
            {t('app.yes')}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default HistoryPage;
