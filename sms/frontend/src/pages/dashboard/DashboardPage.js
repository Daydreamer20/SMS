import React, { useEffect } from 'react';
import { useSelector } from 'react-redux';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardHeader,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  People as PeopleIcon,
  School as SchoolIcon,
  Assignment as AssignmentIcon,
  Event as EventIcon,
} from '@mui/icons-material';

const DashboardPage = () => {
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.roles?.includes('admin');
  const isTeacher = user?.roles?.includes('teacher');
  const isStudent = user?.roles?.includes('student');

  const statistics = [
    {
      title: 'Students',
      value: '250',
      icon: <SchoolIcon color="primary" sx={{ fontSize: 40 }} />,
      color: '#3f51b5',
      access: ['admin', 'teacher'],
    },
    {
      title: 'Teachers',
      value: '32',
      icon: <PeopleIcon color="secondary" sx={{ fontSize: 40 }} />,
      color: '#f50057',
      access: ['admin'],
    },
    {
      title: 'Classes',
      value: '15',
      icon: <AssignmentIcon sx={{ fontSize: 40, color: '#4caf50' }} />,
      color: '#4caf50',
      access: ['admin', 'teacher', 'student'],
    },
    {
      title: 'Events',
      value: '8',
      icon: <EventIcon sx={{ fontSize: 40, color: '#ff9800' }} />,
      color: '#ff9800',
      access: ['admin', 'teacher', 'student'],
    },
  ];

  const recentAnnouncements = [
    {
      title: 'End of Year Ceremony',
      date: '2023-06-15',
      description: 'The end of year ceremony will be held on June 30th at the main auditorium.',
    },
    {
      title: 'Final Exams Schedule',
      date: '2023-05-25',
      description: 'Final exams will begin on June 10th. The detailed schedule is now available.',
    },
    {
      title: 'Summer Break',
      date: '2023-05-15',
      description: 'Summer break will start on July 1st and end on August 31st.',
    },
  ];

  const upcomingEvents = [
    {
      title: 'Parent-Teacher Meeting',
      date: '2023-05-20',
      time: '14:00 - 17:00',
    },
    {
      title: 'Science Exhibition',
      date: '2023-06-05',
      time: '09:00 - 15:00',
    },
    {
      title: 'Sports Day',
      date: '2023-06-12',
      time: '08:00 - 16:00',
    },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="subtitle1" gutterBottom>
        Welcome back, {user?.username || 'User'}!
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {statistics
          .filter((stat) => 
            stat.access.some((role) => user?.roles?.includes(role))
          )
          .map((stat) => (
            <Grid item xs={12} sm={6} md={3} key={stat.title}>
              <Paper
                elevation={3}
                sx={{
                  p: 3,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  borderTop: `4px solid ${stat.color}`,
                }}
              >
                {stat.icon}
                <Typography variant="h4" component="div" sx={{ mt: 1 }}>
                  {stat.value}
                </Typography>
                <Typography variant="subtitle1" color="text.secondary">
                  {stat.title}
                </Typography>
              </Paper>
            </Grid>
          ))}
      </Grid>

      <Grid container spacing={3} sx={{ mt: 3 }}>
        <Grid item xs={12} md={6}>
          <Card elevation={3}>
            <CardHeader title="Recent Announcements" />
            <Divider />
            <CardContent>
              <List>
                {recentAnnouncements.map((announcement, index) => (
                  <React.Fragment key={index}>
                    <ListItem alignItems="flex-start">
                      <ListItemText
                        primary={announcement.title}
                        secondary={
                          <React.Fragment>
                            <Typography
                              sx={{ display: 'inline' }}
                              component="span"
                              variant="body2"
                              color="text.primary"
                            >
                              {announcement.date}
                            </Typography>
                            {` — ${announcement.description}`}
                          </React.Fragment>
                        }
                      />
                    </ListItem>
                    {index < recentAnnouncements.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card elevation={3}>
            <CardHeader title="Upcoming Events" />
            <Divider />
            <CardContent>
              <List>
                {upcomingEvents.map((event, index) => (
                  <React.Fragment key={index}>
                    <ListItem alignItems="flex-start">
                      <ListItemIcon>
                        <EventIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={event.title}
                        secondary={`${event.date} | ${event.time}`}
                      />
                    </ListItem>
                    {index < upcomingEvents.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage; 