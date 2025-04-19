import React, { useState } from 'react';
import {
  Container,
  Typography,
  Button,
  Box,
  TextField,
  MenuItem,
  Alert,
  CircularProgress,
} from '@mui/material';
import axios from 'axios';

const HomePage = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    topic: '',
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [showUnsubscribe, setShowUnsubscribe] = useState(false);

  // Available topics - we'll move this to a config file later
  const topics = [
    { value: 'Artificial Intelligence', label: 'Artificial Intelligence' },
    { value: 'Machine Learning', label: 'Machine Learning' },
    { value: 'Natural Language Processing', label: 'Natural Language Processing' },
    { value: 'Robotics', label: 'Robotics' },
  ];

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await axios.post('http://localhost:5000/subscribe', formData);
      setMessage({ type: 'success', text: response.data.message });
      setShowUnsubscribe(false);
      // Clear form fields after successful subscription
      setFormData({
        name: '',
        email: '',
        topic: '',
      });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.message || 'An error occurred. Please try again.',
      });
      setShowUnsubscribe(error.response?.data?.show_unsubscribe || false);
    } finally {
      setLoading(false);
    }
  };

  const handleUnsubscribe = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/unsubscribe', {
        email: formData.email,
        topic: formData.topic,
      });
      setMessage({ type: 'success', text: response.data.message });
      setShowUnsubscribe(false);
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.message || 'An error occurred. Please try again.',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTestEmail = async () => {
    const password = window.prompt('Enter admin password:');
    if (!password) return;

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/test', { password });
      setMessage({ type: 'success', text: response.data.message });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.message || 'An error occurred. Please try again.',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4, textAlign: 'center' }}>
        <Typography variant="h1" component="h1" gutterBottom>
          AI News Research Assistant
        </Typography>
        <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 4 }}>
          Effortlessly stay informed! This automated AI-powered assistant scours the web for the latest news on your chosen topics, distills the key insights into concise summaries, and delivers them straight to your inbox. Perfect for researchers, professionals, and anyone who wants to keep up with the news—without the noise.
        </Typography>

        {message.text && (
          <Alert severity={message.type} sx={{ mb: 2 }}>
            {message.text}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
          <TextField
            fullWidth
            label="Name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            margin="normal"
          />
          <TextField
            fullWidth
            label="Email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            required
            margin="normal"
            helperText="Only @gmail.com, @yahoo.com, and @outlook.com domains are accepted"
          />
          <TextField
            fullWidth
            select
            label="Topic"
            name="topic"
            value={formData.topic}
            onChange={handleChange}
            required
            margin="normal"
          >
            {topics.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </TextField>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            disabled={loading}
            sx={{ mt: 2 }}
          >
            {loading ? <CircularProgress size={24} /> : 'Subscribe'}
          </Button>
        </Box>

        {showUnsubscribe && (
          <Button
            variant="outlined"
            color="secondary"
            onClick={handleUnsubscribe}
            disabled={loading}
            sx={{ mt: 2 }}
          >
            {loading ? <CircularProgress size={24} /> : 'Unsubscribe'}
          </Button>
        )}

        {window.location.search.includes('mode=admin') && (
          <Button
            variant="outlined"
            color="primary"
            onClick={handleTestEmail}
            disabled={loading}
            sx={{ mt: 2, ml: 2 }}
          >
            Test Email
          </Button>
        )}
      </Box>
    </Container>
  );
};

export default HomePage; 