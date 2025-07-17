import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

// Async thunks
export const fetchStudents = createAsyncThunk(
  'students/fetchStudents',
  async (_, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/students`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch students');
    }
  }
);

export const fetchStudent = createAsyncThunk(
  'students/fetchStudent',
  async (id, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/students/${id}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch student');
    }
  }
);

export const createStudent = createAsyncThunk(
  'students/createStudent',
  async (studentData, { rejectWithValue }) => {
    try {
      const response = await axios.post(`${API_URL}/students`, studentData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to create student');
    }
  }
);

export const updateStudent = createAsyncThunk(
  'students/updateStudent',
  async ({ id, data }, { rejectWithValue }) => {
    try {
      const response = await axios.put(`${API_URL}/students/${id}`, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to update student');
    }
  }
);

export const deleteStudent = createAsyncThunk(
  'students/deleteStudent',
  async (id, { rejectWithValue }) => {
    try {
      const response = await axios.delete(`${API_URL}/students/${id}`);
      return { id, data: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to delete student');
    }
  }
);

// Performance report thunks
export const fetchPerformanceReports = createAsyncThunk(
  'students/fetchPerformanceReports',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/students/performance-reports`, { params });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch performance reports');
    }
  }
);

export const fetchStudentPerformanceReports = createAsyncThunk(
  'students/fetchStudentPerformanceReports',
  async ({ studentId, params = {} }, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/students/performance-reports/student/${studentId}`, { params });
      return { studentId, reports: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch student performance reports');
    }
  }
);

export const fetchPerformanceReport = createAsyncThunk(
  'students/fetchPerformanceReport',
  async (reportId, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/students/performance-reports/${reportId}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch performance report');
    }
  }
);

export const createPerformanceReport = createAsyncThunk(
  'students/createPerformanceReport',
  async (reportData, { rejectWithValue }) => {
    try {
      const response = await axios.post(`${API_URL}/students/performance-reports`, reportData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to create performance report');
    }
  }
);

export const updatePerformanceReport = createAsyncThunk(
  'students/updatePerformanceReport',
  async ({ reportId, data }, { rejectWithValue }) => {
    try {
      const response = await axios.put(`${API_URL}/students/performance-reports/${reportId}`, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to update performance report');
    }
  }
);

export const publishPerformanceReport = createAsyncThunk(
  'students/publishPerformanceReport',
  async (reportId, { rejectWithValue }) => {
    try {
      const response = await axios.put(`${API_URL}/students/performance-reports/${reportId}/publish`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to publish performance report');
    }
  }
);

export const deletePerformanceReport = createAsyncThunk(
  'students/deletePerformanceReport',
  async (reportId, { rejectWithValue }) => {
    try {
      const response = await axios.delete(`${API_URL}/students/performance-reports/${reportId}`);
      return { reportId, data: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to delete performance report');
    }
  }
);

// Initial state
const initialState = {
  students: [],
  currentStudent: null,
  performanceReports: [],
  studentPerformanceReports: {},
  currentReport: null,
  loading: false,
  error: null,
  success: false
};

const studentSlice = createSlice({
  name: 'student',
  initialState,
  reducers: {
    resetSuccess: (state) => {
      state.success = false;
    },
    clearError: (state) => {
      state.error = null;
    },
    clearCurrentStudent: (state) => {
      state.currentStudent = null;
    },
    clearCurrentReport: (state) => {
      state.currentReport = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch students
      .addCase(fetchStudents.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchStudents.fulfilled, (state, action) => {
        state.loading = false;
        state.students = action.payload;
      })
      .addCase(fetchStudents.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch students';
      })
      
      // Fetch single student
      .addCase(fetchStudent.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchStudent.fulfilled, (state, action) => {
        state.loading = false;
        state.currentStudent = action.payload;
      })
      .addCase(fetchStudent.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch student';
      })
      
      // Create student
      .addCase(createStudent.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.success = false;
      })
      .addCase(createStudent.fulfilled, (state, action) => {
        state.loading = false;
        state.success = true;
        state.students.push(action.payload);
      })
      .addCase(createStudent.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to create student';
        state.success = false;
      })
      
      // Update student
      .addCase(updateStudent.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.success = false;
      })
      .addCase(updateStudent.fulfilled, (state, action) => {
        state.loading = false;
        state.success = true;
        const index = state.students.findIndex(s => s.id === action.payload.id);
        if (index !== -1) {
          state.students[index] = action.payload;
        }
        state.currentStudent = action.payload;
      })
      .addCase(updateStudent.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to update student';
        state.success = false;
      })
      
      // Delete student
      .addCase(deleteStudent.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteStudent.fulfilled, (state, action) => {
        state.loading = false;
        state.students = state.students.filter(s => s.id !== action.payload.id);
        state.success = true;
      })
      .addCase(deleteStudent.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to delete student';
      })

      // Fetch performance reports
      .addCase(fetchPerformanceReports.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPerformanceReports.fulfilled, (state, action) => {
        state.loading = false;
        state.performanceReports = action.payload;
      })
      .addCase(fetchPerformanceReports.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch performance reports';
      })

      // Fetch student performance reports
      .addCase(fetchStudentPerformanceReports.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchStudentPerformanceReports.fulfilled, (state, action) => {
        state.loading = false;
        state.studentPerformanceReports = {
          ...state.studentPerformanceReports,
          [action.payload.studentId]: action.payload.reports
        };
      })
      .addCase(fetchStudentPerformanceReports.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch student performance reports';
      })

      // Fetch single performance report
      .addCase(fetchPerformanceReport.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPerformanceReport.fulfilled, (state, action) => {
        state.loading = false;
        state.currentReport = action.payload;
      })
      .addCase(fetchPerformanceReport.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch performance report';
      })

      // Create performance report
      .addCase(createPerformanceReport.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.success = false;
      })
      .addCase(createPerformanceReport.fulfilled, (state, action) => {
        state.loading = false;
        state.success = true;
        state.performanceReports.push(action.payload);
      })
      .addCase(createPerformanceReport.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to create performance report';
        state.success = false;
      })

      // Update performance report
      .addCase(updatePerformanceReport.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.success = false;
      })
      .addCase(updatePerformanceReport.fulfilled, (state, action) => {
        state.loading = false;
        state.success = true;
        const index = state.performanceReports.findIndex(r => r.id === action.payload.id);
        if (index !== -1) {
          state.performanceReports[index] = action.payload;
        }
        state.currentReport = action.payload;
      })
      .addCase(updatePerformanceReport.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to update performance report';
        state.success = false;
      })

      // Publish performance report
      .addCase(publishPerformanceReport.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(publishPerformanceReport.fulfilled, (state, action) => {
        state.loading = false;
        state.success = true;
        const index = state.performanceReports.findIndex(r => r.id === action.payload.id);
        if (index !== -1) {
          state.performanceReports[index] = action.payload;
        }
        if (state.currentReport?.id === action.payload.id) {
          state.currentReport = action.payload;
        }
      })
      .addCase(publishPerformanceReport.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to publish performance report';
      })

      // Delete performance report
      .addCase(deletePerformanceReport.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deletePerformanceReport.fulfilled, (state, action) => {
        state.loading = false;
        state.performanceReports = state.performanceReports.filter(r => r.id !== action.payload.reportId);
        state.success = true;
      })
      .addCase(deletePerformanceReport.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to delete performance report';
      });
  }
});

export const { resetSuccess, clearError, clearCurrentStudent, clearCurrentReport } = studentSlice.actions;

export default studentSlice.reducer; 