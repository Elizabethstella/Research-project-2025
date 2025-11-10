import axios from 'axios';
import db from './db.js';

async function testConnection() {
  console.log(' Testing server connection...\n');

  try {
    // Test Node.js server health
    console.log('1. Testing Node.js server...');
    const health = await axios.get('http://localhost:5000/api/health');
    console.log(' Node.js server:', health.data.status);

    //Test Python service
    console.log('2. Testing Python service...');
    const python = await axios.get('http://localhost:7000/');
    console.log(' Python service:', python.data.message);

    // Test database
    console.log('3. Testing database...');
    const users = db.prepare("SELECT COUNT(*) as count FROM users").get();
    console.log('Database:', `${users.count} users found`);

    console.log('\n All systems are working!');

  } catch (error) {
    console.log(' Test failed:', error.message);
    
    if (error.code === 'ECONNREFUSED') {
      console.log('💡 Make sure both servers are running:');
      console.log('   - Node.js: localhost:5000');
      console.log('   - Python: localhost:7000');
    }
  }
}

testConnection();