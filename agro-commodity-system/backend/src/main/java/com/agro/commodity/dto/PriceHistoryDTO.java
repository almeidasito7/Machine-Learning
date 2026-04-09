package com.agro.commodity.dto;

import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PriceHistoryDTO {
    private Long id;
    private Long commodityId;
    private String commodityName;
    private BigDecimal price;
    private LocalDateTime recordedAt;
    private String source;
    private String notes;
}
