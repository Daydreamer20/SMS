import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// API URL from environment or default
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Initial state
const initialState = {
  staffMembers: [],
  staffMember: null,
  isLoading: false,
  error: null,
};

// Get all staff members
export const getStaffMembers = createAsyncThunk(
  'staff/getStaffMembers',
  async (_, { getState, rejectWithValue }) => {
    try {
      const { auth } = getState();
      const response = await axios.get(`${API_URL}/staff/`, {
        headers: {
          Authorization: `Bearer ${auth.token}`,
        },
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch staff members');
    }
  }
);

// Get staff member by ID
export const getStaffMemberById = createAsyncThunk(
  'staff/getStaffMemberById',
  async (id, { getState, rejectWithValue }) => {
    try {
      const { auth } = getState();
      const response = await axios.get(`${API_URL}/staff/${id}`, {
        headers: {
          Authorization: `Bearer ${auth.token}`,
        },
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch staff member');
    }
  }
);

// Get staff member with classes
export const getStaffMemberWithClasses = createAsyncThunk(
  'staff/getStaffMemberWithClasses',
  async (id, { getState, rejectWithValue }) => {
    try {
      const { auth } = getState();
      const response = await axios.get(`${API_URL}/staff/${id}/classes`, {
        headers: {
          Authorization: `Bearer ${auth.token}`,
        },
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch staff member with classes');
    }
  }
);

// Get current staff profile
export const getCurrentStaff = createAsyncThunk(
  'staff/getCurrentStaff',
  async (_, { getState, rejectWithValue }) => {
    try {
      const { auth } = getState();
      const response = await axios.get(`${API_URL}/staff/me`, {
        headers: {
          Authorization: `Bearer ${auth.token}`,
        },
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch staff profile');
    }
  }
);

// Create staff member
export const createStaffMember = createAsyncThunk(
  'staff/createStaffMember',
  async (staffData, { getState, rejectWithValue }) => {
    try {
      const { auth } = getState();
      const response = await axios.post(`${API_URL}/staff/`, staffData, {
        headers: {
          Authorization: `Bearer ${auth.token}`,
        },
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create staff member');
    }
  }
);

// Update staff member
export const updateStaffMember = createAsyncThunk(
  'staff/updateStaffMember',
  async ({ id, staffData }, { getState, rejectWithValue }) => {
    try {
      const { auth } = getState();
      const response = await axios.put(`${API_URL}/staff/${id}`, staffData, {
        headers: {
          Authorization: `Bearer ${auth.token}`,
        },
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update staff member');
    }
  }
);

// Delete staff member
export const deleteStaffMember = createAsyncThunk(
  'staff/deleteStaffMember',
  async (id, { getState, rejectWithValue }) => {
    try {
      const { auth } = getState();
      await axios.delete(`${API_URL}/staff/${id}`, {
        headers: {
          Authorization: `Bearer ${auth.token}`,
        },
      });
      return id;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete staff member');
    }
  }
);

// Staff slice
const staffSlice = createSlice({
  name: 'staff',
  initialState,
  reducers: {
    clearStaffError: (state) => {
      state.error = null;
    },
    resetStaffMember: (state) => {
      state.staffMember = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Get all staff members
      .addCase(getStaffMembers.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(getStaffMembers.fulfilled, (state, { payload }) => {
        state.isLoading = false;
        state.staffMembers = payload;
      })
      .addCase(getStaffMembers.rejected, (state, { payload }) => {
        state.isLoading = false;
        state.error = payload;
      })
      
      // Get staff member by ID
      .addCase(getStaffMemberById.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(getStaffMemberById.fulfilled, (state, { payload }) => {
        state.isLoading = false;
        state.staffMember = payload;
      })
      .addCase(getStaffMemberById.rejected, (state, { payload }) => {
        state.isLoading = false;
        state.error = payload;
      })
      
      // Get staff member with classes
      .addCase(getStaffMemberWithClasses.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(getStaffMemberWithClasses.fulfilled, (state, { payload }) => {
        state.isLoading = false;
        state.staffMember = payload;
      })
      .addCase(getStaffMemberWithClasses.rejected, (state, { payload }) => {
        state.isLoading = false;
        state.error = payload;
      })
      
      // Get current staff
      .addCase(getCurrentStaff.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(getCurrentStaff.fulfilled, (state, { payload }) => {
        state.isLoading = false;
        state.staffMember = payload;
      })
      .addCase(getCurrentStaff.rejected, (state, { payload }) => {
        state.isLoading = false;
        state.error = payload;
      })
      
      // Create staff member
      .addCase(createStaffMember.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createStaffMember.fulfilled, (state, { payload }) => {
        state.isLoading = false;
        state.staffMembers.push(payload);
      })
      .addCase(createStaffMember.rejected, (state, { payload }) => {
        state.isLoading = false;
        state.error = payload;
      })
      
      // Update staff member
      .addCase(updateStaffMember.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updateStaffMember.fulfilled, (state, { payload }) => {
        state.isLoading = false;
        state.staffMember = payload;
        const index = state.staffMembers.findIndex((staff) => staff.id === payload.id);
        if (index !== -1) {
          state.staffMembers[index] = payload;
        }
      })
      .addCase(updateStaffMember.rejected, (state, { payload }) => {
        state.isLoading = false;
        state.error = payload;
      })
      
      // Delete staff member
      .addCase(deleteStaffMember.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(deleteStaffMember.fulfilled, (state, { payload }) => {
        state.isLoading = false;
        state.staffMembers = state.staffMembers.filter((staff) => staff.id !== payload);
        if (state.staffMember && state.staffMember.id === payload) {
          state.staffMember = null;
        }
      })
      .addCase(deleteStaffMember.rejected, (state, { payload }) => {
        state.isLoading = false;
        state.error = payload;
      });
  },
});

export const { clearStaffError, resetStaffMember } = staffSlice.actions;
export default staffSlice.reducer; 