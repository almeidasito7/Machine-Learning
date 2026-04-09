package com.agro.commodity.service;

import com.agro.commodity.dto.CommodityDTO;
import com.agro.commodity.dto.PriceHistoryDTO;
import com.agro.commodity.model.Commodity;
import com.agro.commodity.model.CommodityType;
import com.agro.commodity.model.PriceHistory;
import com.agro.commodity.repository.CommodityRepository;
import com.agro.commodity.repository.PriceHistoryRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class CommodityService {

    private final CommodityRepository commodityRepository;
    private final PriceHistoryRepository priceHistoryRepository;

    // ─── CRUD ─────────────────────────────────────────────────────────────────

    @Transactional(readOnly = true)
    public List<CommodityDTO> findAll() {
        return commodityRepository.findAll().stream()
                .map(this::toDTO)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public CommodityDTO findById(Long id) {
        return commodityRepository.findById(id)
                .map(this::toDTO)
                .orElseThrow(() -> new IllegalArgumentException("Commodity não encontrada: " + id));
    }

    @Transactional(readOnly = true)
    public List<CommodityDTO> findByType(CommodityType type) {
        return commodityRepository.findByType(type).stream()
                .map(this::toDTO)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<CommodityDTO> search(String term) {
        return commodityRepository.findByNameContainingIgnoreCase(term).stream()
                .map(this::toDTO)
                .collect(Collectors.toList());
    }

    public CommodityDTO create(CommodityDTO dto) {
        if (commodityRepository.existsByCode(dto.getCode())) {
            throw new IllegalArgumentException("Código já cadastrado: " + dto.getCode());
        }
        Commodity commodity = fromDTO(dto);
        commodity = commodityRepository.save(commodity);
        recordPriceHistory(commodity, "MANUAL");
        log.info("Commodity criada: {}", commodity.getCode());
        return toDTO(commodity);
    }

    public CommodityDTO update(Long id, CommodityDTO dto) {
        Commodity commodity = commodityRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Commodity não encontrada: " + id));

        boolean priceChanged = commodity.getCurrentPrice().compareTo(dto.getCurrentPrice()) != 0;

        commodity.setPreviousPrice(commodity.getCurrentPrice());
        commodity.setCurrentPrice(dto.getCurrentPrice());
        commodity.setName(dto.getName());
        commodity.setDescription(dto.getDescription());
        commodity.setOriginRegion(dto.getOriginRegion());
        commodity.setUnit(dto.getUnit());

        commodity = commodityRepository.save(commodity);

        if (priceChanged) {
            recordPriceHistory(commodity, "MANUAL");
        }
        return toDTO(commodity);
    }

    public void delete(Long id) {
        if (!commodityRepository.existsById(id)) {
            throw new IllegalArgumentException("Commodity não encontrada: " + id);
        }
        commodityRepository.deleteById(id);
        log.info("Commodity removida: {}", id);
    }

    // ─── Price Update ─────────────────────────────────────────────────────────

    public CommodityDTO updatePrice(Long id, BigDecimal newPrice) {
        Commodity commodity = commodityRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Commodity não encontrada: " + id));

        commodity.setPreviousPrice(commodity.getCurrentPrice());
        commodity.setCurrentPrice(newPrice);
        commodity = commodityRepository.save(commodity);
        recordPriceHistory(commodity, "UPDATE");
        return toDTO(commodity);
    }

    // ─── Price History ────────────────────────────────────────────────────────

    @Transactional(readOnly = true)
    public List<PriceHistoryDTO> getPriceHistory(Long commodityId, int limit) {
        return priceHistoryRepository
                .findByCommodityIdOrderByRecordedAtDesc(commodityId, PageRequest.of(0, limit))
                .stream()
                .map(this::toPriceHistoryDTO)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<PriceHistoryDTO> getPriceHistoryBetween(Long commodityId, LocalDateTime start, LocalDateTime end) {
        return priceHistoryRepository
                .findByCommodityIdAndRecordedAtBetweenOrderByRecordedAt(commodityId, start, end)
                .stream()
                .map(this::toPriceHistoryDTO)
                .collect(Collectors.toList());
    }

    // ─── Market Summary (for AI context) ──────────────────────────────────────

    @Transactional(readOnly = true)
    public String buildMarketContextSummary() {
        List<Commodity> all = commodityRepository.findAll();
        StringBuilder sb = new StringBuilder("=== RESUMO DO MERCADO DE COMMODITIES ===\n\n");

        for (Commodity c : all) {
            sb.append(String.format("%-20s | Código: %-6s | Preço: R$ %10.2f/%s | Variação: %+.2f%%\n",
                    c.getName(), c.getCode(), c.getCurrentPrice(), c.getUnit(), c.getPriceVariation()));
        }

        sb.append("\nData de referência: ").append(LocalDateTime.now());
        return sb.toString();
    }

    @Transactional(readOnly = true)
    public String buildCommodityContextSummary(Long commodityId) {
        Commodity c = commodityRepository.findById(commodityId)
                .orElseThrow(() -> new IllegalArgumentException("Commodity não encontrada: " + commodityId));

        List<PriceHistory> history = priceHistoryRepository
                .findByCommodityIdOrderByRecordedAtDesc(commodityId, PageRequest.of(0, 10));

        StringBuilder sb = new StringBuilder();
        sb.append("=== ").append(c.getName().toUpperCase()).append(" ===\n");
        sb.append("Tipo: ").append(c.getType().getLabel()).append("\n");
        sb.append("Preço atual: R$ ").append(c.getCurrentPrice()).append("/").append(c.getUnit()).append("\n");
        sb.append("Variação: ").append(String.format("%+.2f%%", c.getPriceVariation())).append("\n");

        if (c.getOriginRegion() != null) {
            sb.append("Região de origem: ").append(c.getOriginRegion()).append("\n");
        }

        if (!history.isEmpty()) {
            sb.append("\nHistórico recente:\n");
            history.forEach(ph -> sb.append(String.format("  %s → R$ %.2f\n",
                    ph.getRecordedAt().toLocalDate(), ph.getPrice())));
        }
        return sb.toString();
    }

    // ─── Mapping helpers ──────────────────────────────────────────────────────

    private void recordPriceHistory(Commodity commodity, String source) {
        PriceHistory ph = PriceHistory.builder()
                .commodity(commodity)
                .price(commodity.getCurrentPrice())
                .source(source)
                .build();
        priceHistoryRepository.save(ph);
    }

    public CommodityDTO toDTO(Commodity c) {
        BigDecimal variation = c.getPriceVariation();
        String variationFormatted = variation.compareTo(BigDecimal.ZERO) >= 0
                ? String.format("+%.2f%%", variation)
                : String.format("%.2f%%", variation);

        return CommodityDTO.builder()
                .id(c.getId())
                .name(c.getName())
                .code(c.getCode())
                .type(c.getType())
                .currentPrice(c.getCurrentPrice())
                .previousPrice(c.getPreviousPrice())
                .unit(c.getUnit())
                .currency(c.getCurrency())
                .description(c.getDescription())
                .originRegion(c.getOriginRegion())
                .lastUpdated(c.getLastUpdated())
                .createdAt(c.getCreatedAt())
                .priceVariation(variation)
                .priceVariationFormatted(variationFormatted)
                .build();
    }

    private Commodity fromDTO(CommodityDTO dto) {
        return Commodity.builder()
                .name(dto.getName())
                .code(dto.getCode().toUpperCase())
                .type(dto.getType())
                .currentPrice(dto.getCurrentPrice())
                .previousPrice(dto.getPreviousPrice())
                .unit(dto.getUnit())
                .currency(dto.getCurrency() != null ? dto.getCurrency() : "BRL")
                .description(dto.getDescription())
                .originRegion(dto.getOriginRegion())
                .build();
    }

    private PriceHistoryDTO toPriceHistoryDTO(PriceHistory ph) {
        return PriceHistoryDTO.builder()
                .id(ph.getId())
                .commodityId(ph.getCommodity().getId())
                .commodityName(ph.getCommodity().getName())
                .price(ph.getPrice())
                .recordedAt(ph.getRecordedAt())
                .source(ph.getSource())
                .notes(ph.getNotes())
                .build();
    }
}
