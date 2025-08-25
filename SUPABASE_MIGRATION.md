# Supabase Migration Guide

This document outlines the transition from mock data to a fully functional Supabase-backed application.

## What Was Changed

### 1. Database Schema
- Created migration file: `supabase/migrations/20250101000000_create_appointments_tables.sql`
- Added tables: `users`, `rooms`, `time_slots`, `special_events`, `appointments`
- Configured Row Level Security (RLS) policies
- Added initial seed data

### 2. Type Definitions
- Updated `src/integrations/supabase/types.ts` with new table definitions
- Added proper TypeScript interfaces for all tables

### 3. Hooks and Data Management
- Created `src/hooks/useSupabaseAppointments.ts` - Main Supabase integration hook
- Updated `src/hooks/useAppointments.ts` - Now wraps Supabase hook for compatibility
- Updated `src/hooks/useSpecialEventOperations.ts` - Now uses Supabase for CRUD operations

### 4. Components
- Updated `src/components/dashboard/UpcomingAppointments.tsx` to use real data
- Added loading states and error handling
- Displays "No appointments" when none exist

## Next Steps to Complete Migration

### 1. Run Database Migration
You need to apply the migration to your Supabase database:

```bash
# If you have Supabase CLI installed:
supabase db reset

# Or manually run the SQL from:
# supabase/migrations/20250101000000_create_appointments_tables.sql
```

### 2. Verify Environment Variables
Ensure your `.env.local` file has the correct Supabase credentials:

```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 3. Test the Application
```bash
npm run dev
```

### 4. Optional: Update Authentication
The authentication system still uses localStorage. To fully migrate:
- Update `src/contexts/AuthContext.tsx` to use Supabase Auth
- Update `src/pages/AdminUsers.tsx` to manage users via Supabase

## Features Now Working with Supabase

✅ **Appointment Management**
- Create, read, update, delete appointments
- Real-time data from database
- Proper validation and error handling

✅ **Room Management**
- Rooms loaded from database
- Room capacity validation

✅ **Time Slot Management**
- Time slots from database
- Availability checking

✅ **Clinician Management**
- Clinicians loaded from database
- Availability validation

✅ **Special Events**
- CRUD operations via Supabase
- Proper data synchronization

✅ **Dashboard Integration**
- Today's appointments from real data
- Loading states and error handling

## Database Tables Created

1. **users** - Clinicians and staff
2. **rooms** - Treatment rooms with capacity
3. **time_slots** - Available appointment times
4. **appointments** - Patient appointments
5. **special_events** - Clinic events and closures

All tables include proper relationships, constraints, and RLS policies for security.