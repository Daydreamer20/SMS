import React, { useState } from 'react';
import { Box, Container, Tabs, Tab } from '@mui/material';
import LibraryList from '../../components/library/LibraryList';
import BookIssueList from '../../components/library/BookIssueList';
import BookForm from '../../components/library/BookForm';

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`library-tabpanel-${index}`}
      aria-labelledby={`library-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ pt: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const LibraryPage = () => {
  const [tabIndex, setTabIndex] = useState(0);
  const [openBookForm, setOpenBookForm] = useState(false);
  const [bookToEdit, setBookToEdit] = useState(null);
  
  const handleTabChange = (event, newValue) => {
    setTabIndex(newValue);
  };
  
  const handleBookFormOpen = (book = null) => {
    setBookToEdit(book);
    setOpenBookForm(true);
  };
  
  const handleBookFormClose = () => {
    setOpenBookForm(false);
    setBookToEdit(null);
  };
  
  const handleBookFormSubmit = (bookData) => {
    // This will be connected to the Redux actions later
    console.log('Book form submitted:', bookData);
    setOpenBookForm(false);
    setBookToEdit(null);
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={tabIndex} 
            onChange={handleTabChange}
            aria-label="library management tabs"
          >
            <Tab label="Books" id="library-tab-0" aria-controls="library-tabpanel-0" />
            <Tab label="Loans" id="library-tab-1" aria-controls="library-tabpanel-1" />
          </Tabs>
        </Box>
        
        <TabPanel value={tabIndex} index={0}>
          <LibraryList onEditBook={handleBookFormOpen} />
        </TabPanel>
        
        <TabPanel value={tabIndex} index={1}>
          <BookIssueList />
        </TabPanel>
        
        <BookForm
          open={openBookForm}
          bookToEdit={bookToEdit}
          onClose={handleBookFormClose}
          onSubmit={handleBookFormSubmit}
        />
      </Box>
    </Container>
  );
};

export default LibraryPage; 