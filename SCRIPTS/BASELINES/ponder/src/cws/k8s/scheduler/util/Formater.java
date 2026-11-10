// SPDX-License-Identifier: GPL-3.0-or-later
// Standalone logging adapter, added 2026-11-10; no prediction arithmetic.
package cws.k8s.scheduler.util;

public final class Formater {
    private Formater() {}
    public static String formatBytes(long bytes) { return bytes + " bytes"; }
}
