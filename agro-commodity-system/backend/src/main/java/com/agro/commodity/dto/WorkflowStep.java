package com.agro.commodity.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class WorkflowStep {
    private String stepName;
    private String description;
    private String status; // COMPLETED, SKIPPED, ERROR
    private String output;
}
