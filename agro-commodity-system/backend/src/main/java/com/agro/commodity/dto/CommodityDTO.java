package com.agro.commodity.dto;

import com.agro.commodity.model.CommodityType;
import jakarta.validation.constraints.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CommodityDTO {

    private Long id;

    @NotBlank(message = "Nome é obrigatório")
    private String name;

    @NotBlank(message = "Código é obrigatório")
    private String code;

    @NotNull(message = "Tipo é obrigatório")
    private CommodityType type;

    @NotNull(message = "Preço atual é obrigatório")
    @DecimalMin(value = "0.0", message = "Preço deve ser positivo")
    private BigDecimal currentPrice;

    private BigDecimal previousPrice;

    @NotBlank(message = "Unidade é obrigatória")
    private String unit;

    private String currency;

    private String description;

    private String originRegion;

    private LocalDateTime lastUpdated;

    private LocalDateTime createdAt;

    private BigDecimal priceVariation;

    private String priceVariationFormatted;
}
