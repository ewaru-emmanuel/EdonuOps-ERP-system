/**
 * Debug utility to check user modules loading
 * This can be called from browser console to debug module loading issues
 */

export const debugUserModules = async () => {
  console.log('🔍 Debugging User Modules Loading');
  console.log('=' * 50);
  
  try {
    // Check localStorage
    console.log('\n1️⃣ Checking localStorage');
    const userPrefs = localStorage.getItem('edonuops_user_preferences');
    const userModules = localStorage.getItem('edonuops_user_modules');
    console.log('User Preferences:', userPrefs ? JSON.parse(userPrefs) : 'Not found');
    console.log('User Modules:', userModules ? JSON.parse(userModules) : 'Not found');
    
    // Check API call
    console.log('\n2️⃣ Testing API call');
    const { default: apiClient } = await import('../services/apiClient');
    
    try {
      const response = await apiClient.get('/api/dashboard/modules/user');
      console.log('API Response Status:', response.status);
      console.log('API Response Data:', response.data);
      console.log('Number of modules:', response.data?.length || 0);
      
      if (response.data && response.data.length > 0) {
        console.log('✅ Modules found in API response:');
        response.data.forEach(module => {
          console.log(`  - ${module.id}: ${module.name} (Active: ${module.is_active})`);
        });
      } else {
        console.log('❌ No modules found in API response');
      }
    } catch (error) {
      console.error('❌ API call failed:', error);
    }
    
    // Check user context
    console.log('\n3️⃣ Checking user context');
    const user = localStorage.getItem('user');
    if (user) {
      const userData = JSON.parse(user);
      console.log('User ID:', userData.id);
      console.log('User authenticated:', !!userData);
    } else {
      console.log('❌ No user found in localStorage');
    }
    
    // Check if backend is running
    console.log('\n4️⃣ Testing backend connectivity');
    try {
      const response = await fetch('http://localhost:5000/api/dashboard/modules/available');
      console.log('Backend Status:', response.status);
      if (response.ok) {
        const data = await response.json();
        console.log('Available modules:', data.length);
      }
    } catch (error) {
      console.error('❌ Backend not reachable:', error);
    }
    
    console.log('\n🎯 DIAGNOSIS:');
    console.log('=' * 20);
    
    // Final diagnosis
    if (userPrefs || userModules) {
      console.log('✅ User has preferences/modules in localStorage');
    } else {
      console.log('❌ No user preferences/modules in localStorage');
    }
    
    try {
      const response = await apiClient.get('/api/dashboard/modules/user');
      if (response.data && response.data.length > 0) {
        console.log('✅ Backend has user modules');
      } else {
        console.log('❌ Backend has no user modules - this is the problem!');
        console.log('💡 SOLUTION: User needs to activate modules');
        console.log('🔧 FIX: Go to /onboarding or manually activate modules');
      }
    } catch (error) {
      console.log('❌ Backend API error:', error.message);
    }
    
  } catch (error) {
    console.error('❌ Debug failed:', error);
  }
};

// Make it available globally for browser console
if (typeof window !== 'undefined') {
  window.debugUserModules = debugUserModules;
}



