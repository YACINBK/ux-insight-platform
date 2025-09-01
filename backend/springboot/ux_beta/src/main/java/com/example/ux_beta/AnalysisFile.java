package com.example.ux_beta;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "analysis_files")
public class AnalysisFile {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "analysis_id", nullable = false)
    private Analysis analysis;
    
    @Column(nullable = false)
    private String filename;
    
    @Column(nullable = false)
    private String filePath;
    
    @Column(nullable = false)
    private String fileType; // SCREENSHOT, ANALYSIS_RESULT, TEMP
    
    @Column
    private String contentType;
    
    @Column
    private Long fileSize;
    
    @Column(nullable = false)
    private Instant createdAt;
    
    @Column
    private String description;
    
    // Constructors
    public AnalysisFile() {}
    
    public AnalysisFile(Analysis analysis, String filename, String filePath, String fileType) {
        this.analysis = analysis;
        this.filename = filename;
        this.filePath = filePath;
        this.fileType = fileType;
        this.createdAt = Instant.now();
    }
    
    // Getters and Setters
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public Analysis getAnalysis() {
        return analysis;
    }
    
    public void setAnalysis(Analysis analysis) {
        this.analysis = analysis;
    }
    
    public String getFilename() {
        return filename;
    }
    
    public void setFilename(String filename) {
        this.filename = filename;
    }
    
    public String getFilePath() {
        return filePath;
    }
    
    public void setFilePath(String filePath) {
        this.filePath = filePath;
    }
    
    public String getFileType() {
        return fileType;
    }
    
    public void setFileType(String fileType) {
        this.fileType = fileType;
    }
    
    public String getContentType() {
        return contentType;
    }
    
    public void setContentType(String contentType) {
        this.contentType = contentType;
    }
    
    public Long getFileSize() {
        return fileSize;
    }
    
    public void setFileSize(Long fileSize) {
        this.fileSize = fileSize;
    }
    
    public Instant getCreatedAt() {
        return createdAt;
    }
    
    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }
    
    public String getDescription() {
        return description;
    }
    
    public void setDescription(String description) {
        this.description = description;
    }
    
    // Helper methods
    public boolean isScreenshot() {
        return "SCREENSHOT".equals(this.fileType);
    }
    
    public boolean isAnalysisResult() {
        return "ANALYSIS_RESULT".equals(this.fileType);
    }
    
    public boolean isTemp() {
        return "TEMP".equals(this.fileType);
    }
    
    public String getFormattedFileSize() {
        if (fileSize == null) {
            return "Unknown";
        }
        
        if (fileSize < 1024) {
            return fileSize + " B";
        } else if (fileSize < 1024 * 1024) {
            return String.format("%.1f KB", fileSize / 1024.0);
        } else {
            return String.format("%.1f MB", fileSize / (1024.0 * 1024.0));
        }
    }
} 