function getAPIUrl(relativePath) {

  if(process.env.NODE_ENV === 'development') {

    if(process.env.API_BASE_URL) {
      return `${process.env.API_BASE_URL}/api/${relativePath}`;
    }

    return `http://localhost:5000/api/${relativePath}`;
  }

  return `/api/${relativePath}`;
}

export default getAPIUrl;
