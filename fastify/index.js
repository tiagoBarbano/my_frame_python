// const _ = require('./otel.js');
const fastify = require('fastify')({ logger: false });
// const fastifyMetrics = require('fastify-metrics');
// const promClient = require('prom-client');

// fastify.register(fastifyMetrics, { endpoint: '/metrics'});

// const httpRequestDurationMicroseconds = new promClient.Histogram({
//   name: 'http_request_duration_seconds_teste',
//   help: 'Histogram of HTTP request durations in seconds',
//   labelNames: ['status_code'],
//   buckets: [0.1, 0.3, 0.5, 1, 2, 5, 10]
// });


fastify.get('/', async (request, reply) => {
  // const end = httpRequestDurationMicroseconds.startTimer();

  try {
    const response = { message: 'Hello World' };
    // end({ status_code: 200 });
    return response;
  } catch (error) {
    // end({ status_code: 500 });
    throw error;
  }
});

const start = async () => {
  try {
    await fastify.listen({ port: 3001 });
    console.log('Server is running at http://localhost:3001');
    console.log('Prometheus metrics available at http://localhost:3001/metrics');
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();