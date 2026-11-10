// SPDX-License-Identifier: GPL-3.0-or-later
// Added 2026-11-10. Request-policy portion adapted from upstream MemoryScaler
// at commit 3046e19d5a3a237c5f6c0df4d16f33e643b31828; see NOTICE.md.
package camp.baselines;

import cws.k8s.scheduler.model.Task;
import cws.k8s.scheduler.prediction.extractor.InputExtractor;
import cws.k8s.scheduler.prediction.extractor.MemoryExtractor;
import cws.k8s.scheduler.prediction.predictor.LinearPredictorCustomLoss;
import cws.k8s.scheduler.prediction.predictor.PonderPredictor;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** One initial decision per task. Observations must be released in causal order. */
public final class PonderAdapter {
    public static final long MIB = 1024L * 1024L;
    private static final long MAX_EXACT_BYTES = (1L << 53) - 1;
    private final Map<String, PonderPredictor> groups = new HashMap<>();
    private final Set<String> observed = new HashSet<>();
    private final Map<String, Long> predictedInputs = new HashMap<>();
    private final Long minBytes;
    private final Long maxBytes;

    public PonderAdapter(Long minBytes, Long maxBytes) {
        if ((minBytes != null && (minBytes <= 0 || minBytes > MAX_EXACT_BYTES)) ||
            (maxBytes != null && (maxBytes <= 0 || maxBytes > MAX_EXACT_BYTES)) ||
            (minBytes != null && maxBytes != null && minBytes > maxBytes)) {
            throw new IllegalArgumentException("Invalid request bounds");
        }
        this.minBytes = minBytes;
        this.maxBytes = maxBytes;
    }

    private static String key(String group, String id) {
        if (group.isEmpty() || id.isEmpty() || group.indexOf('\u0000') >= 0 || id.indexOf('\u0000') >= 0)
            throw new IllegalArgumentException("Nonempty group/task identifiers required");
        return group + '\u0000' + id;
    }

    private static void checkBytes(long value, boolean allowZero) {
        if (value < (allowZero ? 0 : 1) || value > MAX_EXACT_BYTES)
            throw new IllegalArgumentException("Bytes outside supported exact integer range");
    }

    public synchronized void observe(String group, String id, long input, long peak) {
        checkBytes(input, true);
        checkBytes(peak, false);
        String key = key(group, id);
        if (observed.contains(key)) throw new IllegalArgumentException("Duplicate observation: " + id);
        if (predictedInputs.containsKey(key) && predictedInputs.get(key) != input)
            throw new IllegalArgumentException("Input size changed after prediction: " + id);
        PonderPredictor predictor = groups.computeIfAbsent(group, unused ->
            new PonderPredictor(new LinearPredictorCustomLoss(new InputExtractor(), new MemoryExtractor())));
        predictor.addTask(new Task(input, peak));
        observed.add(key);
    }

    public synchronized Decision predict(String group, String id, long input, long defaultBytes) {
        checkBytes(input, true);
        checkBytes(defaultBytes, false);
        String key = key(group, id);
        if (observed.contains(key)) throw new IllegalArgumentException("Target already in history: " + id);
        if (predictedInputs.containsKey(key)) throw new IllegalArgumentException("Duplicate initial decision: " + id);
        PonderPredictor predictor = groups.get(group);
        Double raw = predictor == null ? null : predictor.queryPrediction(new Task(input, 0));
        long request = allocate(raw, defaultBytes, minBytes, maxBytes);
        predictedInputs.put(key, input);
        return new Decision(raw, request, predictor == null ? 0 : predictor.getVersion());
    }

    /** Preserves MemoryScaler's ordered if/else-if policy and MiB rounding.
     * Null prediction keeps the original request without new caps/rounding.
     * Non-finite output is rejected, rather than Java's silent NaN-to-long cast.
     */
    public static long allocate(Double raw, long original, Long min, Long max) {
        if (raw == null) return original;
        if (!Double.isFinite(raw) || raw < 0 || raw > MAX_EXACT_BYTES)
            throw new IllegalStateException("Invalid upstream prediction: " + raw);
        long request = raw.longValue();
        if (min != null && request < min) request = min;
        else if (max != null && request > max) request = max;
        else if (request > original) request = original;
        long remainder = request % MIB;
        return remainder == 0 ? request : request + MIB - remainder;
    }

    public static final class Decision {
        public final Double rawBytes;
        public final long requestBytes;
        public final long historyCount;
        Decision(Double raw, long request, long count) {
            rawBytes = raw; requestBytes = request; historyCount = count;
        }
    }

    public static void main(String[] args) throws Exception {
        Long min = null, max = null;
        for (int i = 0; i < args.length; i += 2) {
            if (i + 1 == args.length) throw new IllegalArgumentException("Missing bound value");
            if (args[i].equals("--min-bytes")) min = Long.valueOf(args[i + 1]);
            else if (args[i].equals("--max-bytes")) max = Long.valueOf(args[i + 1]);
            else throw new IllegalArgumentException("Unknown argument: " + args[i]);
        }
        PonderAdapter adapter = new PonderAdapter(min, max);
        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
        PrintWriter out = new PrintWriter(new OutputStreamWriter(System.out, StandardCharsets.UTF_8), true);
        String header = "event\tgroup\ttask_id\tinput_bytes\tpeak_bytes\tdefault_bytes";
        if (!header.equals(reader.readLine())) throw new IllegalArgumentException("Expected TSV header: " + header);
        out.println("group\ttask_id\thistory_count\traw_prediction_bytes\trequest_bytes\tstatus");
        String line;
        long lineNumber = 1;
        while ((line = reader.readLine()) != null) {
            lineNumber++;
            try {
                String[] f = line.split("\t", -1);
                if (f.length != 6) throw new IllegalArgumentException("Expected six TSV fields");
                if (f[0].equals("observe")) {
                    if (!f[5].isEmpty()) throw new IllegalArgumentException("observe default_bytes must be empty");
                    adapter.observe(f[1], f[2], Long.parseLong(f[3]), Long.parseLong(f[4]));
                } else if (f[0].equals("predict")) {
                    if (!f[4].isEmpty()) throw new IllegalArgumentException("predict peak_bytes must be empty");
                    Decision d = adapter.predict(f[1], f[2], Long.parseLong(f[3]), Long.parseLong(f[5]));
                    out.println(f[1] + "\t" + f[2] + "\t" + d.historyCount + "\t" +
                        (d.rawBytes == null ? "" : d.rawBytes) + "\t" + d.requestBytes + "\t" +
                        (d.rawBytes == null ? "default" : "predicted"));
                } else throw new IllegalArgumentException("event must be predict or observe");
            } catch (RuntimeException e) {
                throw new IllegalArgumentException("Invalid event at line " + lineNumber + ": " + e.getMessage(), e);
            }
        }
        if (out.checkError()) throw new IOException("Output write failed");
    }
}
