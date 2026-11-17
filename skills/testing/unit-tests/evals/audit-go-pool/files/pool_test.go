package pool

import (
	"context"
	"errors"
	"testing"
	"time"
)

var counter int

func TestPool(t *testing.T) {
	p := New(context.Background(), 4)
	for i := 0; i < 10; i++ {
		p.Submit(func(ctx context.Context) error {
			counter++
			return nil
		})
	}
	time.Sleep(100 * time.Millisecond)
	if counter != 10 {
		t.Errorf("got %d", counter)
	}
	p.Close()
}

func TestPool2(t *testing.T) {
	p := New(context.Background(), 2)
	p.Submit(func(ctx context.Context) error { return errors.New("boom") })
	p.Submit(func(ctx context.Context) error { return nil })
	time.Sleep(50 * time.Millisecond)
	if len(p.errs) != 1 {
		t.Fatal("expected 1 error")
	}
	if counter != 10 {
		t.Fatal("counter changed")
	}
	p.Close()
}

func TestConcurrency(t *testing.T) {
	p := New(context.Background(), 3)
	block := make(chan struct{})
	for i := 0; i < 3; i++ {
		go p.Submit(func(ctx context.Context) error { <-block; return nil })
	}
	time.Sleep(20 * time.Millisecond)
	if p.running != 3 {
		t.Errorf("running = %d, want 3", p.running)
	}
	close(block)
	p.Close()
}
