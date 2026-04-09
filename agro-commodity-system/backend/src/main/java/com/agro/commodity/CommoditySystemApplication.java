package com.agro.commodity;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class CommoditySystemApplication {

    public static void main(String[] args) {
        SpringApplication.run(CommoditySystemApplication.class, args);
    }
}
