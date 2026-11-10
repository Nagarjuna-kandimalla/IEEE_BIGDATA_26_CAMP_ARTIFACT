// SPDX-License-Identifier: GPL-3.0-or-later
// Standalone data adapter, added 2026-11-10. Not the upstream scheduler Task.
package cws.k8s.scheduler.model;

public final class Task {
    private final long inputSize;
    private final TaskMetrics metrics;

    public Task(long inputSize, long peakRss) {
        this.inputSize = inputSize;
        this.metrics = new TaskMetrics(peakRss);
    }

    public long getInputSize() { return inputSize; }
    public TaskMetrics getTaskMetrics() { return metrics; }

    public static final class TaskMetrics {
        private final long peakRss;
        TaskMetrics(long peakRss) { this.peakRss = peakRss; }
        public long getPeakRss() { return peakRss; }
    }
}
