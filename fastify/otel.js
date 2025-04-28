const { NodeSDK } = require('@opentelemetry/sdk-node');
const { ConsoleSpanExporter, BatchSpanProcessor } = require('@opentelemetry/sdk-trace-base');
const { HttpInstrumentation } = require('@opentelemetry/instrumentation-http');
const { resourceFromAttributes } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

// Cria SDK completo
const sdk = new NodeSDK({
   resource: resourceFromAttributes({
      [SemanticResourceAttributes.SERVICE_NAME]: 'basic-service',
   }),
   traceExporter: new ConsoleSpanExporter(),
   // spanProcessor: new BatchSpanProcessor(new ConsoleSpanExporter(), {
   //    // Configurações para o BatchSpanProcessor
   //    maxQueueSize: 1000,  // O número máximo de spans que podem ficar na fila
   //    scheduledDelayMillis: 5000,  // Intervalo de tempo entre o envio dos lotes (em ms)
   //    exportTimeoutMillis: 30000,  // Timeout para exportação de cada lote
   //    maxExportBatchSize: 100,  // Número máximo de spans por lote
   // }),
   instrumentations: [
      new HttpInstrumentation(),
   ],
});

// Inicia o SDK
sdk.start()
