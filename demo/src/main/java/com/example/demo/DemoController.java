package com.example.demo;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.server.RouterFunction;

import static org.springframework.web.reactive.function.server.RouterFunctions.route;
import static org.springframework.web.reactive.function.server.RequestPredicates.GET;

@Configuration
public class DemoController {
    @Bean
    public RouterFunction<?> routes(DemoHandler handler) {
        return route(GET("/"), handler::hello)
                .andRoute(GET("/user/{id}"), handler::findByUser)
                .andRoute(GET("/users"),handler::findAllUsers);
    }

}
