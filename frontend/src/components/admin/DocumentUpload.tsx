import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Stack,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
} from '@mui/material';
import { CloudUpload as UploadIcon } from '@mui/icons-material';
import { documentService } from '../../services';
import { DocumentUpload as DocumentUploadType } from '../../types';

interface DocumentUploadProps {
  onUploadSuccess?: () => void;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadSuccess }) => {
  const { t } = useTranslation();
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('general');
  const [tags, setTags] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0]);
      if (!title) {
        setTitle(event.target.files[0].name.split('.')[0]);
      }
    }
  };

  const handleCategoryChange = (event: SelectChangeEvent) => {
    setCategory(event.target.value);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const documentData: DocumentUploadType = {
        file,
        title: title || file.name,
        category,
        tags,
        description,
      };

      await documentService.uploadDocument(documentData);
      setSuccess(t('admin.documents.upload.success'));
      
      // Reset form
      setFile(null);
      setTitle('');
      setCategory('general');
      setTags('');
      setDescription('');
      
      if (onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : t('admin.documents.upload.error')
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        {t('admin.documents.upload.title')}
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
      
      <Box component="form" onSubmit={handleSubmit}>
        <Stack spacing={2}>
          <Button
            variant="outlined"
            component="label"
            startIcon={<UploadIcon />}
            fullWidth
            sx={{ py: 1.5, textTransform: 'none' }}
          >
            {file ? file.name : t('admin.documents.upload.file')}
            <input
              type="file"
              hidden
              accept=".pdf,.docx,.txt,.csv"
              onChange={handleFileChange}
            />
          </Button>
          
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
            <TextField
              fullWidth
              label={t('admin.documents.upload.title.label')}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
            
            <FormControl fullWidth>
              <InputLabel>{t('admin.documents.upload.category')}</InputLabel>
              <Select
                value={category}
                label={t('admin.documents.upload.category')}
                onChange={handleCategoryChange}
              >
                <MenuItem value="general">General</MenuItem>
                <MenuItem value="faq">FAQ</MenuItem>
                <MenuItem value="policy">Policy</MenuItem>
                <MenuItem value="guide">Guide</MenuItem>
                <MenuItem value="technical">Technical</MenuItem>
              </Select>
            </FormControl>
          </Stack>
          
          <TextField
            fullWidth
            label={t('admin.documents.upload.tags')}
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            placeholder="tag1, tag2, tag3"
          />
          
          <TextField
            fullWidth
            label={t('admin.documents.upload.description')}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            multiline
            rows={3}
          />
          
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={!file || loading}
            startIcon={loading && <CircularProgress size={20} />}
            fullWidth
          >
            {loading
              ? t('app.loading')
              : t('admin.documents.upload.submit')}
          </Button>
        </Stack>
      </Box>
    </Paper>
  );
};

export default DocumentUpload;
