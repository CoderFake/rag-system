import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Container,
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Chip,
  Stack,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { DocumentUpload } from '../../components';
import { documentService } from '../../services';
import { useAuth } from '../../contexts';
import { Document } from '../../types';

const DocumentsPage: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState<string | null>(null);
  const [reindexDialogOpen, setReindexDialogOpen] = useState(false);
  const [showUploadForm, setShowUploadForm] = useState(false);

  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'admin') {
      navigate('/login');
      return;
    }

    loadDocuments();
  }, [isAuthenticated, user, navigate]);

  const loadDocuments = async () => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await documentService.getDocuments(page + 1, rowsPerPage);
      setDocuments(response.documents);
    } catch (error) {
      console.error('Failed to load documents:', error);
      setError(t('admin.documents.error'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage);
    loadDocuments();
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
    loadDocuments();
  };

  const handleDeleteClick = (documentId: string) => {
    setDocumentToDelete(documentId);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (documentToDelete) {
      setIsLoading(true);
      setError(null);
      setSuccess(null);

      try {
        const result = await documentService.deleteDocument(documentToDelete);
        if (result.success) {
          setSuccess(t('admin.documents.delete.success'));
          // Remove document from state
          setDocuments(documents.filter(doc => doc.id !== documentToDelete));
        } else {
          setError(t('admin.documents.delete.error'));
        }
      } catch (error) {
        console.error('Failed to delete document:', error);
        setError(t('admin.documents.delete.error'));
      } finally {
        setIsLoading(false);
        setDeleteDialogOpen(false);
        setDocumentToDelete(null);
      }
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setDocumentToDelete(null);
  };

  const handleReindexClick = () => {
    setReindexDialogOpen(true);
  };

  const handleReindexConfirm = async () => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await documentService.reindexDocuments();
      if (result.success) {
        setSuccess(t('admin.documents.reindex.success'));
      } else {
        setError(t('admin.documents.reindex.error'));
      }
    } catch (error) {
      console.error('Failed to reindex documents:', error);
      setError(t('admin.documents.reindex.error'));
    } finally {
      setIsLoading(false);
      setReindexDialogOpen(false);
    }
  };

  const handleReindexCancel = () => {
    setReindexDialogOpen(false);
  };

  const handleUploadSuccess = () => {
    loadDocuments();
    setShowUploadForm(false);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            {t('admin.documents.title')}
          </Typography>
          <Stack direction="row" spacing={2}>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={handleReindexClick}
              disabled={isLoading}
            >
              {t('admin.documents.reindex')}
            </Button>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setShowUploadForm(!showUploadForm)}
            >
              {showUploadForm ? t('app.cancel') : t('admin.documents.add')}
            </Button>
          </Stack>
        </Box>

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

        {showUploadForm && (
          <DocumentUpload onUploadSuccess={handleUploadSuccess} />
        )}

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        ) : documents.length === 0 ? (
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="body1" color="text.secondary">
              {t('admin.documents.empty')}
            </Typography>
          </Paper>
        ) : (
          <Paper sx={{ width: '100%', overflow: 'hidden' }}>
            <TableContainer>
              <Table stickyHeader aria-label="documents table">
                <TableHead>
                  <TableRow>
                    <TableCell>{t('admin.documents.name')}</TableCell>
                    <TableCell>{t('admin.documents.category')}</TableCell>
                    <TableCell>{t('admin.documents.type')}</TableCell>
                    <TableCell>{t('admin.documents.date')}</TableCell>
                    <TableCell align="right">{t('admin.documents.actions')}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {documents.map((document) => (
                    <TableRow key={document.id} hover>
                      <TableCell component="th" scope="row">
                        {document.title}
                      </TableCell>
                      <TableCell>
                        <Chip label={document.category} size="small" />
                      </TableCell>
                      <TableCell>{document.file_type}</TableCell>
                      <TableCell>{formatDate(document.created_at)}</TableCell>
                      <TableCell align="right">
                        <IconButton
                          aria-label="delete"
                          onClick={() => handleDeleteClick(document.id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              rowsPerPageOptions={[5, 10, 25]}
              component="div"
              count={documents.length}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
            />
          </Paper>
        )}
      </Box>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
        aria-labelledby="delete-dialog-title"
        aria-describedby="delete-dialog-description"
      >
        <DialogTitle id="delete-dialog-title">
          {t('admin.documents.delete.confirmation')}
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="delete-dialog-description">
            {t('app.confirmation')}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel}>{t('app.no')}</Button>
          <Button onClick={handleDeleteConfirm} color="error" autoFocus>
            {t('app.yes')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Reindex Confirmation Dialog */}
      <Dialog
        open={reindexDialogOpen}
        onClose={handleReindexCancel}
        aria-labelledby="reindex-dialog-title"
        aria-describedby="reindex-dialog-description"
      >
        <DialogTitle id="reindex-dialog-title">
          {t('admin.documents.reindex.confirmation')}
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="reindex-dialog-description">
            {t('app.confirmation')}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleReindexCancel}>{t('app.no')}</Button>
          <Button onClick={handleReindexConfirm} color="primary" autoFocus>
            {t('app.yes')}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default DocumentsPage;
