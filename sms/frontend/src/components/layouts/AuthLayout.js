import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import {
  Box,
  Container,
  Paper,
  Typography,
  Grid,
  CssBaseline,
} from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';

const AuthLayout = () => {
  const { isAuthenticated } = useSelector((state) => state.auth);

  // Redirect to dashboard if already authenticated
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <Box
      sx={{
        display: 'flex',
        minHeight: '100vh',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: (theme) => theme.palette.grey[100],
      }}
    >
      <CssBaseline />
      <Container maxWidth="sm">
        <Paper
          elevation={6}
          sx={{
            padding: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              mb: 4,
            }}
          >
            <SchoolIcon
              sx={{ fontSize: 50, color: 'primary.main', mb: 2 }}
            />
            <Typography component="h1" variant="h4">
              School Management System
            </Typography>
          </Box>
          <Outlet />
        </Paper>
      </Container>
    </Box>
  );
};

export default AuthLayout; 