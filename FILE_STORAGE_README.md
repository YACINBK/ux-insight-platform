# 📁 File Storage System Documentation

## Overview

The Premium Auto Mode feature includes a comprehensive file storage system that handles all files generated during website analysis, including screenshots, analysis results, and temporary files.

## 🗂️ Directory Structure

```
uploads/
├── screenshots/          # Website screenshots
│   ├── analysis_id_timestamp_filename.png
│   └── ...
├── analysis-results/     # JSON analysis results
│   ├── analysis_analysis_id_timestamp.json
│   └── ...
└── temp/                 # Temporary files
    ├── uuid.ext
    └── ...
```

## 🔧 Configuration

File storage is configured in `application.properties`:

```properties
# File Storage Configuration
app.file.storage.base-path=./uploads
app.file.storage.screenshots=screenshots
app.file.storage.analysis-results=analysis-results
app.file.storage.temp=temp
app.file.storage.max-file-size=10MB
app.file.storage.cleanup-enabled=true
app.file.storage.retention-days=30
```

## 📊 Database Integration

### Analysis Entity
- Tracks each analysis session with unique ID
- Stores file paths and analysis metadata
- Links to associated files through AnalysisFile entity

### AnalysisFile Entity
- Tracks individual files (screenshots, results, temp files)
- Stores file metadata (size, type, path)
- Links back to Analysis entity

## 🚀 How It Works

### 1. Analysis Initiation
```java
// Create analysis record
Analysis analysis = new Analysis(analysisId, url);
analysis.markInProgress();
analysis = analysisRepository.save(analysis);
```

### 2. File Storage
```java
// Save analysis results
String resultsFilename = fileStorageService.saveAnalysisResults(analysisId, jsonContent);

// Save screenshots
String screenshotFilename = fileStorageService.saveScreenshot(imageData, analysisId, "fullpage");
```

### 3. Database Tracking
```java
// Update analysis with file paths
analysis.setAnalysisResultsPath(resultsFilename);
analysis.setScreenshotsPath(screenshotsPath);
analysis.markCompleted();
analysisRepository.save(analysis);
```

## 🧹 Automatic Cleanup

The system automatically cleans up old files based on retention policy:

- **Retention Period**: 30 days (configurable)
- **Cleanup Process**: Runs automatically
- **File Types**: Screenshots, analysis results, temp files
- **Database**: Analysis records are preserved

## 📈 Storage Statistics

The system provides storage statistics:

```java
StorageStats stats = fileStorageService.getStorageStats();
// Returns: file counts, total size, formatted sizes
```

## 🔄 Automation Script Integration

The automation script (`automation_script.js`) integrates with the file storage system:

1. **Takes screenshots** → Saves to local directory
2. **Collects metrics** → Generates analysis data
3. **Sends to backend** → Backend saves to proper storage
4. **Database tracking** → Links files to analysis session

## 🛡️ Security & Validation

- **File Type Validation**: Only allowed file types
- **Size Limits**: Configurable maximum file sizes
- **Path Sanitization**: Prevents directory traversal
- **Access Control**: Files stored outside web root

## 📋 File Types Handled

### Screenshots
- **Format**: PNG
- **Naming**: `{analysis_id}_{timestamp}_{type}.png`
- **Types**: Full page, viewport

### Analysis Results
- **Format**: JSON
- **Naming**: `analysis_{analysis_id}_{timestamp}.json`
- **Content**: Metrics, recommendations, metadata

### Temporary Files
- **Format**: Various (uploads, processing)
- **Naming**: `{uuid}.{extension}`
- **Cleanup**: Automatic after processing

## 🔍 Retrieving Files

### By Analysis ID
```java
// Get analysis results
String results = fileStorageService.getAnalysisResults(analysisId);

// Get screenshots
List<String> screenshots = fileStorageService.getAnalysisScreenshots(analysisId);
```

### By File Path
```java
// Get file content
byte[] content = fileStorageService.getFileContent(filePath);
```

## 🚨 Error Handling

- **File Not Found**: Returns appropriate error messages
- **Storage Full**: Logs warnings, continues operation
- **Permission Issues**: Graceful degradation
- **Database Errors**: File operations continue independently

## 📝 Best Practices

1. **Always use analysis IDs** for file naming
2. **Include timestamps** to prevent conflicts
3. **Validate file types** before storage
4. **Monitor storage usage** regularly
5. **Backup important files** outside the system
6. **Use cleanup policies** to manage storage

## 🔧 Maintenance

### Manual Cleanup
```java
fileStorageService.cleanupOldFiles();
```

### Storage Monitoring
```java
StorageStats stats = fileStorageService.getStorageStats();
System.out.println("Total storage: " + stats.getFormattedTotalSize());
```

### Database Maintenance
```sql
-- Check analysis status
SELECT status, COUNT(*) FROM analyses GROUP BY status;

-- Find large files
SELECT filename, file_size FROM analysis_files ORDER BY file_size DESC LIMIT 10;
```

## 🎯 Future Enhancements

- **Cloud Storage Integration**: AWS S3, Google Cloud Storage
- **File Compression**: Automatic compression for large files
- **CDN Integration**: Fast file delivery
- **Backup System**: Automated backups
- **File Versioning**: Track file changes over time 