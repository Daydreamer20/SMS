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
  Tooltip
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { fetchStudents, deleteStudent } from '../../store/slices/studentSlice';
import { 
  Add as AddIcon, 
  Search as SearchIcon, 
  Edit as EditIcon, 
  Delete as DeleteIcon,
  Assessment as ReportIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import LoadingIndicator from '../common/LoadingIndicator';

const StudentList = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { students, loading, error } = useSelector((state) => state.student);
  
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredStudents, setFilteredStudents] = useState([]);
  
  useEffect(() => {
    dispatch(fetchStudents());
  }, [dispatch]);
  
  useEffect(() => {
    if (students) {
      setFilteredStudents(
        students.filter(student => 
          student.user?.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
          student.admission_number?.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }
  }, [students, searchTerm]);
  
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
  
  const handleAddStudent = () => {
    navigate('/students/create');
  };
  
  const handleEditStudent = (id) => {
    navigate(`/students/edit/${id}`);
  };
  
  const handleDeleteStudent = (id) => {
    if (window.confirm('Are you sure you want to delete this student?')) {
      dispatch(deleteStudent(id));
    }
  };

  const handleViewReports = (id) => {
    navigate(`/students/${id}/performance-reports`);
  };
  
  if (loading) {
    return <LoadingIndicator />;
  }
  
  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" component="h2">
          Students Management
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
            onClick={handleAddStudent}
          >
            Add Student
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
          <Table stickyHeader aria-label="students table">
            <TableHead>
              <TableRow>
                <TableCell>Admission #</TableCell>
                <TableCell>Roll #</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Gender</TableCell>
                <TableCell>Class</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Phone</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredStudents
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((student) => (
                  <TableRow hover key={student.id}>
                    <TableCell>{student.admission_number}</TableCell>
                    <TableCell>{student.roll_number}</TableCell>
                    <TableCell>{student.user?.full_name}</TableCell>
                    <TableCell>{student.gender}</TableCell>
                    <TableCell>{student.class_?.name} {student.class_?.section}</TableCell>
                    <TableCell>{student.user?.email}</TableCell>
                    <TableCell>{student.phone}</TableCell>
                    <TableCell align="center">
                      <Tooltip title="Performance Reports">
                        <IconButton 
                          color="info" 
                          size="small" 
                          onClick={() => handleViewReports(student.id)}
                          sx={{ mr: 1 }}
                        >
                          <ReportIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit">
                        <IconButton 
                          color="primary" 
                          size="small" 
                          onClick={() => handleEditStudent(student.id)}
                          sx={{ mr: 1 }}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton 
                          color="error" 
                          size="small" 
                          onClick={() => handleDeleteStudent(student.id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              {filteredStudents.length === 0 && (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    No students found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={filteredStudents.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
    </Box>
  );
};

export default StudentList; 