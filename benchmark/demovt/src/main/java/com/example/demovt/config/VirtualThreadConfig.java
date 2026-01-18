// package com.example.demovt.config;

// import java.util.concurrent.ExecutorService;
// import java.util.concurrent.Executors;

// import org.springframework.context.annotation.Bean;
// import org.springframework.context.annotation.Configuration;
// import org.springframework.core.task.AsyncTaskExecutor;
// import org.springframework.scheduling.concurrent.ConcurrentTaskExecutor;
// import org.springframework.web.servlet.config.annotation.AsyncSupportConfigurer;
// import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

// @Configuration
// public class VirtualThreadConfig implements WebMvcConfigurer {

//     // cria um ExecutorService que cria uma virtual thread por tarefa
//     @Bean(destroyMethod = "close")
//     public ExecutorService virtualThreadExecutorService() {
//         return Executors.newVirtualThreadPerTaskExecutor();
//     }

//     // adapta para AsyncTaskExecutor (usado pelo Spring MVC Async)
//     @Bean
//     public AsyncTaskExecutor mvcAsyncTaskExecutor(ExecutorService virtualThreadExecutorService) {
//         return new ConcurrentTaskExecutor(virtualThreadExecutorService);
//     }

//     @Override
//     public void configureAsyncSupport(AsyncSupportConfigurer configurer) {
//         // configura Spring MVC para usar nosso executor de virtual threads
//         configurer.setTaskExecutor(mvcAsyncTaskExecutor(virtualThreadExecutorService()));
//         // opcional: timeout (em ms) - 0 = sem timeout por padrão
//         configurer.setDefaultTimeout(0);
//     }
// }