# AI News Research Assistant

An intelligent, automated news aggregation and summarization system that delivers personalized news digests to your inbox. Powered by cutting-edge AI, this assistant scours the web for the latest developments in your chosen topics, distills the information into concise, insightful summaries, and delivers them weekly to keep you informed without the noise.

## Key Features

-   🔍 AI-powered news aggregation and summarization
-   📧 Weekly personalized email digests
-   🔒 Secure user data management
-   🎯 Topic-based content filtering
-   🤖 Automated content processing pipeline

## Tech Stack

-   **Frontend**: React.js (Modern, responsive UI)
-   **Backend**: Python (AI/ML processing)
-   **Database**: Firebase (User management)
-   **APIs & Services**:
    -   SerpApi (Web search)
    -   Scrapy (Content extraction)
    -   Brevo (Email delivery)
    -   Gemini 1.5 Flash (Content summarization)

Now, let me outline the detailed architecture and design considerations:

### System Architecture

1. **Frontend Layer (React.js)**

    - Single-page application with responsive design
    - Form validation and error handling
    - Admin mode with password protection
    - User feedback and status messages

2. **Backend Layer (Python)**

    - RESTful API endpoints:
        - `/subscribe` - User registration
        - `/unsubscribe` - User removal
        - `/test` - Admin testing endpoint
    - Scheduled job (Sunday 7am ET)
    - API rate limiting and quota management

3. **Data Layer (Firebase)**

    - Collections:
        - `users` - User data
        - `topics` - Available news categories
        - `subscriptions` - User-topic mappings

4. **Processing Pipeline**
    ```
    User Input → Firebase Storage → Weekly Job →
    SerpApi Search → Scrapy Extraction →
    Gemini Summarization → Brevo Email Delivery
    ```

### Security Considerations

1. **Data Protection**

    - User data in Firebase
    - Secure API key management
    - Environment variable protection
    - Input validation and sanitization

2. **Access Control**

    - Admin password encryption
    - Rate limiting on API endpoints
    - User quota management
    - Email domain validation

3. **Error Handling**
    - Graceful degradation
    - User-friendly error messages
    - Logging and monitoring
    - Fallback mechanisms

### Implementation Phases

1. **Phase 1: Core Infrastructure**

    - Firebase setup and configuration
    - Basic API endpoints
    - User management system
    - Email validation

2. **Phase 2: News Processing**

    - SerpApi integration
    - Scrapy implementation
    - Gemini API integration
    - Content summarization logic

3. **Phase 3: Email System**

    - Brevo integration
    - Email template design
    - Scheduling system
    - Testing framework

4. **Phase 4: UI/UX**
    - React application
    - Form validation
    - Error handling
    - Admin interface

### Environment Variables Needed

```
FIREBASE_CONFIG={...}
SERPAPI_KEY=your_key
BREVO_API_KEY=your_key
GEMINI_API_KEY=your_key
ADMIN_PWD=encrypted_password
TEST_EMAIL=your_email
MAX_USERS=100
```

### Database Schema

```javascript
// Firebase Collections

// users collection
{
  email: string,
  name: string,
  createdAt: timestamp,
  status: string,
  topic: string
}

// topics collection
{
  name: string,        // Display name for users
  searchTerms: string, // Terms used for SerpApi search
  isActive: boolean    // Whether the topic is available for subscription
}
```
