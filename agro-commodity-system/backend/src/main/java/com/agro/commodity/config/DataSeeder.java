package com.agro.commodity.config;

import com.agro.commodity.model.Commodity;
import com.agro.commodity.model.CommodityType;
import com.agro.commodity.model.PriceHistory;
import com.agro.commodity.repository.CommodityRepository;
import com.agro.commodity.repository.PriceHistoryRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Component
@RequiredArgsConstructor
@Slf4j
public class DataSeeder implements CommandLineRunner {

    private final CommodityRepository commodityRepository;
    private final PriceHistoryRepository priceHistoryRepository;

    @Override
    public void run(String... args) {
        if (commodityRepository.count() > 0) return;

        log.info("Populando banco de dados com commodities iniciais...");

        List<Commodity> commodities = List.of(
            buildCommodity("Soja", "SOY",  CommodityType.GRAOS,           "128.50", "123.20", "saca 60kg",  "Mato Grosso"),
            buildCommodity("Milho","CORN", CommodityType.GRAOS,            "72.30",  "74.80",  "saca 60kg",  "Paraná"),
            buildCommodity("Trigo","WHET", CommodityType.GRAOS,            "89.70",  "88.10",  "saca 60kg",  "Rio Grande do Sul"),
            buildCommodity("Café Arábica","COFA",CommodityType.CAFE,      "1450.00","1380.00","saca 60kg",  "Minas Gerais"),
            buildCommodity("Algodão","COTT",CommodityType.FIBRAS,         "3.85",   "3.92",   "arroba",     "Bahia"),
            buildCommodity("Açúcar Cristal","SUG",CommodityType.ACUCAR_ALCOOL,"148.00","145.50","saca 50kg","São Paulo"),
            buildCommodity("Boi Gordo","BEEF",CommodityType.CARNES,       "265.00", "258.00", "arroba",     "Mato Grosso do Sul"),
            buildCommodity("Etanol","ETHL",CommodityType.ACUCAR_ALCOOL,   "3.42",   "3.38",   "litro",      "São Paulo"),
            buildCommodity("Arroz","RICE", CommodityType.GRAOS,            "76.20",  "74.90",  "saca 50kg",  "Rio Grande do Sul"),
            buildCommodity("Frango","CHKN",CommodityType.CARNES,          "5.80",   "5.65",   "kg",         "Santa Catarina")
        );

        commodityRepository.saveAll(commodities);

        // Seed price history (last 30 days)
        commodities.forEach(c -> {
            BigDecimal basePrice = c.getCurrentPrice();
            for (int i = 30; i >= 1; i--) {
                BigDecimal variation = BigDecimal.valueOf((Math.random() - 0.5) * 0.04);
                BigDecimal price = basePrice.multiply(BigDecimal.ONE.add(variation))
                        .setScale(2, java.math.RoundingMode.HALF_UP);

                PriceHistory ph = PriceHistory.builder()
                        .commodity(c)
                        .price(price)
                        .recordedAt(LocalDateTime.now().minusDays(i))
                        .source("SEED")
                        .build();
                priceHistoryRepository.save(ph);
            }
        });

        log.info("Dados iniciais carregados: {} commodities", commodities.size());
    }

    private Commodity buildCommodity(String name, String code, CommodityType type,
                                      String price, String prevPrice, String unit, String region) {
        Commodity c = Commodity.builder()
                .name(name)
                .code(code)
                .type(type)
                .currentPrice(new BigDecimal(price))
                .previousPrice(new BigDecimal(prevPrice))
                .unit(unit)
                .currency("BRL")
                .originRegion(region)
                .build();
        c.setCreatedAt(LocalDateTime.now());
        c.setLastUpdated(LocalDateTime.now());
        return c;
    }
}
