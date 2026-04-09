package com.agro.commodity.controller;

import com.agro.commodity.dto.CommodityDTO;
import com.agro.commodity.dto.PriceHistoryDTO;
import com.agro.commodity.model.CommodityType;
import com.agro.commodity.service.CommodityService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.net.URI;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/commodities")
@RequiredArgsConstructor
@Tag(name = "Commodities", description = "Gerenciamento de commodities agrícolas")
@CrossOrigin(origins = {"http://localhost:4200", "http://localhost:3000"})
public class CommodityController {

    private final CommodityService commodityService;

    @GetMapping
    @Operation(summary = "Listar todas as commodities")
    public ResponseEntity<List<CommodityDTO>> findAll() {
        return ResponseEntity.ok(commodityService.findAll());
    }

    @GetMapping("/{id}")
    @Operation(summary = "Buscar commodity por ID")
    public ResponseEntity<CommodityDTO> findById(@PathVariable Long id) {
        return ResponseEntity.ok(commodityService.findById(id));
    }

    @GetMapping("/type/{type}")
    @Operation(summary = "Listar commodities por tipo")
    public ResponseEntity<List<CommodityDTO>> findByType(@PathVariable CommodityType type) {
        return ResponseEntity.ok(commodityService.findByType(type));
    }

    @GetMapping("/search")
    @Operation(summary = "Buscar commodities por nome")
    public ResponseEntity<List<CommodityDTO>> search(@RequestParam String term) {
        return ResponseEntity.ok(commodityService.search(term));
    }

    @PostMapping
    @Operation(summary = "Cadastrar nova commodity")
    public ResponseEntity<CommodityDTO> create(@Valid @RequestBody CommodityDTO dto) {
        CommodityDTO created = commodityService.create(dto);
        return ResponseEntity.created(URI.create("/api/commodities/" + created.getId())).body(created);
    }

    @PutMapping("/{id}")
    @Operation(summary = "Atualizar commodity")
    public ResponseEntity<CommodityDTO> update(@PathVariable Long id, @Valid @RequestBody CommodityDTO dto) {
        return ResponseEntity.ok(commodityService.update(id, dto));
    }

    @PatchMapping("/{id}/price")
    @Operation(summary = "Atualizar preço da commodity")
    public ResponseEntity<CommodityDTO> updatePrice(
            @PathVariable Long id,
            @RequestBody Map<String, BigDecimal> body) {
        BigDecimal newPrice = body.get("price");
        if (newPrice == null) {
            return ResponseEntity.badRequest().build();
        }
        return ResponseEntity.ok(commodityService.updatePrice(id, newPrice));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Remover commodity")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        commodityService.delete(id);
        return ResponseEntity.noContent().build();
    }

    // ─── Price History ────────────────────────────────────────────────────────

    @GetMapping("/{id}/history")
    @Operation(summary = "Histórico de preços da commodity")
    public ResponseEntity<List<PriceHistoryDTO>> getPriceHistory(
            @PathVariable Long id,
            @RequestParam(defaultValue = "30") int limit) {
        return ResponseEntity.ok(commodityService.getPriceHistory(id, limit));
    }

    @GetMapping("/{id}/history/range")
    @Operation(summary = "Histórico de preços por período")
    public ResponseEntity<List<PriceHistoryDTO>> getPriceHistoryRange(
            @PathVariable Long id,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime start,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime end) {
        return ResponseEntity.ok(commodityService.getPriceHistoryBetween(id, start, end));
    }
}
