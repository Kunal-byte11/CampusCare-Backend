# CampusCare Backend

A Flask API backend for the CampusCare mental-health support platform, powered by **Supabase** (PostgreSQL + Auth), **Google Gemini**, and **Agora** (video calls).

---

## Project Structure

```
campuscare-backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Environment variable config
│   ├── routes/
│   │   ├── booking.py       # POST/GET /api/booking
│   │   ├── counselors.py    # CRUD /api/counselors
│   │   ├── forum.py         # CRUD /api/forum/posts & /comments
│   │   ├── ai_chat.py       # POST /api/ai/chat
│   │   └── video_call.py    # GET /api/video/token
│   ├── services/
│   │   ├── supabase_client.py   # Singleton Supabase client
│   │   ├── booking_service.py
│   │   ├── counselor_service.py
│   │   ├── forum_service.py
│   │   ├── ai_service.py        # Gemini chat + session persistence
│   │   └── agora_service.py     # Agora RTC token generator
│   └── utils/
│       ├── anonymous_id.py  # UUID anon ID generator
│       ├── sentiment.py     # Mood analysis
│       └── auth_guard.py    # Supabase JWT decorators
├── tests/
├── .env.example
├── requirements.txt
└── run.py
```

---

## Quick Start

### 1. Clone & create virtual environment
```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Fill in your Supabase, Agora, and Gemini credentials in .env
```

### 4. Create Supabase tables

Run these SQL statements in **Supabase → SQL Editor**:

```sql
-- Counselors (required — bookings reference this)
create table counselors (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  specialization text,
  available boolean default true,
  created_at timestamptz default now()
);

-- Bookings
create table bookings (
  id uuid primary key default gen_random_uuid(),
  anonymous_id text not null,
  counselor_id uuid references counselors(id) on delete set null,
  scheduled_at timestamptz not null,
  status text default 'pending' check (status in ('pending','confirmed','cancelled','completed')),
  notes text default '',
  call_started_at timestamptz,
  call_duration_limit int default 300,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Auto-update updated_at on bookings
create or replace function update_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger bookings_updated_at
  before update on bookings
  for each row execute function update_updated_at();

-- Forum posts
create table forum_posts (
  id uuid primary key default gen_random_uuid(),
  anonymous_id text not null,
  title text not null,
  content text not null,
  tags text[] default '{}',
  upvotes int default 0,
  created_at timestamptz default now()
);

-- Forum comments
create table forum_comments (
  id uuid primary key default gen_random_uuid(),
  post_id uuid references forum_posts(id) on delete cascade,
  anonymous_id text not null,
  content text not null,
  created_at timestamptz default now()
);

-- AI chat sessions
create table chat_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  messages jsonb default '[]',
  mood_score float default 0,
  flagged boolean default false,
  created_at timestamptz default now()
);

-- ── RLS (Row Level Security) ──────────────────────────────────────────────────
alter table bookings enable row level security;
alter table forum_posts enable row level security;
alter table forum_comments enable row level security;
alter table chat_sessions enable row level security;

-- Chat sessions: user sees only their own
create policy "user sees own sessions"
  on chat_sessions for all
  using (auth.uid() = user_id);

-- Forum: anyone (students use anon, counselors use authenticated) can read & write
create policy "anyone can read posts"
  on forum_posts for select
  using (true);

create policy "anyone can insert posts"
  on forum_posts for insert
  with check (true);

-- Bookings: open select (anonymous_id ownership handled in app layer)
create policy "user sees own bookings"
  on bookings for select
  using (true);
```

### 5. Run the server
```bash
python run.py
```

Server starts at `http://localhost:5000`.

---

## API Reference

### Health
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health` | None | Liveness check |

### Counselors `/api/counselors`
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/?available=true` | None | List counselors |
| GET | `/<id>` | None | Get counselor details |
| POST | `/` | Counselor JWT | Create counselor profile |
| PATCH | `/<id>/availability` | Counselor JWT | Toggle availability |

### Booking `/api/booking`
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/` | None | Create a booking |
| GET | `/my?anonymous_id=<id>` | None | Get bookings for anon user |
| GET | `/all` | Counselor JWT | List all bookings |
| PATCH | `/<id>/status` | Counselor JWT | Update booking status |

### Forum `/api/forum`
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/posts` | None | List posts (paginated) |
| POST | `/posts` | None | Create a post |
| GET | `/posts/<id>` | None | Get single post |
| DELETE | `/posts/<id>` | None | Delete own post |
| POST | `/posts/<id>/upvote` | None | Upvote a post |
| GET | `/posts/<id>/comments` | None | List comments |
| POST | `/posts/<id>/comments` | None | Add a comment |
| DELETE | `/comments/<id>` | None | Delete own comment |

### AI Chat `/api/ai`
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/chat` | None | Chat with Gemini assistant (returns `flagged` if crisis detected) |
| GET | `/history?session_id=<id>` | None | Get chat history |

### Video `/api/video`
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/token?channel=<name>&uid=<int>&role=publisher` | Supabase JWT | Get Agora RTC token |

---

## Authentication

- **Students**: No auth required for most endpoints. Use an `anonymous_id` (generate once client-side with `/utils/anonymous_id.py` logic, store in `localStorage`).
- **Counselors/Admins**: Protected endpoints require `Authorization: Bearer <supabase_jwt>`. The JWT must have `app_metadata.role = "counselor"` or `"admin"` set in Supabase Auth.

---

## Running Tests
```bash
pytest tests/ -v
```

---

## Gemini Model Options

Set in `.env`:
```
GEMINI_MODEL=gemini-1.5-flash    # fast, cheap (default)
GEMINI_MODEL=gemini-1.5-pro      # more capable
GEMINI_MODEL=gemini-2.0-flash    # latest flash
```
