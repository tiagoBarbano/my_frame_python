package com.example.demovt.controllers;

import java.io.IOException;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import com.example.demovt.model.User;
import com.example.demovt.service.UsuarioService;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.swagger.v3.oas.annotations.Operation;
import jakarta.servlet.http.HttpServletRequest;
import java.io.InputStream;

@RestController
public class Controller {

    private final UsuarioService service;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public Controller(UsuarioService service) {
        this.service = service;
    }

    @GetMapping
    public String hello() {
        return "Hello World!";
    }

    @GetMapping("usuarios-sync/{id}")
    @Operation(summary = "Buscar usuário por ID", description = "Retorna um usuário armazenado no MongoDB com cache Redis.")
    public Optional<User> getUsuario(@PathVariable String id) {
        return service.buscarPorId(id);
    }

    @PostMapping("/usuarios")
    @Operation(summary = "Criar novo usuário", description = "Cria e armazena um usuário no MongoDB e limpa o cache Redis.")
    public User criar(@RequestBody User usuario) {
        return service.salvar(usuario);
    }

    @GetMapping("/usuarios-future/{id}")
    public CompletableFuture<User> getUsuarioFuture(@PathVariable String id) {
        return service.buscarUsuario(id);
    }

    @GetMapping("/usuarios-async/{id}")
    public CompletableFuture<User> getUsuarioAsync(@PathVariable String id) {
        return service.buscarUsuarioAsync(id);
    }

    @PostMapping("/process")
    public ResponseEntity<Map<String, Object>> process(HttpServletRequest request) throws IOException {
        InputStream inputStream = request.getInputStream();
        Map<String, Object> body = objectMapper.readValue(inputStream, Map.class);
        Map<String, Object> res = processBody(body);
        return ResponseEntity.ok(res);
    }

    private Map<String, Object> processBody(Map<String, Object> body) {
        return body;
    }
}