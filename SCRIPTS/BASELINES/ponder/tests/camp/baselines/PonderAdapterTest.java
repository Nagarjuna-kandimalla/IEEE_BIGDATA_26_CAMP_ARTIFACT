// SPDX-License-Identifier: GPL-3.0-or-later
// Synthetic branch/integration checks, added 2026-11-10. Not research results.
package camp.baselines;

import cws.k8s.scheduler.model.Task;
import cws.k8s.scheduler.prediction.extractor.InputExtractor;
import cws.k8s.scheduler.prediction.extractor.MemoryExtractor;
import cws.k8s.scheduler.prediction.predictor.LinearPredictorCustomLoss;
import cws.k8s.scheduler.prediction.predictor.PonderPredictor;
import java.io.*;
import java.nio.charset.StandardCharsets;

public final class PonderAdapterTest {
    private static final long M = 1024L * 1024L, G = 1024L * M;
    private static int checks;

    private static void near(double got, double expected, double tolerance) {
        checks++;
        if (!Double.isFinite(got) || Math.abs(got - expected) > tolerance)
            throw new AssertionError("Expected " + expected + ", got " + got);
    }

    private static void yes(boolean condition) {
        checks++;
        if (!condition) throw new AssertionError("Condition failed");
    }

    private static void rejects(Runnable action) {
        checks++;
        try { action.run(); }
        catch (IllegalArgumentException | IllegalStateException expected) { return; }
        throw new AssertionError("Expected invalid event/prediction rejection");
    }

    public static void main(String[] args) throws Exception {
        PonderAdapter a = new PonderAdapter(null, null);
        PonderAdapter.Decision cold = a.predict("p", "cold", G, 8 * G + 1);
        yes(cold.rawBytes == null && cold.requestBytes == 8 * G + 1 && cold.historyCount == 0);
        a.observe("p", "source", 2 * G, G);
        near(a.predict("p", "smaller", G, 8 * G).rawBytes, G + 128 * M, 0);
        yes(a.predict("p", "equal", 2 * G, 8 * G).rawBytes == null);
        yes(a.predict("p", "larger", 3 * G, 8 * G).rawBytes == null);
        yes(a.predict("other-process", "smaller", G, 8 * G).historyCount == 0);
        rejects(() -> a.observe("p", "source", 2 * G, G));
        rejects(() -> a.predict("p", "source", 2 * G, 8 * G));
        rejects(() -> a.predict("p", "smaller", G, 8 * G));
        rejects(() -> a.observe("p", "cold", 2 * G, G));
        rejects(() -> a.observe("p", "badpeak", G, 0));
        rejects(() -> a.predict("p", "baddefault", G, 0));

        // After five observations: exact positive regression, clipping, extrapolation.
        PonderAdapter linear = new PonderAdapter(null, null);
        for (int i = 1; i <= 5; i++) linear.observe("p", "s" + i, i * G, (2 * i + 3) * G);
        PonderAdapter.Decision middle = linear.predict("p", "middle", 7 * G / 2, 100 * G);
        near(middle.rawBytes, 10 * G + 128 * M, 1);
        yes(middle.historyCount == 5);
        near(linear.predict("p", "below", 0, 100 * G).rawBytes, 5 * G + 128 * M, 1);
        near(linear.predict("p", "above", 6 * G, 100 * G).rawBytes, 15 * G + 128 * M, 1);

        // Negative correlation and degenerate correlation take the history maximum.
        for (boolean constant : new boolean[]{false, true}) {
            PonderAdapter weak = new PonderAdapter(null, null);
            for (int i = 1; i <= 12; i++) weak.observe("p", "s" + i, i * G, constant ? 3 * G : (20 - i) * G);
            near(weak.predict("p", "query", 5 * G, 100 * G).rawBytes,
                 (constant ? 3 : 19) * G + 128 * M, 0);
        }

        // Direct original-core parity across every incremental history size.
        // This exercises unequal-loss fitting and nonzero weighted residual offsets.
        PonderPredictor original = new PonderPredictor(
            new LinearPredictorCustomLoss(new InputExtractor(), new MemoryExtractor()));
        PonderAdapter wrapped = new PonderAdapter(null, null);
        for (int i = 1; i <= 16; i++) {
            long input = i * G;
            long peak = (2 * i + 3) * G + (i % 3 == 0 ? 700 * M : 0);
            original.addTask(new Task(input, peak));
            wrapped.observe("p", "s" + i, input, peak);
            for (long query : new long[]{G / 2, i * G, (i + 2) * G}) {
                Double expected = original.queryPrediction(new Task(query, 0));
                PonderAdapter.Decision got = wrapped.predict("p", i + ":" + query, query, 100 * G);
                if (expected == null) yes(got.rawBytes == null);
                else near(got.rawBytes, expected, 0);
                yes(got.historyCount == i);
            }
        }

        // Preserve original MemoryScaler branch order rather than combining clamps.
        near(PonderAdapter.allocate(100.0, G, 256 * M, null), 256 * M, 0);
        near(PonderAdapter.allocate(10.0 * G, 8 * G, null, 9 * G), 9 * G, 0);
        near(PonderAdapter.allocate(10.0 * G, 8 * G, null, null), 8 * G, 0);
        near(PonderAdapter.allocate(M + 1.25, 8 * G, null, null), 2 * M, 0);
        near(PonderAdapter.allocate(null, 12345, 256 * M, null), 12345, 0);
        rejects(() -> PonderAdapter.allocate(Double.NaN, G, null, null));
        rejects(() -> PonderAdapter.allocate(Double.POSITIVE_INFINITY, G, null, null));

        // Exercise TSV parsing and prediction-only output with the real main entry.
        InputStream savedIn = System.in;
        PrintStream savedOut = System.out;
        ByteArrayOutputStream output = new ByteArrayOutputStream();
        String events = "event\tgroup\ttask_id\tinput_bytes\tpeak_bytes\tdefault_bytes\n" +
            "predict\tp\tt1\t1000\t\t1073741824\n" +
            "observe\tp\tt1\t1000\t536870912\t\n" +
            "predict\tp\tt2\t500\t\t1073741824\n";
        try {
            System.setIn(new ByteArrayInputStream(events.getBytes(StandardCharsets.UTF_8)));
            System.setOut(new PrintStream(output, true, "UTF-8"));
            PonderAdapter.main(new String[]{});
        } finally { System.setIn(savedIn); System.setOut(savedOut); }
        String[] rows = output.toString("UTF-8").trim().split("\\R");
        yes(rows.length == 3);
        yes(rows[1].equals("p\tt1\t0\t\t1073741824\tdefault"));
        yes(rows[2].endsWith("\t671088640\tpredicted"));
        System.out.println("PASS: " + checks + " checks, including 48 original-core parity cases.");
    }
}
