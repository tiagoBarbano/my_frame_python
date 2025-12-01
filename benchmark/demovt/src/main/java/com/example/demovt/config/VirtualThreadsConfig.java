package com.example.demovt.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.scheduling.annotation.EnableAsync;

import java.util.concurrent.Executor;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@Configuration
@EnableAsync
public class VirtualThreadsConfig {

    // Executor para @Async (virtual threads per task)
    @Bean(name = "vtExecutor")
    @Primary
    public Executor vtExecutor() {
        return Executors.newThreadPerTaskExecutor(Thread.ofVirtual().name("vt-", 0).factory());
    }

    // Executor fixo para CPU-bound (JEXL)
    @Bean(name = "cpuBoundExecutor")
    public ExecutorService cpuBoundExecutor() {
        int procs = Math.max(1, Runtime.getRuntime().availableProcessors());
        return Executors.newFixedThreadPool(procs, r -> {
            Thread t = new Thread(r);
            t.setName("cpu-pool-" + t.getId());
            t.setDaemon(true);
            return t;
        });
    }
}