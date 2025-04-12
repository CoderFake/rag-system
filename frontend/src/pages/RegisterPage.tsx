import React, { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Link,
  Alert,
  CircularProgress,
  Stack,
  useTheme,
  useMediaQuery,
  InputAdornment,
  IconButton,
  Divider,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Person as PersonIcon,
  Lock as LockIcon,
  Email as EmailIcon,
  Badge as BadgeIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts';
import { RegisterData } from '../types';

const RegisterPage: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const theme = useTheme();
  const { register, error, clearError, isLoading } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [success, setSuccess] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const isXsScreen = useMediaQuery(theme.breakpoints.down('sm'));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setSuccess(false);

    try {
      const userData: RegisterData = {
        username,
        password,
        name,
        email,
      };
      await register(userData);
      setSuccess(true);
      

      setUsername('');
      setPassword('');
      setName('');
      setEmail('');
      

      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (error) {

      console.error('Registration failed:', error);
    }
  };

  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <Container 
      component="main" 
      maxWidth="sm"
      sx={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: { xs: 'calc(100vh - 112px)', sm: 'calc(100vh - 128px)' },
        justifyContent: 'center',
        px: isXsScreen ? 2 : 3,
      }}
    >
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          width: '100%',
        }}
      >
        <Paper
          elevation={3}
          sx={{
            p: { xs: 2, sm: 3, md: 4 },
            width: '100%',
            maxWidth: '550px',
            borderRadius: { xs: 2, sm: 3 },
          }}
        >
          <Typography 
            component="h1" 
            variant={isXsScreen ? "h5" : "h4"} 
            align="center" 
            gutterBottom
            sx={{ 
              fontWeight: 600,
              mb: 2
            }}
          >
            {t('auth.register.title')}
          </Typography>

          {error && (
            <Alert 
              severity="error" 
              sx={{ 
                mb: 2,
                fontSize: isXsScreen ? '0.875rem' : '1rem'
              }}
            >
              {error}
            </Alert>
          )}

          {success && (
            <Alert 
              severity="success" 
              sx={{ 
                mb: 2,
                fontSize: isXsScreen ? '0.875rem' : '1rem'
              }}
            >
              {t('auth.register.success')}
            </Alert>
          )}

          <Box 
            component="form" 
            onSubmit={handleSubmit} 
            sx={{ mt: 1 }}
            noValidate
          >
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label={t('auth.username')}
              name="username"
              autoComplete="username"
              autoFocus
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={isLoading || success}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <PersonIcon color="action" />
                  </InputAdornment>
                ),
              }}
              size={isXsScreen ? "small" : "medium"}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label={t('auth.password')}
              type={showPassword ? "text" : "password"}
              id="password"
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading || success}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <LockIcon color="action" />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={handleTogglePasswordVisibility}
                      edge="end"
                      size={isXsScreen ? "small" : "medium"}
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                )
              }}
              size={isXsScreen ? "small" : "medium"}
            />
            
            <Divider sx={{ my: 2 }} />
            
            <Typography 
              variant="body2" 
              color="text.secondary" 
              sx={{ mb: 1 }}
            >
              {t('app.profile')} {t('app.information')}
            </Typography>
            
            <Stack 
              direction={{ xs: 'column', sm: 'row' }} 
              spacing={2} 
              sx={{ mt: 1 }}
            >
              <TextField
                fullWidth
                id="name"
                label={t('auth.name')}
                name="name"
                autoComplete="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={isLoading || success}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <BadgeIcon color="action" />
                    </InputAdornment>
                  ),
                }}
                size={isXsScreen ? "small" : "medium"}
              />
              <TextField
                fullWidth
                id="email"
                label={t('auth.email')}
                name="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading || success}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <EmailIcon color="action" />
                    </InputAdornment>
                  ),
                }}
                size={isXsScreen ? "small" : "medium"}
              />
            </Stack>
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ 
                mt: 3, 
                mb: 2,
                py: isXsScreen ? 1 : 1.5 
              }}
              disabled={isLoading || success || !username || !password}
            >
              {isLoading ? (
                <CircularProgress size={24} />
              ) : (
                t('auth.register.submit')
              )}
            </Button>
            <Box sx={{ textAlign: 'center' }}>
              <Link 
                component={RouterLink} 
                to="/login" 
                variant="body2"
                sx={{
                  textDecoration: 'none',
                  '&:hover': {
                    textDecoration: 'underline'
                  }
                }}
              >
                {t('auth.register.login')}
              </Link>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default RegisterPage;