import React, { useState, useEffect } from 'react';
import {
  Box, Button, Typography, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, IconButton, Chip, TextField, InputAdornment,
  Dialog, DialogTitle, DialogContent, DialogActions, MenuItem, Select, FormControl, InputLabel
} from '@mui/material';
import { Edit, Delete, Add, Search, FilterList } from '@mui/icons-material';
import LoadingIndicator from '../common/LoadingIndicator';
import { useDispatch, useSelector } from 'react-redux';
// Import actions will be added once we create the library slice

const bookStatusColors = {
  available: 'success',
  issued: 'warning',
  lost: 'error',
  damaged: 'error',
  under_repair: 'warning',
  reserved: 'info'
};

const LibraryList = () => {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [categories, setCategories] = useState([]);
  const [openFilter, setOpenFilter] = useState(false);
  
  const dispatch = useDispatch();
  // const { books, loading } = useSelector(state => state.library);
  // Uncomment when library slice is ready
  
  useEffect(() => {
    // Fetch books and categories
    // Will be implemented when API is connected
    setLoading(false);
    
    // Mock data for now
    setBooks([
      {
        id: 1,
        title: 'Mathematics for High School',
        author: 'John Smith',
        isbn: '9781234567897',
        publisher: 'Education Press',
        publication_year: 2020,
        category: { id: 1, name: 'Mathematics' },
        available_copies: 5,
        total_copies: 10,
        status: 'available'
      },
      {
        id: 2,
        title: 'Introduction to Physics',
        author: 'Robert Johnson',
        isbn: '9789876543210',
        publisher: 'Science Books',
        publication_year: 2019,
        category: { id: 2, name: 'Physics' },
        available_copies: 0,
        total_copies: 3,
        status: 'issued'
      },
      {
        id: 3,
        title: 'History of the World',
        author: 'Mary Williams',
        isbn: '9785432109876',
        publisher: 'History Press',
        publication_year: 2021,
        category: { id: 3, name: 'History' },
        available_copies: 1,
        total_copies: 5,
        status: 'available'
      }
    ]);
    
    setCategories([
      { id: 1, name: 'Mathematics' },
      { id: 2, name: 'Physics' },
      { id: 3, name: 'History' },
      { id: 4, name: 'Literature' },
      { id: 5, name: 'Computer Science' }
    ]);
  }, [dispatch]);
  
  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
  };
  
  const filteredBooks = books.filter(book => {
    const matchesSearch = searchTerm === '' || 
      book.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
      book.author.toLowerCase().includes(searchTerm.toLowerCase()) ||
      book.isbn.includes(searchTerm);
    
    const matchesCategory = categoryFilter === '' || 
      book.category.id === parseInt(categoryFilter);
    
    const matchesStatus = statusFilter === '' || 
      book.status === statusFilter;
    
    return matchesSearch && matchesCategory && matchesStatus;
  });
  
  const handleOpenFilter = () => {
    setOpenFilter(true);
  };
  
  const handleCloseFilter = () => {
    setOpenFilter(false);
  };
  
  const clearFilters = () => {
    setCategoryFilter('');
    setStatusFilter('');
    handleCloseFilter();
  };
  
  const handleEditBook = (id) => {
    // Will be implemented when connecting to API
    console.log('Edit book with ID:', id);
  };
  
  const handleDeleteBook = (id) => {
    // Will be implemented when connecting to API
    console.log('Delete book with ID:', id);
  };
  
  const handleAddBook = () => {
    // Will be implemented when connecting to API
    console.log('Add new book');
  };
  
  if (loading) {
    return <LoadingIndicator />;
  }
  
  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Library Books</Typography>
        <Box>
          <Button 
            variant="outlined" 
            startIcon={<FilterList />} 
            onClick={handleOpenFilter}
            sx={{ mr: 1 }}
          >
            Filter
          </Button>
          <Button 
            variant="contained" 
            color="primary" 
            startIcon={<Add />} 
            onClick={handleAddBook}
          >
            Add Book
          </Button>
        </Box>
      </Box>
      
      <TextField
        fullWidth
        margin="normal"
        variant="outlined"
        placeholder="Search by title, author, or ISBN..."
        value={searchTerm}
        onChange={handleSearch}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Search />
            </InputAdornment>
          ),
        }}
      />
      
      {/* Filter Dialog */}
      <Dialog open={openFilter} onClose={handleCloseFilter}>
        <DialogTitle>Filter Books</DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin="normal">
            <InputLabel id="category-filter-label">Category</InputLabel>
            <Select
              labelId="category-filter-label"
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              label="Category"
            >
              <MenuItem value="">All Categories</MenuItem>
              {categories.map((category) => (
                <MenuItem key={category.id} value={category.id}>
                  {category.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <FormControl fullWidth margin="normal">
            <InputLabel id="status-filter-label">Status</InputLabel>
            <Select
              labelId="status-filter-label"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              label="Status"
            >
              <MenuItem value="">All Statuses</MenuItem>
              <MenuItem value="available">Available</MenuItem>
              <MenuItem value="issued">Issued</MenuItem>
              <MenuItem value="lost">Lost</MenuItem>
              <MenuItem value="damaged">Damaged</MenuItem>
              <MenuItem value="under_repair">Under Repair</MenuItem>
              <MenuItem value="reserved">Reserved</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={clearFilters}>Clear</Button>
          <Button onClick={handleCloseFilter} color="primary">Apply</Button>
        </DialogActions>
      </Dialog>
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Title</TableCell>
              <TableCell>Author</TableCell>
              <TableCell>ISBN</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Availability</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredBooks.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  No books found
                </TableCell>
              </TableRow>
            ) : (
              filteredBooks.map((book) => (
                <TableRow key={book.id}>
                  <TableCell>{book.title}</TableCell>
                  <TableCell>{book.author}</TableCell>
                  <TableCell>{book.isbn}</TableCell>
                  <TableCell>{book.category.name}</TableCell>
                  <TableCell>{`${book.available_copies} / ${book.total_copies}`}</TableCell>
                  <TableCell>
                    <Chip 
                      label={book.status.replace('_', ' ')} 
                      color={bookStatusColors[book.status] || 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton 
                      size="small" 
                      onClick={() => handleEditBook(book.id)}
                    >
                      <Edit fontSize="small" />
                    </IconButton>
                    <IconButton 
                      size="small" 
                      onClick={() => handleDeleteBook(book.id)}
                    >
                      <Delete fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default LibraryList; 