import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';

// Layouts
import MainLayout from './components/layouts/MainLayout';
import AuthLayout from './components/layouts/AuthLayout';

// Authentication Pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';

// Dashboard Pages
import DashboardPage from './pages/dashboard/DashboardPage';

// User Pages
import UserListPage from './pages/users/UserListPage';
import UserDetailPage from './pages/users/UserDetailPage';

// Student Pages
import StudentListPage from './pages/students/StudentListPage';
import StudentDetailPage from './pages/students/StudentDetailPage';
import StudentPerformanceReportPage from './pages/student/StudentPerformanceReportPage';

// Staff Pages
import StaffListPage from './pages/staff/StaffListPage';
import StaffDetailPage from './pages/staff/StaffDetailPage';

// Library Pages
import LibraryPage from './pages/library/LibraryPage';

// Error Pages
import NotFoundPage from './pages/errors/NotFoundPage';

// Protected Route Component
const ProtectedRoute = ({ children, requiredRole }) => {
  const { isAuthenticated, user } = useSelector((state) => state.auth);
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && (!user.roles || !user.roles.includes(requiredRole))) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};

function App() {
  return (
    <Routes>
      {/* Auth Routes */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>

      {/* Main App Routes */}
      <Route element={
        <ProtectedRoute>
          <MainLayout />
        </ProtectedRoute>
      }>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        
        {/* User Routes */}
        <Route path="/users" element={
          <ProtectedRoute requiredRole="admin">
            <UserListPage />
          </ProtectedRoute>
        } />
        <Route path="/users/:id" element={
          <ProtectedRoute requiredRole="admin">
            <UserDetailPage />
          </ProtectedRoute>
        } />
        
        {/* Student Routes */}
        <Route path="/students" element={
          <ProtectedRoute requiredRole="teacher">
            <StudentListPage />
          </ProtectedRoute>
        } />
        <Route path="/students/:id" element={
          <ProtectedRoute requiredRole="teacher">
            <StudentDetailPage />
          </ProtectedRoute>
        } />
        <Route path="/students/:studentId/performance-reports" element={
          <ProtectedRoute requiredRole="teacher">
            <StudentPerformanceReportPage />
          </ProtectedRoute>
        } />
        <Route path="/performance-reports" element={
          <ProtectedRoute requiredRole="teacher">
            <StudentPerformanceReportPage />
          </ProtectedRoute>
        } />
        
        {/* Staff Routes */}
        <Route path="/staff" element={
          <ProtectedRoute requiredRole="admin">
            <StaffListPage />
          </ProtectedRoute>
        } />
        <Route path="/staff/:id" element={
          <ProtectedRoute requiredRole="admin">
            <StaffDetailPage />
          </ProtectedRoute>
        } />
        
        {/* Library Routes */}
        <Route path="/library" element={
          <ProtectedRoute>
            <LibraryPage />
          </ProtectedRoute>
        } />
      </Route>
      
      {/* Error Routes */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}

export default App; 