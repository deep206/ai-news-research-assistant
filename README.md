# Subscribe to AI Newsletter!

An intelligent, automated news aggregation and summarization system that delivers personalized news digests to your inbox every Sunday at 7am ET,. Powered by cutting-edge AI, this assistant scours the web for the latest developments in your chosen topics, distills the information into concise, insightful summaries, and delivers them weekly to keep you informed without the noise.

## [Live Demo Available Here](https://subscribeainews.web.app)

#### Please note that this is a research project so I have throttled maximum users due to cost constraints. [Please email me directly](mailto:deep@currently.com) if you are interested in contributing or supporting me. Thank you!

## Local Development

### Make sure you have following dependencies installed in your machine

    - Git, Python (v3.10+), Node version 18+

1. Fork and clone repo
2. Open terminal
3. For Front end setup, run following commands from project root:
    - `cd frontend` // navigate to frontend directory
    - `npm install`
    - `npm start` // this will run your frontend on localhost, for example: (http://localhost:3000)
4. For backend setup, login to free accounts and get API keys/secrets from SerpApi, Brevo and Gemini and replace values in ".env" file, then, run following commands from project root:
    - `cd backend` // navigate to backend directory
    - `python -m venv venv`
    - `source venv/Source/activate`
    - `python --version`
    - `pip install -r requirements.txt`
    - `python -m src.app` // this will initialize app file and run server locally, for example: (http://localhost:5000)
5. Have fun playing with the source code. Cheers!

## Deployment

### Frontend (Firebase)

1. Open terminal and run following commands
2. npm install -g firebase-tools
3. firebase login
4. firebase init // select Hosting option
5. firebase deploy

### Backend (Render)

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the following environment variables:
    - `FLASK_APP=src.app:create_app()`
    - `FLASK_ENV=production`
    - `GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account.json`
    - Other required environment variables from `.env.example`
4. Deploy the service

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
