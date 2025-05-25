import './otel.js';
import 'dotenv/config';
import pino from 'pino';
import Fastify from 'fastify';
import fastifyMetrics from 'fastify-metrics';
import fastifyRedis from '@fastify/redis';
import fastifyMongo from '@fastify/mongodb';
import cacheable from './cacheable.js';
import fastifySwagger from '@fastify/swagger';
import fastifySwaggerUi from '@fastify/swagger-ui';

const log = pino({ level: 'info' });

const fastify = Fastify({ logger: false });

await fastify.register(import('fastify-healthcheck'))
await fastify.register(fastifySwagger);
await fastify.register(fastifySwaggerUi, {
  routePrefix: '/docs',
  uiConfig: {
    docExpansion: 'full',
    deepLinking: false
  },
  uiHooks: {
    onRequest: function (request, reply, next) { next() },
    preHandler: function (request, reply, next) { next() }
  },
  staticCSP: true,
  transformStaticCSP: (header) => header,
  transformSpecification: (swaggerObject, request, reply) => { return swaggerObject },
  transformSpecificationClone: true
})
await fastify.register(fastifyRedis, {
  // host: 'redis',
  host: 'localhost',
  port: 6379,
  password: 'redis1234',
  db: 0,
});
await fastify.register(fastifyMongo, {
  forceClose: true,
  // url: 'mongodb://mongodb:27017/cotador',
  url: 'mongodb://localhost:27017/cotador',
});
await fastify.register(fastifyMetrics, {
  endpoint: '/metrics',
  routeMetrics: {
    enabled: {
      histogram: true,
      summary: false
    },
  }
});

fastify.decorate('cache', {
  async getOrSet(key, ttl, fetchFn) {
    const { redis } = fastify;
    const cached = await redis.get(key);
    if (cached) {
      return JSON.parse(cached);
    }
    const result = await fetchFn();
    if (result) {
      await redis.set(key, JSON.stringify(result), 'EX', ttl);
    }
    return result;
  }
});

// Rota com cache
fastify.get(
  '/user/:id',
  {
    schema: {
      description: 'Consulta usuário pelo id',
      tags: ['user'],
      summary: 'Consulta usuário pelo id',
      params: {
        type: 'object',
        properties: {
          id: {
            type: 'string',
            description: 'user id'
          }
        }
      },
      response: {
        200: {
          description: 'Successful response',
          type: 'object',
          properties: {
            _id: { type: 'string' },
            empresa: { type: 'string' },
            cotacao_final: { type: 'number' },
            created_at: { type: 'string' },
            updated_at: { type: 'string' },
            deleted: { type: 'boolean' },
          }
        },
        400: {
          description: 'Bad request',
          type: 'object',
          properties: {
            error: { type: 'string' }
          }
        },
        500: {
          description: 'Internal server error',
          type: 'object',
          properties: {
            error: { type: 'string' }
          }
        }
      }
    }
  },
  cacheable({
    keyBuilder: (req) => `user:${req.params.id}`,
    ttlSeconds: 120,
  })(async function (req, reply) {
    try {
      const users = fastify.mongo.db.collection('users');
      const user = await users.findOne({ _id: req.params.id });
      if (!user) {
        log.info(`User not found: ${req.params.id}`);
        return reply.code(204).send();
      }
    } catch (err) {
      return reply.code(500).send({ error: 'Erro ao buscar usuário' });
    }
  })
);

// Lista usuários
fastify.get('/users', {
  schema: {
    description: 'Consulta todos os usuários',
    tags: ['user'],
    summary: 'Consulta todos os usuários',
    response: {
      200: {
        description: 'Successful response',
        type: 'array',
        items: {
          type: 'object',
          properties: {
            _id: { type: 'string' },
            empresa: { type: 'string' },
            cotacao_final: { type: 'number' },
            created_at: { type: 'string' },
            updated_at: { type: 'string' },
            deleted: { type: 'boolean' },
          }
        }
      },
      400: {
        description: 'Bad request',
        type: 'object',
        properties: {
          error: { type: 'string' }
        }
      },
      500: {
        description: 'Internal server error',
        type: 'object',
        properties: {
          error: { type: 'string' }
        }
      }
    }
  }
}, async function (req, reply) {
  try {
    const users = this.mongo.db.collection('users');
    return await users.find({}).toArray();
  } catch (err) {
    console.error(err);
    return reply.code(500).send({ error: 'Erro ao buscar usuários' });
  }
});


fastify.get('/', {
  schema: {
    description: 'Hello World',
    tags: ['HelloWorld'],
    summary: 'Hello World'
  }
}, async (request, reply) => {
  return { message: 'Hello World' };

});

// Inicia servidor
const start = async () => {
  try {
    await fastify.listen({ port: 3000, host: '0.0.0.0' });
    console.log('Server is running at http://localhost:3000');
    console.log('Prometheus metrics at http://localhost:3000/metrics');
    console.log('Swagger-ui at http://localhost:3000/docs');
    console.log('Health Check at http://localhost:3000/health');
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();
