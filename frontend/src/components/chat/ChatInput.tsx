import React, { useState, KeyboardEvent, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  TextField,
  IconButton,
  Paper,
  InputAdornment,
  CircularProgress,
  useTheme,
  alpha,
  Tooltip,
} from '@mui/material';
import { 
  Send as SendIcon,
  DeleteOutline as ClearIcon
} from '@mui/icons-material';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
  disabled?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading = false,
  disabled = false,
}) => {
  const { t } = useTranslation();
  const theme = useTheme();
  const [message, setMessage] = useState('');
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto focus input when component mounts
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const handleSendMessage = () => {
    if (message.trim() && !isLoading && !disabled) {
      onSendMessage(message);
      setMessage('');
      // Re-focus the input after sending
      setTimeout(() => {
        if (inputRef.current) {
          inputRef.current.focus();
        }
      }, 0);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleClearMessage = () => {
    setMessage('');
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: { xs: 1, sm: 2 },
        borderRadius: '16px',
        backgroundColor: theme.palette.mode === 'dark' 
          ? alpha(theme.palette.background.paper, 0.8)
          : theme.palette.background.paper,
        backdropFilter: 'blur(8px)',
        boxShadow: theme.palette.mode === 'dark'
          ? '0 4px 20px rgba(0, 0, 0, 0.25)'
          : '0 4px 20px rgba(0, 0, 0, 0.1)',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'flex-end' }}>
        <TextField
          fullWidth
          placeholder={t('chat.placeholder')}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          multiline
          maxRows={4}
          disabled={isLoading || disabled}
          variant="standard"
          inputRef={inputRef}
          InputProps={{
            disableUnderline: true,
            sx: {
              p: 1,
              fontSize: '1rem',
              '&.Mui-focused': {
                boxShadow: 'none',
              },
            },
            endAdornment: (
              <InputAdornment position="end">
                {message.length > 0 && !isLoading && (
                  <Tooltip title={t('app.cancel') || 'Clear'}>
                    <IconButton
                      size="small"
                      onClick={handleClearMessage}
                      sx={{ mr: 0.5, color: theme.palette.text.secondary }}
                    >
                      <ClearIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                )}
                {isLoading ? (
                  <CircularProgress size={24} thickness={4} />
                ) : (
                  <IconButton
                    color="primary"
                    onClick={handleSendMessage}
                    disabled={!message.trim() || disabled}
                    sx={{
                      bgcolor: message.trim() ? theme.palette.primary.main : 'transparent',
                      color: message.trim() ? theme.palette.primary.contrastText : theme.palette.text.disabled,
                      '&:hover': {
                        bgcolor: message.trim() ? theme.palette.primary.dark : 'transparent',
                      },
                      '&.Mui-disabled': {
                        bgcolor: 'transparent',
                      },
                      transition: theme.transitions.create(['background-color', 'box-shadow']),
                    }}
                  >
                    <SendIcon />
                  </IconButton>
                )}
              </InputAdornment>
            ),
          }}
          sx={{
            '& .MuiInputBase-root': {
              borderRadius: '24px',
              backgroundColor: theme.palette.mode === 'dark' 
                ? alpha(theme.palette.background.default, 0.5)
                : alpha(theme.palette.background.default, 0.5),
              p: '8px 16px',
              transition: theme.transitions.create(['background-color', 'box-shadow']),
              '&:hover': {
                backgroundColor: theme.palette.mode === 'dark' 
                  ? alpha(theme.palette.background.default, 0.7)
                  : alpha(theme.palette.background.default, 0.7),
              },
              '&.Mui-focused': {
                backgroundColor: theme.palette.mode === 'dark' 
                  ? alpha(theme.palette.background.default, 0.9)
                  : alpha(theme.palette.background.default, 0.9),
                boxShadow: `0 0 0 2px ${alpha(theme.palette.primary.main, 0.25)}`,
              },
            },
          }}
        />
      </Box>
    </Paper>
  );
};

export default ChatInput;