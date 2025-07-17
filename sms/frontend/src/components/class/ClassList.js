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
import { fetchClasses, deleteClass } from '../../store/slices/classSlice';
import { Add as AddIcon, Search as SearchIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import LoadingIndicator from '../common/LoadingIndicator';

const ClassList = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { classes, loading, error } = useSelector((state) => state.class);
  
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredClasses, setFilteredClasses] = useState([]);
  
  useEffect(() => {
    dispatch(fetchClasses());
  }, [dispatch]);
  
  useEffect(() => {
    if (classes) {
      setFilteredClasses(
        classes.filter(cls => 
          cls.name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
          cls.section?.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }
  }, [classes, searchTerm]);
  
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
  
  const handleAddClass = () => {
    navigate('/classes/create');
  };
  
  const handleEditClass = (id) => {
    navigate(`/classes/edit/${id}`);
  };
  
  const handleDeleteClass = (id) => {
    if (window.confirm('Are you sure you want to delete this class?')) {
      dispatch(deleteClass(id));
    }
  };
  
  if (loading) {
    return <LoadingIndicator />;
  }
  
  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" component="h2">
          Class Management
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
            onClick={handleAddClass}
          >
            Add Class
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
          <Table stickyHeader aria-label="classes table">
            <TableHead>
              <TableRow>
                <TableCell>Class Name</TableCell>
                <TableCell>Section</TableCell>
                <TableCell>Grade Level</TableCell>
                <TableCell>Academic Year</TableCell>
                <TableCell>Class Teacher</TableCell>
                <TableCell>Students</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredClasses
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((cls) => (
                  <TableRow hover key={cls.id}>
                    <TableCell>{cls.name}</TableCell>
                    <TableCell>{cls.section}</TableCell>
                    <TableCell>{cls.grade_level}</TableCell>
                    <TableCell>{cls.academic_year?.name}</TableCell>
                    <TableCell>{cls.teacher?.user?.full_name || 'Not Assigned'}</TableCell>
                    <TableCell>
                      <Chip 
                        label={`${cls.students?.length || 0} students`} 
                        color="primary" 
                        size="small" 
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell align="center">
                      <IconButton 
                        color="primary" 
                        size="small" 
                        onClick={() => handleEditClass(cls.id)}
                        sx={{ mr: 1 }}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton 
                        color="error" 
                        size="small" 
                        onClick={() => handleDeleteClass(cls.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              {filteredClasses.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    No classes found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={filteredClasses.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
    </Box>
  );
};

export default ClassList; 