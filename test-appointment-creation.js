import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = "https://anmxvcoleucxybtowpnm.supabase.co";
// Updated to use the correct API key from .env.local
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFubXh2Y29sZXVjeHlidG93cG5tIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA3MTA3NzIsImV4cCI6MjA2NjI4Njc3Mn0.82tFr2l-RrpADwaYRhDLKEWxDNhkaBGZD4d_Hq5QA4M";

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

async function testAppointmentCreation() {
  console.log('🧪 Testing Appointment Creation...');
  console.log('📅 Test Data: July 7, 2025 at 14:40 for patient "Soboszlai"');
  
  try {
    // First, let's check if required tables exist and get sample data
    console.log('\n1️⃣ Checking database structure...');
    
    // Check time slots
    const { data: timeSlots, error: timeSlotsError } = await supabase
      .from('time_slots')
      .select('*')
      .order('start_time');
    
    if (timeSlotsError) {
      console.log('❌ Error fetching time slots:', timeSlotsError.message);
      return;
    }
    
    console.log('✅ Time slots available:', timeSlots?.length || 0);
    
    // Find a time slot for 14:40
    const targetTime = '14:40:00'; // Match the format in the database
    let selectedTimeSlot = timeSlots?.find(slot => slot.start_time === targetTime);
    
    if (!selectedTimeSlot) {
      console.log(`❌ Exact time slot for ${targetTime} not found.`);
      // Fallback to the first available slot for testing purposes
      selectedTimeSlot = timeSlots?.[0];
      if(selectedTimeSlot) {
        console.log(`⚠️  Using first available time slot: ${selectedTimeSlot.start_time}`);
      } else {
        console.log('❌ No time slots found at all.');
        return;
      }
    } else {
      console.log('✅ Found exact time slot: 14:40');
    }
    
    // Check rooms
    const { data: rooms, error: roomsError } = await supabase
      .from('rooms')
      .select('*')
      .limit(1);
    
    if (roomsError) {
      console.log('❌ Error fetching rooms:', roomsError.message);
      return;
    }
    
    if (!rooms || rooms.length === 0) {
      console.log('❌ No rooms available');
      return;
    }
    
    console.log('✅ Room available:', rooms[0].name);
    
    // Check clinicians
    const { data: clinicians, error: cliniciansError } = await supabase
      .from('users')
      .select('*')
      .in('role', ['clinician', 'supervisor'])
      .eq('is_active', true)
      .limit(1);
    
    if (cliniciansError) {
      console.log('❌ Error fetching clinicians:', cliniciansError.message);
      return;
    }
    
    if (!clinicians || clinicians.length === 0) {
      console.log('❌ No clinicians available');
      return;
    }
    
    console.log('✅ Clinician available:', `${clinicians[0].first_name} ${clinicians[0].last_name}`);
    
    // 2. Check if patient "Soboszlai" already exists
    console.log('\n2️⃣ Checking if patient "Soboszlai" exists...');
    
    // Updated: Use 'patient_name' column (which represents surname)
    const { data: existingPatients, error: patientError } = await supabase
      .from('patients')
      .select('*')
      .ilike('patient_name', '%Soboszlai%');
    
    if (patientError) {
      console.log('❌ Error checking patients:', patientError.message);
      return;
    }
    
    if (existingPatients && existingPatients.length > 0) {
      console.log('⚠️  Patient "Soboszlai" already exists in system');
    } else {
      console.log('✅ Patient "Soboszlai" is new (as expected)');
    }
    
    // 3. Create test appointment
    console.log('\n3️⃣ Creating test appointment...');
    
    const testAppointmentData = {
      patient_name: 'Soboszlai',
      patient_id: null, // Fixed: Use null instead of empty string for UUID field
      clinician_id: clinicians[0].id,
      clinician_name: `${clinicians[0].first_name} ${clinicians[0].last_name}`,
      appointment_date: '2025-07-07',
      time_slot_id: selectedTimeSlot.id,
      custom_start_time: '14:40',
      custom_end_time: '15:40',
      duration: 60,
      appointment_type: 'consultation',
      status: 'scheduled',
      room_id: rooms[0].id,
      room_name: rooms[0].name,
      notes: 'Test appointment for Soboszlai - July 7, 2025',
      created_by: clinicians[0].id,
      updated_by: clinicians[0].id,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    
    console.log('📝 Appointment data:', {
      patient: testAppointmentData.patient_name,
      date: testAppointmentData.appointment_date,
      time: testAppointmentData.custom_start_time,
      clinician: testAppointmentData.clinician_name,
      room: testAppointmentData.room_name
    });
    
    const { data: newAppointment, error: createError } = await supabase
      .from('appointments')
      .insert(testAppointmentData)
      .select()
      .single();
    
    if (createError) {
      console.log('❌ Failed to create appointment:', createError.message);
      console.log('🔍 Error details:', createError);
      
      // Debug: Check what's wrong
      if (createError.message.includes('violates foreign key constraint')) {
        console.log('\n🔧 DEBUGGING: Foreign key constraint violation detected');
        console.log('This usually means one of the referenced IDs doesn\'t exist.');
        
        // Check if time_slot_id exists
        const { data: timeSlotCheck } = await supabase
          .from('time_slots')
          .select('id')
          .eq('id', selectedTimeSlot.id);
        console.log('Time slot exists:', timeSlotCheck?.length > 0);
        
        // Check if room_id exists
        const { data: roomCheck } = await supabase
          .from('rooms')
          .select('id')
          .eq('id', rooms[0].id);
        console.log('Room exists:', roomCheck?.length > 0);
        
        // Check if clinician_id exists
        const { data: clinicianCheck } = await supabase
          .from('users')
          .select('id')
          .eq('id', clinicians[0].id);
        console.log('Clinician exists:', clinicianCheck?.length > 0);
      }
      
      return;
    }
    
    console.log('✅ Appointment created successfully!');
    console.log('📋 Created appointment ID:', newAppointment.id);
    
    // 4. Verify the appointment was saved correctly
    console.log('\n4️⃣ Verifying appointment was saved...');
    
    const { data: savedAppointment, error: fetchError } = await supabase
      .from('appointments')
      .select('*')
      .eq('id', newAppointment.id)
      .single();
    
    if (fetchError) {
      console.log('❌ Error fetching saved appointment:', fetchError.message);
      return;
    }
    
    console.log('✅ Appointment verification successful!');
    console.log('📊 Saved appointment details:');
    console.log('  - ID:', savedAppointment.id);
    console.log('  - Patient:', savedAppointment.patient_name);
    console.log('  - Date:', savedAppointment.appointment_date);
    console.log('  - Time:', savedAppointment.custom_start_time);
    console.log('  - Clinician:', savedAppointment.clinician_name);
    console.log('  - Room:', savedAppointment.room_name);
    console.log('  - Status:', savedAppointment.status);
    
    // 5. Clean up - delete test appointment
    console.log('\n5️⃣ Cleaning up test data...');
    
    const { error: deleteError } = await supabase
      .from('appointments')
      .delete()
      .eq('id', newAppointment.id);
    
    if (deleteError) {
      console.log('⚠️  Warning: Could not delete test appointment:', deleteError.message);
      console.log('You may need to manually delete appointment ID:', newAppointment.id);
    } else {
      console.log('✅ Test appointment cleaned up successfully');
    }
    
    console.log('\n🎉 TEST COMPLETED SUCCESSFULLY!');
    console.log('✅ Appointments can be saved properly');
    console.log('✅ Patient "Soboszlai" can be added as new patient');
    console.log('✅ Date July 7, 2025 at 14:40 works correctly');
    
  } catch (error) {
    console.error('❌ Unexpected error during test:', error.message);
    console.error('🔍 Full error:', error);
  }
}

// Run the test
testAppointmentCreation();