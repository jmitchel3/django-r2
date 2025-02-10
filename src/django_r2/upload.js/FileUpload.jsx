/** @jsxRuntime classic */
/** @jsx h */
/** @jsxFrag Fragment */

import { h, Fragment } from 'preact';
import { useState, useEffect, useRef } from 'preact/hooks';
import { getCsrfToken, updateTimeEstimate, formatBytes } from './utils';
import { useS3Upload } from './hooks/useS3Upload';
import { FileDisplay } from './FileDisplay';
import { getMediaMetadata } from './media';
import { CloudIcon } from './icons/cloud';


export function FileUpload({ callbackUrl, targetUrl }) {
  const { uploadToS3, cancelUpload, activeXHRs } = useS3Upload();
  const [uploadProgress, setUploadProgress] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [completedFiles, setCompletedFiles] = useState(new Set());
  const fileInputRef = useRef(null);
  const [uploadStatus, setUploadStatus] = useState({});
  const [timeEstimates, setTimeEstimates] = useState({});
  const [uploadStartTimes, setUploadStartTimes] = useState({});
  const MAX_CONCURRENT_UPLOADS = 10;
  const [activeUploads, setActiveUploads] = useState(0);
  const uploadQueue = useRef([]);
  const [isDragging, setIsDragging] = useState(false);
  const dropZoneRef = useRef(null);

  const handleUploadProgress = (file, xhr, progressEvent, data) => {
    const percent = (progressEvent.loaded / progressEvent.total) * 100;
    setUploadProgress(prev => ({
      ...prev,
      [file.name]: percent
    }));
    
    if (uploadStatus[file.name] === 'uploading') {
      setTimeEstimates(prev => ({
        ...prev,
        [file.name]: updateTimeEstimate(
          file,
          progressEvent.loaded,
          progressEvent.total,
          uploadStartTimes[file.name]
        )
      }));
    }
  };

  const processQueue = async () => {
    if (activeUploads >= MAX_CONCURRENT_UPLOADS || uploadQueue.current.length === 0) {
      return;
    }

    const file = uploadQueue.current.shift();
    setActiveUploads(prev => prev + 1);

    try {
      const data = await presignFileForUpload(file);
      const objectData = await uploadToS3(file, data, handleUploadProgress);
      await handleUploadComplete(objectData, file);
    } catch (err) {
      console.error('Upload error:', err);
      setUploadStatus(prev => ({ ...prev, [file.name]: 'error' }));
    } finally {
      setActiveUploads(prev => prev - 1);
      // Process next item in queue
      processQueue();
    }
  };

  // Start processing queue whenever a new file is added or an upload completes
  useEffect(() => {
    if (uploadQueue.current.length > 0 && activeUploads < MAX_CONCURRENT_UPLOADS) {
      processQueue();
    }
  }, [activeUploads]);

  const handleFileSelect = async (event) => {
    const files = Array.from(event.target.files);
    setSelectedFiles(prev => [...prev, ...files]);
    
    const initialProgress = {};
    files.forEach(file => {
      initialProgress[file.name] = 0;
      setUploadStatus(prev => ({ ...prev, [file.name]: 'uploading' }));
      setUploadStartTimes(prev => ({ ...prev, [file.name]: Date.now() }));
    });
    setUploadProgress(prev => ({ ...prev, ...initialProgress }));
    event.target.value = '';

    // Add files to queue
    uploadQueue.current.push(...files);
    // Start processing queue
    processQueue();
  };

  const handleSubmit = (event) => {
    event.preventDefault();
  };

  const presignFileForUpload = async (file) => {
    const csrfToken = getCsrfToken();
    const formData = new FormData();
    formData.append("filename", file.name);
    
    const response = await fetch(targetUrl, {
      method: "POST",
      body: formData,
      headers: {
        "X-CSRFTOKEN": csrfToken,
      }
    });
    return response.json();
  };


  const handleUploadComplete = async (object_data, file) => {
    setCompletedFiles(prev => new Set([...prev, file.name]));
    const mediaMetadata = await getMediaMetadata(file);
    const data = {
      object_data: object_data,
      file_data: {
        size: file.size,
        name: file.name,
        type: file.type,
        duration: mediaMetadata?.duration || null,
        width: mediaMetadata?.width || null,
        height: mediaMetadata?.height || null,
        lastModified: file.lastModified,
        lastModifiedDate: file.lastModifiedDate,
      },
      completed: true
    };

    fetch(callbackUrl, {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        "X-CSRFTOKEN": getCsrfToken(),
      }
    });
  };

  const toggleUpload = (fileName) => {
    if (uploadStatus[fileName] === 'uploading') {
      cancelUpload(fileName);
      setUploadStatus(prev => ({ ...prev, [fileName]: 'paused' }));
      setTimeEstimates(prev => ({ ...prev, [fileName]: '--:--:--' }));
    } else if (uploadStatus[fileName] === 'paused') {
      setUploadStatus(prev => ({ ...prev, [fileName]: 'uploading' }));
      setUploadStartTimes(prev => ({ ...prev, [fileName]: Date.now() }));
      handleSubmit({ preventDefault: () => {} });
    }
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.target === dropZoneRef.current) {
      setIsDragging(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      // Reuse existing file handling logic
      const initialProgress = {};
      files.forEach(file => {
        initialProgress[file.name] = 0;
        setUploadStatus(prev => ({ ...prev, [file.name]: 'uploading' }));
        setUploadStartTimes(prev => ({ ...prev, [file.name]: Date.now() }));
      });
      setUploadProgress(prev => ({ ...prev, ...initialProgress }));
      setSelectedFiles(prev => [...prev, ...files]);
      
      // Add files to queue
      uploadQueue.current.push(...files);
      // Start processing queue
      processQueue();
    }
  };

  return <div>
    <div
      ref={dropZoneRef}
      className={`mb-4 p-8 border-2 border-dashed rounded-lg transition-colors duration-200 ${
        isDragging 
          ? 'border-blue-500 bg-blue-50' 
          : 'border-gray-300 hover:border-blue-500'
      }`}
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <form className='mb-4' onSubmit={handleSubmit}>
        <div className="flex gap-2">
          <label htmlFor="file-upload" className="flex w-full items-center px-4 py-2 bg-white text-blue-500 rounded-lg shadow-lg tracking-wide uppercase border border-blue-500 cursor-pointer hover:bg-blue-500 hover:text-white transition-colors duration-300">
            <span className="flex items-center gap-2">
              <CloudIcon />
              Select Files to Upload
            </span>
            <input 
              ref={fileInputRef}
              id="file-upload" 
              type="file" 
              name="file" 
              multiple 
              className="hidden"
              onChange={handleFileSelect}
            />
          </label>
        </div>

        <input type="hidden" name="callback_url" value={callbackUrl} />
        <input type="hidden" name="target_url" value={targetUrl} />
      </form>
      <div className="text-center text-gray-500 mt-2">
        or drag and drop files here
      </div>
    </div>
    <div className="space-y-3">
      {Object.entries(uploadProgress).map(([fileName, progress]) => {
        const file = selectedFiles.find(f => f.name === fileName);
        
        return (
          <FileDisplay
            key={fileName}
            fileName={fileName}
            progress={progress}
            file={file}
            uploadStatus={uploadStatus[fileName]}
            completedFiles={completedFiles}
            timeEstimates={timeEstimates[fileName]}
            toggleUpload={toggleUpload}
            cancelUpload={cancelUpload}
          />
        );
      })}
    </div>
  </div>
}
