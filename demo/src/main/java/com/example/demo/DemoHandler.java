package com.example.demo;

import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.server.ServerRequest;
import org.springframework.web.reactive.function.server.ServerResponse;

import com.example.demo.model.User;
import com.example.demo.repository.UserRepository;

import lombok.extern.java.Log;
import reactor.core.publisher.Mono;

@Log
@Component
public class DemoHandler {
    private final UserRepository repository;

    public DemoHandler(UserRepository repository) {
        this.repository = repository;
    }

    public Mono<ServerResponse> hello(ServerRequest request) {
        return ServerResponse.ok().bodyValue("Hello, WebFlux!");
    }

    public Mono<ServerResponse> findByUser(ServerRequest request) {
        String id = request.pathVariable("id");
        return repository.findById(id)
                .flatMap(user -> ServerResponse.ok().bodyValue(user))
                .switchIfEmpty(ServerResponse.noContent().build());
    }

    public Mono<ServerResponse> findAllUsers(ServerRequest request) {
        return ServerResponse.ok().body(repository.findAll(), User.class);
    }
}
