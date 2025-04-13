import React, { useState, useEffect, useRef } from 'react';
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
  Chip,
  useTheme,
  Tooltip,
  Divider,
  alpha,
  Avatar,
  Zoom,
  Fade,
} from '@mui/material';
import {
  ThumbUp,
  ThumbDown,
  ExpandMore,
  ExpandLess,
  Article as ArticleIcon,
  Person as PersonIcon,
  Android as BotIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { ChatMessage as ChatMessageType, DocumentSource } from '../../types';

const TypeWriter = ({ content, speed = 15 }: { content: string; speed?: number }) => {
  const [displayedContent, setDisplayedContent] = useState('');
  const [isComplete, setIsComplete] = useState(false);
  const position = useRef(0);

  useEffect(() => {
    position.current = 0;
    setDisplayedContent('');
    setIsComplete(false);
  }, [content]);

  useEffect(() => {
    if (displayedContent === content) {
      setIsComplete(true);
      return;
    }

    const timer = setTimeout(() => {
      position.current += 1;
      setDisplayedContent(content.slice(0, position.current));
    }, speed);

    return () => clearTimeout(timer);
  }, [displayedContent, content, speed]);

  const blinkAnimation = `@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
  }`;

  return (
    <>
      {displayedContent}
      {!isComplete && (
        <Box 
          component="span" 
          sx={{ 
            opacity: 0.7, 
            animation: 'blink 1s infinite',
            '@keyframes blink': {
              '0%, 100%': { opacity: 1 },
              '50%': { opacity: 0 },
            }
          }}
        >
          ▌
        </Box>
      )}
    </>
  );
};

const MarkdownContent = React.memo(({ content, animate = false }: { content: string; animate?: boolean }) => {
  const theme = useTheme();
  
  return (
    <ReactMarkdown
      components={{
        p: ({ node, ...props }) => (
          <Typography variant="body1" gutterBottom {...props}>
            {animate ? <TypeWriter content={props.children as string} /> : props.children}
          </Typography>
        ),
        h1: ({ node, ...props }) => (
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mt: 2 }} {...props}>
            {animate ? <TypeWriter content={props.children as string} /> : props.children}
          </Typography>
        ),
        h2: ({ node, ...props }) => (
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mt: 2 }} {...props}>
            {animate ? <TypeWriter content={props.children as string} /> : props.children}
          </Typography>
        ),
        h3: ({ node, ...props }) => (
          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600, mt: 1.5 }} {...props}>
            {animate ? <TypeWriter content={props.children as string} /> : props.children}
          </Typography>
        ),
        ul: ({ node, ...props }) => <Box component="ul" sx={{ pl: 2, my: 1 }} {...props} />,
        ol: ({ node, ...props }) => <Box component="ol" sx={{ pl: 2, my: 1 }} {...props} />,
        li: ({ node, ...props }) => (
          <Box component="li" sx={{ mb: 0.5 }} {...props}>
            {animate ? <TypeWriter content={props.children as string} /> : props.children}
          </Box>
        ),
        code: ({ node, ...props }) => {
          const isInline = props.className ? !props.className.includes('language-') : true;
          
          return isInline ? 
            <Box 
              component="code" 
              sx={{ 
                backgroundColor: theme.palette.mode === 'dark' ? alpha('#000', 0.3) : alpha('#eee', 0.8),
                borderRadius: '4px',
                px: 0.5,
                py: 0.25,
                fontFamily: 'monospace',
              }} 
              {...props} 
            /> : 
            <Box
              component="pre"
              sx={{
                backgroundColor: theme.palette.mode === 'dark' ? alpha('#000', 0.3) : alpha('#eee', 0.8),
                borderRadius: '6px',
                p: 1.5,
                my: 1.5,
                overflowX: 'auto',
                fontFamily: 'monospace',
                fontSize: '0.875rem',
                border: `1px solid ${theme.palette.divider}`,
              }}
              {...props}
            />
        },
        blockquote: ({ node, ...props }) => (
          <Box
            component="blockquote"
            sx={{
              borderLeft: `4px solid ${theme.palette.primary.main}`,
              pl: 2,
              py: 0.5,
              my: 1,
              color: 'text.secondary',
              fontStyle: 'italic',
            }}
            {...props}
          />
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
});

