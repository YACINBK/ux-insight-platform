package com.example.ux_beta;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

public class QueryRequest {
    private String question;
    @JsonProperty("num_results")
    private Integer num_results = 3;
    @JsonProperty("include_metadata")
    private Boolean include_metadata = false;
    @JsonProperty("tracked_data")
    private List<Map<String, Object>> tracked_data;

    public String getQuestion() { return question; }
    public void setQuestion(String question) { this.question = question; }
    public Integer getNum_results() { return num_results; }
    public void setNum_results(Integer num_results) { this.num_results = num_results; }
    public Boolean getInclude_metadata() { return include_metadata; }
    public void setInclude_metadata(Boolean include_metadata) { this.include_metadata = include_metadata; }
    public List<Map<String, Object>> getTracked_data() { return tracked_data; }
    public void setTracked_data(List<Map<String, Object>> tracked_data) { this.tracked_data = tracked_data; }
} 