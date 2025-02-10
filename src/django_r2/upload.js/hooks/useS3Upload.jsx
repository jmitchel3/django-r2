/** @jsxRuntime classic */
/** @jsx h */
/** @jsxFrag Fragment */

import { h, Fragment } from 'preact';
import { useState } from 'preact/hooks';

export function useS3Upload() {
  const [activeXHRs, setActiveXHRs] = useState({});
  
  const uploadToS3 = async (file, data, onProgress) => {
    const fileName = data.filename || file.name;
    const newFileObject = new File([file], fileName, { type: file.type });
    const url = data.url;

    if (!url) {
      throw new Error("Error with your request, please try again.");
    }

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open('PUT', url, true);
      
      setActiveXHRs(prev => ({
        ...prev,
        [file.name]: xhr
      }));

      xhr.upload.onprogress = (event) => {
        onProgress?.(file, xhr, event, data);
      };

      xhr.onload = function() {
        setActiveXHRs(prev => {
          const newXHRs = { ...prev };
          delete newXHRs[file.name];
          return newXHRs;
        });
        
        if (xhr.status === 200) {
          resolve(data.object_data);
        } else {
          reject(new Error(xhr.statusText));
        }
      };

      xhr.onerror = function() {
        setActiveXHRs(prev => {
          const newXHRs = { ...prev };
          delete newXHRs[file.name];
          return newXHRs;
        });
        reject(new Error(`Upload failed: ${xhr.status}`));
      };

      xhr.setRequestHeader('Content-Type', newFileObject.type);
      xhr.send(newFileObject);
    });
  };

  const cancelUpload = (fileName) => {
    if (activeXHRs[fileName]) {
      activeXHRs[fileName].abort();
      setActiveXHRs(prev => {
        const newXHRs = { ...prev };
        delete newXHRs[fileName];
        return newXHRs;
      });
    }
  };

  return {
    uploadToS3,
    cancelUpload,
    activeXHRs
  };
} 