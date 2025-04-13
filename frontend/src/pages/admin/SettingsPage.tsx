import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Divider,
  Stack,
  useTheme,
} from '@mui/material';
import { Save as SaveIcon } from '@mui/icons-material';
import { settingsService } from '../../services';
import { useAuth } from '../../contexts';
import { Settings } from '../../types';

const SettingsPage: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const theme = useTheme(); 
  const { isAuthenticated, user } = useAuth();
  const [settings, setSettings] = useState<Settings>({
    chunk_size: 1000,
    chunk_overlap: 200,
    embedding_model: 'text-embedding-ada-002',
    llm_provider: 'gemini',
    supported_languages: ['vi', 'en'],
  });
  const [isLoading, setIsLoading] = useState(true); 
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'admin') {
      navigate('/login');
      return;
    }

    loadSettings();
  }, [isAuthenticated, user, navigate]);

  const loadSettings = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await settingsService.getSettings();
      setSettings(response);
    } catch (error) {
      console.error('Failed to load settings:', error);
      setError(t('admin.settings.error'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleChunkSizeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value);
    if (!isNaN(value) && value > 0) {
      setSettings({ ...settings, chunk_size: value });
    }
  };

  const handleChunkOverlapChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value);
    if (!isNaN(value) && value >= 0) {
      setSettings({ ...settings, chunk_overlap: value });
    }
  };

  const handleEmbeddingModelChange = (e: SelectChangeEvent<string>) => {
    setSettings({ ...settings, embedding_model: e.target.value });
  };

  const handleLlmProviderChange = (e: SelectChangeEvent<'gemini' | 'ollama'>) => {
    setSettings({ ...settings, llm_provider: e.target.value as 'gemini' | 'ollama' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const settingsToUpdate: Partial<Settings> = {
        chunk_size: settings.chunk_size,
        chunk_overlap: settings.chunk_overlap,
        embedding_model: settings.embedding_model,
        llm_provider: settings.llm_provider,
      };

      const result = await settingsService.updateSettings(settingsToUpdate);
      if (result.success) {
        setSuccess(result.message || t('admin.settings.save.success'));
      } else {
        setError(t('admin.settings.save.error'));
      }
    } catch (error) {
      console.error('Failed to save settings:', error);
      setError(t('admin.settings.save.error'));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {t('admin.settings.title')}
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Paper elevation={2} sx={{ p: 3 }}>
            <Box component="form" onSubmit={handleSubmit}>
              <Stack spacing={3}>
                <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
                  <TextField
                    fullWidth
                    label={t('admin.settings.chunk_size')}
                    type="number"
                    value={settings.chunk_size}
                    onChange={handleChunkSizeChange}
                    InputProps={{ inputProps: { min: 100, step: 100 } }}
                    disabled={isSaving}
                    helperText="Recommended: 1000"
                  />
                  <TextField
                    fullWidth
                    label={t('admin.settings.chunk_overlap')}
                    type="number"
                    value={settings.chunk_overlap}
                    onChange={handleChunkOverlapChange}
                    InputProps={{ inputProps: { min: 0, step: 50 } }}
                    disabled={isSaving}
                    helperText="Recommended: 200"
                  />
                </Stack>
                
                <FormControl fullWidth disabled={isSaving}>
                  <InputLabel>{t('admin.settings.embedding_model')}</InputLabel>
                  <Select
                    value={settings.embedding_model}
                    label={t('admin.settings.embedding_model')}
                    onChange={handleEmbeddingModelChange}
                  >
                    <MenuItem value="text-embedding-ada-002">OpenAI Ada 002</MenuItem>
                    <MenuItem value="text-embedding-3-small">OpenAI Embedding 3 Small</MenuItem>
                    <MenuItem value="text-embedding-3-large">OpenAI Embedding 3 Large</MenuItem>
                    {/* Add other embedding models if available */}
                  </Select>
                </FormControl>

                <Divider sx={{ pt: 2 }} />
                <Typography variant="h6" sx={{ mb: -1 }}>{t('admin.settings.llm_provider.title', 'LLM Provider')}</Typography>

                <FormControl fullWidth disabled={isSaving}>
                  <InputLabel>{t('admin.settings.llm_provider.label', 'Chat Response Model')}</InputLabel>
                  <Select
                    value={settings.llm_provider}
                    label={t('admin.settings.llm_provider.label', 'Chat Response Model')}
                    onChange={handleLlmProviderChange}
                  >
                    <MenuItem value="gemini">Gemini (Cloud API)</MenuItem>
                    <MenuItem value="ollama">Ollama (Local)</MenuItem>
                  </Select>
                </FormControl>

                 {/* Optionally display Ollama settings (read-only for now) */}
                 {settings.llm_provider === 'ollama' && (
                   <Stack spacing={1} sx={{ pl: 1, borderLeft: `2px solid ${theme.palette.divider}`, ml: 1 }}>
                     <Typography variant="body2" color="text.secondary">
                       Ollama Base URL: {settings.ollama_base_url || 'N/A'}
                     </Typography>
                     <Typography variant="body2" color="text.secondary">
                       Ollama Model: {settings.ollama_model_name || 'N/A'}
                     </Typography>
                     <Typography variant="caption" color="text.secondary">
                       {t('admin.settings.ollama.info', 'These settings are configured in the backend .env file.')}
                     </Typography>
                   </Stack>
                 )}
                
                <Box>
                  <Divider sx={{ my: 2 }} />
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                    <Button
                      type="submit"
                      variant="contained"
                      color="primary"
                      startIcon={isSaving ? <CircularProgress size={20} /> : <SaveIcon />}
                      disabled={isSaving}
                    >
                      {isSaving ? t('app.loading') : t('admin.settings.save')}
                    </Button>
                  </Box>
                </Box>
              </Stack>
            </Box>
          </Paper>
        )}
      </Box>
    </Container>
  );
};

export default SettingsPage;
