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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Tooltip
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { 
  fetchPerformanceReports,
  fetchStudentPerformanceReports,
  fetchPerformanceReport,
  createPerformanceReport,
  updatePerformanceReport,
  publishPerformanceReport,
  deletePerformanceReport 
} from '../../store/slices/studentSlice';
import { 
  Search as SearchIcon,
  Edit as EditIcon, 
  Delete as DeleteIcon, 
  Visibility as ViewIcon,
  Check as PublishIcon,
  Add as AddIcon
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import LoadingIndicator from '../common/LoadingIndicator';

const StudentPerformanceReports = ({ studentId = null }) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const params = useParams();
  
  // If studentId is not provided as prop, try to get from URL params
  const activeStudentId = studentId || params.studentId;
  
  const { 
    performanceReports, 
    studentPerformanceReports, 
    currentReport,
    loading, 
    error 
  } = useSelector((state) => state.student);
  
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredReports, setFilteredReports] = useState([]);
  const [openViewDialog, setOpenViewDialog] = useState(false);
  const [openFormDialog, setOpenFormDialog] = useState(false);
  const [formData, setFormData] = useState({
    term: '',
    academic_year: '',
    overall_grade: '',
    overall_percentage: '',
    attendance_percentage: '',
    remarks: '',
    teacher_comments: '',
    principal_comments: '',
    strengths: '',
    areas_for_improvement: '',
    is_published: false,
    student_id: activeStudentId || '',
    class_id: ''
  });
  const [editingReportId, setEditingReportId] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);
  const [filters, setFilters] = useState({
    term: '',
    academic_year: '',
    is_published: ''
  });
  
  useEffect(() => {
    // If studentId is provided, fetch reports for this student only
    if (activeStudentId) {
      dispatch(fetchStudentPerformanceReports({ 
        studentId: activeStudentId,
        params: {
          term: filters.term || undefined,
          academic_year: filters.academic_year || undefined
        }
      }));
    } else {
      // Otherwise fetch all reports with optional filters
      const params = {
        term: filters.term || undefined,
        academic_year: filters.academic_year || undefined
      };
      
      if (filters.is_published !== '') {
        params.is_published = filters.is_published === 'true';
      }
      
      dispatch(fetchPerformanceReports(params));
    }
  }, [dispatch, activeStudentId, filters]);
  
  useEffect(() => {
    // Get the reports to display based on whether we're showing all or student-specific
    const reports = activeStudentId 
      ? studentPerformanceReports[activeStudentId] || [] 
      : performanceReports;
    
    if (reports) {
      setFilteredReports(
        reports.filter(report => 
          report.term?.toLowerCase().includes(searchTerm.toLowerCase()) || 
          report.academic_year?.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }
  }, [studentPerformanceReports, performanceReports, activeStudentId, searchTerm]);
  
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
  
  const handleFilterChange = (event) => {
    setFilters({
      ...filters,
      [event.target.name]: event.target.value
    });
  };
  
  const handleViewReport = (reportId) => {
    dispatch(fetchPerformanceReport(reportId)).then((action) => {
      if (!action.error) {
        setSelectedReport(action.payload);
        setOpenViewDialog(true);
      }
    });
  };
  
  const handleCloseViewDialog = () => {
    setOpenViewDialog(false);
    setSelectedReport(null);
  };
  
  const handleAddReport = () => {
    setFormData({
      term: '',
      academic_year: '',
      overall_grade: '',
      overall_percentage: '',
      attendance_percentage: '',
      remarks: '',
      teacher_comments: '',
      principal_comments: '',
      strengths: '',
      areas_for_improvement: '',
      is_published: false,
      student_id: activeStudentId || '',
      class_id: ''
    });
    setEditingReportId(null);
    setOpenFormDialog(true);
  };
  
  const handleEditReport = (report) => {
    setFormData({
      term: report.term,
      academic_year: report.academic_year,
      overall_grade: report.overall_grade || '',
      overall_percentage: report.overall_percentage || '',
      attendance_percentage: report.attendance_percentage || '',
      remarks: report.remarks || '',
      teacher_comments: report.teacher_comments || '',
      principal_comments: report.principal_comments || '',
      strengths: report.strengths || '',
      areas_for_improvement: report.areas_for_improvement || '',
      is_published: report.is_published,
      student_id: report.student_id,
      class_id: report.class_id
    });
    setEditingReportId(report.id);
    setOpenFormDialog(true);
  };
  
  const handleCloseFormDialog = () => {
    setOpenFormDialog(false);
    setEditingReportId(null);
  };
  
  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };
  
  const handleSubmitForm = () => {
    if (editingReportId) {
      dispatch(updatePerformanceReport({ reportId: editingReportId, data: formData }))
        .then((action) => {
          if (!action.error) {
            handleCloseFormDialog();
          }
        });
    } else {
      dispatch(createPerformanceReport(formData))
        .then((action) => {
          if (!action.error) {
            handleCloseFormDialog();
          }
        });
    }
  };
  
  const handlePublishReport = (reportId) => {
    if (window.confirm('Are you sure you want to publish this report? This action cannot be undone.')) {
      dispatch(publishPerformanceReport(reportId));
    }
  };
  
  const handleDeleteReport = (reportId) => {
    if (window.confirm('Are you sure you want to delete this report?')) {
      dispatch(deletePerformanceReport(reportId));
    }
  };
  
  if (loading && !filteredReports.length) {
    return <LoadingIndicator />;
  }
  
  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" component="h2">
          {activeStudentId ? 'Student Performance Reports' : 'All Performance Reports'}
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
            onClick={handleAddReport}
          >
            Add Report
          </Button>
        </Box>
      </Box>

      {/* Filters */}
      <Box sx={{ mb: 3, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
        <Typography variant="subtitle1" sx={{ mb: 2 }}>
          Filters
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth size="small">
              <InputLabel>Term</InputLabel>
              <Select
                name="term"
                value={filters.term}
                label="Term"
                onChange={handleFilterChange}
              >
                <MenuItem value="">All Terms</MenuItem>
                <MenuItem value="Term 1">Term 1</MenuItem>
                <MenuItem value="Term 2">Term 2</MenuItem>
                <MenuItem value="Term 3">Term 3</MenuItem>
                <MenuItem value="Final">Final</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth size="small">
              <InputLabel>Academic Year</InputLabel>
              <Select
                name="academic_year"
                value={filters.academic_year}
                label="Academic Year"
                onChange={handleFilterChange}
              >
                <MenuItem value="">All Years</MenuItem>
                <MenuItem value="2023-2024">2023-2024</MenuItem>
                <MenuItem value="2022-2023">2022-2023</MenuItem>
                <MenuItem value="2021-2022">2021-2022</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          {!activeStudentId && (
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  name="is_published"
                  value={filters.is_published}
                  label="Status"
                  onChange={handleFilterChange}
                >
                  <MenuItem value="">All Status</MenuItem>
                  <MenuItem value="true">Published</MenuItem>
                  <MenuItem value="false">Draft</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          )}
        </Grid>
      </Box>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          Error: {error}
        </Typography>
      )}

      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        <TableContainer sx={{ maxHeight: 'calc(100vh - 340px)' }}>
          <Table stickyHeader aria-label="performance reports table">
            <TableHead>
              <TableRow>
                <TableCell>Term</TableCell>
                <TableCell>Academic Year</TableCell>
                {!activeStudentId && <TableCell>Student</TableCell>}
                <TableCell>Overall Grade</TableCell>
                <TableCell>Overall %</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredReports
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((report) => (
                  <TableRow hover key={report.id}>
                    <TableCell>{report.term}</TableCell>
                    <TableCell>{report.academic_year}</TableCell>
                    {!activeStudentId && (
                      <TableCell>{report.student?.user?.full_name || `Student #${report.student_id}`}</TableCell>
                    )}
                    <TableCell>{report.overall_grade || 'N/A'}</TableCell>
                    <TableCell>{report.overall_percentage ? `${report.overall_percentage}%` : 'N/A'}</TableCell>
                    <TableCell>
                      {report.is_published ? (
                        <Chip size="small" color="success" label="Published" />
                      ) : (
                        <Chip size="small" color="warning" label="Draft" />
                      )}
                    </TableCell>
                    <TableCell align="center">
                      <Tooltip title="View">
                        <IconButton 
                          color="info" 
                          size="small" 
                          onClick={() => handleViewReport(report.id)}
                          sx={{ mr: 1 }}
                        >
                          <ViewIcon />
                        </IconButton>
                      </Tooltip>
                      
                      {!report.is_published && (
                        <>
                          <Tooltip title="Edit">
                            <IconButton 
                              color="primary" 
                              size="small" 
                              onClick={() => handleEditReport(report)}
                              sx={{ mr: 1 }}
                            >
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Publish">
                            <IconButton 
                              color="success" 
                              size="small" 
                              onClick={() => handlePublishReport(report.id)}
                              sx={{ mr: 1 }}
                            >
                              <PublishIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton 
                              color="error" 
                              size="small" 
                              onClick={() => handleDeleteReport(report.id)}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              {filteredReports.length === 0 && (
                <TableRow>
                  <TableCell colSpan={activeStudentId ? 6 : 7} align="center">
                    No performance reports found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={filteredReports.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>

      {/* View Report Dialog */}
      <Dialog 
        open={openViewDialog} 
        onClose={handleCloseViewDialog}
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>
          Performance Report Details
          {selectedReport?.is_published && (
            <Chip 
              size="small" 
              color="success" 
              label="Published" 
              sx={{ ml: 2 }}
            />
          )}
        </DialogTitle>
        <DialogContent>
          {selectedReport && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardHeader title="Basic Information" />
                  <CardContent>
                    <Typography variant="body2"><strong>Term:</strong> {selectedReport.term}</Typography>
                    <Typography variant="body2"><strong>Academic Year:</strong> {selectedReport.academic_year}</Typography>
                    <Typography variant="body2">
                      <strong>Student:</strong> {selectedReport.student?.user?.full_name || `Student #${selectedReport.student_id}`}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Class:</strong> {selectedReport.class_?.name} {selectedReport.class_?.section}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardHeader title="Performance Summary" />
                  <CardContent>
                    <Typography variant="body2"><strong>Overall Grade:</strong> {selectedReport.overall_grade || 'N/A'}</Typography>
                    <Typography variant="body2"><strong>Overall Percentage:</strong> {selectedReport.overall_percentage ? `${selectedReport.overall_percentage}%` : 'N/A'}</Typography>
                    <Typography variant="body2"><strong>Attendance:</strong> {selectedReport.attendance_percentage ? `${selectedReport.attendance_percentage}%` : 'N/A'}</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12}>
                <Card variant="outlined">
                  <CardHeader title="Comments & Remarks" />
                  <CardContent>
                    <Typography variant="body2"><strong>Remarks:</strong> {selectedReport.remarks || 'N/A'}</Typography>
                    <Typography variant="body2" sx={{ mt: 1 }}><strong>Teacher Comments:</strong> {selectedReport.teacher_comments || 'N/A'}</Typography>
                    <Typography variant="body2" sx={{ mt: 1 }}><strong>Principal Comments:</strong> {selectedReport.principal_comments || 'N/A'}</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardHeader title="Strengths" />
                  <CardContent>
                    <Typography variant="body2">{selectedReport.strengths || 'No strengths recorded'}</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardHeader title="Areas for Improvement" />
                  <CardContent>
                    <Typography variant="body2">{selectedReport.areas_for_improvement || 'No areas for improvement recorded'}</Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseViewDialog}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Add/Edit Report Dialog */}
      <Dialog 
        open={openFormDialog} 
        onClose={handleCloseFormDialog}
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>
          {editingReportId ? 'Edit Performance Report' : 'Add Performance Report'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                name="term"
                label="Term"
                fullWidth
                value={formData.term}
                onChange={handleInputChange}
                required
                select
              >
                <MenuItem value="Term 1">Term 1</MenuItem>
                <MenuItem value="Term 2">Term 2</MenuItem>
                <MenuItem value="Term 3">Term 3</MenuItem>
                <MenuItem value="Final">Final</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                name="academic_year"
                label="Academic Year"
                fullWidth
                value={formData.academic_year}
                onChange={handleInputChange}
                required
                select
              >
                <MenuItem value="2023-2024">2023-2024</MenuItem>
                <MenuItem value="2022-2023">2022-2023</MenuItem>
                <MenuItem value="2021-2022">2021-2022</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                name="student_id"
                label="Student ID"
                type="number"
                fullWidth
                value={formData.student_id}
                onChange={handleInputChange}
                required
                disabled={!!activeStudentId}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                name="class_id"
                label="Class ID"
                type="number"
                fullWidth
                value={formData.class_id}
                onChange={handleInputChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                name="overall_grade"
                label="Overall Grade"
                fullWidth
                value={formData.overall_grade}
                onChange={handleInputChange}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                name="overall_percentage"
                label="Overall Percentage"
                type="number"
                fullWidth
                value={formData.overall_percentage}
                onChange={handleInputChange}
                InputProps={{
                  endAdornment: <InputAdornment position="end">%</InputAdornment>,
                }}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                name="attendance_percentage"
                label="Attendance Percentage"
                type="number"
                fullWidth
                value={formData.attendance_percentage}
                onChange={handleInputChange}
                InputProps={{
                  endAdornment: <InputAdornment position="end">%</InputAdornment>,
                }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                name="remarks"
                label="Remarks"
                multiline
                rows={2}
                fullWidth
                value={formData.remarks}
                onChange={handleInputChange}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                name="teacher_comments"
                label="Teacher Comments"
                multiline
                rows={3}
                fullWidth
                value={formData.teacher_comments}
                onChange={handleInputChange}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                name="principal_comments"
                label="Principal Comments"
                multiline
                rows={3}
                fullWidth
                value={formData.principal_comments}
                onChange={handleInputChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                name="strengths"
                label="Strengths"
                multiline
                rows={3}
                fullWidth
                value={formData.strengths}
                onChange={handleInputChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                name="areas_for_improvement"
                label="Areas for Improvement"
                multiline
                rows={3}
                fullWidth
                value={formData.areas_for_improvement}
                onChange={handleInputChange}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseFormDialog}>Cancel</Button>
          <Button onClick={handleSubmitForm} variant="contained">
            {editingReportId ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default StudentPerformanceReports; 