package com.example.demovt.helpers;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.BiFunction;

import org.apache.commons.jexl3.JexlBuilder;
import org.apache.commons.jexl3.JexlContext;
import org.apache.commons.jexl3.JexlEngine;
import org.apache.commons.jexl3.JexlExpression;
import org.apache.commons.jexl3.MapContext;
import org.springframework.context.annotation.Configuration;

import com.example.demovt.helpers.RegraConfig.PayloadRetorno;

@Configuration
public class AdvancedRuleEvaluator {

    private final JexlEngine jexl = new JexlBuilder()
        .silent(false)
        .cache(0)
        .strict(true)
        .create();
    private final Map<String, BiFunction<Map<String, Object>, Object, Object>> evaluators = new HashMap<>();
    private final Map<String, JexlExpression> expressionCache = new ConcurrentHashMap<>();

    public AdvancedRuleEvaluator() {
        evaluators.put("boolean", this::evaluateRuleBooleanWrapper);
        evaluators.put("json", this::evaluateRuleMapWrapper);
    }

    public Object evaluete(String nomeMetodo, Map<String, Object> jsonPedido, Object regra) {
        BiFunction<Map<String, Object>, Object, Object> biFuncao = evaluators.get(nomeMetodo);

        if (biFuncao == null) {
            return "ERRO: Método '" + nomeMetodo + "' não encontrado.";
        }

        return biFuncao.apply(jsonPedido, regra);
    }

    public Object evaluateRuleBooleanWrapper(Map<String, Object> jsonPedido, Object regra) {
        boolean resultado = this.evaluateRuleBoolean(jsonPedido, regra);
        return resultado;
    }

    public Object evaluateRuleMapWrapper(Map<String, Object> jsonPedido, Object regra) {
        PayloadRetorno resultado = this.evaluateRuleMap(jsonPedido, regra);
        return resultado;
    }

    public boolean evaluateRuleBoolean(Map<String, Object> jsonPedido, Object regra) {
        JexlContext contexto = new MapContext();
        contexto.set("dados", jsonPedido);

        JexlExpression exp = getCachedExpression(((RegraConfig) regra).condicao());
        return (Boolean) exp.evaluate(contexto);
    }

    public PayloadRetorno evaluateRuleMap(Map<String, Object> jsonPedido, Object regra) {
        JexlContext contexto = new MapContext();
        contexto.set("dados", jsonPedido);

        JexlExpression exp = getCachedExpression(((RegraConfig) regra).condicao());
        Boolean flagResponseExp = (Boolean) exp.evaluate(contexto);

        if (flagResponseExp) {
            return ((RegraConfig) regra).payloadRetorno();
        }
        return PayloadRetorno.empty();
    }

    private JexlExpression getCachedExpression(String regra) {
        return expressionCache.computeIfAbsent(regra, jexl::createExpression);
    }

}