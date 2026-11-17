// Package pool runs jobs on a fixed number of worker goroutines.
package pool

import (
	"context"
	"sync"
)

// Job is a unit of work.
type Job func(ctx context.Context) error

// Pool runs submitted jobs on n workers.
type Pool struct {
	jobs    chan Job
	wg      sync.WaitGroup
	mu      sync.Mutex
	errs    []error
	running int
}

// New starts a pool with n workers.
func New(ctx context.Context, n int) *Pool {
	p := &Pool{jobs: make(chan Job)}
	for i := 0; i < n; i++ {
		p.wg.Add(1)
		go p.work(ctx)
	}
	return p
}

func (p *Pool) work(ctx context.Context) {
	defer p.wg.Done()
	for job := range p.jobs {
		p.mu.Lock()
		p.running++
		p.mu.Unlock()
		if err := job(ctx); err != nil {
			p.mu.Lock()
			p.errs = append(p.errs, err)
			p.mu.Unlock()
		}
		p.mu.Lock()
		p.running--
		p.mu.Unlock()
	}
}

// Submit queues a job; it blocks until a worker is free.
func (p *Pool) Submit(job Job) { p.jobs <- job }

// Close stops accepting jobs, waits for running ones, and returns their errors.
func (p *Pool) Close() []error {
	close(p.jobs)
	p.wg.Wait()
	p.mu.Lock()
	defer p.mu.Unlock()
	return append([]error(nil), p.errs...)
}
