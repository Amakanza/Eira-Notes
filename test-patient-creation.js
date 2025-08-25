import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = "https://anmxvcoleucxybtowpnm.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFubXh2Y29sZXVjeHlidG93cG5tIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA3MTA3NzIsImV4cCI6MjA2NjI4Njc3Mn0.82tFr2l-RrpADwaYRhDLKEWxDNhkaBGZD4d_Hq5QA4M";

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

async function testPatientCreation() {
  console.log('🧪 Testing Patient Creation...');
  
  try {
    // Test creating a patient
    const { data, error } = await supabase
      .from('patients')
      .insert([
        {
          patient_name: 'Test Patient',
          case_number: 'TEST001',
          occupation: 'Software Developer',
          diagnosis: 'Test diagnosis',
          physiotherapist: 'Dr. Test'
        }
      ])
      .select();

    if (error) {
      console.error('❌ Error creating patient:', error);
    } else {
      console.log('✅ Patient created successfully:', data);
    }

    // Test fetching patients
    const { data: patients, error: fetchError } = await supabase
      .from('patients')
      .select('*');

    if (fetchError) {
      console.error('❌ Error fetching patients:', fetchError);
    } else {
      console.log('✅ Patients fetched successfully:', patients.length, 'patients found');
    }

  } catch (error) {
    console.error('❌ Unexpected error:', error);
  }
}

testPatientCreation();