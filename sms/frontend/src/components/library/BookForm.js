import React, { useState, useEffect } from 'react';
import {
  Box, Button, TextField, Typography, Grid, MenuItem,
  Dialog, DialogTitle, DialogContent, DialogActions, FormControl, InputLabel, Select
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
// Import actions will be added once we create the library slice

const BookForm = ({ open, bookToEdit, onClose, onSubmit }) => {
  const initialFormState = {
    title: '',
    author: '',
    isbn: '',
    publisher: '',
    publication_year: '',
    edition: '',
    description: '',
    category_id: '',
    total_copies: 1,
    available_copies: 1,
    shelf_location: '',
    status: 'available'
  };
  
  const [formData, setFormData] = useState(initialFormState);
  const [categories, setCategories] = useState([]);
  const [errors, setErrors] = useState({});
  
  const dispatch = useDispatch();
  // const { categories } = useSelector(state => state.library);
  // Uncomment when library slice is ready
  
  useEffect(() => {
    // Reset form when dialog opens/closes
    if (open) {
      if (bookToEdit) {
        setFormData({
          ...bookToEdit,
          category_id: bookToEdit.category?.id || ''
        });
      } else {
        setFormData(initialFormState);
      }
      setErrors({});
    }
    
    // Mock categories data until API is connected
    setCategories([
      { id: 1, name: 'Mathematics' },
      { id: 2, name: 'Physics' },
      { id: 3, name: 'History' },
      { id: 4, name: 'Literature' },
      { id: 5, name: 'Computer Science' }
    ]);
  }, [open, bookToEdit]);
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when field is edited
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };
  
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }
    
    if (!formData.author.trim()) {
      newErrors.author = 'Author is required';
    }
    
    if (formData.isbn && (formData.isbn.length !== 10 && formData.isbn.length !== 13)) {
      newErrors.isbn = 'ISBN must be 10 or 13 characters';
    }
    
    if (formData.publication_year) {
      const year = parseInt(formData.publication_year);
      const currentYear = new Date().getFullYear();
      if (isNaN(year) || year < 1000 || year > currentYear) {
        newErrors.publication_year = `Year must be between 1000 and ${currentYear}`;
      }
    }
    
    if (parseInt(formData.total_copies) < 0) {
      newErrors.total_copies = 'Total copies cannot be negative';
    }
    
    if (parseInt(formData.available_copies) < 0) {
      newErrors.available_copies = 'Available copies cannot be negative';
    }
    
    if (parseInt(formData.available_copies) > parseInt(formData.total_copies)) {
      newErrors.available_copies = 'Available copies cannot exceed total copies';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      // Convert string values to appropriate types
      const formattedData = {
        ...formData,
        publication_year: formData.publication_year ? parseInt(formData.publication_year) : null,
        total_copies: parseInt(formData.total_copies),
        available_copies: parseInt(formData.available_copies),
        category_id: formData.category_id ? parseInt(formData.category_id) : null
      };
      
      onSubmit(formattedData);
    }
  };
  
  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {bookToEdit ? 'Edit Book' : 'Add New Book'}
      </DialogTitle>
      <DialogContent>
        <Box component="form" noValidate sx={{ mt: 2 }} onSubmit={handleSubmit}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                error={!!errors.title}
                helperText={errors.title}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Author"
                name="author"
                value={formData.author}
                onChange={handleChange}
                error={!!errors.author}
                helperText={errors.author}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="ISBN"
                name="isbn"
                value={formData.isbn}
                onChange={handleChange}
                error={!!errors.isbn}
                helperText={errors.isbn}
                placeholder="10 or 13 digits"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Publisher"
                name="publisher"
                value={formData.publisher}
                onChange={handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Publication Year"
                name="publication_year"
                value={formData.publication_year}
                onChange={handleChange}
                error={!!errors.publication_year}
                helperText={errors.publication_year}
                type="number"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Edition"
                name="edition"
                value={formData.edition}
                onChange={handleChange}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel id="category-label">Category</InputLabel>
                <Select
                  labelId="category-label"
                  name="category_id"
                  value={formData.category_id}
                  onChange={handleChange}
                  label="Category"
                >
                  <MenuItem value="">
                    <em>None</em>
                  </MenuItem>
                  {categories.map((category) => (
                    <MenuItem key={category.id} value={category.id}>
                      {category.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Total Copies"
                name="total_copies"
                value={formData.total_copies}
                onChange={handleChange}
                type="number"
                InputProps={{ inputProps: { min: 0 } }}
                error={!!errors.total_copies}
                helperText={errors.total_copies}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Available Copies"
                name="available_copies"
                value={formData.available_copies}
                onChange={handleChange}
                type="number"
                InputProps={{ inputProps: { min: 0 } }}
                error={!!errors.available_copies}
                helperText={errors.available_copies}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Shelf Location"
                name="shelf_location"
                value={formData.shelf_location}
                onChange={handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel id="status-label">Status</InputLabel>
                <Select
                  labelId="status-label"
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                  label="Status"
                >
                  <MenuItem value="available">Available</MenuItem>
                  <MenuItem value="issued">Issued</MenuItem>
                  <MenuItem value="lost">Lost</MenuItem>
                  <MenuItem value="damaged">Damaged</MenuItem>
                  <MenuItem value="under_repair">Under Repair</MenuItem>
                  <MenuItem value="reserved">Reserved</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                multiline
                rows={4}
              />
            </Grid>
          </Grid>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" color="primary">
          {bookToEdit ? 'Update' : 'Create'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default BookForm; 