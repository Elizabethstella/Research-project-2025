export function validateEnv() {
  const required = ['JWT_SECRET', 'PYTHON_SERVICE_URL'];
  const missing = required.filter(key => !process.env[key]);
  
  if (missing.length > 0) {
    throw new Error(`Missing environment variables: ${missing.join(', ')}`);
  }
  
  console.log("Environment validation passed");
}