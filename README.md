
**Note**:
This architecture was originally drafted for Buzzler, a larger AI-powered content platform I’ve since shelved. The prototype — Buzzy — was built with pure Next.js + Appwrite. This FastAPI/Next.js/Celery stack won’t be used to build a full product, but instead serves as a reference architecture and boilerplate for future projects. Think of it as a “production-grade pattern library” — not a shipping product.

It features a modern, decoupled architecture with a Next.js frontend and a FastAPI backend, leveraging asynchronous processing for a seamless user experience.

## Table of Contents

- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
  - [Frontend (Next.js)](#frontend-nextjs)
  - [Backend (FastAPI)](#backend-fastapi)
- [Key Features](#key-features)
  - [Video Upload and Processing](#video-upload-and-processing)
  - [Asynchronous Task Handling with Celery](#asynchronous-task-handling-with-celery)
- [Authentication Flow](#authentication-flow)
  - [Email/Password Authentication](#emailpassword-authentication)
  - [OAuth 2.0 (Google)](#oauth-20-google)
  - [Security Measures](#security-measures)
- [Database Schema](#database-schema)
- [Getting Started](#getting-started)

## Tech Stack

| Category      | Technology                                                              |
|---------------|-------------------------------------------------------------------------|
| **Frontend**  | [**Next.js**](https://nextjs.org/) (React), [**TypeScript**](https://www.typescriptlang.org/), [**Tailwind CSS**](https://tailwindcss.com/) |
|               | [**Zustand**](https://zustand-demo.pmnd.rs/) for state management, [**Axios**](https://axios-http.com/) for API calls         |
| **Backend**   | [**FastAPI**](https://fastapi.tiangolo.com/), [**Python 3.11+**](https://www.python.org/)                               |
|               | [**SQLAlchemy 2.0**](https://www.sqlalchemy.org/) (Async with `asyncpg`) for ORM      |
| **Database**  | [**PostgreSQL**](https://www.postgresql.org/)                                           |
| **Async Tasks**| [**Celery**](https://docs.celeryq.dev/) for background processing, [**Redis**](https://redis.io/) as message broker & result backend |
| **Storage**   | [**Azure Blob Storage**](https://azure.microsoft.com/en-us/products/storage/blobs) for video and file storage |
| **Containerization** | [**Docker**](https://www.docker.com/) & Docker Compose                               |

## Architecture

The application is structured as a monorepo with two main packages: `frontend` and `backend`.

### Frontend (Next.js)

The frontend is a modern React application built with Next.js and TypeScript, utilizing the App Router for file-based routing.

- **`app/`**: Contains all the routes and pages.
  - **`(main-app)/`**: Layout and pages for the authenticated part of the application (e.g., dashboard, settings).
  - **`auth/`**: Authentication-related pages like login, registration, and OAuth callbacks.
- **`components/`**: Reusable React components, organized by feature (e.g., `auth`, `layout`, `upload`).
- **`lib/`**: Core logic and utilities.
  - **`store/`**: State management stores using **Zustand** (`authStore`, `uploadStore`).
  - **`axios/`**: Axios instance and interceptors for handling API requests, including authentication headers and token refresh logic.
- **`hooks/`**: Custom React hooks encapsulating business logic, such as `useVideoImport` for handling video URL imports and progress polling.
- **`styles/`**: Global styles and Tailwind CSS configuration. The application features a custom, modern dark theme.

### Backend (FastAPI)

The backend is a high-performance asynchronous API built with FastAPI and Python. It follows a clean, modular structure.

- **`main.py`**: The entry point of the FastAPI application, where middleware (CORS, CSRF, Security Headers) and routers are configured.
- **`api/endpoints/`**: API routers are organized by resource (e.g., `users`, `video`). This is where the HTTP endpoints are defined.
- **`core/`**: Handles core application logic, most notably authentication.
  - **`auth/`**: Implements the entire authentication flow, including JWT creation, password hashing, OAuth provider integration, and token refresh logic.
  - **`security/`**: Contains security implementations like CSRF protection (double submit cookie pattern), security headers, and rate limiting.
- **`db/`**: Manages database connections using SQLAlchemy's asynchronous engine and session management.
- **`models/`**: Defines the database schema through SQLAlchemy 2.0 declarative models.
- **`schemas/`**: Pydantic models for request/response validation and serialization, ensuring data integrity.
- **`services/`**: Encapsulates business logic that interacts with external services (e.g., `AzureUploadService`) or performs complex operations (`VideoService`).
- **`celery/`**: Configures the Celery application and defines asynchronous tasks for background processing.

## Key Features

### Video Upload and Processing

The application supports two primary methods for video ingestion:

1.  **Direct File Upload**: The frontend requests a secure **SAS (Shared Access Signature) URL** from the backend. It then uploads the file directly to Azure Blob Storage. This approach offloads the bandwidth from the backend server, making uploads fast and scalable.
2.  **URL Import**: Users can paste a URL from platforms like YouTube. A Celery task is dispatched to handle the import. The backend uses `yt-dlp` to stream the video content directly to Azure Blob Storage in chunks, **without saving the file to local disk**. This is highly efficient for serverless or containerized environments with ephemeral storage.

### Asynchronous Task Handling with Celery

Long-running processes are handled in the background by Celery workers to prevent blocking the API and to provide a non-blocking user experience.

- **Task Queues**: Tasks are routed to different queues based on their type (e.g., `import_tasks`, `video_processing`), allowing for dedicated workers and resource allocation.
- **Real-time Progress Tracking**: For URL imports, the Celery task periodically pushes progress updates (percentage, uploaded bytes, current step) to a **Redis** key. The frontend polls an API endpoint that reads this Redis key, enabling a real-time progress bar and status updates for the user.
- **Concurrency Limiting**: The number of concurrent URL imports is managed using a semaphore to prevent overwhelming the server's resources.

## Authentication Flow

The authentication system is robust, secure, and supports multiple methods.

### Email/Password Authentication

1.  **Registration**: A user registers with an email and password. The password is
    hashed using `bcrypt`. A verification email with a JWT is sent to the user.
2.  **Login**: The user logs in, and upon successful credential verification, the backend returns an `access_token` and sets a secure, `HttpOnly` `refresh_token` cookie.
3.  **Session Management**: The `access_token` (a short-lived JWT) is stored in memory (Zustand store) on the frontend and sent in the `Authorization` header for API requests.
4.  **Token Refresh**: When the `access_token` expires, an Axios interceptor automatically makes a request to the `/auth/refresh` endpoint. This endpoint uses the `refresh_token` from the cookie to issue a new `access_token`.

### OAuth 2.0 (Google)

1.  **Initiation**: The frontend redirects the user to the Google OAuth consent screen.
2.  **Callback**: After authorization, Google redirects the user back to the backend's `/auth/oauth/callback` endpoint with an authorization `code`.
3.  **Token Exchange**: The backend exchanges the `code` for a Google access token and fetches the user's profile information.
4.  **User Provisioning**: It either creates a new user or links the OAuth identity to an existing user based on the email address.
5.  **Frontend Redirect**: The backend redirects the user to a dedicated frontend page (`/auth/oauth/success`) with a short-lived `access_token` in the URL.
6.  **Session Setup**: The frontend page uses this token to call the `/auth/setup-session` endpoint, which sets the `HttpOnly` `refresh_token` cookie and CSRF token, establishing a full-fledged session.

### Security Measures

-   **CSRF Protection**: Implemented using the **Double Submit Cookie** pattern. A CSRF token is set in a cookie accessible to JavaScript, and the frontend sends this token in a custom `X-CSRF-Token` header for all state-changing requests. The backend verifies that the cookie token matches the header token.
-   **Secure Cookies**: Refresh tokens are stored in `HttpOnly` cookies, making them inaccessible to client-side scripts and mitigating XSS attacks. Cookies are marked as `Secure` in production.
-   **Security Headers**: A middleware adds essential security headers like `X-Content-Type-Options`, `X-Frame-Options`, and `Strict-Transport-Security` to every response.
-   **Rate Limiting**: Applied to sensitive endpoints like login and password reset to prevent brute-force attacks.

## Database Schema

The database is designed with SQLAlchemy ORM and includes the following core models:

-   `User`: Stores user authentication details, profile information, and relationships to other models.
-   `Video`: Contains metadata about each uploaded video, including its source, status, and Azure storage paths.
-   `Clip`: Represents a short-form clip generated from a `Video`.
-   `SocialAccount`: Stores credentials for connected social media accounts (e.g., Twitter, Instagram).
-   `Post`: Represents a social media post that has been scheduled or published.
-   `FileStorage`: A generic model to track all files stored in Azure, linking them to their respective entities (e.g., a video, a user avatar).

## Getting Started

To run this project locally, you will need Docker, Python, and Node.js installed.

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd buzzler
    ```

2.  **Backend Setup:**
    - Navigate to the `backend` directory.
    - Create a `.env` file based on the configuration in `app/config.py`.
    - Install dependencies: `pip install -r requirements.txt`
    - Run the database migrations with Alembic.
    - Start the FastAPI server and Celery workers.

3.  **Frontend Setup:**
    - Navigate to the `frontend` directory.
    - Create a `.env.local` file and set `NEXT_PUBLIC_BACKEND_URL`.
    - Install dependencies: `npm install`
    - Start the Next.js development server: `npm run dev`

4.  **Run with Docker:**
    - Configure the `docker-compose.yml` file with the necessary environment variables.
    - Build and start the services:
      ```bash
      docker-compose up --build
      ```
