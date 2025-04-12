import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Box, Typography, Paper, Container, Button } from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { ChatMessage, ChatInput } from '../components';
import { chatService } from '../services';
import { useAuth, useLanguage } from '../contexts';
import { ChatMessage as ChatMessageType, FeedbackData } from '../types';

const HomePage: React.FC = () => {
  const { t } = useTranslation();
  const { isAuthenticated } = useAuth();
  const { language } = useLanguage();
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Get or create session ID
    const currentSessionId = chatService.getSessionId();
    setSessionId(currentSessionId);

    // Load chat history if authenticated
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

    // Add user message to chat
    const userMessage: ChatMessageType = {
      id: `temp_${Date.now()}`,
      type: 'query',
      content: message,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Send message to API
      const response = await chatService.sendMessage(message, sessionId, language);

      // Add bot response to chat
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
      
      // Add error message
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
    <Container maxWidth="lg" sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5">{t('app.chat')}</Typography>
        <Button
          variant="outlined"
          startIcon={<AddIcon />}
          onClick={handleNewChat}
        >
          {t('chat.new')}
        </Button>
      </Box>

      <Paper
        elevation={0}
        sx={{
          flexGrow: 1,
          mb: 2,
          p: 2,
          overflow: 'auto',
          maxHeight: 'calc(100vh - 240px)',
          bgcolor: 'background.default',
        }}
      >
        {messages.length === 0 ? (
          <Box
            sx={{
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
            }}
          >
            <Typography variant="body1" color="text.secondary">
              {t('chat.empty')}
            </Typography>
          </Box>
        ) : (
          <Box>
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
      </Paper>

      <ChatInput
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
      />
    </Container>
  );
};

export default HomePage;
