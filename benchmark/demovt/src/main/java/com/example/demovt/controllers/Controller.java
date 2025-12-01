package com.example.demovt.controllers;

import java.io.IOException;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executor;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import com.example.demovt.controllers.Controller.ResponseRules;
import com.example.demovt.helpers.AdvancedRuleEvaluator;
import com.example.demovt.helpers.RegraConfig;
import com.example.demovt.helpers.RegraConfig.PayloadRetorno;
import com.example.demovt.model.User;
import com.example.demovt.service.UsuarioService;
import com.fasterxml.jackson.databind.ObjectMapper;

// import io.swagger.v3.oas.annotations.Operation;
import jakarta.servlet.http.HttpServletRequest;
import java.io.InputStream;
import java.time.Instant;

@RestController
public class Controller {

    private final UsuarioService service;
    private final AdvancedRuleEvaluator advanceRuleEvaluator;
    private final ObjectMapper objectMapper = new ObjectMapper();
    private Executor cpuExecutor;
    private Executor vtExecutor;

    private final RegraConfig REGRA_FIDELIDADE = new RegraConfig(
            "json",
            "dados.cliente.score > 700 && dados.valorTotal > 1000",
            new PayloadRetorno(
                    "APROVADO",
                    "Desconto de 10% aplicado devido ao Score.",
                    "DESCONTO_10"));

    private final RegraConfig REGRA_PRODUTOS_RESTRITOS = new RegraConfig(
            "json",
            "dados.cliente.vip == true && dados.produtosComprados.contains('ALIMENTO')",
            new PayloadRetorno(
                    "AVISO",
                    "Cliente VIP comprou ALIMENTO. Requer aprovação manual.",
                    "MANUAL_REVIEW"));

    public Controller(UsuarioService service, AdvancedRuleEvaluator advanceRuleEvaluator,
            @Qualifier("cpuBoundExecutor") Executor cpuExecutor,
            @Qualifier("vtExecutor") Executor vtExecutor) {
        this.service = service;
        this.advanceRuleEvaluator = advanceRuleEvaluator;
        this.cpuExecutor = cpuExecutor;
        this.vtExecutor = vtExecutor;
    }

    @GetMapping
    public String hello() {
        return "Hello World!";
    }

    @GetMapping("usuarios-sync/{id}")
    // @Operation(summary = "Buscar usuário por ID", description = "Retorna um
    // usuário armazenado no MongoDB com cache Redis.")
    public Optional<User> getUsuario(@PathVariable String id) {
        return service.buscarPorId(id);
    }

    @PostMapping("/usuarios")
    // @Operation(summary = "Criar novo usuário", description = "Cria e armazena um
    // usuário no MongoDB e limpa o cache Redis.")
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
        try {
            Thread.sleep(1);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            System.out.println("Thread interrompida durante sleep");
        }
        return body;
    }

    public record ResponseRules(
            Object result,
            Instant createdAt) {

    }

    /*
     * {
     * "cliente": {
     * "nome": "Carla",
     * "score": 750,
     * "vip": false
     * },
     * "valorTotal": 1250.50,
     * "descontoAplicado": 0.10,
     * "produtosComprados": ["ELETRONICO", "VESTUARIO"]
     * }
     */
    @PostMapping(path = "/regras", consumes = "application/json", produces = "application/json")
    public ResponseEntity<ResponseRules> testeRegrasMap(@RequestBody Map<String, Object> jsonPedido) {
        Object resultado = advanceRuleEvaluator.evaluete(REGRA_FIDELIDADE.tipoRetorno(), jsonPedido, REGRA_FIDELIDADE);
        ResponseRules responseRules = new ResponseRules(resultado, Instant.now());
        return ResponseEntity.ok(responseRules);
    }

    @GetMapping("/check")
    public String check() {
        System.out.println("Thread atual: " + Thread.currentThread());
        System.out.println("Virtual? " + Thread.currentThread().isVirtual());
        return "ok";
    }

}