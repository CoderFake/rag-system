import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Typography,
  Paper,
  IconButton,
  Collapse,
  List,
  ListItem,
  ListItemText,
  TextField,
  Button,
} from '@mui/material';
import {
  ThumbUp,
  ThumbDown,
  ExpandMore,
  ExpandLess,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import ReactMarkdown from 'react-markdown';
import { ChatMessage as ChatMessageType, DocumentSource } from '../../types';

const MessagePaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(2),
  maxWidth: '80%',
  borderRadius: 12,
}));

const UserMessage = styled(MessagePaper)(({ theme }) => ({
  marginLeft: 'auto',
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
}));

const BotMessage = styled(MessagePaper)(({ theme }) => ({
  marginRight: 'auto',
  backgroundColor: theme.palette.background.paper,
}));

const MarkdownContent = styled(ReactMarkdown)(({ theme }) => ({
  '& p': {
    margin: 0,
  },
  '& pre': {
    backgroundColor: theme.palette.mode === 'dark' ? '#333' : '#f5f5f5',
    padding: theme.spacing(1),
    borderRadius: 4,
    overflowX: 'auto',
  },
  '& code': {
    backgroundColor: theme.palette.mode === 'dark' ? '#333' : '#f5f5f5',
    padding: '2px 4px',
    borderRadius: 4,
  },
}));

interface ChatMessageProps {
  message: ChatMessageType;
  onFeedback?: (responseId: string, type: string, value: string) => Promise<void>;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, onFeedback }) => {
  const { t } = useTranslation();
  const [showSources, setShowSources] = useState(false);
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);
  const [feedbackComment, setFeedbackComment] = useState('');
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  const toggleSources = () => {
    setShowSources(!showSources);
  };

  const handleFeedback = async (type: 'thumbs_up' | 'thumbs_down') => {
    if (message.id && onFeedback) {
      await onFeedback(message.id, type, '');
      if (type === 'thumbs_down') {
        setShowFeedbackForm(true);
      } else {
        setFeedbackSubmitted(true);
      }
    }
  };

  const submitFeedbackComment = async () => {
    if (message.id && onFeedback && feedbackComment) {
      await onFeedback(message.id, 'comment', feedbackComment);
      setFeedbackComment('');
      setShowFeedbackForm(false);
      setFeedbackSubmitted(true);
    }
  };

  const hasSources = message.sources && message.sources.length > 0;

  if (message.type === 'query') {
    return (
      <UserMessage elevation={1}>
        <Typography variant="body1">{message.content}</Typography>
      </UserMessage>
    );
  }

  return (
    <Box sx={{ width: '100%', mb: 2 }}>
      <BotMessage elevation={1}>
        <MarkdownContent>{message.content}</MarkdownContent>

        {hasSources && (
          <Box sx={{ mt: 2 }}>
            <Button
              size="small"
              startIcon={showSources ? <ExpandLess /> : <ExpandMore />}
              onClick={toggleSources}
              sx={{ textTransform: 'none' }}
            >
              {t('chat.sources')} ({message.sources?.length})
            </Button>
            <Collapse in={showSources} timeout="auto" unmountOnExit>
              <List dense>
                {message.sources?.map((source: DocumentSource) => (
                  <ListItem key={source.id}>
                    <ListItemText
                      primary={source.title}
                      secondary={source.category}
                    />
                  </ListItem>
                ))}
              </List>
            </Collapse>
          </Box>
        )}

        {!feedbackSubmitted && onFeedback && (
          <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
            <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
              {t('chat.feedback.helpful')}
            </Typography>
            <IconButton
              size="small"
              onClick={() => handleFeedback('thumbs_up')}
              color="primary"
            >
              <ThumbUp fontSize="small" />
            </IconButton>
            <IconButton
              size="small"
              onClick={() => handleFeedback('thumbs_down')}
              color="primary"
            >
              <ThumbDown fontSize="small" />
            </IconButton>
          </Box>
        )}

        {showFeedbackForm && (
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              size="small"
              placeholder={t('chat.feedback.comment')}
              value={feedbackComment}
              onChange={(e) => setFeedbackComment(e.target.value)}
              multiline
              rows={2}
              variant="outlined"
              sx={{ mb: 1 }}
            />
            <Button
              size="small"
              variant="contained"
              onClick={submitFeedbackComment}
              disabled={!feedbackComment}
            >
              {t('chat.feedback.submit')}
            </Button>
          </Box>
        )}

        {feedbackSubmitted && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {t('chat.feedback.thanks')}
          </Typography>
        )}
      </BotMessage>
    </Box>
  );
};

export default ChatMessage;
