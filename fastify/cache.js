module.exports = async function (fastify, opts) {
    fastify.decorate('cache', {
        async getOrSet(key, ttlSeconds, fetchFn) {
            const cached = await fastify.redis.get(key);
            if (cached) {
                try {
                    return JSON.parse(cached);
                } catch {
                    return cached; // fallback se não for JSON
                }
            }

            const result = await fetchFn();

            try {
                await fastify.redis.set(key, JSON.stringify(result), 'EX', ttlSeconds);
            } catch (err) {
                fastify.log.warn('Falha ao setar cache: ' + err.message);
            }

            return result;
        }
    });
};
