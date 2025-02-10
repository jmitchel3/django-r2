export const getMediaMetadata = (file) => {
    return new Promise((resolve) => {
      // Handle images
      if (file.type.startsWith('image/')) {
        return handleImageMetadata(file, resolve);
      }
  
      // Handle audio/video
      if (file.type.startsWith('video/') || file.type.startsWith('audio/')) {
        return handleAudioVideoMetadata(file, resolve);
      }
  
      resolve(null);
    });
  };
  
  const handleImageMetadata = (file, resolve) => {
    const img = new Image();
    img.onload = () => {
      const metadata = {
        width: img.naturalWidth,
        height: img.naturalHeight,
        duration: null
      };
      window.URL.revokeObjectURL(img.src);
      resolve(metadata);
    };
    img.onerror = () => {
      window.URL.revokeObjectURL(img.src);
      resolve(null);
    };
    img.src = window.URL.createObjectURL(file);
  };
  
  const handleAudioVideoMetadata = (file, resolve) => {
    const element = file.type.startsWith('video/') 
      ? document.createElement('video') 
      : document.createElement('audio');
    element.preload = 'metadata';
  
    element.onloadedmetadata = () => {
      const metadata = {
        duration: element.duration,
        width: element.videoWidth || null,
        height: element.videoHeight || null,
      };
      window.URL.revokeObjectURL(element.src);
      resolve(metadata);
    };
  
    element.onerror = () => {
      window.URL.revokeObjectURL(element.src);
      resolve(null);
    };
  
    element.src = window.URL.createObjectURL(file);
  };