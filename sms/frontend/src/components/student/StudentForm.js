import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Divider,
  Grid,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  FormHelperText,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { fetchStudentById, createStudent, updateStudent } from '../../store/slices/studentSlice';
import LoadingIndicator from '../common/LoadingIndicator';

const genders = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'other', label: 'Other' },
  { value: 'not_specified', label: 'Not Specified' },
];

const bloodGroups = [
  { value: 'A+', label: 'A+' },
  { value: 'A-', label: 'A-' },
  { value: 'B+', label: 'B+' },
  { value: 'B-', label: 'B-' },
  { value: 'AB+', label: 'AB+' },
  { value: 'AB-', label: 'AB-' },
  { value: 'O+', label: 'O+' },
  { value: 'O-', label: 'O-' },
  { value: 'Not Known', label: 'Not Known' },
];

const StudentForm = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { id } = useParams();
  const isEdit = Boolean(id);
  
  const { currentStudent, loading, error } = useSelector((state) => state.student);
  const { classes } = useSelector((state) => state.classes || { classes: [] });
  
  const [formData, setFormData] = useState({
    user: {
      email: '',
      full_name: '',
      username: '',
      password: '',
      role: 'student',
    },
    admission_number: '',
    roll_number: '',
    date_of_birth: null,
    gender: 'not_specified',
    blood_group: 'Not Known',
    class_id: '',
    address: '',
    city: '',
    state: '',
    country: '',
    postal_code: '',
    phone: '',
  });
  
  const [errors, setErrors] = useState({});
  
  useEffect(() => {
    if (isEdit) {
      dispatch(fetchStudentById(id));
    }
  }, [dispatch, id, isEdit]);
  
  useEffect(() => {
    if (isEdit && currentStudent) {
      setFormData({
        user: {
          email: currentStudent.user?.email || '',
          full_name: currentStudent.user?.full_name || '',
          username: currentStudent.user?.username || '',
          password: '',
          role: 'student',
        },
        admission_number: currentStudent.admission_number || '',
        roll_number: currentStudent.roll_number || '',
        date_of_birth: currentStudent.date_of_birth ? new Date(currentStudent.date_of_birth) : null,
        gender: currentStudent.gender || 'not_specified',
        blood_group: currentStudent.blood_group || 'Not Known',
        class_id: currentStudent.class_id || '',
        address: currentStudent.address || '',
        city: currentStudent.city || '',
        state: currentStudent.state || '',
        country: currentStudent.country || '',
        postal_code: currentStudent.postal_code || '',
        phone: currentStudent.phone || '',
      });
    }
  }, [currentStudent, isEdit]);
  
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.user.full_name) newErrors.full_name = 'Full name is required';
    if (!formData.user.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.user.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!formData.user.username) newErrors.username = 'Username is required';
    
    if (!isEdit && !formData.user.password) {
      newErrors.password = 'Password is required';
    } else if (!isEdit && formData.user.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }
    
    if (!formData.admission_number) newErrors.admission_number = 'Admission number is required';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleChange = (event) => {
    const { name, value } = event.target;
    
    if (name.startsWith('user.')) {
      const userField = name.split('.')[1];
      setFormData({
        ...formData,
        user: {
          ...formData.user,
          [userField]: value,
        },
      });
    } else {
      setFormData({
        ...formData,
        [name]: value,
      });
    }
  };
  
  const handleDateChange = (date) => {
    setFormData({
      ...formData,
      date_of_birth: date,
    });
  };
  
  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!validateForm()) return;
    
    const payload = {
      ...formData,
      date_of_birth: formData.date_of_birth 
        ? formData.date_of_birth.toISOString().split('T')[0] 
        : null,
    };
    
    if (isEdit) {
      await dispatch(updateStudent({ id, studentData: payload }));
    } else {
      await dispatch(createStudent(payload));
    }
    
    navigate('/students');
  };
  
  if (loading && isEdit) {
    return <LoadingIndicator message="Loading student data..." />;
  }
  
  return (
    <form autoComplete="off" onSubmit={handleSubmit}>
      <Card>
        <CardHeader
          title={isEdit ? 'Edit Student' : 'Add New Student'}
          subheader={isEdit ? 'Update student information' : 'Create a new student profile'}
        />
        <Divider />
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Box sx={{ typography: 'subtitle1', fontWeight: 'bold', mb: 2 }}>User Information</Box>
            </Grid>
            
            <Grid item md={6} xs={12}>
              <TextField
                fullWidth
                label="Full Name"
                name="user.full_name"
                onChange={handleChange}
                required
                value={formData.user.full_name}
                variant="outlined"
                error={Boolean(errors.full_name)}
                helperText={errors.full_name}
              />
            </Grid>
            
            <Grid item md={6} xs={12}>
              <TextField
                fullWidth
                label="Username"
                name="user.username"
                onChange={handleChange}
                required
                value={formData.user.username}
                variant="outlined"
                error={Boolean(errors.username)}
                helperText={errors.username}
              />
            </Grid>
            
            <Grid item md={6} xs={12}>
              <TextField
                fullWidth
                label="Email Address"
                name="user.email"
                onChange={handleChange}
                required
                type="email"
                value={formData.user.email}
                variant="outlined"
                error={Boolean(errors.email)}
                helperText={errors.email}
              />
            </Grid>
            
            <Grid item md={6} xs={12}>
              <TextField
                fullWidth
                label={isEdit ? "Password (leave blank to keep current)" : "Password"}
                name="user.password"
                onChange={handleChange}
                required={!isEdit}
                type="password"
                value={formData.user.password}
                variant="outlined"
                error={Boolean(errors.password)}
                helperText={errors.password}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Box sx={{ typography: 'subtitle1', fontWeight: 'bold', mb: 2, mt: 2 }}>Student Information</Box>
            </Grid>
            
            <Grid item md={4} xs={12}>
              <TextField
                fullWidth
                label="Admission Number"
                name="admission_number"
                onChange={handleChange}
                required
                value={formData.admission_number}
                variant="outlined"
                error={Boolean(errors.admission_number)}
                helperText={errors.admission_number}
              />
            </Grid>
            
            <Grid item md={4} xs={12}>
              <TextField
                fullWidth
                label="Roll Number"
                name="roll_number"
                onChange={handleChange}
                value={formData.roll_number}
                variant="outlined"
              />
            </Grid>
            
            <Grid item md={4} xs={12}>
              <FormControl fullWidth variant="outlined">
                <InputLabel id="class-label">Class</InputLabel>
                <Select
                  labelId="class-label"
                  id="class_id"
                  name="class_id"
                  value={formData.class_id}
                  onChange={handleChange}
                  label="Class"
                >
                  <MenuItem value="">
                    <em>None</em>
                  </MenuItem>
                  {classes && classes.map((cls) => (
                    <MenuItem key={cls.id} value={cls.id}>
                      {cls.name} - {cls.section}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item md={4} xs={12}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="Date of Birth"
                  value={formData.date_of_birth}
                  onChange={handleDateChange}
                  renderInput={(params) => <TextField {...params} fullWidth variant="outlined" />}
                />
              </LocalizationProvider>
            </Grid>
            
            <Grid item md={4} xs={12}>
              <FormControl fullWidth variant="outlined">
                <InputLabel id="gender-label">Gender</InputLabel>
                <Select
                  labelId="gender-label"
                  id="gender"
                  name="gender"
                  value={formData.gender}
                  onChange={handleChange}
                  label="Gender"
                >
                  {genders.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item md={4} xs={12}>
              <FormControl fullWidth variant="outlined">
                <InputLabel id="blood-group-label">Blood Group</InputLabel>
                <Select
                  labelId="blood-group-label"
                  id="blood_group"
                  name="blood_group"
                  value={formData.blood_group}
                  onChange={handleChange}
                  label="Blood Group"
                >
                  {bloodGroups.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item md={6} xs={12}>
              <TextField
                fullWidth
                label="Phone Number"
                name="phone"
                onChange={handleChange}
                value={formData.phone}
                variant="outlined"
              />
            </Grid>
            
            <Grid item md={6} xs={12}>
              <TextField
                fullWidth
                label="Address"
                name="address"
                onChange={handleChange}
                value={formData.address}
                variant="outlined"
                multiline
                rows={2}
              />
            </Grid>
            
            <Grid item md={3} xs={12}>
              <TextField
                fullWidth
                label="City"
                name="city"
                onChange={handleChange}
                value={formData.city}
                variant="outlined"
              />
            </Grid>
            
            <Grid item md={3} xs={12}>
              <TextField
                fullWidth
                label="State/Province"
                name="state"
                onChange={handleChange}
                value={formData.state}
                variant="outlined"
              />
            </Grid>
            
            <Grid item md={3} xs={12}>
              <TextField
                fullWidth
                label="Country"
                name="country"
                onChange={handleChange}
                value={formData.country}
                variant="outlined"
              />
            </Grid>
            
            <Grid item md={3} xs={12}>
              <TextField
                fullWidth
                label="Postal Code"
                name="postal_code"
                onChange={handleChange}
                value={formData.postal_code}
                variant="outlined"
              />
            </Grid>
          </Grid>
          
          {error && (
            <Box sx={{ color: 'error.main', mt: 2 }}>
              Error: {error}
            </Box>
          )}
        </CardContent>
        <Divider />
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', p: 2 }}>
          <Button
            color="primary"
            variant="contained"
            type="submit"
            sx={{ ml: 1 }}
          >
            {isEdit ? 'Update Student' : 'Create Student'}
          </Button>
          <Button
            color="secondary"
            variant="outlined"
            onClick={() => navigate('/students')}
            sx={{ ml: 1 }}
          >
            Cancel
          </Button>
        </Box>
      </Card>
    </form>
  );
};

export default StudentForm; 