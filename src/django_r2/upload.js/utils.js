export const getCsrfToken = () => {
  const hxHeaders = document.body.getAttribute('hx-headers');
  return JSON.parse(hxHeaders)['X-CSRFToken'];
};

export const updateTimeEstimate = (file, loaded, total, startTime) => {
  if (loaded === 0) return '--:--:--';
  
  const elapsed = (Date.now() - startTime) / 1000;
  const rate = loaded / elapsed;
  const remaining = (total - loaded) / rate;
  
  const hours = Math.floor(remaining / 3600);
  const minutes = Math.floor((remaining % 3600) / 60);
  const seconds = Math.floor(remaining % 60);
  
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
};

export const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
};
