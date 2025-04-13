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


const TypeWriter = ({ content, speed = 15, animate = true, onComplete = () => {} }: { 
  content: string; 
  speed?: number; 
  animate?: boolean;
  onComplete?: () => void;
}) => {
  const [displayedContent, setDisplayedContent] = useState(animate ? '' : content);
  const [isComplete, setIsComplete] = useState(!animate);
  const position = useRef(0);
  const contentRef = useRef(content);

  useEffect(() => {
    if (content !== contentRef.current) {
      contentRef.current = content;
      
      if (animate) {
        position.current = 0;
        setDisplayedContent('');
        setIsComplete(false);
      } else {
        setDisplayedContent(content);
        setIsComplete(true);
        onComplete();
      }
    }
  }, [content, animate, onComplete]);

  useEffect(() => {
    if (!animate || isComplete) {
      return;
    }

    if (position.current >= content.length) {
      setIsComplete(true);
      onComplete();
      return;
    }

    const timer = setTimeout(() => {
      position.current += 1;
      setDisplayedContent(content.slice(0, position.current));
    }, speed);

    return () => clearTimeout(timer);
  }, [displayedContent, content, speed, animate, isComplete, onComplete]);

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


const SequentialTypeWriter = ({ 
  blocks, 
  speed = 15, 
  animate = false 
}: { 
  blocks: { type: string; content: string }[]; 
  speed?: number; 
  animate?: boolean;
}) => {
  const [currentBlockIndex, setCurrentBlockIndex] = useState(animate ? 0 : blocks.length);
  const theme = useTheme();

  const renderBlock = (block: { type: string; content: string }, index: number) => {
    const isActive = index <= currentBlockIndex;
    
    switch (block.type) {
      case 'paragraph':
        return (
          <Typography key={index} variant="body1" gutterBottom>
            {isActive ? (
              index === currentBlockIndex && animate ? (
                <TypeWriter 
                  content={block.content} 
                  animate={animate} 
                  speed={speed}
                  onComplete={() => setCurrentBlockIndex(prev => prev + 1)}
                />
              ) : block.content
            ) : ''}
          </Typography>
        );
      case 'heading1':
        return (
          <Typography key={index} variant="h5" gutterBottom sx={{ fontWeight: 600, mt: 2 }}>
            {isActive ? (
              index === currentBlockIndex && animate ? (
                <TypeWriter 
                  content={block.content} 
                  animate={animate} 
                  speed={speed}
                  onComplete={() => setCurrentBlockIndex(prev => prev + 1)}
                />
              ) : block.content
            ) : ''}
          </Typography>
        );
      case 'heading2':
        return (
          <Typography key={index} variant="h6" gutterBottom sx={{ fontWeight: 600, mt: 2 }}>
            {isActive ? (
              index === currentBlockIndex && animate ? (
                <TypeWriter 
                  content={block.content} 
                  animate={animate} 
                  speed={speed}
                  onComplete={() => setCurrentBlockIndex(prev => prev + 1)}
                />
              ) : block.content
            ) : ''}
          </Typography>
        );
      case 'heading3':
        return (
          <Typography key={index} variant="subtitle1" gutterBottom sx={{ fontWeight: 600, mt: 1.5 }}>
            {isActive ? (
              index === currentBlockIndex && animate ? (
                <TypeWriter 
                  content={block.content} 
                  animate={animate} 
                  speed={speed}
                  onComplete={() => setCurrentBlockIndex(prev => prev + 1)}
                />
              ) : block.content
            ) : ''}
          </Typography>
        );
      case 'listItem':
        return (
          <Box key={index} component="li" sx={{ mb: 0.5 }}>
            {isActive ? (
              index === currentBlockIndex && animate ? (
                <TypeWriter 
                  content={block.content} 
                  animate={animate} 
                  speed={speed}
                  onComplete={() => setCurrentBlockIndex(prev => prev + 1)}
                />
              ) : block.content
            ) : ''}
          </Box>
        );
      case 'code':
        return (
          <Box 
            key={index}
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
          >
            {isActive ? (
              index === currentBlockIndex && animate ? (
                <TypeWriter 
                  content={block.content} 
                  animate={animate} 
                  speed={speed}
                  onComplete={() => setCurrentBlockIndex(prev => prev + 1)}
                />
              ) : block.content
            ) : ''}
          </Box>
        );
      case 'inlineCode':
        return (
          <Box 
            key={index}
            component="code" 
            sx={{ 
              backgroundColor: theme.palette.mode === 'dark' ? alpha('#000', 0.3) : alpha('#eee', 0.8),
              borderRadius: '4px',
              px: 0.5,
              py: 0.25,
              fontFamily: 'monospace',
            }} 
          >
            {isActive ? (
              index === currentBlockIndex && animate ? (
                <TypeWriter 
                  content={block.content} 
                  animate={animate} 
                  speed={speed}
                  onComplete={() => setCurrentBlockIndex(prev => prev + 1)}
                />
              ) : block.content
            ) : ''}
          </Box>
        );
      case 'blockquote':
        return (
          <Box
            key={index}
            component="blockquote"
            sx={{
              borderLeft: `4px solid ${theme.palette.primary.main}`,
              pl: 2,
              py: 0.5,
              my: 1,
              color: 'text.secondary',
              fontStyle: 'italic',
            }}
          >
            {isActive ? (
              index === currentBlockIndex && animate ? (
                <TypeWriter 
                  content={block.content} 
                  animate={animate} 
                  speed={speed}
                  onComplete={() => setCurrentBlockIndex(prev => prev + 1)}
                />
              ) : block.content
            ) : ''}
          </Box>
        );
      default:
        return null;
    }
  };

  return <>{blocks.map((block, index) => renderBlock(block, index))}</>;
};


const parseMarkdownContent = (content: string): { type: string; content: string }[] => {
  const lines = content.split('\n');
  const blocks: { type: string; content: string }[] = [];
  
  let currentBlock: { type: string; content: string } | null = null;
  
  lines.forEach(line => {
    const trimmedLine = line.trim();
    

    let blockType: string | null = null;
    
    if (trimmedLine.startsWith('# ')) {
      blockType = 'heading1';
    } else if (trimmedLine.startsWith('## ')) {
      blockType = 'heading2';
    } else if (trimmedLine.startsWith('### ')) {
      blockType = 'heading3';
    } else if (trimmedLine.startsWith('- ') || trimmedLine.startsWith('* ') || /^\d+\.\s/.test(trimmedLine)) {
      blockType = 'listItem';
    } else if (trimmedLine.startsWith('> ')) {
      blockType = 'blockquote';
    } else if (trimmedLine.startsWith('```')) {
      blockType = 'code';
    } else if (trimmedLine.length > 0) {
      blockType = 'paragraph';
    }
    

    if (trimmedLine.length === 0) {
      if (currentBlock) {
        blocks.push(currentBlock);
        currentBlock = null;
      }
    } else if (blockType) {

      let cleanContent = trimmedLine;
      if (blockType === 'heading1') cleanContent = trimmedLine.substring(2);
      else if (blockType === 'heading2') cleanContent = trimmedLine.substring(3);
      else if (blockType === 'heading3') cleanContent = trimmedLine.substring(4);
      else if (blockType === 'blockquote') cleanContent = trimmedLine.substring(2);
      else if (blockType === 'code' && trimmedLine === '```') {

        if (currentBlock && currentBlock.type === 'code') {
          blocks.push(currentBlock);
          currentBlock = null;
        }
        return;
      }
      
      if (currentBlock && currentBlock.type === blockType) {

        currentBlock.content += '\n' + cleanContent;
      } else {

        if (currentBlock) blocks.push(currentBlock);
        currentBlock = { type: blockType, content: cleanContent };
      }
    }
  });
  

  if (currentBlock) {
    blocks.push(currentBlock);
  }
  
  return blocks;
};

const ContentDisplay = ({ content, animate = false }: { content: string; animate?: boolean }) => {
  const theme = useTheme();
  const [useSequentialTyping, setUseSequentialTyping] = useState(true);
  

  const blocks = parseMarkdownContent(content);
  

  if (blocks.length > 10 || content.includes('```') || content.includes('|')) {
    return (
      <ReactMarkdown
        components={{
          p: ({ node, ...props }) => (
            <Typography variant="body1" gutterBottom {...props} />
          ),
          h1: ({ node, ...props }) => (
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mt: 2 }} {...props} />
          ),
          h2: ({ node, ...props }) => (
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mt: 2 }} {...props} />
          ),
          h3: ({ node, ...props }) => (
            <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600, mt: 1.5 }} {...props} />
          ),
          ul: ({ node, ...props }) => <Box component="ul" sx={{ pl: 2, my: 1 }} {...props} />,
          ol: ({ node, ...props }) => <Box component="ol" sx={{ pl: 2, my: 1 }} {...props} />,
          li: ({ node, ...props }) => (
            <Box component="li" sx={{ mb: 0.5 }} {...props} />
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
  }
  

  return <SequentialTypeWriter blocks={blocks} animate={animate} />;
};

interface ChatMessageProps {
  message: ChatMessageType;
  onFeedback?: (responseId: string, type: string, value: string) => Promise<void>;
  animate?: boolean;
  isNewMessage?: boolean;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ 
  message, 
  onFeedback, 
  animate = true,
  isNewMessage = false 
}) => {
  const { t } = useTranslation();
  const theme = useTheme();
  const [showSources, setShowSources] = useState(false);
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);
  const [feedbackComment, setFeedbackComment] = useState('');
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [isJustAdded, setIsJustAdded] = useState(isNewMessage);
  
  const shouldAnimate = animate && isNewMessage;

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
            <ContentDisplay 
              content={message.content} 
              animate={shouldAnimate} 
            />

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