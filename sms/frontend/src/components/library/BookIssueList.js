import React, { useState, useEffect } from 'react';
import {
  Box, Button, Typography, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, IconButton, Chip, TextField, InputAdornment,
  Dialog, DialogTitle, DialogContent, DialogActions, MenuItem, Select, FormControl, InputLabel,
  Tab, Tabs
} from '@mui/material';
import { CheckCircle, Add, Search, FilterList, ArrowBack, Info } from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { format } from 'date-fns';
import LoadingIndicator from '../common/LoadingIndicator';

const BookIssueList = () => {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tabValue, setTabValue] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [openIssueDialog, setOpenIssueDialog] = useState(false);
  const [openReturnDialog, setOpenReturnDialog] = useState(false);
  const [selectedIssue, setSelectedIssue] = useState(null);
  const [returnFine, setReturnFine] = useState('0');
  const [returnRemarks, setReturnRemarks] = useState('');
  
  const dispatch = useDispatch();
  // const { issues, loading } = useSelector(state => state.library);
  // Uncomment when library slice is ready
  
  useEffect(() => {
    // Fetch book issues
    // Will be implemented when API is connected
    setLoading(false);
    
    // Mock data for now
    setIssues([
      {
        id: 1,
        book: { 
          id: 1, 
          title: 'Mathematics for High School',
          author: 'John Smith',
          isbn: '9781234567897'
        },
        user_name: 'Emily Johnson',
        user_role: 'student',
        issue_date: '2023-09-15',
        due_date: '2023-09-29',
        returned: false,
        fine_amount: 0,
        remarks: ''
      },
      {
        id: 2,
        book: { 
          id: 2, 
          title: 'Introduction to Physics',
          author: 'Robert Johnson',
          isbn: '9789876543210'
        },
        user_name: 'Michael Smith',
        user_role: 'teacher',
        issue_date: '2023-09-10',
        due_date: '2023-10-10',
        return_date: '2023-09-25',
        returned: true,
        fine_amount: 0,
        remarks: 'Returned on time'
      },
      {
        id: 3,
        book: { 
          id: 3, 
          title: 'History of the World',
          author: 'Mary Williams',
          isbn: '9785432109876'
        },
        user_name: 'David Wilson',
        user_role: 'student',
        issue_date: '2023-08-20',
        due_date: '2023-09-03',
        returned: false,
        fine_amount: 0,
        remarks: ''
      }
    ]);
  }, [dispatch]);
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
  };
  
  const handleReturnBook = (issue) => {
    setSelectedIssue(issue);
    setOpenReturnDialog(true);
    
    // Calculate overdue days and suggest fine if overdue
    const today = new Date();
    const dueDate = new Date(issue.due_date);
    
    if (today > dueDate) {
      const overdueDays = Math.floor((today - dueDate) / (1000 * 60 * 60 * 24));
      // Assuming fine rate of $0.50 per day
      const suggestedFine = overdueDays * 50; // In cents
      setReturnFine(suggestedFine.toString());
      setReturnRemarks(`Overdue by ${overdueDays} days`);
    } else {
      setReturnFine('0');
      setReturnRemarks('');
    }
  };
  
  const confirmReturn = () => {
    // Will be implemented when API is connected
    console.log('Return book with ID:', selectedIssue.id, 'Fine:', returnFine, 'Remarks:', returnRemarks);
    setOpenReturnDialog(false);
    
    // Mock update for now
    setIssues(prev => 
      prev.map(issue => 
        issue.id === selectedIssue.id 
          ? { 
              ...issue, 
              returned: true, 
              return_date: format(new Date(), 'yyyy-MM-dd'),
              fine_amount: parseInt(returnFine),
              remarks: returnRemarks
            } 
          : issue
      )
    );
  };
  
  const handleAddIssue = () => {
    setOpenIssueDialog(true);
  };
  
  const closeIssueDialog = () => {
    setOpenIssueDialog(false);
  };
  
  const closeReturnDialog = () => {
    setOpenReturnDialog(false);
    setReturnFine('0');
    setReturnRemarks('');
  };
  
  const filteredIssues = issues.filter(issue => {
    const matchesSearch = searchTerm === '' || 
      issue.book.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
      issue.book.author.toLowerCase().includes(searchTerm.toLowerCase()) ||
      issue.user_name.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesTab = 
      (tabValue === 0) || // All issues
      (tabValue === 1 && !issue.returned) || // Active loans
      (tabValue === 2 && issue.returned); // Returned books
    
    return matchesSearch && matchesTab;
  });
  
  if (loading) {
    return <LoadingIndicator />;
  }
  
  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5">Book Loans</Typography>
        <Button 
          variant="contained" 
          color="primary" 
          startIcon={<Add />} 
          onClick={handleAddIssue}
        >
          Issue Book
        </Button>
      </Box>
      
      <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 2 }}>
        <Tab label="All" />
        <Tab label="Active Loans" />
        <Tab label="Returned" />
      </Tabs>
      
      <TextField
        fullWidth
        margin="normal"
        variant="outlined"
        placeholder="Search by book title, author, or borrower name..."
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
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Book Title</TableCell>
              <TableCell>Borrower</TableCell>
              <TableCell>Issue Date</TableCell>
              <TableCell>Due Date</TableCell>
              <TableCell>Return Date</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Fine</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredIssues.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  No book loans found
                </TableCell>
              </TableRow>
            ) : (
              filteredIssues.map((issue) => (
                <TableRow key={issue.id}>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {issue.book.title}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      by {issue.book.author}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {issue.user_name}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {issue.user_role}
                    </Typography>
                  </TableCell>
                  <TableCell>{issue.issue_date}</TableCell>
                  <TableCell>{issue.due_date}</TableCell>
                  <TableCell>{issue.return_date || '-'}</TableCell>
                  <TableCell>
                    <Chip 
                      label={issue.returned ? 'Returned' : 'Active'} 
                      color={issue.returned ? 'success' : 
                             (new Date(issue.due_date) < new Date() ? 'error' : 'primary')}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {issue.fine_amount > 0 ? `$${(issue.fine_amount / 100).toFixed(2)}` : '-'}
                  </TableCell>
                  <TableCell>
                    {!issue.returned && (
                      <IconButton 
                        size="small" 
                        color="primary"
                        onClick={() => handleReturnBook(issue)}
                        title="Return book"
                      >
                        <CheckCircle fontSize="small" />
                      </IconButton>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
      
      {/* Return Book Dialog */}
      <Dialog open={openReturnDialog} onClose={closeReturnDialog}>
        <DialogTitle>Return Book</DialogTitle>
        <DialogContent>
          {selectedIssue && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                {selectedIssue.book.title}
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Borrowed by: {selectedIssue.user_name}
              </Typography>
              <Typography variant="body2" gutterBottom>
                Due date: {selectedIssue.due_date}
              </Typography>
              
              <TextField
                fullWidth
                label="Fine Amount (cents)"
                type="number"
                value={returnFine}
                onChange={(e) => setReturnFine(e.target.value)}
                margin="normal"
                InputProps={{ inputProps: { min: 0 } }}
                helperText={`$${(parseInt(returnFine || 0) / 100).toFixed(2)}`}
              />
              
              <TextField
                fullWidth
                label="Remarks"
                value={returnRemarks}
                onChange={(e) => setReturnRemarks(e.target.value)}
                margin="normal"
                multiline
                rows={2}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={closeReturnDialog}>Cancel</Button>
          <Button onClick={confirmReturn} variant="contained" color="primary">
            Confirm Return
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* TODO: Implement Issue Book Dialog */}
      <Dialog open={openIssueDialog} onClose={closeIssueDialog}>
        <DialogTitle>Issue Book</DialogTitle>
        <DialogContent>
          <Typography variant="body1">
            Book issue form will be implemented here
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeIssueDialog}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BookIssueList; 