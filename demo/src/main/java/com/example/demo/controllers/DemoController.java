package com.example.demo.controllers;

import lombok.RequiredArgsConstructor;

import org.springframework.web.bind.annotation.*;
import org.springframework.web.reactive.function.server.ServerResponse;

import com.example.demo.model.User;
import com.example.demo.service.DemoService;

import reactor.core.publisher.Mono;


@RestController
@RequestMapping("/")
@RequiredArgsConstructor
public class DemoController {

    private final DemoService handler;
    
    @GetMapping
    public Mono<String> hello() {
        return Mono.just("Hello!");
    }

    @GetMapping("/user/{id}")
    public Mono<User> findByUser(@PathVariable String id) {
        return this.handler.findUserByIdTest(id);
    }

    @GetMapping("/users")
    public Mono<ServerResponse> findAll() {
        return this.handler.findAllUsers();
    }
}