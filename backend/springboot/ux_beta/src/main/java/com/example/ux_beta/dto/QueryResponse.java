package com.example.ux_beta;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

public class QueryResponse {
    private String question;
    @JsonProperty("relevant_context")
    private List<String> relevant_context;
    private List<Map<String, Object>> metadata;
    private String answer;
    private List<String> sources;
    @JsonProperty("llm_endpoint")
    private String llm_endpoint;

    public String getQuestion() { return question; }
    public void setQuestion(String question) { this.question = question; }
    public List<String> getRelevant_context() { return relevant_context; }
    public void setRelevant_context(List<String> relevant_context) { this.relevant_context = relevant_context; }
    public List<Map<String, Object>> getMetadata() { return metadata; }
    public void setMetadata(List<Map<String, Object>> metadata) { this.metadata = metadata; }
    public String getAnswer() { return answer; }
    public void setAnswer(String answer) { this.answer = answer; }
    public List<String> getSources() { return sources; }
    public void setSources(List<String> sources) { this.sources = sources; }
    public String getLlm_endpoint() { return llm_endpoint; }
    public void setLlm_endpoint(String llm_endpoint) { this.llm_endpoint = llm_endpoint; }
} 