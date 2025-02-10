/** @jsxRuntime classic */
/** @jsx h */
/** @jsxFrag Fragment */

import { h, Fragment } from 'preact';
import { formatBytes } from './utils';

export function FileDisplay({ 
  fileName,
  progress,
  file,
  uploadStatus,
  completedFiles,
  timeEstimates,
  toggleUpload,
  cancelUpload
}) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between items-center text-sm text-gray-600">
        <span className="truncate flex-1">{fileName}</span>
        <div className="flex items-center gap-4">
          {uploadStatus === 'uploading' && !completedFiles.has(fileName) && (
            <>
              <span className="text-blue-500 whitespace-nowrap">
                {progress.toFixed(1)}% • {timeEstimates} left
              </span>
              <span className="text-gray-500 whitespace-nowrap">
                {formatBytes(progress * file.size / 100)} / {formatBytes(file.size)}
              </span>
            </>
          )}
          
          {completedFiles.has(fileName) && (
            <>
              <span className="text-gray-500 whitespace-nowrap">
                {formatBytes(file.size)}
              </span>
              <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
              </svg>
            </>
          )}
          
          {!completedFiles.has(fileName) && (
            <>
              {uploadStatus === 'uploading' && (
                <button
                  type="button"
                  onClick={() => toggleUpload(fileName)}
                  className="text-yellow-500 hover:text-yellow-700"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 9v6m4-6v6" />
                  </svg>
                </button>
              )}
              {uploadStatus === 'paused' && (
                <button
                  type="button"
                  onClick={() => toggleUpload(fileName)}
                  className="text-blue-500 hover:text-blue-700"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                </button>
              )}
              <button
                type="button"
                onClick={() => cancelUpload(fileName)}
                className="text-red-500 hover:text-red-700"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </>
          )}
        </div>
      </div>
      {uploadStatus === 'uploading' && !completedFiles.has(fileName) && (
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="h-2 rounded-full transition-all duration-300 bg-blue-500"
            style={{ width: `${progress}%` }} 
          />
        </div>
      )}
    </div>
  );
} 