# Ward House Survey — Django REST API & Android Integration Guide

Backend REST API and built-in Web API Testing Dashboard for the **Ward House Survey Android Application**, built with **Django**, **Django REST Framework (DRF)**, and **SQLite**.

Supports **Admin** and **Field Agent** roles with Token Authentication, multi-angle house photo storage inside the project (`media/house_photos/<house_id>/`), **Form 1: Home Survey Form**, and **Form 2: Family Member Form**.

---

## Table of Contents

1. [Quick Start (Anaconda)](#1-quick-start-anaconda)
2. [Default Test Credentials & URLs](#2-default-test-credentials--urls)
3. [Android App Connection Setup](#3-android-app-connection-setup)
4. [Authentication & Headers](#4-authentication--headers)
5. [Role Permissions Matrix](#5-role-permissions-matrix)
6. [Complete API Reference (25 Endpoints)](#6-complete-api-reference-25-endpoints)
   - [6.1 Admin Authentication](#61-admin-authentication)
   - [6.2 Field Agent Authentication](#62-field-agent-authentication)
   - [6.3 Logout & User Profile](#63-logout--user-profile)
   - [6.4 Field Agent Management (Admin Only)](#64-field-agent-management-admin-only)
   - [6.5 Form 1 — Home Survey API](#65-form-1--home-survey-api)
   - [6.6 House Multiple-Angle Photos API](#66-house-multiple-angle-photos-api)
   - [6.7 Form 2 — Family Members API](#67-form-2--family-members-api)
   - [6.8 Admin Full Survey Report API](#68-admin-full-survey-report-api)
7. [Dropdown / Choice Field Values](#7-dropdown--choice-field-values)
8. [Error Response Formats](#8-error-response-formats)
9. [Android Retrofit + OkHttp Code Examples (Kotlin)](#9-android-retrofit--okhttp-code-examples-kotlin)
10. [Project Structure](#10-project-structure)

---

## 1. Quick Start (Anaconda)

Open **Anaconda Prompt** (or PowerShell) in `d:\Espiritron\ward_house_servey`:

```powershell
# 1. Install dependencies (first time only)
C:\ProgramData\Anaconda3\python.exe -m pip install -r requirements.txt

# 2. Run database migrations (first time only)
C:\ProgramData\Anaconda3\python.exe manage.py migrate

# 3. Start server on 0.0.0.0:8000 (reachable by Browser + Android App on Wi-Fi)
C:\ProgramData\Anaconda3\python.exe manage.py runserver 0.0.0.0:8000
```

> **Important for Physical Android Devices:** Always run with `0.0.0.0:8000` (not just `runserver`) so phones on the same Wi-Fi network can reach your PC.

---

## 2. Default Test Credentials & URLs

| Interface | URL | Notes |
|-----------|-----|-------|
| **Web API Testing Dashboard** | `http://127.0.0.1:8000/` or `http://127.0.0.1:8000/dashboard/` | Calls the exact same REST APIs via `fetch()` — includes Home Form & Family Form testers |
| **Django Admin Panel** | `http://127.0.0.1:8000/admin/` | Database inspection |
| **API Base URL (Browser/PC)** | `http://127.0.0.1:8000/api/` | Local testing |
| **API Base URL (Android Emulator)** | `http://10.0.2.2:8000/api/` | Maps to host PC `127.0.0.1` |
| **API Base URL (Real Android Phone)** | `http://<YOUR_PC_WIFI_IP>:8000/api/` | Find PC IP via `ipconfig` (e.g., `http://192.168.1.10:8000/api/`) |

### Pre-configured Accounts

| Role | Username | Password | Login Endpoint |
|------|----------|----------|----------------|
| **Admin** | `admin` | `Admin@1234` | `POST /api/auth/admin/login/` |
| **Field Agent** | `agent01` | `Agent@1234` | `POST /api/auth/agent/login/` |

---

## 3. Android App Connection Setup

### Step 1: Permissions & Cleartext HTTP in `AndroidManifest.xml`
During local HTTP development (non-HTTPS), enable `usesCleartextTraffic` and permissions:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission android:name="android.permission.CAMERA" />

<application
    android:usesCleartextTraffic="true"
    ... >
</application>
```

### Step 2: Recommended Android Screen Flow
1. **Login Screen** → Choose **Admin Login** (`POST /api/auth/admin/login/`) or **Field Agent Login** (`POST /api/auth/agent/login/`).
2. Save `token` and `user.role` in `SharedPreferences` / `DataStore`.
3. **If `role == "field_agent"`:**
   - **My Uploaded Houses** → `GET /api/survey/houses/` (returns only this agent's houses).
   - **Form 1 (Home Form)** → `POST /api/survey/houses/` (`multipart/form-data` with text fields + multiple `photos` + `captions`). Extract `response.house.id`.
   - **Form 2 (Family Form)** → `POST /api/survey/houses/<house_id>/family/` (`application/json` — send a single member object or an array `[...]` of all family members).
4. **If `role == "admin"`:**
   - **Manage Field Agents** → `GET /api/auth/agents/`, `POST /api/auth/agent/register/`, `PATCH /api/auth/agents/<id>/toggle-active/`, `DELETE /api/auth/agents/<id>/`.
   - **View All Uploaded Houses** → `GET /api/survey/houses/` or `GET /api/survey/admin/report/`.

---

## 4. Authentication & Headers

- **Public Endpoints (Do NOT send `Authorization` header):**
  - `POST /api/auth/admin/register/`
  - `POST /api/auth/admin/login/`
  - `POST /api/auth/agent/login/`
  > **Note:** Do **not** attach an old/expired `Authorization` header to login/register requests; DRF validates any `Authorization` header before checking `AllowAny` and will return `401 Invalid token` if a stale token is sent.

- **Protected Endpoints (Required Header):**
  ```http
  Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
  ```
  *(Note the literal word `Token` followed by a single space and the token string — NOT `Bearer`.)*

---

## 5. Role Permissions Matrix

| Feature / Endpoint | Admin | Field Agent |
|--------------------|:-----:|:-----------:|
| Register Admin (`POST /api/auth/admin/register/`) | Public | Public |
| Register Field Agent (`POST /api/auth/agent/register/`) | ✅ | ❌ (`403`) |
| List / View Field Agents (`GET /api/auth/agents/`) | ✅ | ❌ (`403`) |
| Activate / Deactivate Agent (`PATCH .../toggle-active/`) | ✅ | ❌ (`403`) |
| Delete Field Agent (`DELETE /api/auth/agents/<id>/`) | ✅ | ❌ (`403`) |
| Submit Home Form (`POST /api/survey/houses/`) | ❌ (`403`) | ✅ |
| List Houses (`GET /api/survey/houses/`) | ✅ **Sees ALL** | ✅ **Sees OWN only** |
| View House Detail (`GET /api/survey/houses/<id>/`) | ✅ **Any house** | ✅ **Own house only** |
| Edit House (`PATCH /api/survey/houses/<id>/`) | ❌ (`403`) | ✅ **Own house only** |
| Delete House (`DELETE /api/survey/houses/<id>/`) | ✅ **Any house** | ❌ (`403`) |
| Upload Extra House Photos (`POST /api/survey/houses/<id>/photos/`) | ❌ (`403`) | ✅ **Own house only** |
| Delete Single Photo (`DELETE /api/survey/photos/<photo_id>/`) | ✅ **Any photo** | ✅ **Own house only** |
| Submit Family Form (`POST /api/survey/houses/<id>/family/`) | ❌ (`403`) | ✅ **Own house only** |
| Edit Family Member (`PATCH /api/survey/family/<member_id>/`) | ❌ (`403`) | ✅ **Own house only** |
| Delete Family Member (`DELETE /api/survey/family/<member_id>/`) | ✅ **Any member** | ✅ **Own house only** |
| Full Admin Report (`GET /api/survey/admin/report/`) | ✅ | ❌ (`403`) |

---

## 6. Complete API Reference (25 Endpoints)

### Summary Table

| # | Method | Endpoint | Auth | Content-Type | Purpose |
|---|--------|----------|------|--------------|---------|
| 1 | `POST` | `/api/auth/admin/register/` | Public | `application/json` | Register new Admin |
| 2 | `POST` | `/api/auth/admin/login/` | Public | `application/json` | Admin login |
| 3 | `POST` | `/api/auth/agent/register/` | Admin | `application/json` | Admin creates Field Agent |
| 4 | `POST` | `/api/auth/agent/login/` | Public | `application/json` | Field Agent login |
| 5 | `POST` | `/api/auth/logout/` | Any Token | `application/json` | Logout (deletes token) |
| 6 | `GET` | `/api/auth/profile/` | Any Token | — | Get logged-in user profile |
| 7 | `PATCH` | `/api/auth/profile/` | Any Token | `application/json` | Update logged-in user profile |
| 8 | `GET` | `/api/auth/agents/` | Admin | — | List all Field Agents + house counts |
| 9 | `GET` | `/api/auth/agents/<id>/` | Admin | — | Single Field Agent detail |
| 10 | `PATCH` | `/api/auth/agents/<id>/toggle-active/` | Admin | `application/json` | Activate / Deactivate agent (force logout) |
| 11 | `DELETE` | `/api/auth/agents/<id>/` | Admin | — | Permanently delete Field Agent |
| 12 | `POST` | `/api/survey/houses/` | Agent | `multipart/form-data` | **Form 1:** Submit Home Form + angle photos |
| 13 | `GET` | `/api/survey/houses/` | Any Token | — | List houses (Admin=all, Agent=own) |
| 14 | `GET` | `/api/survey/houses/<id>/` | Any Token | — | Full house detail + photos + family |
| 15 | `PATCH` | `/api/survey/houses/<id>/` | Agent | `application/json` | Update own house survey |
| 16 | `DELETE` | `/api/survey/houses/<id>/` | Admin | — | Delete house survey |
| 17 | `POST` | `/api/survey/houses/<id>/photos/` | Agent | `multipart/form-data` | Upload additional angle photos |
| 18 | `GET` | `/api/survey/houses/<id>/photos/` | Any Token | — | List all photos of a house |
| 19 | `DELETE` | `/api/survey/photos/<photo_id>/` | Any Token | — | Delete single photo (removes file on disk) |
| 20 | `POST` | `/api/survey/houses/<id>/family/` | Agent | `application/json` | **Form 2:** Add single or bulk family members |
| 21 | `GET` | `/api/survey/houses/<id>/family/` | Any Token | — | List all family members of a house |
| 22 | `GET` | `/api/survey/family/<member_id>/` | Any Token | — | Get single family member detail |
| 23 | `PATCH` | `/api/survey/family/<member_id>/` | Agent | `application/json` | Update family member |
| 24 | `DELETE` | `/api/survey/family/<member_id>/` | Any Token | — | Delete family member |
| 25 | `GET` | `/api/survey/admin/report/` | Admin | — | Full report of all houses, photos & families |

---

### 6.1 Admin Authentication

#### 1) Register Admin
- **URL:** `POST /api/auth/admin/register/`
- **Headers:** `Content-Type: application/json` (No `Authorization` header)
- **Request Body:**
```json
{
  "username": "admin2",
  "password": "Admin@1234",
  "confirm_password": "Admin@1234",
  "email": "admin2@wardsurvey.com",
  "phone": "9876543210",
  "first_name": "Super",
  "last_name": "Admin"
}
```
*(Required: `username`, `password` [min 6 chars], `confirm_password`. Optional: `email`, `phone`, `first_name`, `last_name`.)*

- **Success Response (`201 Created`):**
```json
{
  "message": "Admin registered successfully.",
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "username": "admin2",
    "email": "admin2@wardsurvey.com",
    "first_name": "Super",
    "last_name": "Admin",
    "phone": "9876543210",
    "role": "admin",
    "is_active": true,
    "created_at": "2026-11-03T10:30:00+05:30"
  }
}
```

---

#### 2) Admin Login
- **URL:** `POST /api/auth/admin/login/`
- **Headers:** `Content-Type: application/json` (No `Authorization` header)
- **Request Body:**
```json
{
  "username": "admin",
  "password": "Admin@1234"
}
```
- **Success Response (`200 OK`):**
```json
{
  "message": "Admin login successful.",
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@wardsurvey.com",
    "first_name": "Super",
    "last_name": "Admin",
    "phone": "9876543210",
    "role": "admin",
    "is_active": true,
    "created_at": "2026-11-02T08:00:00+05:30"
  }
}
```
- **Error if Field Agent tries Admin Login (`403 Forbidden`):**
```json
{
  "error": "This account is not an admin account."
}
```

---

### 6.2 Field Agent Authentication

#### 3) Register Field Agent *(Admin Token Required)*
- **URL:** `POST /api/auth/agent/register/`
- **Headers:**
  ```http
  Authorization: Token <admin_token>
  Content-Type: application/json
  ```
- **Request Body:**
```json
{
  "username": "agent02",
  "password": "Agent@1234",
  "confirm_password": "Agent@1234",
  "email": "agent02@wardsurvey.com",
  "phone": "9123456789",
  "first_name": "Ravi",
  "last_name": "Kumar"
}
```
- **Success Response (`201 Created`):**
```json
{
  "message": "Field agent registered successfully.",
  "token": "a5b1c3d7e9f2a4b6c8d0e1f3a5b7c9d0e2f4a6b8",
  "user": {
    "id": 3,
    "username": "agent02",
    "email": "agent02@wardsurvey.com",
    "first_name": "Ravi",
    "last_name": "Kumar",
    "phone": "9123456789",
    "role": "field_agent",
    "is_active": true,
    "created_at": "2026-11-03T11:00:00+05:30"
  }
}
```

---

#### 4) Field Agent Login
- **URL:** `POST /api/auth/agent/login/`
- **Headers:** `Content-Type: application/json` (No `Authorization` header)
- **Request Body:**
```json
{
  "username": "agent01",
  "password": "Agent@1234"
}
```
- **Success Response (`200 OK`):**
```json
{
  "message": "Field agent login successful.",
  "token": "a5b1c3d7e9f2a4b6c8d0e1f3a5b7c9d0e2f4a6b8",
  "user": {
    "id": 2,
    "username": "agent01",
    "email": "agent01@wardsurvey.com",
    "first_name": "Ravi",
    "last_name": "Kumar",
    "phone": "9876500001",
    "role": "field_agent",
    "is_active": true,
    "created_at": "2026-11-03T11:11:00+05:30"
  }
}
```
- **Error if Deactivated by Admin (`400 Bad Request`):**
```json
{
  "non_field_errors": [
    "Your account has been deactivated. Contact admin."
  ]
}
```

---

### 6.3 Logout & User Profile

#### 5) Logout (Admin or Field Agent)
- **URL:** `POST /api/auth/logout/`
- **Headers:** `Authorization: Token <your_token>`
- **Request Body:** None
- **Success Response (`200 OK`):**
```json
{
  "message": "Logged out successfully."
}
```

---

#### 6) Get My Profile
- **URL:** `GET /api/auth/profile/`
- **Headers:** `Authorization: Token <your_token>`
- **Success Response (`200 OK`):**
```json
{
  "id": 2,
  "username": "agent01",
  "email": "agent01@wardsurvey.com",
  "first_name": "Ravi",
  "last_name": "Kumar",
  "phone": "9876500001",
  "role": "field_agent",
  "is_active": true,
  "created_at": "2026-11-03T11:11:00+05:30"
}
```

---

#### 7) Update My Profile
- **URL:** `PATCH /api/auth/profile/`
- **Headers:**
  ```http
  Authorization: Token <your_token>
  Content-Type: application/json
  ```
- **Request Body (Partial JSON):**
```json
{
  "first_name": "Ravi",
  "last_name": "Gowda",
  "phone": "9988776655",
  "email": "ravi@wardsurvey.com"
}
```
- **Success Response (`200 OK`):** Returns the updated user profile object (same structure as `GET /api/auth/profile/`).

---

### 6.4 Field Agent Management *(Admin Only)*

#### 8) List All Field Agents
- **URL:** `GET /api/auth/agents/`
- **Headers:** `Authorization: Token <admin_token>`
- **Success Response (`200 OK`):**
```json
{
  "count": 1,
  "agents": [
    {
      "id": 2,
      "username": "agent01",
      "email": "agent01@wardsurvey.com",
      "first_name": "Ravi",
      "last_name": "Kumar",
      "phone": "9876500001",
      "role": "field_agent",
      "is_active": true,
      "created_at": "2026-11-03T11:11:00+05:30",
      "total_houses": 4
    }
  ]
}
```

---

#### 9) Get Single Field Agent Detail
- **URL:** `GET /api/auth/agents/<id>/` (e.g., `/api/auth/agents/2/`)
- **Headers:** `Authorization: Token <admin_token>`
- **Success Response (`200 OK`):**
```json
{
  "id": 2,
  "username": "agent01",
  "email": "agent01@wardsurvey.com",
  "first_name": "Ravi",
  "last_name": "Kumar",
  "phone": "9876500001",
  "role": "field_agent",
  "is_active": true,
  "created_at": "2026-11-03T11:11:00+05:30",
  "total_houses": 4
}
```

---

#### 10) Activate / Deactivate Field Agent (Force Logout)
- **URL:** `PATCH /api/auth/agents/<id>/toggle-active/` (e.g., `/api/auth/agents/2/toggle-active/`)
- **Headers:** `Authorization: Token <admin_token>`
- **Request Body:** None (toggles `is_active` between `true` and `false`)
- **Success Response (`200 OK`):**
```json
{
  "message": "Field agent deactivated successfully.",
  "is_active": false,
  "agent_id": 2,
  "username": "agent01"
}
```
> **Note:** Deactivating an agent **immediately deletes their auth token** on the server. Their very next Android API request will return `401 Unauthorized` (`{"detail": "Invalid token."}`), forcing immediate logout in the app. Calling `toggle-active` again reactivates the account (`"is_active": true`).

---

#### 11) Delete Field Agent
- **URL:** `DELETE /api/auth/agents/<id>/` (e.g., `/api/auth/agents/2/`)
- **Headers:** `Authorization: Token <admin_token>`
- **Success Response:** `204 No Content` (empty body — check `response.code() == 204` or `response.isSuccessful` in Retrofit).
> **Warning:** Permanently deletes the agent and cascades to their uploaded surveys. Use `toggle-active` if you want to disable access while keeping their uploaded survey records.

---

### 6.5 Form 1 — Home Survey API

#### 12) Submit Home Form with Multiple Angle Photos *(Field Agent Only)*
- **URL:** `POST /api/survey/houses/`
- **Headers:**
  ```http
  Authorization: Token <agent_token>
  Content-Type: multipart/form-data
  ```
- **Multipart Form Fields:**

| Key | Type | Required | Description / Example |
|-----|------|:--------:|-----------------------|
| `house_number` | String | ✅ | `"HN-104/A"` |
| `ward_no` | String | ✅ | `"Ward-05"` |
| `address` | String | ✅ | `"104, 4th Cross, Gandhi Nagar"` |
| `landmark` | String | ❌ | `"Near Govt Primary School"` |
| `owner_name` | String | ✅ | `"Ramesh Gowda"` |
| `ownership` | Choice | ✅ | `own` \| `rent` \| `lease` \| `others` |
| `house_type` | Choice | ✅ | `permanent` \| `semi_permanent` \| `temporary` |
| `roof_type` | Choice | ✅ | `rcc` \| `tiles` \| `asbestos` \| `thatched` \| `others` |
| `water_source` | Choice | ✅ | `tap` \| `well` \| `borewell` \| `river` \| `others` |
| `electricity` | Choice | ✅ | `yes` \| `no` \| `solar` |
| `toilet` | Choice | ✅ | `yes` \| `no` \| `shared` |
| `ration_card_type` | Choice | ✅ | `apl` \| `bpl` \| `aay` \| `none` |
| `latitude` | Decimal String | ❌ | `"12.971598"` (up to 6 decimal places) |
| `longitude` | Decimal String | ❌ | `"77.594566"` (up to 6 decimal places) |
| `remarks` | String | ❌ | `"Two-storey residential house"` |
| `photos` | File (repeat key) | ❌ | Multiple image files (`photos`, `photos`, `photos`...) |
| `captions` | String (repeat key) | ❌ | Matching angle captions (`"Front View"`, `"Back View"`, `"Left Side"`...) |

- **Success Response (`201 Created`):**
```json
{
  "message": "House survey submitted successfully.",
  "house": {
    "id": 1,
    "field_agent": 2,
    "field_agent_name": "agent01",
    "house_number": "HN-104/A",
    "ward_no": "Ward-05",
    "address": "104, 4th Cross, Gandhi Nagar",
    "landmark": "Near Govt Primary School",
    "owner_name": "Ramesh Gowda",
    "ownership": "own",
    "ownership_display": "Own",
    "house_type": "permanent",
    "house_type_display": "Permanent",
    "roof_type": "rcc",
    "roof_type_display": "RCC",
    "water_source": "tap",
    "water_source_display": "Tap Water",
    "electricity": "yes",
    "electricity_display": "Yes",
    "toilet": "yes",
    "toilet_display": "Yes (Private)",
    "ration_card_type": "bpl",
    "ration_card_type_display": "BPL",
    "latitude": "12.971598",
    "longitude": "77.594566",
    "remarks": "Two-storey residential house",
    "photos": [
      {
        "id": 1,
        "photo": "/media/house_photos/1/front_view.jpg",
        "photo_url": "http://192.168.1.10:8000/media/house_photos/1/front_view.jpg",
        "caption": "Front View",
        "uploaded_at": "2026-11-03T11:30:00+05:30"
      },
      {
        "id": 2,
        "photo": "/media/house_photos/1/left_side.jpg",
        "photo_url": "http://192.168.1.10:8000/media/house_photos/1/left_side.jpg",
        "caption": "Left Side",
        "uploaded_at": "2026-11-03T11:30:00+05:30"
      }
    ],
    "family_members": [],
    "created_at": "2026-11-03T11:30:00+05:30",
    "updated_at": "2026-11-03T11:30:00+05:30"
  }
}
```
> **Android Tip:** Read `response.house.id` (e.g. `1`) and pass it to the Family Form screen (`POST /api/survey/houses/1/family/`). Use `photo_url` directly with **Glide** or **Coil** to load images.

---

#### 13) List Houses (Role-Filtered)
- **URL:** `GET /api/survey/houses/`
- **Headers:** `Authorization: Token <token>`
- **Behavior:**
  - **Admin Token** → returns **all houses** uploaded by **all field agents**.
  - **Field Agent Token** → returns **only houses uploaded by that field agent**.
- **Success Response (`200 OK`):**
```json
{
  "count": 1,
  "houses": [
    {
      "id": 1,
      "house_number": "HN-104/A",
      "ward_no": "Ward-05",
      "address": "104, 4th Cross, Gandhi Nagar",
      "owner_name": "Ramesh Gowda",
      "ownership": "own",
      "house_type": "permanent",
      "field_agent_name": "agent01",
      "total_photos": 2,
      "total_family_members": 3,
      "created_at": "2026-11-03T11:30:00+05:30"
    }
  ]
}
```

---

#### 14) Get Single House Detail (with Nested Photos & Family Members)
- **URL:** `GET /api/survey/houses/<id>/` (e.g., `/api/survey/houses/1/`)
- **Headers:** `Authorization: Token <token>`
- **Success Response (`200 OK`):**
```json
{
  "id": 1,
  "field_agent": 2,
  "field_agent_name": "agent01",
  "house_number": "HN-104/A",
  "ward_no": "Ward-05",
  "address": "104, 4th Cross, Gandhi Nagar",
  "landmark": "Near Govt Primary School",
  "owner_name": "Ramesh Gowda",
  "ownership": "own",
  "ownership_display": "Own",
  "house_type": "permanent",
  "house_type_display": "Permanent",
  "roof_type": "rcc",
  "roof_type_display": "RCC",
  "water_source": "tap",
  "water_source_display": "Tap Water",
  "electricity": "yes",
  "electricity_display": "Yes",
  "toilet": "yes",
  "toilet_display": "Yes (Private)",
  "ration_card_type": "bpl",
  "ration_card_type_display": "BPL",
  "latitude": "12.971598",
  "longitude": "77.594566",
  "remarks": "Two-storey residential house",
  "photos": [
    {
      "id": 1,
      "photo": "/media/house_photos/1/front_view.jpg",
      "photo_url": "http://192.168.1.10:8000/media/house_photos/1/front_view.jpg",
      "caption": "Front View",
      "uploaded_at": "2026-11-03T11:30:00+05:30"
    }
  ],
  "family_members": [
    {
      "id": 1,
      "house": 1,
      "name": "Ramesh Gowda",
      "relationship": "head",
      "relationship_display": "Head of Family",
      "gender": "male",
      "gender_display": "Male",
      "dob": "1982-05-14",
      "age": 44,
      "education": "PUC / 12th",
      "occupation": "Agriculture",
      "phone": "9876543210"
    }
  ],
  "created_at": "2026-11-03T11:30:00+05:30",
  "updated_at": "2026-11-03T11:30:00+05:30"
}
```

---

#### 15) Update House Survey *(Field Agent — Own House Only)*
- **URL:** `PATCH /api/survey/houses/<id>/`
- **Headers:**
  ```http
  Authorization: Token <agent_token>
  Content-Type: application/json
  ```
- **Request Body (Send only the fields to update):**
```json
{
  "remarks": "Updated remarks after second visit",
  "electricity": "solar"
}
```
- **Success Response (`200 OK`):**
```json
{
  "message": "House survey updated successfully.",
  "house": {
    "id": 1,
    "house_number": "HN-104/A",
    "...": "full house object (same as GET /api/survey/houses/<id>/)"
  }
}
```

---

#### 16) Delete House Survey *(Admin Only)*
- **URL:** `DELETE /api/survey/houses/<id>/`
- **Headers:** `Authorization: Token <admin_token>`
- **Success Response:** `204 No Content`

---

### 6.6 House Multiple-Angle Photos API

All photos are stored inside the project under `media/house_photos/<house_id>/<filename>`.

#### 17) Upload Additional Angle Photos *(Field Agent — Own House Only)*
- **URL:** `POST /api/survey/houses/<id>/photos/` (e.g., `/api/survey/houses/1/photos/`)
- **Headers:**
  ```http
  Authorization: Token <agent_token>
  Content-Type: multipart/form-data
  ```
- **Multipart Form Fields:**
  - `photos`: One or more image files (`JPG`, `PNG`, `WEBP`)
  - `captions`: Optional repeated string parts matching each photo (`"Back View"`, `"Roof View"`)
- **Success Response (`201 Created`):**
```json
{
  "message": "2 photo(s) uploaded successfully.",
  "photos": [
    {
      "id": 3,
      "photo": "/media/house_photos/1/back_view.jpg",
      "photo_url": "http://192.168.1.10:8000/media/house_photos/1/back_view.jpg",
      "caption": "Back View",
      "uploaded_at": "2026-11-03T11:35:00+05:30"
    },
    {
      "id": 4,
      "photo": "/media/house_photos/1/roof_view.jpg",
      "photo_url": "http://192.168.1.10:8000/media/house_photos/1/roof_view.jpg",
      "caption": "Roof View",
      "uploaded_at": "2026-11-03T11:35:00+05:30"
    }
  ]
}
```

---

#### 18) List Photos of a House
- **URL:** `GET /api/survey/houses/<id>/photos/`
- **Headers:** `Authorization: Token <token>`
- **Success Response (`200 OK`):**
```json
{
  "count": 4,
  "photos": [
    {
      "id": 1,
      "photo": "/media/house_photos/1/front_view.jpg",
      "photo_url": "http://192.168.1.10:8000/media/house_photos/1/front_view.jpg",
      "caption": "Front View",
      "uploaded_at": "2026-11-03T11:30:00+05:30"
    }
  ]
}
```

---

#### 19) Delete Single Photo
- **URL:** `DELETE /api/survey/photos/<photo_id>/` (e.g., `/api/survey/photos/3/`)
- **Headers:** `Authorization: Token <token>` (Admin can delete any; Field Agent can delete own house photos)
- **Success Response:** `204 No Content` (Deletes both database record and image file on disk).

---

### 6.7 Form 2 — Family Members API

#### 20) Submit Family Form *(Field Agent — Own House Only)*
- **URL:** `POST /api/survey/houses/<house_id>/family/` (e.g., `/api/survey/houses/1/family/`)
- **Headers:**
  ```http
  Authorization: Token <agent_token>
  Content-Type: application/json
  ```

| Field | Type | Required | Format / Choices |
|-------|------|:--------:|------------------|
| `name` | String | ✅ | `"Ramesh Gowda"` |
| `relationship` | Choice | ✅ | `head` \| `spouse` \| `son` \| `daughter` \| `father` \| `mother` \| `others` |
| `gender` | Choice | ✅ | `male` \| `female` \| `other` |
| `dob` | Date String | ✅ | `"YYYY-MM-DD"` (e.g. `"1982-05-14"`) |
| `age` | Integer | ✅ | `44` |
| `education` | String | ❌ | `"PUC / 12th"` |
| `occupation` | String | ❌ | `"Agriculture"` |
| `phone` | String | ❌ | `"9876543210"` |

##### Mode A — Add Multiple Family Members at Once (Recommended for Android Family Form)
Send a **JSON Array** `[...]` — even for 1 member (`[member1]`), sending an array guarantees `family_members` in the response is **always a JSON Array**!

- **Request Body (JSON Array):**
```json
[
  {
    "name": "Ramesh Gowda",
    "relationship": "head",
    "gender": "male",
    "dob": "1982-05-14",
    "age": 44,
    "education": "PUC / 12th",
    "occupation": "Agriculture",
    "phone": "9876543210"
  },
  {
    "name": "Savitha Gowda",
    "relationship": "spouse",
    "gender": "female",
    "dob": "1986-08-22",
    "age": 40,
    "education": "B.A.",
    "occupation": "Tailor",
    "phone": "9876543211"
  }
]
```
- **Success Response (`201 Created` — `family_members` is an Array):**
```json
{
  "message": "Family member(s) added successfully.",
  "family_members": [
    {
      "id": 1,
      "house": 1,
      "name": "Ramesh Gowda",
      "relationship": "head",
      "relationship_display": "Head of Family",
      "gender": "male",
      "gender_display": "Male",
      "dob": "1982-05-14",
      "age": 44,
      "education": "PUC / 12th",
      "occupation": "Agriculture",
      "phone": "9876543210"
    },
    {
      "id": 2,
      "house": 1,
      "name": "Savitha Gowda",
      "relationship": "spouse",
      "relationship_display": "Spouse",
      "gender": "female",
      "gender_display": "Female",
      "dob": "1986-08-22",
      "age": 40,
      "education": "B.A.",
      "occupation": "Tailor",
      "phone": "9876543211"
    }
  ]
}
```

##### Mode B — Add Single Family Member Object
- **Request Body (Single JSON Object):**
```json
{
  "name": "Kiran Gowda",
  "relationship": "son",
  "gender": "male",
  "dob": "2008-11-10",
  "age": 17,
  "education": "11th Std",
  "occupation": "Student",
  "phone": ""
}
```
- **Success Response (`201 Created` — `family_members` is a Single Object):**
```json
{
  "message": "Family member(s) added successfully.",
  "family_members": {
    "id": 3,
    "house": 1,
    "name": "Kiran Gowda",
    "relationship": "son",
    "relationship_display": "Son",
    "gender": "male",
    "gender_display": "Male",
    "dob": "2008-11-10",
    "age": 17,
    "education": "11th Std",
    "occupation": "Student",
    "phone": ""
  }
}
```

---

#### 21) List Family Members of a House
- **URL:** `GET /api/survey/houses/<house_id>/family/`
- **Headers:** `Authorization: Token <token>`
- **Success Response (`200 OK`):**
```json
{
  "count": 3,
  "family_members": [
    {
      "id": 1,
      "house": 1,
      "name": "Ramesh Gowda",
      "relationship": "head",
      "relationship_display": "Head of Family",
      "gender": "male",
      "gender_display": "Male",
      "dob": "1982-05-14",
      "age": 44,
      "education": "PUC / 12th",
      "occupation": "Agriculture",
      "phone": "9876543210"
    }
  ]
}
```

---

#### 22) Get Single Family Member Detail
- **URL:** `GET /api/survey/family/<member_id>/` (e.g., `/api/survey/family/1/`)
- **Headers:** `Authorization: Token <token>`
- **Success Response (`200 OK`):**
```json
{
  "id": 1,
  "house": 1,
  "name": "Ramesh Gowda",
  "relationship": "head",
  "relationship_display": "Head of Family",
  "gender": "male",
  "gender_display": "Male",
  "dob": "1982-05-14",
  "age": 44,
  "education": "PUC / 12th",
  "occupation": "Agriculture",
  "phone": "9876543210"
}
```

---

#### 23) Update Family Member *(Field Agent — Own House Only)*
- **URL:** `PATCH /api/survey/family/<member_id>/` (e.g., `/api/survey/family/1/`)
- **Headers:**
  ```http
  Authorization: Token <agent_token>
  Content-Type: application/json
  ```
- **Request Body (Partial JSON):**
```json
{
  "occupation": "Dairy Farming",
  "phone": "9876500099"
}
```
- **Success Response (`200 OK`):**
```json
{
  "message": "Family member updated.",
  "family_member": {
    "id": 1,
    "house": 1,
    "name": "Ramesh Gowda",
    "relationship": "head",
    "relationship_display": "Head of Family",
    "gender": "male",
    "gender_display": "Male",
    "dob": "1982-05-14",
    "age": 44,
    "education": "PUC / 12th",
    "occupation": "Dairy Farming",
    "phone": "9876500099"
  }
}
```

---

#### 24) Delete Family Member
- **URL:** `DELETE /api/survey/family/<member_id>/`
- **Headers:** `Authorization: Token <token>` (Admin = any; Field Agent = own house only)
- **Success Response:** `204 No Content`

---

### 6.8 Admin Full Survey Report API

#### 25) Full Admin Report (All Houses + Photos + Family Members)
- **URL:** `GET /api/survey/admin/report/`
- **Headers:** `Authorization: Token <admin_token>`
- **Success Response (`200 OK`):**
```json
{
  "total_houses": 1,
  "houses": [
    {
      "id": 1,
      "field_agent": 2,
      "field_agent_name": "agent01",
      "house_number": "HN-104/A",
      "ward_no": "Ward-05",
      "address": "104, 4th Cross, Gandhi Nagar",
      "landmark": "Near Govt Primary School",
      "owner_name": "Ramesh Gowda",
      "ownership": "own",
      "ownership_display": "Own",
      "house_type": "permanent",
      "house_type_display": "Permanent",
      "roof_type": "rcc",
      "roof_type_display": "RCC",
      "water_source": "tap",
      "water_source_display": "Tap Water",
      "electricity": "yes",
      "electricity_display": "Yes",
      "toilet": "yes",
      "toilet_display": "Yes (Private)",
      "ration_card_type": "bpl",
      "ration_card_type_display": "BPL",
      "latitude": "12.971598",
      "longitude": "77.594566",
      "remarks": "Two-storey residential house",
      "photos": [
        {
          "id": 1,
          "photo": "/media/house_photos/1/front_view.jpg",
          "photo_url": "http://192.168.1.10:8000/media/house_photos/1/front_view.jpg",
          "caption": "Front View",
          "uploaded_at": "2026-11-03T11:30:00+05:30"
        }
      ],
      "family_members": [
        {
          "id": 1,
          "house": 1,
          "name": "Ramesh Gowda",
          "relationship": "head",
          "relationship_display": "Head of Family",
          "gender": "male",
          "gender_display": "Male",
          "dob": "1982-05-14",
          "age": 44,
          "education": "PUC / 12th",
          "occupation": "Agriculture",
          "phone": "9876543210"
        }
      ],
      "created_at": "2026-11-03T11:30:00+05:30",
      "updated_at": "2026-11-03T11:30:00+05:30"
    }
  ]
}
```

---

## 7. Dropdown / Choice Field Values

Send the **exact lowercase `API Value`** when submitting forms; display the `Display Label` in Android Spinners / Dropdowns.

### Home Form Choices

| Field | API Value | Display Label |
|-------|-----------|---------------|
| `ownership` | `own`, `rent`, `lease`, `others` | Own, Rent, Lease, Others |
| `house_type` | `permanent`, `semi_permanent`, `temporary` | Permanent, Semi-Permanent, Temporary |
| `roof_type` | `rcc`, `tiles`, `asbestos`, `thatched`, `others` | RCC, Tiles, Asbestos, Thatched, Others |
| `water_source` | `tap`, `well`, `borewell`, `river`, `others` | Tap Water, Well, Borewell, River, Others |
| `electricity` | `yes`, `no`, `solar` | Yes, No, Solar |
| `toilet` | `yes`, `no`, `shared` | Yes (Private), No, Shared |
| `ration_card_type` | `apl`, `bpl`, `aay`, `none` | APL, BPL, AAY (Antyodaya), None |

### Family Form Choices

| Field | API Value | Display Label |
|-------|-----------|---------------|
| `relationship` | `head`, `spouse`, `son`, `daughter`, `father`, `mother`, `others` | Head of Family, Spouse, Son, Daughter, Father, Mother, Others |
| `gender` | `male`, `female`, `other` | Male, Female, Other |

---

## 8. Error Response Formats

| HTTP Status | Scenario | Example Response Body | Android Handling |
|-------------|----------|-----------------------|------------------|
| `400 Bad Request` | Invalid login / deactivated user | `{"non_field_errors": ["Invalid username or password."]}` or `{"non_field_errors": ["Your account has been deactivated. Contact admin."]}` | Show message toast/error |
| `400 Bad Request` | Missing/invalid form field | `{"house_number": ["This field is required."], "ownership": ["\"xyz\" is not a valid choice."]}` | Highlight invalid input fields |
| `401 Unauthorized` | Missing, logged-out, or deactivated token | `{"detail": "Authentication credentials were not provided."}` or `{"detail": "Invalid token."}` | Clear saved token & navigate to Login |
| `403 Forbidden` | Wrong role | `{"error": "Only field agents can submit house surveys."}` or `{"detail": "Access restricted to admin users only."}` | Restrict UI by `user.role` |
| `404 Not Found` | Invalid ID or another agent's house | `{"error": "House survey not found."}` | Refresh list |

---

## 9. Android Retrofit + OkHttp Code Examples (Kotlin)

### 1) Auth Interceptor (Skips public login/register routes automatically)
```kotlin
class AuthInterceptor(private val tokenProvider: () -> String?) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val original = chain.request()
        val path = original.url.encodedPath
        val isPublicAuth = path.endsWith("/admin/login/") ||
                           path.endsWith("/admin/register/") ||
                           path.endsWith("/agent/login/")

        val token = tokenProvider()
        val request = if (!isPublicAuth && !token.isNullOrBlank()) {
            original.newBuilder()
                .header("Authorization", "Token $token")
                .build()
        } else {
            original
        }
        return chain.proceed(request)
    }
}
```

### 2) Retrofit API Service Interface
```kotlin
interface WardSurveyApi {

    // ── Auth ──
    @POST("api/auth/admin/login/")
    suspend fun adminLogin(@Body body: LoginRequest): AuthResponse

    @POST("api/auth/agent/login/")
    suspend fun agentLogin(@Body body: LoginRequest): AuthResponse

    @POST("api/auth/agent/register/")
    suspend fun registerAgent(@Body body: RegisterUserRequest): AuthResponse

    @POST("api/auth/logout/")
    suspend fun logout(): MessageResponse

    // ── Admin: Manage Field Agents ──
    @GET("api/auth/agents/")
    suspend fun listAgents(): AgentListResponse

    @PATCH("api/auth/agents/{id}/toggle-active/")
    suspend fun toggleAgentActive(@Path("id") agentId: Int): ToggleAgentResponse

    @DELETE("api/auth/agents/{id}/")
    suspend fun deleteAgent(@Path("id") agentId: Int): retrofit2.Response<Unit>

    // ── Form 1: Home Survey (Multipart with Multi-Angle Photos) ──
    @Multipart
    @POST("api/survey/houses/")
    suspend fun submitHomeForm(
        @PartMap fields: Map<String, @JvmSuppressWildcards RequestBody>,
        @Part photos: List<MultipartBody.Part>,
        @Part captions: List<MultipartBody.Part>
    ): HouseSubmitResponse

    @GET("api/survey/houses/")
    suspend fun listHouses(): HouseListResponse

    @GET("api/survey/houses/{id}/")
    suspend fun getHouseDetail(@Path("id") houseId: Int): HouseDetail

    @DELETE("api/survey/houses/{id}/")
    suspend fun deleteHouse(@Path("id") houseId: Int): retrofit2.Response<Unit>

    // ── Form 2: Family Members (Send List<FamilyMemberRequest> for consistent array response) ──
    @POST("api/survey/houses/{id}/family/")
    suspend fun submitFamilyForm(
        @Path("id") houseId: Int,
        @Body members: List<FamilyMemberRequest>
    ): FamilyBulkSubmitResponse

    @GET("api/survey/houses/{id}/family/")
    suspend fun listFamilyMembers(@Path("id") houseId: Int): FamilyListResponse

    // ── Admin Full Report ──
    @GET("api/survey/admin/report/")
    suspend fun getAdminReport(): AdminReportResponse
}
```

### 3) Building Multipart Request for Form 1 (Home Form + Multi-Angle Photos)
```kotlin
fun String.toTextBody(): RequestBody =
    this.toRequestBody("text/plain".toMediaTypeOrNull())

suspend fun uploadHouseSurvey(api: WardSurveyApi, imageFiles: List<Pair<File, String>>) {
    val fields = mutableMapOf(
        "house_number"     to "HN-104/A".toTextBody(),
        "ward_no"          to "Ward-05".toTextBody(),
        "address"          to "104, 4th Cross, Gandhi Nagar".toTextBody(),
        "landmark"         to "Near Govt Primary School".toTextBody(),
        "owner_name"       to "Ramesh Gowda".toTextBody(),
        "ownership"        to "own".toTextBody(),
        "house_type"       to "permanent".toTextBody(),
        "roof_type"        to "rcc".toTextBody(),
        "water_source"     to "tap".toTextBody(),
        "electricity"      to "yes".toTextBody(),
        "toilet"           to "yes".toTextBody(),
        "ration_card_type" to "bpl".toTextBody(),
        "latitude"         to "12.971598".toTextBody(),
        "longitude"        to "77.594566".toTextBody(),
        "remarks"          to "Good condition".toTextBody()
    )

    val photoParts = imageFiles.map { (file, _) ->
        val reqFile = file.asRequestBody("image/*".toMediaTypeOrNull())
        MultipartBody.Part.createFormData("photos", file.name, reqFile)
    }

    val captionParts = imageFiles.map { (_, angleCaption) ->
        MultipartBody.Part.createFormData("captions", angleCaption)
    }

    val res = api.submitHomeForm(fields, photoParts, captionParts)
    val createdHouseId = res.house.id // Pass this ID to Family Form!
}
```

---

## 10. Project Structure

```text
ward_house_servey/
├── manage.py
├── requirements.txt
├── db.sqlite3                          # SQLite database
├── README.md                           # Full API & Android Integration Guide
├── templates/
│   └── dashboard/
│       └── index.html                  # Built-in Web API Testing UI (/ & /dashboard/)
├── media/
│   └── house_photos/
│       └── <house_id>/                 # Multi-angle house images stored per house
├── ward_house_survey/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                           # Admin & Field Agent Auth + Agent Management
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
└── survey/                             # Home Form, Multi-Angle Photos & Family Form APIs
    ├── models.py
    ├── serializers.py
    ├── urls.py
    └── views.py
```
