package com.example.ux_beta;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.List;
import java.util.ArrayList;

@Entity
@Table(name = "analyses")
public class Analysis {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String analysisId; // UUID for the analysis session
    
    @Column(nullable = false)
    private String url;
    
    @Column(nullable = false)
    private String status; // PENDING, IN_PROGRESS, COMPLETED, FAILED
    
    @Column(columnDefinition = "TEXT")
    private String resultsJson; // JSON results from analysis
    
    @Column
    private String screenshotsPath; // Path to screenshots directory
    
    @Column
    private String analysisResultsPath; // Path to analysis results file
    
    @Column(nullable = false)
    private Instant createdAt;
    
    @Column
    private Instant completedAt;
    
    @Column
    private String errorMessage;
    
    @Column
    private String analysisType; // DEMO, REAL
    
    @OneToMany(mappedBy = "analysis", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<AnalysisFile> files = new ArrayList<>();
    
    // Constructors
    public Analysis() {}
    
    public Analysis(String analysisId, String url) {
        this.analysisId = analysisId;
        this.url = url;
        this.status = "PENDING";
        this.createdAt = Instant.now();
        this.analysisType = "DEMO";
    }
    
    // Getters and Setters
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public String getAnalysisId() {
        return analysisId;
    }
    
    public void setAnalysisId(String analysisId) {
        this.analysisId = analysisId;
    }
    
    public String getUrl() {
        return url;
    }
    
    public void setUrl(String url) {
        this.url = url;
    }
    
    public String getStatus() {
        return status;
    }
    
    public void setStatus(String status) {
        this.status = status;
    }
    
    public String getResultsJson() {
        return resultsJson;
    }
    
    public void setResultsJson(String resultsJson) {
        this.resultsJson = resultsJson;
    }
    
    public String getScreenshotsPath() {
        return screenshotsPath;
    }
    
    public void setScreenshotsPath(String screenshotsPath) {
        this.screenshotsPath = screenshotsPath;
    }
    
    public String getAnalysisResultsPath() {
        return analysisResultsPath;
    }
    
    public void setAnalysisResultsPath(String analysisResultsPath) {
        this.analysisResultsPath = analysisResultsPath;
    }
    
    public Instant getCreatedAt() {
        return createdAt;
    }
    
    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }
    
    public Instant getCompletedAt() {
        return completedAt;
    }
    
    public void setCompletedAt(Instant completedAt) {
        this.completedAt = completedAt;
    }
    
    public String getErrorMessage() {
        return errorMessage;
    }
    
    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }
    
    public String getAnalysisType() {
        return analysisType;
    }
    
    public void setAnalysisType(String analysisType) {
        this.analysisType = analysisType;
    }
    
    public List<AnalysisFile> getFiles() {
        return files;
    }
    
    public void setFiles(List<AnalysisFile> files) {
        this.files = files;
    }
    
    // Helper methods
    public void markCompleted() {
        this.status = "COMPLETED";
        this.completedAt = Instant.now();
    }
    
    public void markFailed(String errorMessage) {
        this.status = "FAILED";
        this.errorMessage = errorMessage;
        this.completedAt = Instant.now();
    }
    
    public void markInProgress() {
        this.status = "IN_PROGRESS";
    }
    
    public boolean isCompleted() {
        return "COMPLETED".equals(this.status);
    }
    
    public boolean isFailed() {
        return "FAILED".equals(this.status);
    }
    
    public boolean isPending() {
        return "PENDING".equals(this.status);
    }
    
    public boolean isInProgress() {
        return "IN_PROGRESS".equals(this.status);
    }
} 