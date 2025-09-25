package com.example.demovt.controllers;

import java.util.Optional;
import java.util.concurrent.CompletableFuture;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import com.example.demovt.model.User;
import com.example.demovt.service.UsuarioService;

import io.swagger.v3.oas.annotations.Operation;


@RestController
public class Controller {

    private final UsuarioService service;

    public Controller(UsuarioService service) {
        this.service = service;
    }

    @GetMapping("/{id}")
    @Operation(summary = "Buscar usuário por ID", description = "Retorna um usuário armazenado no MongoDB com cache Redis.")
    public Optional<User> getUsuario(@PathVariable String id) {
        return service.buscarPorId(id);
    }

    @PostMapping
    @Operation(summary = "Criar novo usuário", description = "Cria e armazena um usuário no MongoDB e limpa o cache Redis.")
    public User criar(@RequestBody User usuario) {
        return service.salvar(usuario);
    }

    @GetMapping("/usuarios/{id}")
    public CompletableFuture<User> getUsuarioFuture(@PathVariable String id) {
        return service.buscarUsuario(id);
    }
    
    @GetMapping("/usuarios-async/{id}")
    public CompletableFuture<User> getUsuarioAsync(@PathVariable String id) {
        return service.buscarUsuarioAsync(id);
    }

}