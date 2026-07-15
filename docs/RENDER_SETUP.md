# Multi-Tenant AI News Curator — Render Setup Guide (with Supabase PostgreSQL)

This guide walks you through deploying the complete multi-tenant SaaS application to Render.com, backed by a persistent **Supabase PostgreSQL database** (which is completely free and won't expire or reset data like Render's free PostgreSQL databases do).

---

## 🚀 Deployment Overview

We deploy the system using a **Render Blueprint** (`render.yaml`), which automatically provisions:
1.  **FastAPI Backend (Web Service):** Built using the root `Dockerfile`. Runs the API endpoints and starts the persistent scheduler.
2.  **React Frontend (Static Site):** Installs Node packages, builds the static bundle, and serves the dashboard UI publicly.

---

## 🔧 Step-by-Step Setup

### Step 1: Create a Supabase Database
1.  Go to [Supabase.com](https://supabase.com) and sign up for a free account.
2.  Click **New Project** and name it (e.g., `ai-news-curator`). Set a secure Database Password.
3.  Once the project is created, navigate to **Project Settings** (gear icon) → **Database**.
4.  Scroll down to the **Connection string** section, choose **URI**, and copy the connection string.
    *   *Example format:* `postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres`
    *   *Note:* Replace `[YOUR-PASSWORD]` with the actual database password you chose.

### Step 2: Deploy the Blueprint to Render
1.  Go to [Render.com](https://render.com) and log in.
2.  Click **New** → **Blueprint**.
3.  Connect your GitHub repository containing this project.
4.  Select your branch (e.g., `main` or `master`).
5.  Render will read the `render.yaml` configuration file automatically.
6.  Click **Apply** to begin provisioning the web backend and frontend static site.

### Step 3: Configure Environment Variables
While the services are building, configure the necessary keys in the **Render Dashboard**:

1.  Select the **`ai-news-curator-backend`** Web Service.
2.  Navigate to the **Environment** tab.
3.  Add the following required variables:
    *   `DATABASE_URL`: The Supabase URI connection string you copied in Step 1 (with your password filled in).
    *   `GEMINI_API_KEY`: Your Google GenAI API key.
    *   `JWT_SECRET_KEY`: A secure random string to sign auth tokens.
    *   `MY_EMAIL`: The default system email address for SMTP sending fallbacks.
    *   `APP_PASSWORD`: The corresponding 16-character Google App Password (if using Gmail).

---

## 📁 Migration Setup (First-Time Deploy)

Once the backend service successfully builds and is online, you must initialize the 9 database tables on your Supabase instance:

1.  In the Render Dashboard, select the **`ai-news-curator-backend`** Web Service.
2.  Click the **Shell** tab on the left menu to open a terminal inside the running container.
3.  Run the migration command to construct the tables:
    ```bash
    uv run alembic upgrade head
    ```
4.  Verify that your tables exist and are reachable:
    ```bash
    uv run python -m app.database.check_connection
    ```

---

## 🌐 Navigating the Application

*   **Frontend Dashboard Console:** Open the public URL generated for your `ai-news-curator-frontend` static site (e.g., `https://ai-news-curator-frontend.onrender.com`).
*   **Create Account:** Go to the landing page and register. Your profile, sources, and schedules will be stored securely in Supabase.
*   **Immediate Test:** In the UI dashboard, go to settings and click **"Run Now"** to verify SMTP email sending and Gemini curation scoring logs instantly.
