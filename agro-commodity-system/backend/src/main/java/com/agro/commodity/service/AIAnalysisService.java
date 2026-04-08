package com.agro.commodity.service;

import com.agro.commodity.ai.LangGraphWorkflow;
import com.agro.commodity.dto.AIAnalysisRequest;
import com.agro.commodity.dto.AIAnalysisResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
@Slf4j
public class AIAnalysisService {

    private final LangGraphWorkflow langGraphWorkflow;
    private final CommodityService commodityService;

    public AIAnalysisResponse analyze(AIAnalysisRequest request) {
        log.info("AI analysis request: type={}, commodityId={}", request.getAnalysisType(), request.getCommodityId());

        String context = buildContext(request);

        return switch (request.getAnalysisType() != null ? request.getAnalysisType() : "CHAT") {
            case "MARKET_ANALYSIS", "PRICE_PREDICTION", "RECOMMENDATION" ->
                    langGraphWorkflow.runAnalysisWorkflow(request.getQuestion(), context);
            default ->
                    langGraphWorkflow.runChatWorkflow(request.getQuestion(), context);
        };
    }

    private String buildContext(AIAnalysisRequest request) {
        try {
            if (request.getCommodityId() != null) {
                return commodityService.buildCommodityContextSummary(request.getCommodityId());
            }
            return commodityService.buildMarketContextSummary();
        } catch (Exception e) {
            log.warn("Could not build context: {}", e.getMessage());
            return "";
        }
    }
}
