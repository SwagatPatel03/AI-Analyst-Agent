import { AlertCircle, CheckCircle, File, Upload, X } from 'lucide-react';
import React, { useRef, useState } from 'react';
import { reportService } from '../../services/reportService';
import { getErrorMessage } from '../../utils/helpers';
import '../Dashboard/UploadModal.css';

interface FileUploadProps {
  onUploadComplete: () => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadComplete }) => {
  const [file, setFile] = useState<File | null>(null);
  const [companyName, setCompanyName] = useState('');
  const [reportYear, setReportYear] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [progress, setProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (selectedFile: File) => {
    // Validate file type
    if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setError('Please select a PDF file');
      return;
    }

    // Validate file size (50MB)
    if (selectedFile.size > 50 * 1024 * 1024) {
      setError('File size must be less than 50MB');
      return;
    }

    setFile(selectedFile);
    setError('');
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file');
      return;
    }

    if (!companyName.trim()) {
      setError('Please enter company name');
      return;
    }

    setLoading(true);
    setError('');
    setProgress(0);

    // Simulate progress (since we can't track actual upload progress easily)
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 10;
      });
    }, 300);

    try {
      await reportService.uploadReport(
        file,
        companyName,
        reportYear ? parseInt(reportYear) : undefined
      );
      
      clearInterval(progressInterval);
      setProgress(100);
      setSuccess(true);
      
      setTimeout(() => {
        onUploadComplete();
      }, 1500);
    } catch (err: unknown) {
      clearInterval(progressInterval);
      setProgress(0);
      setError(getErrorMessage(err) || 'Upload failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const removeFile = () => {
    setFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <form onSubmit={handleSubmit} className="upload-form">
      <p className="upload-modal-description">
        Upload a PDF annual report to automatically extract and analyze financial data using AI.
      </p>

      {error && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          border: '2px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '12px',
          padding: '1rem',
          display: 'flex',
          alignItems: 'start',
          animation: 'fadeIn 0.2s ease-out'
        }}>
          <AlertCircle style={{ width: '1.25rem', height: '1.25rem', color: '#ef4444', marginRight: '0.75rem', flexShrink: 0, marginTop: '0.125rem' }} />
          <div style={{ flex: 1 }}>
            <p style={{ fontSize: '0.875rem', fontWeight: 600, color: '#fca5a5' }}>{error}</p>
          </div>
          <button
            type="button"
            onClick={() => setError('')}
            style={{
              color: '#fca5a5',
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              transition: 'color 0.2s'
            }}
            onMouseEnter={(e) => e.currentTarget.style.color = '#ef4444'}
            onMouseLeave={(e) => e.currentTarget.style.color = '#fca5a5'}
            aria-label="Dismiss error"
          >
            <X style={{ width: '1rem', height: '1rem' }} />
          </button>
        </div>
      )}

      {success && (
        <div style={{
          background: 'rgba(34, 197, 94, 0.1)',
          border: '2px solid rgba(34, 197, 94, 0.3)',
          borderRadius: '12px',
          padding: '1rem',
          display: 'flex',
          alignItems: 'start',
          animation: 'fadeIn 0.2s ease-out'
        }}>
          <CheckCircle style={{ width: '1.25rem', height: '1.25rem', color: '#22c55e', marginRight: '0.75rem', flexShrink: 0, marginTop: '0.125rem' }} />
          <p style={{ fontSize: '0.875rem', fontWeight: 600, color: '#86efac' }}>
            Report uploaded successfully! Processing will begin shortly.
          </p>
        </div>
      )}

      <div>
        <label className="block text-sm font-bold mb-3" style={{ color: '#e2e8f0' }}>
          Company Name <span style={{ color: '#ef4444' }}>*</span>
        </label>
        <input
          type="text"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          className="upload-form-input"
          placeholder="e.g., Apple Inc., Tesla, Microsoft"
          required
          disabled={loading || success}
        />
      </div>

      <div>
        <label className="block text-sm font-bold mb-3" style={{ color: '#e2e8f0' }}>
          Report Year <span className="text-sm font-normal" style={{ color: '#94a3b8' }}>(Optional)</span>
        </label>
        <input
          type="number"
          value={reportYear}
          onChange={(e) => setReportYear(e.target.value)}
          className="upload-form-input"
          placeholder="2024"
          min="2000"
          max="2030"
          disabled={loading || success}
        />
      </div>

      <div>
        <label className="block text-sm font-bold mb-3" style={{ color: '#e2e8f0' }}>
          Annual Report (PDF) <span style={{ color: '#ef4444' }}>*</span>
        </label>
        
        <div
          className={`upload-file-area ${dragActive ? 'drag-active' : ''} ${loading || success ? 'opacity-50 cursor-not-allowed' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => !loading && !success && fileInputRef.current?.click()}
        >
          <div className="space-y-3 text-center">
            <Upload className="upload-file-icon" />
            <div className="flex flex-col text-sm">
              <span className="upload-file-text">
                Click to upload
              </span>
              <p className="upload-file-subtext">or drag and drop</p>
            </div>
            <p className="upload-file-subtext text-xs">PDF file up to 50MB</p>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            className="upload-file-input"
            accept=".pdf"
            onChange={handleFileChange}
            disabled={loading || success}
          />
        </div>

        {file && (
          <div className="upload-file-selected">
            <File className="h-6 w-6" style={{ color: '#8b5cf6' }} />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold truncate" style={{ color: '#e2e8f0' }}>{file.name}</p>
              <p className="text-xs font-medium" style={{ color: '#94a3b8' }}>{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
            {!loading && !success && (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  removeFile();
                }}
                className="ml-4 p-2 rounded-lg transition-all duration-200"
                style={{ color: '#94a3b8' }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.color = '#ef4444';
                  e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.color = '#94a3b8';
                  e.currentTarget.style.background = 'transparent';
                }}
                aria-label="Remove file"
              >
                <X className="h-5 w-5" />
              </button>
            )}
          </div>
        )}
      </div>

      {loading && progress > 0 && (
        <div className="upload-progress">
          <div className="upload-progress-text flex justify-between">
            <span>Uploading...</span>
            <span>{progress}%</span>
          </div>
          <div className="upload-progress-bar">
            <div
              className="upload-progress-bar-fill"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      <button
        type="submit"
        disabled={loading || success || !file}
        className="upload-btn-primary"
      >
        {loading ? (
          <span className="flex items-center">
            <svg className="upload-btn-icon spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Processing Report...
          </span>
        ) : success ? (
          <span className="flex items-center">
            <CheckCircle className="upload-btn-icon" />
            Upload Complete
          </span>
        ) : (
          <span className="flex items-center">
            <Upload className="upload-btn-icon" />
            Upload & Process Report
          </span>
        )}
      </button>

      <p className="text-xs text-center font-medium" style={{ color: '#94a3b8' }}>
        The report will be processed automatically using AI to extract financial data and generate insights.
      </p>
    </form>
  );
};

export default FileUpload;
