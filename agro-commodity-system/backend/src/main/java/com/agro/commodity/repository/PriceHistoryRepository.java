package com.agro.commodity.repository;

import com.agro.commodity.model.PriceHistory;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface PriceHistoryRepository extends JpaRepository<PriceHistory, Long> {

    List<PriceHistory> findByCommodityIdOrderByRecordedAtDesc(Long commodityId);

    List<PriceHistory> findByCommodityIdOrderByRecordedAtDesc(Long commodityId, Pageable pageable);

    List<PriceHistory> findByCommodityIdAndRecordedAtBetweenOrderByRecordedAt(
            Long commodityId, LocalDateTime start, LocalDateTime end);

    @Query("SELECT ph FROM PriceHistory ph WHERE ph.commodity.id = :commodityId ORDER BY ph.recordedAt DESC")
    List<PriceHistory> findLatestByCommodity(Long commodityId, Pageable pageable);
}
