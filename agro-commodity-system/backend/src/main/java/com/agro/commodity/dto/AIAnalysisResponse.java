package com.agro.commodity.dto;

import lombok.*;

import java.time.LocalDateTime;
import java.util.List;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AIAnalysisResponse {
    private String answer;
    private String analysisType;
    private List<String> insights;
    private List<String> recommendations;
    private String sentiment;        // BULLISH, BEARISH, NEUTRAL
    private Double confidenceScore;
    private LocalDateTime generatedAt;
    private String modelUsed;
    private List<WorkflowStep> workflowSteps; // LangGraph steps
}
