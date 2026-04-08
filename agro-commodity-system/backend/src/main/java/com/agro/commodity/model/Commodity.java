package com.agro.commodity.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "commodities")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Commodity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    @Column(nullable = false, unique = true)
    private String name;

    @NotBlank
    private String code; // ex: SOY, CORN, COFFEE, COTTON, SUGAR

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private CommodityType type;

    @NotNull
    @DecimalMin("0.0")
    @Column(nullable = false, precision = 15, scale = 4)
    private BigDecimal currentPrice;

    @Column(precision = 15, scale = 4)
    private BigDecimal previousPrice;

    @Column(nullable = false)
    private String unit; // saca, tonelada, arroba

    private String currency = "BRL";

    @Column(columnDefinition = "TEXT")
    private String description;

    private String originRegion; // Mato Grosso, Paraná, etc.

    @Column(nullable = false)
    private LocalDateTime lastUpdated;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @OneToMany(mappedBy = "commodity", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    @Builder.Default
    private List<PriceHistory> priceHistory = new ArrayList<>();

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        lastUpdated = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        lastUpdated = LocalDateTime.now();
    }

    public BigDecimal getPriceVariation() {
        if (previousPrice == null || previousPrice.compareTo(BigDecimal.ZERO) == 0) {
            return BigDecimal.ZERO;
        }
        return currentPrice.subtract(previousPrice)
                .divide(previousPrice, 4, java.math.RoundingMode.HALF_UP)
                .multiply(BigDecimal.valueOf(100));
    }
}
