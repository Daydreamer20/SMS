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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Typography
} from '@mui/material';
import { fetchClassById, createClass, updateClass } from '../../store/slices/classSlice';
import { fetchAcademicYears } from '../../store/slices/academicYearSlice';
import { fetchStaff } from '../../store/slices/staffSlice';
import LoadingIndicator from '../common/LoadingIndicator';

const ClassForm = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { id } = useParams();
  const isEdit = Boolean(id);
  
  const { currentClass, loading: classLoading, error: classError } = useSelector((state) => state.class);
  const { academicYears, loading: academicYearLoading } = useSelector((state) => state.academicYear || { academicYears: [] });
  const { staff, loading: staffLoading } = useSelector((state) => state.staff || { staff: [] });
  
  const [formData, setFormData] = useState({
    name: '',
    section: '',
    grade_level: '',
    academic_year_id: '',
    teacher_id: '',
  });
  
  const [errors, setErrors] = useState({});
  
  useEffect(() => {
    dispatch(fetchAcademicYears());
    dispatch(fetchStaff({ staff_type: 'teacher' }));
    
    if (isEdit) {
      dispatch(fetchClassById(id));
    }
  }, [dispatch, id, isEdit]);
  
  useEffect(() => {
    if (isEdit && currentClass) {
      setFormData({
        name: currentClass.name || '',
        section: currentClass.section || '',
        grade_level: currentClass.grade_level || '',
        academic_year_id: currentClass.academic_year_id || '',
        teacher_id: currentClass.teacher_id || '',
      });
    }
  }, [currentClass, isEdit]);
  
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name) newErrors.name = 'Class name is required';
    if (!formData.section) newErrors.section = 'Section is required';
    if (!formData.grade_level) {
      newErrors.grade_level = 'Grade level is required';
    } else if (isNaN(Number(formData.grade_level))) {
      newErrors.grade_level = 'Grade level must be a number';
    }
    if (!formData.academic_year_id) newErrors.academic_year_id = 'Academic year is required';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };
  
  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!validateForm()) return;
    
    const payload = {
      ...formData,
      grade_level: Number(formData.grade_level),
    };
    
    if (isEdit) {
      await dispatch(updateClass({ id, classData: payload }));
    } else {
      await dispatch(createClass(payload));
    }
    
    navigate('/classes');
  };
  
  if (classLoading || academicYearLoading || staffLoading) {
    return <LoadingIndicator message="Loading data..." />;
  }
  
  return (
    <form autoComplete="off" onSubmit={handleSubmit}>
      <Card>
        <CardHeader
          title={isEdit ? 'Edit Class' : 'Add New Class'}
          subheader={isEdit ? 'Update class information' : 'Create a new class'}
        />
        <Divider />
        <CardContent>
          <Grid container spacing={3}>
            <Grid item md={6} xs={12}>
              <TextField
                fullWidth
                label="Class Name"
                name="name"
                onChange={handleChange}
                required
                value={formData.name}
                variant="outlined"
                error={Boolean(errors.name)}
                helperText={errors.name}
              />
            </Grid>
            
            <Grid item md={6} xs={12}>
              <TextField
                fullWidth
                label="Section"
                name="section"
                onChange={handleChange}
                required
                value={formData.section}
                variant="outlined"
                error={Boolean(errors.section)}
                helperText={errors.section}
              />
            </Grid>
            
            <Grid item md={4} xs={12}>
              <TextField
                fullWidth
                label="Grade Level"
                name="grade_level"
                onChange={handleChange}
                required
                type="number"
                value={formData.grade_level}
                variant="outlined"
                error={Boolean(errors.grade_level)}
                helperText={errors.grade_level}
              />
            </Grid>
            
            <Grid item md={4} xs={12}>
              <FormControl fullWidth variant="outlined" error={Boolean(errors.academic_year_id)}>
                <InputLabel id="academic-year-label">Academic Year</InputLabel>
                <Select
                  labelId="academic-year-label"
                  id="academic_year_id"
                  name="academic_year_id"
                  value={formData.academic_year_id}
                  onChange={handleChange}
                  label="Academic Year"
                  required
                >
                  <MenuItem value="">
                    <em>Select Academic Year</em>
                  </MenuItem>
                  {academicYears && academicYears.map((year) => (
                    <MenuItem key={year.id} value={year.id}>
                      {year.name}
                      {year.is_active && (
                        <Chip 
                          label="Active" 
                          color="success" 
                          size="small" 
                          sx={{ ml: 1 }} 
                        />
                      )}
                    </MenuItem>
                  ))}
                </Select>
                {errors.academic_year_id && (
                  <Typography variant="caption" color="error">
                    {errors.academic_year_id}
                  </Typography>
                )}
              </FormControl>
            </Grid>
            
            <Grid item md={4} xs={12}>
              <FormControl fullWidth variant="outlined">
                <InputLabel id="teacher-label">Class Teacher</InputLabel>
                <Select
                  labelId="teacher-label"
                  id="teacher_id"
                  name="teacher_id"
                  value={formData.teacher_id}
                  onChange={handleChange}
                  label="Class Teacher"
                >
                  <MenuItem value="">
                    <em>Not Assigned</em>
                  </MenuItem>
                  {staff && staff.map((teacher) => (
                    <MenuItem key={teacher.id} value={teacher.id}>
                      {teacher.user?.full_name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
          
          {classError && (
            <Box sx={{ color: 'error.main', mt: 2 }}>
              Error: {classError}
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
            {isEdit ? 'Update Class' : 'Create Class'}
          </Button>
          <Button
            color="secondary"
            variant="outlined"
            onClick={() => navigate('/classes')}
            sx={{ ml: 1 }}
          >
            Cancel
          </Button>
        </Box>
      </Card>
    </form>
  );
};

export default ClassForm; 