import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TablePagination, 
  TableRow,
  Typography,
  TextField,
  InputAdornment,
  IconButton,
  Chip
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { fetchExaminations, deleteExamination } from '../../store/slices/examinationSlice';
import { 
  Add as AddIcon, 
  Search as SearchIcon, 
  Edit as EditIcon, 
  Delete as DeleteIcon,
  Assessment as AssessmentIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import LoadingIndicator from '../common/LoadingIndicator';

const ExaminationList = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { examinations, loading, error } = useSelector((state) => state.examination);
  
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredExaminations, setFilteredExaminations] = useState([]);
  
  useEffect(() => {
    dispatch(fetchExaminations());
  }, [dispatch]);
  
  useEffect(() => {
    if (examinations) {
      setFilteredExaminations(
        examinations.filter(exam => 
          exam.name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
          exam.exam_type?.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }
  }, [examinations, searchTerm]);
  
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
    setPage(0);
  };
  
  const handleAddExamination = () => {
    navigate('/examinations/create');
  };
  
  const handleEditExamination = (id) => {
    navigate(`/examinations/edit/${id}`);
  };
  
  const handleViewResults = (id) => {
    navigate(`/examinations/${id}/results`);
  };
  
  const handleManageSubjects = (id) => {
    navigate(`/examinations/${id}/subjects`);
  };
  
  const handleDeleteExamination = (id) => {
    if (window.confirm('Are you sure you want to delete this examination?')) {
      dispatch(deleteExamination(id));
    }
  };
  
  const getExamStatusColor = (exam) => {
    const currentDate = new Date();
    const startDate = new Date(exam.start_date);
    const endDate = new Date(exam.end_date);
    
    if (currentDate < startDate) {
      return 'info'; // Upcoming
    } else if (currentDate >= startDate && currentDate <= endDate) {
      return 'warning'; // In progress
    } else {
      return 'success'; // Completed
    }
  };
  
  const getExamStatus = (exam) => {
    const currentDate = new Date();
    const startDate = new Date(exam.start_date);
    const endDate = new Date(exam.end_date);
    
    if (currentDate < startDate) {
      return 'Upcoming';
    } else if (currentDate >= startDate && currentDate <= endDate) {
      return 'In Progress';
    } else {
      return 'Completed';
    }
  };
  
  if (loading) {
    return <LoadingIndicator />;
  }
  
  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" component="h2">
          Examinations Management
        </Typography>
        <Box sx={{ display: 'flex' }}>
          <TextField
            size="small"
            label="Search"
            variant="outlined"
            value={searchTerm}
            onChange={handleSearch}
            sx={{ mr: 2 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleAddExamination}
          >
            Add Examination
          </Button>
        </Box>
      </Box>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          Error: {error}
        </Typography>
      )}

      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        <TableContainer sx={{ maxHeight: 'calc(100vh - 240px)' }}>
          <Table stickyHeader aria-label="examinations table">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Class</TableCell>
                <TableCell>Start Date</TableCell>
                <TableCell>End Date</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Published</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredExaminations
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((exam) => (
                  <TableRow hover key={exam.id}>
                    <TableCell>{exam.name}</TableCell>
                    <TableCell>
                      {exam.exam_type}
                    </TableCell>
                    <TableCell>{exam.class_?.name} {exam.class_?.section}</TableCell>
                    <TableCell>
                      {format(new Date(exam.start_date), 'dd MMM yyyy')}
                    </TableCell>
                    <TableCell>
                      {format(new Date(exam.end_date), 'dd MMM yyyy')}
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={getExamStatus(exam)} 
                        color={getExamStatusColor(exam)} 
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={exam.is_published ? 'Published' : 'Draft'} 
                        color={exam.is_published ? 'success' : 'default'} 
                        size="small"
                        variant={exam.is_published ? 'filled' : 'outlined'}
                      />
                    </TableCell>
                    <TableCell align="center">
                      <IconButton 
                        color="primary" 
                        size="small" 
                        onClick={() => handleEditExamination(exam.id)}
                        title="Edit"
                        sx={{ mr: 0.5 }}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <IconButton 
                        color="secondary" 
                        size="small" 
                        onClick={() => handleManageSubjects(exam.id)}
                        title="Manage Subjects"
                        sx={{ mr: 0.5 }}
                      >
                        <AssessmentIcon fontSize="small" />
                      </IconButton>
                      <IconButton 
                        color="info" 
                        size="small" 
                        onClick={() => handleViewResults(exam.id)}
                        title="View Results"
                        sx={{ mr: 0.5 }}
                      >
                        <VisibilityIcon fontSize="small" />
                      </IconButton>
                      <IconButton 
                        color="error" 
                        size="small" 
                        onClick={() => handleDeleteExamination(exam.id)}
                        title="Delete"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              {filteredExaminations.length === 0 && (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    No examinations found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={filteredExaminations.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
    </Box>
  );
};

export default ExaminationList; 