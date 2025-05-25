import { resourceFromAttributes } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { B3InjectEncoding, B3Propagator } from '@opentelemetry/propagator-b3';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { HttpInstrumentation } from '@opentelemetry/instrumentation-http';
import { MongoDBInstrumentation } from '@opentelemetry/instrumentation-mongodb';
import { RedisInstrumentation } from '@opentelemetry/instrumentation-redis';
import { AsyncLocalStorageContextManager } from '@opentelemetry/context-async-hooks';
import { NodeTracerProvider, BatchSpanProcessor, ConsoleSpanExporter } from '@opentelemetry/sdk-trace-node';
import { logs } from '@opentelemetry/sdk-node';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { PinoInstrumentation } from '@opentelemetry/instrumentation-pino';

const traceExporter = new OTLPTraceExporter({
   concurrencyLimit: 10,
   compression: 'gzip'
})

const contextManager = new AsyncLocalStorageContextManager().enable();

// Create and configure NodeTracerProvider
const provider = new NodeTracerProvider({
   resource: resourceFromAttributes({
      [SemanticResourceAttributes.SERVICE_NAME]: 'fastify-service',
      [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
   }),
   spanProcessors: [
      new BatchSpanProcessor(new ConsoleSpanExporter()),
      new BatchSpanProcessor(traceExporter, {
         maxQueueSize: 1000, // The maximum queue size. After the size is reached spans are dropped.
         scheduledDelayMillis: 1000 // The interval between two consecutive exports
      })
   ],
   logRecordProcessor: new logs.SimpleLogRecordProcessor(new logs.ConsoleLogRecordExporter()),
   propagator: new B3Propagator({
      injectEncoding: B3InjectEncoding.MULTI_HEADER,
   }),
   contextManager: contextManager,
});


// Initialize the provider
provider.register();

registerInstrumentations({
   instrumentations: [
      new HttpInstrumentation(),
      new RedisInstrumentation(),
      new MongoDBInstrumentation(),
      new PinoInstrumentation({
         // Optional: Configure Pino instrumentation
         logKeys: {
            traceId: 'TraceId',
            spanId: 'SpanId',
            traceFlags: 'TraceFlags',
         },
      }),
   ],
});