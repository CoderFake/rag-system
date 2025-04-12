import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Box, 
  Typography, 
  Paper, 
  Container, 
  Button,
  Divider,
  useTheme,
  useMediaQuery
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { ChatMessage, ChatInput } from '../components';
import { chatService } from '../services';
import { useAuth, useLanguage } from '../contexts';
import { ChatMessage as ChatMessageType, FeedbackData } from '../types';

const HomePage: React.FC = () => {
  const { t } = useTranslation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { isAuthenticated } = useAuth();
  const { language } = useLanguage();
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {

    const currentSessionId = chatService.getSessionId();
    setSessionId(currentSessionId);
    setMessages([]);

    if (isAuthenticated) {
      loadChatHistory(currentSessionId);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadChatHistory = async (sid: string) => {
    try {
      setIsLoading(true);
      const response = await chatService.getChatHistory(sid);
      if (response.history && response.history.length > 0) {
        setMessages(response.history);
      }
    } catch (error) {
      console.error('Failed to load chat history:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;


    const userMessage: ChatMessageType = {
      id: `temp_${Date.now()}`,
      type: 'query',
      content: message,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await chatService.sendMessage(message, sessionId, language);
      const botMessage: ChatMessageType = {
        id: response.response_id,
        type: 'response',
        content: response.response,
        created_at: new Date().toISOString(),
        query_id: response.query_id,
        sources: response.source_documents,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      
      const errorMessage: ChatMessageType = {
        id: `error_${Date.now()}`,
        type: 'response',
        content: t('chat.error'),
        created_at: new Date().toISOString(),
      };
      
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedback = async (responseId: string, type: string, value: string) => {
    try {
      const feedbackData: FeedbackData = {
        response_id: responseId,
        type: type as 'thumbs_up' | 'thumbs_down' | 'comment',
        value,
      };
      
      await chatService.addFeedback(feedbackData);
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }
  };

  const handleNewChat = () => {
    const newSessionId = chatService.generateSessionId();
    chatService.setSessionId(newSessionId);
    setSessionId(newSessionId);
    setMessages([]);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <Container 
      maxWidth="lg" 
      sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        height: `calc(100vh - ${theme.spacing(8)})`,
        maxHeight: `calc(100vh - ${theme.spacing(8)})`,
        pt: 2,
        pb: 2,
        width: '100%',
      }}
    >
      <Box 
        sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          mb: 2,
          px: 1
        }}
      >
        <Typography variant="h5" sx={{ fontWeight: 600 }}>
          {t('app.chat')}
        </Typography>
        <Button
          variant="outlined"
          startIcon={<AddIcon />}
          onClick={handleNewChat}
          size={isMobile ? "small" : "medium"}
        >
          {t('chat.new')}
        </Button>
      </Box>

      <Divider sx={{ mb: 2 }} />

      <Box
        ref={messagesContainerRef}
        sx={{
          flexGrow: 1,
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          mb: 2,
          px: isMobile ? 0 : 1,
          borderRadius: 2,
          '&::-webkit-scrollbar': {
            width: '8px',
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: theme.palette.mode === 'dark' 
              ? 'rgba(255, 255, 255, 0.2)' 
              : 'rgba(0, 0, 0, 0.2)',
            borderRadius: '4px',
          },
          '&::-webkit-scrollbar-track': {
            backgroundColor: 'transparent',
          },
        }}
      >
        {messages.length === 0 ? (
          <Paper
            elevation={0}
            sx={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              textAlign: 'center',
              p: 4,
              m: 2,
              flexGrow: 1,
              borderRadius: 4,
              backgroundColor: theme.palette.mode === 'dark' 
                ? 'rgba(255, 255, 255, 0.05)' 
                : 'rgba(0, 0, 0, 0.02)',
              border: `1px dashed ${theme.palette.divider}`,
            }}
          >
            <Typography variant="h6" color="text.secondary" gutterBottom>
              {t('chat.empty')}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {t('chat.placeholder')}
            </Typography>
          </Paper>
        ) : (
          <Box sx={{ 
            p: isMobile ? 1 : 2,
            width: '100%',
            maxWidth: '100%',
          }}>
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                onFeedback={handleFeedback}
              />
            ))}
            <div ref={messagesEndRef} />
          </Box>
        )}
      </Box>

      <Box sx={{ position: 'sticky', bottom: 0, width: '100%' }}>
        <ChatInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      </Box>
    </Container>
  );
};

export default HomePage;