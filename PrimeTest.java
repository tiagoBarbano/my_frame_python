import java.util.concurrent.*;
import java.util.*;

public class PrimeTest {
    public static boolean isPrime(int n) {
        if (n <= 1) return false;
        for (int i = 2; i * i <= n; i++) {
            if (n % i == 0) return false;
        }
        return true;
    }
    public static void main(String[] args) throws InterruptedException {
        int limit = 500000000;
        int threads = 22;
        long startTime = System.nanoTime();
        ExecutorService executor = Executors.newFixedThreadPool(threads);
        List<Future<Integer>> futures = new ArrayList<>();
        int chunk = limit / threads;
        for (int i = 0; i < threads; i++) {
            final int start = i * chunk;
            final int end = (i + 1) * chunk;
            futures.add(executor.submit(() -> {
                int count = 0;
                for (int j = start; j < end; j++) {
                    if (isPrime(j)) count++;
                }
                return count;
            }));
        }
        int totalPrimes = 0;
        for (Future<Integer> f : futures) {
            try {
                totalPrimes += f.get();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        executor.shutdown();
        System.out.println("Total primes: " + totalPrimes);
        long endTime = System.nanoTime();
        double elapsedSeconds = (endTime - startTime) / 1_000_000_000.0;
        System.out.printf("Tempo de execução: %.5f segundos%n", elapsedSeconds);
    }
}
