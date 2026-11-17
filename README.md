# Haritha Kerala Household Survey — Postman & Android API Guide

Complete backend REST API documentation for the **Haritha Kerala Household Survey** application (Django + Django REST Framework + SQLite), with step-by-step **Postman instructions**, **example request values**, and **exact JSON responses** for every API.

---

## Table of Contents

1. [Server Setup & Base URLs](#1-server-setup--base-urls)
2. [How to Configure Postman (Important)](#2-how-to-configure-postman-important)
3. [Authentication APIs (Postman Examples & Responses)](#3-authentication-apis-postman-examples--responses)
   - [3.1 Register Admin](#31-register-admin)
   - [3.2 Admin Login](#32-admin-login)
   - [3.3 Register Field Agent (Admin Only)](#33-register-field-agent-admin-only)
   - [3.4 Field Agent Login](#34-field-agent-login)
   - [3.5 Logout](#35-logout)
   - [3.6 View & Update My Profile](#36-view--update-my-profile)
4. [Field Agent Management APIs (Admin Only)](#4-field-agent-management-apis-admin-only)
   - [4.1 List All Field Agents](#41-list-all-field-agents)
   - [4.2 Get Single Field Agent Detail](#42-get-single-field-agent-detail)
   - [4.3 Activate / Deactivate Field Agent (Force Logout)](#43-activate--deactivate-field-agent-force-logout)
   - [4.4 Delete Field Agent](#44-delete-field-agent)
5. [8-Section Haritha Kerala Survey API (Single Submit)](#5-8-section-haritha-kerala-survey-api-single-submit)
   - [5.1 Method A — Submit in Postman as Raw JSON (with URL or Base64 Image)](#51-method-a--submit-in-postman-as-raw-json-with-url-or-base64-image)
   - [5.2 Method B — Submit in Postman as `form-data` (JSON + Image Files in One Call)](#52-method-b--submit-in-postman-as-form-data-json--image-files-in-one-call)
   - [5.3 Method C — Upload Photo Standalone (`POST /api/survey/upload-photo/`)](#53-method-c--upload-photo-standalone-post-apisurveyupload-photo)
6. [List, View, Update & Delete Survey APIs](#6-list-view-update--delete-survey-apis)
   - [6.1 List Surveys (Admin = All, Field Agent = Own Only)](#61-list-surveys-admin--all-field-agent--own-only)
   - [6.2 Get Single Survey Detail](#62-get-single-survey-detail)
   - [6.3 Update Survey (Field Agent Only)](#63-update-survey-field-agent-only)
   - [6.4 Delete Survey (Admin Only)](#64-delete-survey-admin-only)
7. [Family Members APIs](#7-family-members-apis)
8. [House Photos APIs](#8-house-photos-apis)
9. [Admin Full Report API](#9-admin-full-report-api)
10. [Common Error Responses](#10-common-error-responses)

---

## 1. Server Setup & Base URLs

### Run Locally (Anaconda Prompt)
```powershell
C:\ProgramData\Anaconda3\python.exe manage.py migrate
C:\ProgramData\Anaconda3\python.exe manage.py runserver 0.0.0.0:8000
```

### Base URLs

| Environment | Base URL |
|-------------|----------|
| **Local PC / Postman** | `http://127.0.0.1:8000` |
| **Render Cloud Deployment** | `https://ward-house-survey.onrender.com` |
| **Android Emulator** | `http://10.0.2.2:8000` |
| **Web Testing Dashboard** | `http://127.0.0.1:8000/dashboard/` (or `https://ward-house-survey.onrender.com/dashboard/`) |

*(In all Postman examples below, you can use either `http://127.0.0.1:8000` or `https://ward-house-survey.onrender.com` as `<BASE_URL>`.)*

### Pre-Created Test Accounts

| Role | Username | Password |
|------|----------|----------|
| **Admin** | `admin` | `Admin@1234` |
| **Field Agent** | `agent01` | `Agent@1234` |

---

## 2. How to Configure Postman (Important)

### Rule 1: How to Pass the Auth Token in Postman
Django REST Framework uses `Token <your_token>` (NOT `Bearer <your_token>`).
In Postman, for any protected API:
1. Click the **Authorization** tab -> select **No Auth**.
2. Click the **Headers** tab and add:

| Key | Value |
|-----|-------|
| `Authorization` | `Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b` |

> **Warning:** On **Public** endpoints (`admin/login/`, `admin/register/`, `agent/login/`), **uncheck** or remove the `Authorization` header in Postman so an old/expired token is not sent.

### Rule 2: How to Send JSON in Postman
1. Go to the **Body** tab.
2. Select **raw**.
3. Change the dropdown on the right from `Text` to **JSON**.
4. Paste the JSON payload and click **Send**.

### Rule 3: How to Send Image Files (`form-data`) in Postman
1. Go to the **Body** tab.
2. Select **form-data**.
3. Hover over the **Key** column, change the right-side dropdown from `Text` to **File**, and click **Select Files** to pick an image from your computer.

---

## 3. Authentication APIs (Postman Examples & Responses)

### 3.1 Register Admin
- **Method:** `POST`
- **URL:** `<BASE_URL>/api/auth/admin/register/`
- **Postman Headers:**
  - `Content-Type`: `application/json` *(No `Authorization` header)*
- **Postman Body (`raw` → `JSON`):**
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
- **Return from API (`201 Created`):**
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
    "created_at": "2026-11-17T20:30:00+05:30"
  }
}
```

---

### 3.2 Admin Login
- **Method:** `POST`
- **URL:** `<BASE_URL>/api/auth/admin/login/`
- **Postman Headers:**
  - `Content-Type`: `application/json` *(No `Authorization` header)*
- **Postman Body (`raw` → `JSON`):**
```json
{
  "username": "admin",
  "password": "Admin@1234"
}
```
- **Return from API (`200 OK`):**
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

---

### 3.3 Register Field Agent *(Admin Only)*
- **Method:** `POST`
- **URL:** `<BASE_URL>/api/auth/agent/register/`
- **Postman Headers:**
  - `Authorization`: `Token <ADMIN_TOKEN>`
  - `Content-Type`: `application/json`
- **Postman Body (`raw` → `JSON`):**
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
- **Return from API (`201 Created`):**
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
    "created_at": "2026-11-17T20:35:00+05:30"
  }
}
```

---

### 3.4 Field Agent Login
- **Method:** `POST`
- **URL:** `<BASE_URL>/api/auth/agent/login/`
- **Postman Headers:**
  - `Content-Type`: `application/json` *(No `Authorization` header)*
- **Postman Body (`raw` → `JSON`):**
```json
{
  "username": "agent01",
  "password": "Agent@1234"
}
```
- **Return from API (`200 OK`):**
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

---

### 3.5 Logout
- **Method:** `POST`
- **URL:** `<BASE_URL>/api/auth/logout/`
- **Postman Headers:**
  - `Authorization`: `Token <YOUR_TOKEN>`
- **Postman Body:** None
- **Return from API (`200 OK`):**
```json
{
  "message": "Logged out successfully."
}
```

---

### 3.6 View & Update My Profile
- **View Profile:** `GET <BASE_URL>/api/auth/profile/`
- **Update Profile:** `PATCH <BASE_URL>/api/auth/profile/`
- **Postman Headers:**
  - `Authorization`: `Token <YOUR_TOKEN>`
  - `Content-Type`: `application/json` *(for `PATCH`)*
- **Postman Body for `PATCH` (`raw` → `JSON`):**
```json
{
  "first_name": "Ravi",
  "last_name": "Kumar",
  "phone": "9876500001"
}
```
- **Return from API (`200 OK`):**
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

## 4. Field Agent Management APIs *(Admin Only)*

### 4.1 List All Field Agents
- **Method:** `GET`
- **URL:** `<BASE_URL>/api/auth/agents/`
- **Postman Headers:**
  - `Authorization`: `Token <ADMIN_TOKEN>`
- **Return from API (`200 OK`):**
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
      "total_houses": 2
    }
  ]
}
```

---

### 4.2 Get Single Field Agent Detail
- **Method:** `GET`
- **URL:** `<BASE_URL>/api/auth/agents/2/`
- **Postman Headers:**
  - `Authorization`: `Token <ADMIN_TOKEN>`
- **Return from API (`200 OK`):**
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
  "total_houses": 2
}
```

---

### 4.3 Activate / Deactivate Field Agent (Force Logout)
- **Method:** `PATCH`
- **URL:** `<BASE_URL>/api/auth/agents/2/toggle-active/`
- **Postman Headers:**
  - `Authorization`: `Token <ADMIN_TOKEN>`
- **Postman Body:** None
- **Return from API (`200 OK`):**
```json
{
  "message": "Field agent deactivated successfully.",
  "is_active": false,
  "agent_id": 2,
  "username": "agent01"
}
```
*(Calling it again reactivates the agent and returns `"is_active": true`.)*

---

### 4.4 Delete Field Agent
- **Method:** `DELETE`
- **URL:** `<BASE_URL>/api/auth/agents/2/`
- **Postman Headers:**
  - `Authorization`: `Token <ADMIN_TOKEN>`
- **Return from API:** Status `204 No Content` (Empty response body).

---

## 5. 8-Section Haritha Kerala Survey API (Single Submit)

When the Field Agent completes all 8 tabs (`1/8` → `8/8`) and clicks **Submit Survey**, all 8 sections + multiple family members + images are sent in **one single API call** to:

- **Method:** `POST`
- **URL:** `<BASE_URL>/api/survey/houses/` *(also works at `/api/survey/submit/` and `/api/survey/surveys/`)*
- **Role Required:** **Field Agent Token** (`Authorization: Token <FIELD_AGENT_TOKEN>`)

You can test this in Postman using **Method A (Raw JSON)** or **Method B (`form-data` with Image Files)**.

---

### 5.1 Method A — Submit in Postman as Raw JSON (with URL or Base64 Image)

1. Set Method to **`POST`** and URL to **`<BASE_URL>/api/survey/houses/`**.
2. In **Headers**, set:
   - `Authorization`: `Token <FIELD_AGENT_TOKEN>`
   - `Content-Type`: `application/json`
3. In **Body** → select **`raw`** → **`JSON`** and paste:

```json
{
  "survey": {
    "language": "en",

    "household_details": {
      "family_head_name": "Sanoop",
      "residence_name": "Green Villa",
      "residence_type": "OWNED",
      "house_name": "Puthen Veedu",
      "house_number": "123",
      "house_number_type": "NEW",
      "phone_number": "+919876543210",
      "blood_group": "O+",
      "age": 25,
      "gender": "M",
      "education": "Degree",
      "occupation": "Software Developer",
      "willing_to_donate_blood": true,
      "photo_url": "https://example.com/photo.jpg",
      "location": {
        "latitude": 11.123456,
        "longitude": 76.123456,
        "address": "Nilambur, Kerala, India"
      }
    },

    "family_members": [
      {
        "name": "Member Name 1",
        "age": 48,
        "gender": "F",
        "education": "SSLC",
        "occupation": "Homemaker",
        "blood_group": "B+",
        "willing_to_donate_blood": false
      },
      {
        "name": "Member Name 2",
        "age": 20,
        "gender": "M",
        "education": "Degree",
        "occupation": "Student",
        "blood_group": "A+",
        "willing_to_donate_blood": true
      }
    ],

    "retired_government_employee": {
      "has_retired_employee": true,
      "department": "Education",
      "sector": "GOVERNMENT",
      "designation": "Teacher"
    },

    "agriculture": {
      "currently_farming": true,
      "interested_in_farming": true
    },

    "water_management": {
      "water_sources": [
        "WELL",
        "WATER_AUTHORITY",
        "NEIGHBOUR_WELL",
        "OTHER"
      ],
      "other_water_source": null,
      "needs_pipeline_connection": true
    },

    "waste_management": {
      "organic_waste_method": "BIOGAS",
      "other_method": null,
      "hands_over_non_organic_waste_to_haritha_karma_sena": true
    },

    "green_energy": {
      "has_solar": true,
      "interested_in_installing_solar": true,
      "has_ev": true,
      "ev_vehicle_types": [
        "TWO_WHEELER",
        "FOUR_WHEELER"
      ]
    },

    "health_accessibility": {
      "has_differently_abled_person": false,
      "has_bedridden_patient": false,
      "is_haritha_bhavan": false,
      "interested_in_haritha_bhavan_scheme": true,
      "uses_diapers": false
    },

    "property_and_public_spaces": {
      "has_vacant_public_land": true,
      "public_land_location": "Near community hall",
      "public_land_photo_url": "https://example.com/public-land.jpg",

      "has_vacant_house_or_land_nearby": true,
      "vacant_property_photo_url": "https://example.com/property.jpg",
      "vacant_property_location": "Near main road",

      "is_waste_dumped_in_vacant_land": false
    },

    "domestic_animals": {
      "has_animals": true,
      "animals": {
        "chicken": 10,
        "cow": 2,
        "goat": 3,
        "buffalo": 0
      }
    },

    "entrepreneurship": {
      "has_existing_business": true,
      "interested_in_starting_home_business": true,
      "business_details": "Homemade food products"
    },

    "additional_feedback": {
      "suggestions": "Need better waste collection facilities in our area."
    }
  }
}
```
> **Tip for Base64 Camera Photos in JSON:** If the mobile app passes `"data:image/jpeg;base64,/9j/4AAQ..."` (or raw Base64) in `photo_url`, `public_land_photo_url`, or `vacant_property_photo_url`, Django automatically decodes the image, saves it into `media/house_photos/<id>/`, and returns the generated `http://.../media/house_photos/<id>/...` URL in the response!

---

### 5.2 Method B — Submit in Postman as `form-data` (JSON + Image Files in One Call)

To upload actual image files (`JPG`/`PNG`) along with the 8-section JSON in a **single Postman request**:

1. Set Method to **`POST`** and URL to **`<BASE_URL>/api/survey/houses/`**.
2. In **Headers**, set **only**:
   - `Authorization`: `Token <FIELD_AGENT_TOKEN>`
   *(Do NOT manually set `Content-Type`; Postman sets `multipart/form-data; boundary=...` automatically).*
3. In **Body** → select **`form-data`** and add these keys:

| Key | Type (Dropdown) | Value |
|-----|-----------------|-------|
| `survey` | **Text** | Paste the entire `{"survey": { ... }}` JSON string from Section 5.1 |
| `house_photo` | **File** | Select an image file from your PC (for `household_details.photo_url`) |
| `public_land_photo` | **File** | Select an image file from your PC (for `public_land_photo_url`) |
| `vacant_property_photo` | **File** | Select an image file from your PC (for `vacant_property_photo_url`) |

#### Return from API (`201 Created`)

```json
{
  "message": "Household survey submitted successfully.",
  "id": 1,
  "house": {
    "id": 1,
    "field_agent": 2,
    "field_agent_name": "agent01",
    "survey": {
      "language": "en",
      "household_details": {
        "family_head_name": "Sanoop",
        "residence_name": "Green Villa",
        "residence_type": "OWNED",
        "house_name": "Puthen Veedu",
        "house_number": "123",
        "house_number_type": "NEW",
        "phone_number": "+919876543210",
        "blood_group": "O+",
        "age": 25,
        "gender": "M",
        "education": "Degree",
        "occupation": "Software Developer",
        "willing_to_donate_blood": true,
        "photo_url": "http://127.0.0.1:8000/media/house_photos/1/house.jpg",
        "location": {
          "latitude": 11.123456,
          "longitude": 76.123456,
          "address": "Nilambur, Kerala, India"
        }
      },
      "family_members": [
        {
          "id": 1,
          "name": "Member Name 1",
          "age": 48,
          "gender": "F",
          "education": "SSLC",
          "occupation": "Homemaker",
          "blood_group": "B+",
          "willing_to_donate_blood": false
        },
        {
          "id": 2,
          "name": "Member Name 2",
          "age": 20,
          "gender": "M",
          "education": "Degree",
          "occupation": "Student",
          "blood_group": "A+",
          "willing_to_donate_blood": true
        }
      ],
      "retired_government_employee": {
        "has_retired_employee": true,
        "department": "Education",
        "sector": "GOVERNMENT",
        "designation": "Teacher"
      },
      "agriculture": {
        "currently_farming": true,
        "interested_in_farming": true
      },
      "water_management": {
        "water_sources": [
          "WELL",
          "WATER_AUTHORITY",
          "NEIGHBOUR_WELL",
          "OTHER"
        ],
        "other_water_source": null,
        "needs_pipeline_connection": true
      },
      "waste_management": {
        "organic_waste_method": "BIOGAS",
        "other_method": null,
        "hands_over_non_organic_waste_to_haritha_karma_sena": true
      },
      "green_energy": {
        "has_solar": true,
        "interested_in_installing_solar": true,
        "has_ev": true,
        "ev_vehicle_types": [
          "TWO_WHEELER",
          "FOUR_WHEELER"
        ],
        "interested_in_ev": false,
        "other_green_initiatives": null
      },
      "health_accessibility": {
        "has_differently_abled_person": false,
        "has_bedridden_patient": false,
        "is_haritha_bhavan": false,
        "interested_in_haritha_bhavan_scheme": true,
        "uses_diapers": false
      },
      "property_and_public_spaces": {
        "has_vacant_public_land": true,
        "public_land_location": "Near community hall",
        "public_land_photo_url": "http://127.0.0.1:8000/media/house_photos/1/pub.jpg",
        "has_vacant_house_or_land_nearby": true,
        "vacant_property_photo_url": "http://127.0.0.1:8000/media/house_photos/1/vac.jpg",
        "vacant_property_location": "Near main road",
        "is_waste_dumped_in_vacant_land": false
      },
      "domestic_animals": {
        "has_animals": true,
        "animals": {
          "chicken": 10,
          "cow": 2,
          "goat": 3,
          "buffalo": 0
        }
      },
      "entrepreneurship": {
        "has_existing_business": true,
        "interested_in_starting_home_business": true,
        "business_details": "Homemade food products"
      },
      "additional_feedback": {
        "suggestions": "Need better waste collection facilities in our area."
      }
    },
    "photos": [
      {
        "id": 1,
        "house": 1,
        "photo": "/media/house_photos/1/house.jpg",
        "photo_url": "http://127.0.0.1:8000/media/house_photos/1/house.jpg",
        "caption": "House Photo",
        "uploaded_at": "2026-11-17T21:08:14+05:30"
      },
      {
        "id": 2,
        "house": 1,
        "photo": "/media/house_photos/1/pub.jpg",
        "photo_url": "http://127.0.0.1:8000/media/house_photos/1/pub.jpg",
        "caption": "Public Land Photo",
        "uploaded_at": "2026-11-17T21:08:14+05:30"
      },
      {
        "id": 3,
        "house": 1,
        "photo": "/media/house_photos/1/vac.jpg",
        "photo_url": "http://127.0.0.1:8000/media/house_photos/1/vac.jpg",
        "caption": "Vacant Property Photo",
        "uploaded_at": "2026-11-17T21:08:14+05:30"
      }
    ],
    "created_at": "2026-11-17T21:08:14+05:30",
    "updated_at": "2026-11-17T21:08:14+05:30"
  },
  "survey": { "...same full 8-section survey object..." }
}
```

---

### 5.3 Method C — Upload Photo Standalone (`POST /api/survey/upload-photo/`)

If your mobile app wants to upload a photo immediately when captured and get back a `photo_url`:

- **Method:** `POST`
- **URL:** `<BASE_URL>/api/survey/upload-photo/`
- **Postman Headers:**
  - `Authorization`: `Token <FIELD_AGENT_TOKEN>`
- **Postman Body (`form-data`):**

| Key | Type | Value |
|-----|------|-------|
| `photo` | **File** | Select image file (`JPG`/`PNG`) |
| `caption` | **Text** | `House Photo` |

- **Return from API (`201 Created`):**
```json
{
  "message": "Photo uploaded successfully.",
  "id": 4,
  "photo_url": "http://127.0.0.1:8000/media/house_photos/general/photo.jpg",
  "caption": "House Photo",
  "photo": {
    "id": 4,
    "house": null,
    "photo": "/media/house_photos/general/photo.jpg",
    "photo_url": "http://127.0.0.1:8000/media/house_photos/general/photo.jpg",
    "caption": "House Photo",
    "uploaded_at": "2026-11-17T21:10:00+05:30"
  }
}
```

---

## 6. List, View, Update & Delete Survey APIs

### 6.1 List Surveys (Admin = All, Field Agent = Own Only)
- **Method:** `GET`
- **URL:** `<BASE_URL>/api/survey/houses/`
- **Postman Headers:**
  - `Authorization`: `Token <ADMIN_OR_AGENT_TOKEN>`
- **Return from API (`200 OK`):**
```json
{
  "count": 1,
  "houses": [
    {
      "id": 1,
      "house_number": "123",
      "house_number_type": "NEW",
      "house_name": "Puthen Veedu",
      "residence_name": "Green Villa",
      "residence_type": "OWNED",
      "family_head_name": "Sanoop",
      "phone_number": "+919876543210",
      "address": "Nilambur, Kerala, India",
      "field_agent_name": "agent01",
      "total_photos": 3,
      "total_family_members": 2,
      "survey": {
        "language": "en",
        "household_details": { "...": "..." },
        "family_members": [ "..." ],
        "retired_government_employee": { "...": "..." },
        "agriculture": { "...": "..." },
        "water_management": { "...": "..." },
        "waste_management": { "...": "..." },
        "green_energy": { "...": "..." },
        "health_accessibility": { "...": "..." },
        "property_and_public_spaces": { "...": "..." },
        "domestic_animals": { "...": "..." },
        "entrepreneurship": { "...": "..." },
        "additional_feedback": { "...": "..." }
      },
      "created_at": "2026-11-17T21:08:14+05:30"
    }
  ]
}
```

---

### 6.2 Get Single Survey Detail
- **Method:** `GET`
- **URL:** `<BASE_URL>/api/survey/houses/1/`
- **Postman Headers:**
  - `Authorization`: `Token <ADMIN_OR_AGENT_TOKEN>`
- **Return from API (`200 OK`):**
Returns the full house object (`id`, `field_agent`, `field_agent_name`, `survey`, `photos`, `created_at`, `updated_at`).

---

### 6.3 Update Survey *(Field Agent — Own Survey Only)*
- **Method:** `PATCH`
- **URL:** `<BASE_URL>/api/survey/houses/1/`
- **Postman Headers:**
  - `Authorization`: `Token <FIELD_AGENT_TOKEN>`
  - `Content-Type`: `application/json`
- **Postman Body (`raw` → `JSON` — send only the sections you want to update):**
```json
{
  "survey": {
    "agriculture": {
      "currently_farming": false,
      "interested_in_farming": true
    },
    "additional_feedback": {
      "suggestions": "Updated suggestion from Postman."
    }
  }
}
```
- **Return from API (`200 OK`):**
```json
{
  "message": "Household survey updated successfully.",
  "id": 1,
  "house": { "...updated full house object..." },
  "survey": { "...updated full survey object..." }
}
```

---

### 6.4 Delete Survey *(Admin Only)*
- **Method:** `DELETE`
- **URL:** `<BASE_URL>/api/survey/houses/1/`
- **Postman Headers:**
  - `Authorization`: `Token <ADMIN_TOKEN>`
- **Return from API:** Status `204 No Content`.

---

## 7. Family Members APIs

*(Note: Family members are already created automatically when you submit `family_members` inside `POST /api/survey/houses/`. You can also manage them individually with these endpoints.)*

### 7.1 Add Family Member(s) to an Existing House
- **Method:** `POST`
- **URL:** `<BASE_URL>/api/survey/houses/1/family/`
- **Postman Headers:**
  - `Authorization`: `Token <FIELD_AGENT_TOKEN>`
  - `Content-Type`: `application/json`
- **Postman Body (`raw` → `JSON` — single object or array `[...]`):**
```json
[
  {
    "name": "Member Name 3",
    "age": 16,
    "gender": "F",
    "education": "Plus Two",
    "occupation": "Student",
    "blood_group": "O+",
    "willing_to_donate_blood": false
  }
]
```
- **Return from API (`201 Created`):**
```json
{
  "message": "Family member(s) added successfully.",
  "family_members": [
    {
      "id": 1,
      "house": 1,
      "name": "Member Name 1",
      "age": 48,
      "gender": "F",
      "education": "SSLC",
      "occupation": "Homemaker",
      "blood_group": "B+",
      "willing_to_donate_blood": false
    },
    {
      "id": 2,
      "house": 1,
      "name": "Member Name 2",
      "age": 20,
      "gender": "M",
      "education": "Degree",
      "occupation": "Student",
      "blood_group": "A+",
      "willing_to_donate_blood": true
    },
    {
      "id": 3,
      "house": 1,
      "name": "Member Name 3",
      "age": 16,
      "gender": "F",
      "education": "Plus Two",
      "occupation": "Student",
      "blood_group": "O+",
      "willing_to_donate_blood": false
    }
  ]
}
```

### 7.2 List Family Members of a House
- **Method:** `GET`
- **URL:** `<BASE_URL>/api/survey/houses/1/family/`
- **Headers:** `Authorization: Token <TOKEN>`
- **Return (`200 OK`):** `{"count": 3, "family_members": [ ... ]}`

### 7.3 Update / Delete a Single Family Member
- **Get Detail:** `GET <BASE_URL>/api/survey/family/1/`
- **Update (`PATCH`):** `PATCH <BASE_URL>/api/survey/family/1/`
  ```json
  {
    "occupation": "Teacher",
    "willing_to_donate_blood": true
  }
  ```
- **Delete (`DELETE`):** `DELETE <BASE_URL>/api/survey/family/1/` → `204 No Content`

---

## 8. House Photos APIs

- **Upload Additional Photos (`POST`):** `<BASE_URL>/api/survey/houses/1/photos/` (`Body` → `form-data` → key `photos` [File], key `captions` [Text])
- **List Photos of a House (`GET`):** `<BASE_URL>/api/survey/houses/1/photos/`
- **Delete Photo (`DELETE`):** `<BASE_URL>/api/survey/photos/1/` → `204 No Content`

---

## 9. Admin Full Report API

- **Method:** `GET`
- **URL:** `<BASE_URL>/api/survey/admin/report/`
- **Postman Headers:**
  - `Authorization`: `Token <ADMIN_TOKEN>`
- **Return from API (`200 OK`):**
```json
{
  "total_houses": 1,
  "houses": [
    {
      "id": 1,
      "field_agent": 2,
      "field_agent_name": "agent01",
      "survey": { "...all 8 sections + family_members..." },
      "photos": [ "...all uploaded photo objects with photo_url..." ],
      "created_at": "2026-11-17T21:08:14+05:30",
      "updated_at": "2026-11-17T21:08:14+05:30"
    }
  ]
}
```

---

## 10. Common Error Responses

| Status Code | Example Return from API | Cause & Fix |
|-------------|-------------------------|-------------|
| `400 Bad Request` | `{"non_field_errors": ["Invalid username or password."]}` | Check username/password |
| `400 Bad Request` | `{"non_field_errors": ["Your account has been deactivated. Contact admin."]}` | Admin deactivated this field agent |
| `400 Bad Request` | `{"household_details": "This section is required inside 'survey'."}` | Missing `household_details` in JSON |
| `401 Unauthorized` | `{"detail": "Authentication credentials were not provided."}` | Add `Authorization: Token <token>` in Postman Headers |
| `401 Unauthorized` | `{"detail": "Invalid token."}` | Token was logged out or agent was deactivated; log in again |
| `403 Forbidden` | `{"error": "Only field agents can submit house surveys."}` | You used an Admin token instead of a Field Agent token |
| `404 Not Found` | `{"error": "House survey not found."}` | Wrong House ID or belongs to a different Field Agent |
