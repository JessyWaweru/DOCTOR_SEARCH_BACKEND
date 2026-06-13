# 🩺 DocRank — Backend API

> Django REST Framework API powering the DocRank doctor search platform. Handles JWT authentication with OTP email verification, doctor listings, reviews, and saved doctors. Deployed on Render with Supabase PostgreSQL.

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?style=flat&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/REST_Framework-3.16-ff1709?style=flat)](https://www.django-rest-framework.org/)
[![JWT](https://img.shields.io/badge/Auth-JWT-F7B731?style=flat)](https://django-rest-framework-simplejwt.readthedocs.io/)
[![PostgreSQL](https://img.shields.io/badge/DB-PostgreSQL-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Render](https://img.shields.io/badge/Deployed_on-Render-46E3B7?style=flat&logo=render&logoColor=white)](https://render.com/)

---

## 📸 App Preview

> Screenshots from the live app at [docrank.jbnmedia.org](https://docrank.jbnmedia.org)  
> Each view shown in both **desktop** and **mobile**.

---

### 🗂️ Doctor Listing

| Desktop | Mobile |
|:---:|:---:|
| ![Doctor Listing Desktop](screenshots/01_doctor_listing.png) | ![Doctor Listing Mobile](screenshots/01_doctor_listing_mobile.png) |

---

### 🩺 Doctor Detail — Profile & Info

| Desktop | Mobile |
|:---:|:---:|
| ![Doctor Detail Desktop](screenshots/02_doctor_detail_1_desktop.png) | ![Doctor Detail Mobile](screenshots/02_doctor_detail_1_mobile.png) |

---

### ⭐ Doctor Detail — Reviews Section

| Desktop | Mobile |
|:---:|:---:|
| ![Doctor Reviews Desktop](screenshots/02_doctor_detail_2_desktop.png) | ![Doctor Reviews Mobile](screenshots/02_doctor_detail_2_mobile.png) |

---

### 🔐 Register Page

| Desktop | Mobile |
|:---:|:---:|
| ![Register Desktop](screenshots/03_register_desktop.png) | ![Register Mobile](screenshots/03_register_mobile.png) |

---

### 🔖 Saved Doctors

| Desktop | Mobile |
|:---:|:---:|
| ![Saved Doctors Desktop](screenshots/04_saved_desktop.png) | ![Saved Doctors Mobile](screenshots/04_saved_mobile.png) |

---

## 🌐 Overview

DocRank Backend is a RESTful API serving the DocRank platform — a doctor discovery and review system focused on the Kenyan healthcare market (Nairobi, Kisumu, Mombasa). It handles:

- 🔐 **OTP-verified registration** — accounts are inactive until email is confirmed
- 🔑 **JWT authentication** — login supports both username and email
- 🩺 **Doctor directory** — search, filter by specialty/location, order by rating
- ⭐ **Reviews** — authenticated users rate doctors on a 1–10 scale
- 🔖 **Saved doctors** — toggle save/unsave per user with duplicate prevention
- 📧 **Async email** — OTP emails sent via Resend API in background threads (prevents Render worker timeouts)
- 🚀 **Production-ready** — Render deployment + Supabase PostgreSQL + WhiteNoise static files

---

## ✨ Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 5.2 + Django REST Framework 3.16 |
| Authentication | JWT via `djangorestframework-simplejwt` |
| Email | Resend API (threaded, async) |
| Filtering | `django-filter` + DRF `SearchFilter` + `OrderingFilter` |
| Database (local) | SQLite (auto fallback) |
| Database (production) | Supabase PostgreSQL via `dj-database-url` |
| Static Files | WhiteNoise |
| Server | Gunicorn |
| Deployment | Render |
| Testing | pytest + pytest-django + pytest-cov |

---

## 📁 Project Structure

```
DOCTOR_SEARCH_BACKEND/
├── core/
│   ├── settings.py           # Environment-aware config (local vs Render)
│   ├── urls.py               # Root URL config
│   ├── wsgi.py
│   └── asgi.py
├── doctor_search_app/
│   ├── models.py             # User, Doctor, Review, SavedDoctor
│   ├── serializers.py        # DRF serializers
│   ├── views.py              # All API views and ViewSets
│   ├── urls.py               # App URL patterns
│   ├── admin.py
│   ├── tests.py
│   ├── management/
│   │   └── commands/
│   │       └── seeds.py      # DB seeder: doctors + dummy users + reviews
│   └── migrations/
├── screenshots/              # App preview screenshots
├── manage.py
├── requirements.txt
└── build.sh                  # Render build script
```

---

## 🗄️ Data Models

### `User` (extends `AbstractUser`)

| Field | Type | Notes |
|---|---|---|
| `email` | `EmailField` | Unique |
| `is_email_verified` | `BooleanField` | Set `True` after OTP confirmation |
| `otp_code` | `CharField(6)` | Generated at registration / password reset |
| `otp_created_at` | `DateTimeField` | OTP expires after **10 minutes** |
| `recovery_pin` | `CharField(10)` | Optional recovery field |

### `Doctor`

| Field | Type | Notes |
|---|---|---|
| `name` | `CharField` | |
| `specialty` | `CharField` | e.g. Cardiologist, Dentist, Obs/Gyn |
| `hospital` | `CharField` | |
| `location` | `CharField` | e.g. Nairobi, Kisumu, Mombasa |
| `email` | `CharField` | Optional |
| `cell` | `CharField` | |
| `image` | `URLField` | Profile photo URL (falls back to placeholder) |

### `Review`

| Field | Type | Notes |
|---|---|---|
| `doctor` | FK → `Doctor` | Cascades on delete |
| `user` | FK → `User` | Cascades on delete |
| `rating` | `IntegerField` | Validated: 1–10 |
| `comment` | `TextField` | Optional |
| Unique constraint | `(doctor, user)` | One review per user per doctor |

### `SavedDoctor`

| Field | Type | Notes |
|---|---|---|
| `user` | FK → `User` | |
| `doctor` | FK → `Doctor` | |
| `created_at` | `DateTimeField` | Auto-set |
| Unique constraint | `(user, doctor)` | No duplicate saves |

---

## 🔌 API Endpoints

All endpoints are prefixed with `/api/`.

### 🔐 Authentication

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Public | Create account (inactive) + send OTP to email |
| `POST` | `/api/auth/verify-email/` | Public | Verify OTP → activate account → return JWT |
| `POST` | `/api/auth/login/` | Public | Login with username **or** email → JWT |
| `POST` | `/api/auth/password-reset/` | Public | Send password reset OTP to email |
| `POST` | `/api/auth/password-reset/confirm/` | Public | Verify OTP + set new password |

### 🩺 Doctors

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/doctors/` | Public | All doctors, annotated with avg rating + review count |
| `GET` | `/api/doctors/?search=<q>` | Public | Search name, specialty, hospital, location |
| `GET` | `/api/doctors/?specialty=<s>` | Public | Filter by specialty |
| `GET` | `/api/doctors/?location=<l>` | Public | Filter by location |
| `GET` | `/api/doctors/?ordering=average_rating` | Public | Sort by rating (desc) |
| `GET` | `/api/doctors/<id>/` | Public | Single doctor detail |

### ⭐ Reviews

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/reviews/?doctor_id=<id>` | Public | All reviews for a doctor |
| `GET` | `/api/reviews/?mine=true` | 🔒 Required | Current user's reviews |
| `POST` | `/api/reviews/` | 🔒 Required | Submit a review |
| `DELETE` | `/api/reviews/<id>/` | 🔒 Required | Delete own review |

### 🔖 Saved Doctors

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/saved-doctors/toggle/` | 🔒 Required | Toggle save/unsave a doctor |
| `GET` | `/api/saved-doctors/` | 🔒 Required | List current user's saved doctors |

---

## 🔐 Auth & OTP Flow

```
1. POST /auth/register/
   → Account created (is_active=False)
   → 6-digit OTP emailed via Resend (background thread)

2. POST /auth/verify-email/  { username, otp }
   → OTP verified (expires after 10 min)
   → is_active=True, is_email_verified=True
   → JWT access + refresh tokens returned → user is logged in

3. POST /auth/login/  { username/email, password }
   → Supports login by username OR email
   → JWT access + refresh tokens returned

4. POST /auth/password-reset/  { email }
   → OTP emailed if account exists (silent failure if not)

5. POST /auth/password-reset/confirm/  { email, otp, new_password }
   → OTP verified → password updated → account re-activated
```

> OTP emails are sent in a **background thread** using Python's `threading.Thread`. This prevents Render's Gunicorn worker from timing out during slow SMTP operations.

---

## ⚙️ Local Setup

### Prerequisites

- Python 3.12+
- pip

### Installation

```bash
# Clone the repo
git clone https://github.com/JessyWaweru/DOCTOR_SEARCH_BACKEND.git
cd DOCTOR_SEARCH_BACKEND

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations (SQLite used locally by default)
python manage.py migrate

# Seed the database with doctors, users, and reviews
python manage.py seeds

# Start the development server
python manage.py runserver
```

API available at: `http://localhost:8000/api/`

Browsable DRF interface (local only): `http://localhost:8000/api/doctors/`

---

## 🌍 Environment Variables

Create a `.env` file in the project root (or set these on Render's dashboard):

```env
SECRET_KEY=your-django-secret-key

# Production database (Supabase PostgreSQL)
# Not required locally — falls back to SQLite automatically
DATABASE_URL=postgresql://user:password@host:port/dbname

# Resend email API
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxx
DEFAULT_FROM_EMAIL=DocRank <noreply@jbnmedia.org>

# Render deployment
ALLOWED_HOSTS=your-app.onrender.com
CORS_ALLOWED_ORIGINS=https://docrank.jbnmedia.org
```

---

## 🚀 Deployment (Render)

The `build.sh` script runs automatically on each Render deploy:

```bash
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

**Render start command:**

```bash
gunicorn core.wsgi:application
```

**Required environment variables on Render:**
`SECRET_KEY` · `DATABASE_URL` · `RESEND_API_KEY` · `DEFAULT_FROM_EMAIL` · `ALLOWED_HOSTS` · `CORS_ALLOWED_ORIGINS`

> The `RENDER` environment variable is set automatically by the platform and used internally to toggle production mode — disables DEBUG, switches to PostgreSQL, and restricts CORS.

---

## 🧪 Running Tests

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=doctor_search_app --cov-report=term-missing
```

---

## 🌱 Seeding the Database

```bash
python manage.py seeds
```

This creates:

- **36 doctors** across Nairobi, Kisumu, and Mombasa covering specialties including Cardiology, Dentistry, Obs/Gyn, Paediatrics, Neurology, ENT, Dermatology, and more
- **20 dummy users** with Kenyan names for review generation
- **4–7 randomised reviews** per seeded doctor with realistic rating distributions (70% positive, 20% average, 10% negative)

---

## 🖥️ Frontend

The DocRank frontend is a React + TypeScript SPA built with Vite and TailwindCSS. It consumes this API and is deployed separately.

**Repo:** [DOCTOR_SEARCH_FRONTEND](https://github.com/JessyWaweru/DOCTOR_SEARCH_FRONTEND)  
**Live app:** [docrank.jbnmedia.org](https://docrank.jbnmedia.org)

### Tech Stack

| Layer | Technology |
|---|---|
| Framework | React 19 + TypeScript 5.9 |
| Build Tool | Vite 7 |
| Styling | TailwindCSS 4 + shadcn/ui + Radix UI |
| Routing | React Router DOM v7 |
| HTTP Client | Axios (with JWT Bearer interceptor) |
| Icons | Lucide React |
| Linting | ESLint 9 + TypeScript ESLint |

### Pages & Routes

| Route | Access | Page | Description |
|---|---|---|---|
| `/` | Public | `Home.tsx` | Landing page |
| `/doctors` | Public | `Doctors.tsx` | Browse, search, and filter doctors |
| `/saved` | 🔒 Protected | `SavedDoctors.tsx` | User's bookmarked doctors |
| `/my-reviews` | 🔒 Protected | `MyReviews.tsx` | User's submitted reviews |
| `/login` | Public | `Login.tsx` | Login with username or email |
| `/register` | Public | `Register.tsx` | Register + OTP email verification |
| `/forgot-password` | Public | `ForgotPassword.tsx` | Request password reset OTP |
| `/reset-password` | Public | `ResetPassword.tsx` | Confirm OTP + set new password |

### Key Components

| Component | Description |
|---|---|
| `Navbar.tsx` | Top navigation with auth state awareness |
| `Layout.tsx` | Persistent wrapper for main routes |
| `DoctorCard.tsx` | Doctor listing card with save toggle |
| `DoctorDetails.tsx` | Full doctor profile modal with reviews + rating form |
| `AuthContext.tsx` | JWT state: login, logout, token persistence via `localStorage` |
| `SavedContext.tsx` | Saved doctors state shared across the app |

### Frontend Setup

```bash
# Clone the repo
git clone https://github.com/JessyWaweru/DOCTOR_SEARCH_FRONTEND.git
cd DOCTOR_SEARCH_FRONTEND

# Install dependencies
npm install

# Start dev server
npm run dev
```

Create a `.env` file in the frontend root:

```env
VITE_API_URL=http://localhost:8000/api
```

In production, set `VITE_API_URL` to your deployed Render backend URL.

| Script | Description |
|---|---|
| `npm run dev` | Start Vite dev server with HMR |
| `npm run build` | Type-check + production build |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint |

---

## 👤 Author

**Jessy Waweru**
[github.com/JessyWaweru](https://github.com/JessyWaweru)

---

## 🔗 Links

| | |
|---|---|
| 🖥️ Frontend repo | [DOCTOR_SEARCH_FRONTEND](https://github.com/JessyWaweru/DOCTOR_SEARCH_FRONTEND) |
| 🔧 Backend repo | [DOCTOR_SEARCH_BACKEND](https://github.com/JessyWaweru/DOCTOR_SEARCH_BACKEND) |
| 🌍 Live app | [docrank.jbnmedia.org](https://docrank.jbnmedia.org) |
