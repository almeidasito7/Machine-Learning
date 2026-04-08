package com.agro.commodity.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AIAnalysisRequest {
    private String question;
    private Long commodityId;     // optional: specific commodity context
    private String analysisType;  // MARKET_ANALYSIS, PRICE_PREDICTION, RECOMMENDATION, CHAT
}
