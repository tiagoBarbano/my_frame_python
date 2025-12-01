package com.example.demovt.helpers;

public record RegraConfig(
        String tipoRetorno,
        String condicao,
        PayloadRetorno payloadRetorno) {

    public record PayloadRetorno(
            String status,
            String mensagem,
            String codigoAprovacao) {

        public static PayloadRetorno empty() {
            return new PayloadRetorno("Sem condição", "Não foram encontradas condições validas para esta regra", "");
        }

    }
}