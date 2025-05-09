import React, { useState, useEffect } from 'react';
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
import config from '../config';

const HomePage = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    topic: '',
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [showUnsubscribe, setShowUnsubscribe] = useState(false);
  const [topics, setTopics] = useState([]);
  const [topicsLoading, setTopicsLoading] = useState(true);
  const [topicsError, setTopicsError] = useState(null);
  const github_url = 'https://github.com/deep206/subscribe-to-ai-news';

  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const response = await axios.get(`${config.apiUrl}/topics`);
        setTopics(response.data.topics);
        setTopicsError(null);
      } catch (error) {
        setTopicsError('Failed to load available topics. Please try again later.');
        console.error('Error fetching topics:', error);
      } finally {
        setTopicsLoading(false);
      }
    };

    fetchTopics();
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await axios.post(`${config.apiUrl}/subscribe`, formData);
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
      const response = await axios.post(`${config.apiUrl}/unsubscribe`, {
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
      const response = await axios.post(`${config.apiUrl}/test`, { password });
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
        <Typography variant="h1" component="h1" gutterBottom sx={{ mb: 2 }}>
          Subscribe to AI Newsletter!
        </Typography>
        <Typography variant="h2" component="h3" gutterBottom sx={{ mb: 2 }}>
          Effortlessly stay informed.
        </Typography>
        <Typography variant="h5" component="h5" gutterBottom sx={{ mb: 4 }}>
          This automated AI-powered service scours the web for the latest news on your chosen topics, distills the key insights into concise summaries, and delivers them every Sunday straight to your inbox. Perfect for researchers, professionals, and anyone who wants to keep up with the news—without the noise.
        </Typography>

        {message.text && (
          <Alert severity={message.type} sx={{ mb: 2 }}>
            {message.text}
          </Alert>
        )}

        {topicsError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {topicsError}
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
            disabled={topicsLoading}
          >
            {topicsLoading ? (
              <MenuItem value="">
                <em>Loading topics...</em>
              </MenuItem>
            ) : (
              topics.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))
            )}
          </TextField>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            disabled={loading || topicsLoading}
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
        <div style={{ marginTop: '2em' }}>
          <Typography variant="b1" component="b1">
            Built with ❤️ / &copy; {new Date().getFullYear()} Deep Patel / <a href={github_url} target='_blank' rel="noreferrer" style={{ textDecoration: 'none', color: 'blue' }}>Source code</a>
          </Typography>
        </div>
      </Box>
    </Container>
  );
};

export default HomePage; 