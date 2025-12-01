package main

import (
	"fmt"
	"math"
	"runtime"
	"sync"
	"time"
)

func isPrime(n int) bool {
	if n <= 1 {
		return false
	}
	limit := int(math.Sqrt(float64(n)))
	for i := 2; i <= limit; i++ {
		if n%i == 0 {
			return false
		}
	}
	return true
}

func countPrimes(start, end int, wg *sync.WaitGroup, results chan int) {
	defer wg.Done()
	count := 0
	for j := start; j < end; j++ {
		if isPrime(j) {
			count++
		}
	}
	results <- count
}

func main() {
	limit := 500000000
	threads := runtime.NumCPU() // ou fixe, ex: 8
	chunk := limit / threads

	results := make(chan int, threads)
	var wg sync.WaitGroup

	startTime := time.Now()

	for i := 0; i < threads; i++ {
		start := i * chunk
		end := (i + 1) * chunk
		wg.Add(1)
		go countPrimes(start, end, &wg, results)
	}

	wg.Wait()
	close(results)

	totalPrimes := 0
	for r := range results {
		totalPrimes += r
	}

	elapsed := time.Since(startTime)

	fmt.Println("Total primes:", totalPrimes)
	fmt.Printf("Tempo de execução: %.5f segundos\n", elapsed.Seconds())
}
