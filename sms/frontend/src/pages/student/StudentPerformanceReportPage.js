import React from 'react';
import { Box, Typography, Breadcrumbs, Link, Container } from '@mui/material';
import { Link as RouterLink, useParams } from 'react-router-dom';
import MainLayout from '../../components/layouts/MainLayout';
import StudentPerformanceReports from '../../components/student/StudentPerformanceReports';

const StudentPerformanceReportPage = () => {
  const { studentId } = useParams();
  
  return (
    <MainLayout>
      <Container maxWidth="xl">
        <Box sx={{ mt: 3, mb: 4 }}>
          <Breadcrumbs aria-label="breadcrumb">
            <Link component={RouterLink} to="/" color="inherit">
              Dashboard
            </Link>
            <Link component={RouterLink} to="/students" color="inherit">
              Students
            </Link>
            {studentId ? (
              <Link component={RouterLink} to={`/students/${studentId}`} color="inherit">
                Student Profile
              </Link>
            ) : null}
            <Typography color="text.primary">
              {studentId ? 'Student Performance Reports' : 'Performance Reports'}
            </Typography>
          </Breadcrumbs>
          
          <Typography variant="h4" sx={{ mt: 2, mb: 4 }}>
            {studentId ? 'Student Performance Reports' : 'Performance Reports Management'}
          </Typography>
          
          <StudentPerformanceReports studentId={studentId} />
        </Box>
      </Container>
    </MainLayout>
  );
};

export default StudentPerformanceReportPage; 