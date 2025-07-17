import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// Define async thunks for API calls

// Book operations
export const fetchBooks = createAsyncThunk(
  'library/fetchBooks',
  async (_, { rejectWithValue }) => {
    try {
      const response = await axios.get('/api/library/books');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const createBook = createAsyncThunk(
  'library/createBook',
  async (bookData, { rejectWithValue }) => {
    try {
      const response = await axios.post('/api/library/books', bookData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const updateBook = createAsyncThunk(
  'library/updateBook',
  async ({ id, bookData }, { rejectWithValue }) => {
    try {
      const response = await axios.put(`/api/library/books/${id}`, bookData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const deleteBook = createAsyncThunk(
  'library/deleteBook',
  async (id, { rejectWithValue }) => {
    try {
      await axios.delete(`/api/library/books/${id}`);
      return id;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

// Category operations
export const fetchCategories = createAsyncThunk(
  'library/fetchCategories',
  async (_, { rejectWithValue }) => {
    try {
      const response = await axios.get('/api/library/categories');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const createCategory = createAsyncThunk(
  'library/createCategory',
  async (categoryData, { rejectWithValue }) => {
    try {
      const response = await axios.post('/api/library/categories', categoryData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

// Book Issue operations
export const fetchBookIssues = createAsyncThunk(
  'library/fetchBookIssues',
  async (params, { rejectWithValue }) => {
    try {
      const response = await axios.get('/api/library/issues', { params });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const createBookIssue = createAsyncThunk(
  'library/createBookIssue',
  async (issueData, { rejectWithValue }) => {
    try {
      const response = await axios.post('/api/library/issues', issueData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const returnBook = createAsyncThunk(
  'library/returnBook',
  async ({ issueId, returnData }, { rejectWithValue }) => {
    try {
      const response = await axios.put(
        `/api/library/issues/${issueId}/return`,
        returnData
      );
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

// Library settings operations
export const fetchLibrarySettings = createAsyncThunk(
  'library/fetchLibrarySettings',
  async (_, { rejectWithValue }) => {
    try {
      const response = await axios.get('/api/library/library-settings');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const updateLibrarySettings = createAsyncThunk(
  'library/updateLibrarySettings',
  async (settingsData, { rejectWithValue }) => {
    try {
      const response = await axios.put('/api/library/library-settings', settingsData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

// Initial state
const initialState = {
  books: [],
  categories: [],
  issues: [],
  settings: null,
  selectedBook: null,
  selectedIssue: null,
  loading: false,
  error: null,
  success: false,
  message: ''
};

// Create slice
const librarySlice = createSlice({
  name: 'library',
  initialState,
  reducers: {
    resetLibraryState: (state) => {
      state.error = null;
      state.success = false;
      state.message = '';
    },
    setSelectedBook: (state, action) => {
      state.selectedBook = action.payload;
    },
    clearSelectedBook: (state) => {
      state.selectedBook = null;
    },
    setSelectedIssue: (state, action) => {
      state.selectedIssue = action.payload;
    },
    clearSelectedIssue: (state) => {
      state.selectedIssue = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Books
      .addCase(fetchBooks.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchBooks.fulfilled, (state, action) => {
        state.loading = false;
        state.books = action.payload;
        state.error = null;
      })
      .addCase(fetchBooks.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.message || 'Failed to fetch books';
      })
      .addCase(createBook.pending, (state) => {
        state.loading = true;
      })
      .addCase(createBook.fulfilled, (state, action) => {
        state.loading = false;
        state.books.push(action.payload);
        state.success = true;
        state.message = 'Book created successfully';
        state.error = null;
      })
      .addCase(createBook.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.message || 'Failed to create book';
      })
      .addCase(updateBook.pending, (state) => {
        state.loading = true;
      })
      .addCase(updateBook.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.books.findIndex(book => book.id === action.payload.id);
        if (index !== -1) {
          state.books[index] = action.payload;
        }
        state.success = true;
        state.message = 'Book updated successfully';
        state.error = null;
      })
      .addCase(updateBook.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.message || 'Failed to update book';
      })
      .addCase(deleteBook.pending, (state) => {
        state.loading = true;
      })
      .addCase(deleteBook.fulfilled, (state, action) => {
        state.loading = false;
        state.books = state.books.filter(book => book.id !== action.payload);
        state.success = true;
        state.message = 'Book deleted successfully';
        state.error = null;
      })
      .addCase(deleteBook.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.message || 'Failed to delete book';
      })
      
      // Categories
      .addCase(fetchCategories.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchCategories.fulfilled, (state, action) => {
        state.loading = false;
        state.categories = action.payload;
        state.error = null;
      })
      .addCase(fetchCategories.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.message || 'Failed to fetch categories';
      })
      .addCase(createCategory.fulfilled, (state, action) => {
        state.categories.push(action.payload);
        state.success = true;
        state.message = 'Category created successfully';
      })
      
      // Book Issues
      .addCase(fetchBookIssues.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchBookIssues.fulfilled, (state, action) => {
        state.loading = false;
        state.issues = action.payload;
        state.error = null;
      })
      .addCase(fetchBookIssues.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.message || 'Failed to fetch book issues';
      })
      .addCase(createBookIssue.fulfilled, (state, action) => {
        state.issues.push(action.payload);
        state.success = true;
        state.message = 'Book issued successfully';
      })
      .addCase(returnBook.fulfilled, (state, action) => {
        const index = state.issues.findIndex(issue => issue.id === action.payload.id);
        if (index !== -1) {
          state.issues[index] = action.payload;
        }
        state.success = true;
        state.message = 'Book returned successfully';
      })
      
      // Library Settings
      .addCase(fetchLibrarySettings.fulfilled, (state, action) => {
        state.settings = action.payload;
      })
      .addCase(updateLibrarySettings.fulfilled, (state, action) => {
        state.settings = action.payload;
        state.success = true;
        state.message = 'Library settings updated successfully';
      });
  }
});

export const { 
  resetLibraryState,
  setSelectedBook,
  clearSelectedBook,
  setSelectedIssue,
  clearSelectedIssue
} = librarySlice.actions;

export default librarySlice.reducer; 