interface ChatMessageProps {
  message: ChatMessageType;
  onFeedback?: (responseId: string, type: string, value: string) => Promise<void>;
  animate?: boolean;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, onFeedback, animate = true }) => {
  const { t } = useTranslation();
  const theme = useTheme();
  const [showSources, setShowSources] = useState(false);
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);
  const [feedbackComment, setFeedbackComment] = useState('');
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [isJustAdded, setIsJustAdded] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsJustAdded(false);
    }, 300);
    return () => clearTimeout(timer);
  }, []);

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
      <Fade in={true} timeout={500}>
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
          <Paper 
            elevation={0}
            sx={{
              p: 2,
              maxWidth: '80%',
              borderRadius: '18px 4px 18px 18px',
              backgroundColor: theme.palette.primary.main,
              color: theme.palette.primary.contrastText,
              position: 'relative',
              display: 'flex',
              alignItems: 'flex-start',
              gap: 1.5,
            }}
          >
            <Avatar 
              sx={{ 
                width: 32, 
                height: 32, 
                bgcolor: alpha(theme.palette.common.white, 0.2),
                display: { xs: 'none', sm: 'flex' }
              }}
            >
              <PersonIcon fontSize="small" />
            </Avatar>
            <Typography variant="body1">{message.content}</Typography>
          </Paper>
        </Box>
      </Fade>
    );
  }

  return (
    <Zoom in={true} style={{ transitionDelay: isJustAdded ? '300ms' : '0ms' }}>
      <Box sx={{ display: 'flex', mb: 3 }}>
        <Paper
          elevation={0}
          sx={{
            p: 2,
            maxWidth: '85%',
            borderRadius: '4px 18px 18px 18px',
            backgroundColor: theme.palette.mode === 'dark' 
              ? alpha(theme.palette.background.paper, 0.6) 
              : theme.palette.background.paper,
            boxShadow: theme.palette.mode === 'dark' 
              ? `0 1px 2px ${alpha('#000', 0.1)}` 
              : `0 1px 4px ${alpha('#000', 0.1)}`,
            position: 'relative',
            display: 'flex',
            alignItems: 'flex-start',
            gap: 1.5,
          }}
        >
          <Avatar 
            sx={{ 
              width: 32, 
              height: 32, 
              bgcolor: theme.palette.primary.main,
              color: theme.palette.primary.contrastText,
              display: { xs: 'none', sm: 'flex' }
            }}
          >
            <BotIcon fontSize="small" />
          </Avatar>
          
          <Box sx={{ flexGrow: 1 }}>
            <MarkdownContent content={message.content} animate={animate} />

            {hasSources && (
              <Box sx={{ mt: 2 }}>
                <Button
                  size="small"
                  startIcon={showSources ? <ExpandLess /> : <ExpandMore />}
                  onClick={toggleSources}
                  sx={{ 
                    textTransform: 'none',
                    color: theme.palette.text.secondary,
                    mb: 1,
                  }}
                  endIcon={
                    <Chip 
                      label={message.sources?.length || 0} 
                      size="small" 
                      color="primary" 
                      variant="outlined" 
                      sx={{ height: 20, fontSize: '0.7rem' }}
                    />
                  }
                >
                  {t('chat.sources')}
                </Button>
                
                <Collapse in={showSources} timeout="auto" unmountOnExit>
                  <List
                    dense
                    sx={{
                      bgcolor: theme.palette.mode === 'dark' 
                        ? alpha(theme.palette.background.default, 0.4) 
                        : alpha(theme.palette.background.default, 0.7),
                      borderRadius: 1,
                      p: 1,
                    }}
                  >
                    {message.sources?.map((source: DocumentSource) => (
                      <ListItem 
                        key={source.id}
                        sx={{ 
                          borderBottom: `1px solid ${alpha(theme.palette.divider, 0.5)}`, 
                          '&:last-child': { 
                            borderBottom: 'none' 
                          } 
                        }}
                      >
                        <ArticleIcon 
                          fontSize="small" 
                          color="primary" 
                          sx={{ mr: 1, opacity: 0.7 }} 
                        />
                        <ListItemText
                          primary={<Typography variant="body2" fontWeight="medium">{source.title}</Typography>}
                          secondary={
                            <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                              <Chip 
                                label={source.category} 
                                size="small" 
                                sx={{ 
                                  height: 20, 
                                  fontSize: '0.7rem',
                                  mr: 1,
                                }} 
                              />
                              {source.relevance_score && (
                                <Typography variant="caption" color="text.secondary">
                                  {Math.round(source.relevance_score * 100)}% match
                                </Typography>
                              )}
                            </Box>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                </Collapse>
              </Box>
            )}

            {!feedbackSubmitted && onFeedback && (
              <Box sx={{ mt: 2 }}>
                <Divider sx={{ my: 1 }} />
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mr: 1, fontSize: '0.8rem' }}>
                    {t('chat.feedback.helpful')}
                  </Typography>
                  <Tooltip title={t('chat.feedback.thumbs_up')}>
                    <IconButton
                      size="small"
                      onClick={() => handleFeedback('thumbs_up')}
                      color="primary"
                      sx={{ mr: 1 }}
                    >
                      <ThumbUp fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title={t('chat.feedback.thumbs_down')}>
                    <IconButton
                      size="small"
                      onClick={() => handleFeedback('thumbs_down')}
                      color="primary"
                    >
                      <ThumbDown fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
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
              <Typography variant="body2" color="success.main" sx={{ mt: 1, fontSize: '0.8rem' }}>
                {t('chat.feedback.thanks')}
              </Typography>
            )}
          </Box>
        </Paper>
      </Box>
    </Zoom>
  );
};

export default ChatMessage;
