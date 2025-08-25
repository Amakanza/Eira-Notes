import { createClient } from '@supabase/supabase-js';
import fs from 'fs';
import path from 'path';

const SUPABASE_URL = "https://anmxvcoleucxybtowpnm.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFubXh2Y29sZXVjeHlidG93cG5tIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA3MTA3NzIsImV4cCI6MjA2NjI4Njc3Mn0.82tFr2l-RrpADwaYRhDLKEWxDNhkaBGZD4d_Hq5QA4M";

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

async function testConnection() {
  console.log('Testing Supabase connection...');
  
  try {
    // Test basic connection
    const { data, error } = await supabase.from('patients').select('count').limit(1);
    
    if (error) {
      console.log('Connection test result:', error.message);
    } else {
      console.log('✅ Supabase connection successful!');
    }
    
    // Check if appointment tables exist
    const { data: tables, error: tableError } = await supabase
      .from('information_schema.tables')
      .select('table_name')
      .eq('table_schema', 'public');
      
    if (tableError) {
      console.log('❌ Could not check tables:', tableError.message);
    } else {
      console.log('📋 Available tables:', tables?.map(t => t.table_name));
      
      const appointmentTables = ['appointments', 'users', 'rooms', 'time_slots', 'special_events'];
      const missingTables = appointmentTables.filter(table => 
        !tables?.some(t => t.table_name === table)
      );
      
      if (missingTables.length > 0) {
        console.log('⚠️  Missing tables:', missingTables);
        console.log('📝 You need to run the migration file to create these tables.');
      } else {
        console.log('✅ All appointment tables exist!');
      }
    }
    
  } catch (err) {
    console.error('❌ Connection failed:', err.message);
  }
}

testConnection();