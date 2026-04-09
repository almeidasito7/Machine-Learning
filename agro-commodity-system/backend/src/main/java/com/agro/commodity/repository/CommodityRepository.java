package com.agro.commodity.repository;

import com.agro.commodity.model.Commodity;
import com.agro.commodity.model.CommodityType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface CommodityRepository extends JpaRepository<Commodity, Long> {

    Optional<Commodity> findByCode(String code);

    List<Commodity> findByType(CommodityType type);

    List<Commodity> findByNameContainingIgnoreCase(String name);

    @Query("SELECT c FROM Commodity c ORDER BY c.currentPrice DESC")
    List<Commodity> findAllOrderByPriceDesc();

    @Query("SELECT c FROM Commodity c WHERE ABS((c.currentPrice - c.previousPrice) / c.previousPrice * 100) > :threshold")
    List<Commodity> findByPriceVariationAbove(double threshold);

    boolean existsByCode(String code);
}
