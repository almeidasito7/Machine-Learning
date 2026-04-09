package com.agro.commodity.repository;

import com.agro.commodity.model.MarketAlert;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface MarketAlertRepository extends JpaRepository<MarketAlert, Long> {

    List<MarketAlert> findByCommodityIdAndActiveTrue(Long commodityId);

    List<MarketAlert> findByActiveTrueAndTriggeredFalse();

    List<MarketAlert> findByTriggeredTrue();
}
