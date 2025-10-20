package com.example.demovt.service;

import org.springframework.cache.annotation.Cacheable;
import org.springframework.scheduling.annotation.Async;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.stereotype.Service;

import com.example.demovt.model.User;
import com.example.demovt.repository.UserRepository;

import java.util.Optional;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

@Service
public class UsuarioService {

    private final UserRepository repository;
    // Executor de virtual threads
    private final Executor executor = Executors.newVirtualThreadPerTaskExecutor();

    public UsuarioService(UserRepository repository) {
        this.repository = repository;
    }

    @Cacheable(value = "usuarios", key = "#id", unless = "#result == null")
    public Optional<User> buscarPorId(String id) {
        // System.out.println("Buscando no MongoDB...");
        return repository.findById(id);
    }

    public CompletableFuture<User> buscarUsuario(String id) {
        return CompletableFuture.supplyAsync(() -> {
            Optional<User> usuario = repository.findById(id); // MongoDB bloqueante
            return usuario.orElse(null);
        }, executor);
    }

    @Async
    public CompletableFuture<User> buscarUsuarioAsync(String id) {
        User usuario = repository.findById(id).orElse(null); // bloqueante, mas seguro em virtual thread
        return CompletableFuture.completedFuture(usuario);
    }

    @CacheEvict(value = "usuarios", key = "#usuario.id")
    public User salvar(User usuario) {
        return repository.save(usuario);
    }
}
