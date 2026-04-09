package com.agro.commodity.model;

import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "market_alerts")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MarketAlert {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "commodity_id", nullable = false)
    private Commodity commodity;

    @Enumerated(EnumType.STRING)
    private AlertType alertType;

    @Column(precision = 15, scale = 4)
    private BigDecimal thresholdPrice;

    @Column(columnDefinition = "TEXT")
    private String message;

    private boolean triggered = false;

    private boolean active = true;

    private LocalDateTime createdAt;

    private LocalDateTime triggeredAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }

    public enum AlertType {
        PRICE_ABOVE, PRICE_BELOW, VARIATION_PERCENT, AI_RECOMMENDATION
    }
}
