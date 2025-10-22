export function handleRouteError(res, error, defaultMessage) {
  console.error("Route error:", error);
  
  if (error.response?.data) {
    return res.status(error.response.status).json({
      success: false,
      error: error.response.data.error || defaultMessage
    });
  }
  
  if (error.code === 'SQLITE_CONSTRAINT') {
    return res.status(400).json({
      success: false,
      error: "Database constraint error"
    });
  }
  
  res.status(500).json({ 
    success: false,
    error: defaultMessage 
  });
}

export function validationError(res, message) {
  return res.status(400).json({
    success: false,
    error: message
  });
}