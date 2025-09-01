package com.example.ux_beta;

import java.util.List;

public class DashboardStats {
    private long totalQuestions;
    private long totalAttachments;
    private List<RecentQuestionProjection> recentQuestions;

    public long getTotalQuestions() { return totalQuestions; }
    public void setTotalQuestions(long totalQuestions) { this.totalQuestions = totalQuestions; }
    public long getTotalAttachments() { return totalAttachments; }
    public void setTotalAttachments(long totalAttachments) { this.totalAttachments = totalAttachments; }
    public List<RecentQuestionProjection> getRecentQuestions() { return recentQuestions; }
    public void setRecentQuestions(List<RecentQuestionProjection> recentQuestions) { this.recentQuestions = recentQuestions; }
} 