package pl.tlumacz.filterhost;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import net.sf.okapi.common.Event;
import net.sf.okapi.common.LocaleId;
import net.sf.okapi.common.filters.IFilter;
import net.sf.okapi.common.filterwriter.IFilterWriter;
import net.sf.okapi.common.resource.Code;
import net.sf.okapi.common.resource.RawDocument;
import net.sf.okapi.common.resource.TextFragment;
import net.sf.okapi.common.resource.TextPart;
import net.sf.okapi.common.resource.TextUnit;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

public final class FilterHost {
    private static final ObjectMapper JSON = new ObjectMapper();
    private static final int PROTOCOL_VERSION = 1;
    private static final String BRIDGE_VERSION = "1.0";
    private static final Path FILTER_STORE = Paths.get(System.getenv().getOrDefault(
        "TLUMACZ_FILTER_STORE", Paths.get(System.getProperty("user.home"), ".config", "tlumacz", "filters").toString()
    ));
    private static final Map<String, Session> SESSIONS = new HashMap<>();

    private static final class Session {
        final String id, filterName;
        final LocaleId sourceLocale, targetLocale;
        final Path input, output;
        final RawDocument raw;
        final IFilter filter;
        final FilterLoader.LoadedFilter loadedFilter;
        final IFilterWriter writer;
        Event pendingEvent;
        TextUnit pendingUnit;
        int ordinal, applied;

        Session(String id, String filterName, LocaleId sourceLocale, LocaleId targetLocale,
                Path input, Path output, RawDocument raw, FilterLoader.LoadedFilter loadedFilter, IFilterWriter writer) {
            this.id = id; this.filterName = filterName; this.sourceLocale = sourceLocale;
            this.targetLocale = targetLocale; this.input = input; this.output = output;
            this.raw = raw; this.loadedFilter = loadedFilter; this.filter = loadedFilter.filter; this.writer = writer;
        }
    }

    private static final class BridgeException extends RuntimeException {
        final String code;
        final boolean retryable;
        BridgeException(String code, String message, boolean retryable) {
            super(message); this.code = code; this.retryable = retryable;
        }
    }

    public static void main(String[] args) throws Exception {
        try (BufferedReader in = new BufferedReader(new InputStreamReader(System.in))) {
            String line;
            while ((line = in.readLine()) != null) {
                if (line.isBlank()) continue;
                String requestId = "";
                boolean legacy = false;
                try {
                    JsonNode parsed = JSON.readTree(line);
                    if (!parsed.isObject()) throw error("INVALID_REQUEST", "Żądanie musi być obiektem JSON", false);
                    ObjectNode req = (ObjectNode) parsed;
                    requestId = req.path("request_id").asText("");
                    legacy = req.has("op") && !req.has("operation");
                    ObjectNode result = dispatch(req);
                    ObjectNode out = JSON.createObjectNode();
                    out.put("protocol_version", PROTOCOL_VERSION);
                    out.put("request_id", requestId);
                    out.put("ok", true);
                    if (legacy) out.setAll(result);
                    else out.set("result", result);
                    System.out.println(JSON.writeValueAsString(out));
                } catch (Throwable e) {
                    ObjectNode out = JSON.createObjectNode();
                    out.put("protocol_version", PROTOCOL_VERSION);
                    out.put("request_id", requestId);
                    out.put("ok", false);
                    ObjectNode err = out.putObject("error");
                    String errorCode;
                    String errorMessage;
                    boolean retryable;
                    if (e instanceof BridgeException bridge) {
                        errorCode = bridge.code;
                        errorMessage = bridge.getMessage();
                        retryable = bridge.retryable;
                    } else {
                        errorCode = "INTERNAL_ERROR";
                        errorMessage = String.valueOf(e.getMessage());
                        retryable = false;
                    }
                    err.put("code", errorCode);
                    err.put("message", errorMessage);
                    err.put("retryable", retryable);
                    if (legacy) {
                        out.put("message", errorMessage);
                        out.put("error_code", errorCode);
                    }
                    System.out.println(JSON.writeValueAsString(out));
                }
                System.out.flush();
            }
        } finally {
            for (Session s : new ArrayList<>(SESSIONS.values())) cleanup(s);
            SESSIONS.clear();
        }
    }

    private static BridgeException error(String code, String message, boolean retryable) {
        return new BridgeException(code, message, retryable);
    }

    private static ObjectNode dispatch(ObjectNode req) throws Exception {
        if (req.path("protocol_version").asInt(-1) != PROTOCOL_VERSION)
            throw error("UNSUPPORTED_PROTOCOL", "Wymagana jest wersja protokołu 1", false);
        String operation = req.path("operation").asText(req.path("op").asText(""));
        boolean legacy = req.has("op") && !req.has("operation");
        ObjectNode params = req.has("payload") && req.get("payload").isObject()
                ? (ObjectNode) req.get("payload")
                : req;
        if (legacy) return switch (operation) {
            case "capabilities" -> legacyCapabilities(params.path("filter").asText(""));
            case "probe" -> legacyProbe(params);
            case "extract" -> legacyExtract(params);
            case "merge" -> legacyMerge(params);
            default -> throw error("INVALID_REQUEST", "Nieznana operacja: " + operation, false);
        };
        return switch (operation) {
            case "hello" -> hello();
            case "version" -> version();
            case "health" -> health();
            case "capabilities" -> capabilities(params.path("filter").asText(""));
            case "extract" -> legacyExtract(params);
            case "merge" -> legacyMerge(params);
            case "open" -> open(params);
            case "next" -> next(params);
            case "apply" -> apply(params);
            case "close" -> close(params);
            case "cancel" -> cancel(params);
            default -> throw error("INVALID_REQUEST", "Nieznana operacja", false);
        };
    }


    private static ObjectNode legacyProbe(ObjectNode req) throws Exception {
        Path input = requiredPath(req, "input");
        if (!Files.isRegularFile(input)) throw error("INPUT_NOT_FOUND", "Nie znaleziono pliku wejściowego: " + input, false);
        FilterLoader.LoadedFilter loaded = loadFilter(req.path("filter").asText(""));
        IFilter filter = loaded.filter;
        RawDocument raw = new RawDocument(input.toUri(), "UTF-8", locale(req.path("source").asText("auto")), locale(req.path("target").asText("pl")));
        try (FilterContext ignored = new FilterContext(loaded)) {
            filter.open(raw, false);
            ObjectNode result = JSON.createObjectNode();
            result.put("filter", req.path("filter").asText(""));
            result.put("input", input.toString());
            return result;
        } finally { safeClose(raw); loaded.close(); }
    }

    private static ObjectNode legacyCapabilities(String name) throws Exception {
        ObjectNode result = filterCapabilities(name);
        result.put("name", "okf_" + name);
        return result;
    }

    private static ObjectNode legacyExtract(ObjectNode req) throws Exception {
        String filterName = req.path("filter").asText("");
        Path input = requiredPath(req, "input");
        Path unitsPath = requiredPath(req, "units");
        if (!Files.isRegularFile(input)) throw error("INPUT_NOT_FOUND", "Nie znaleziono pliku wejściowego: " + input, false);
        FilterLoader.LoadedFilter loaded = loadFilter(filterName);
        IFilter filter = loaded.filter;
        RawDocument raw = new RawDocument(
                input.toUri(), "UTF-8",
                locale(req.path("source").asText("auto")),
                locale(req.path("target").asText("pl")));
        ArrayNode units = JSON.createArrayNode();
        try (FilterContext ignored = new FilterContext(loaded)) {
            filter.open(raw, false);
            int ordinal = 0;
            while (filter.hasNext()) {
                Event event = filter.next();
                if (!event.isTextUnit()) continue;
                ordinal++;
                units.add(unitToJson((TextUnit) event.getTextUnit(), ordinal));
            }
        } finally {
            safeClose(raw);
            loaded.close();
        }
        Path parent = unitsPath.toAbsolutePath().getParent();
        if (parent != null) Files.createDirectories(parent);
        JSON.writeValue(unitsPath.toFile(), units);
        ObjectNode result = JSON.createObjectNode();
        result.put("filter", filterName);
        result.put("count", units.size());
        result.set("units", units);
        return result;
    }

    private static ObjectNode legacyMerge(ObjectNode req) throws Exception {
        String filterName = req.path("filter").asText("");
        Path input = requiredPath(req, "input");
        Path targetsPath = requiredPath(req, "targets");
        Path output = requiredPath(req, "output");
        if (!Files.isRegularFile(input)) throw error("INPUT_NOT_FOUND", "Nie znaleziono pliku wejściowego: " + input, false);
        JsonNode targets = JSON.readTree(targetsPath.toFile());
        Map<String, String> byId = new HashMap<>();
        if (targets.isObject()) targets.fields().forEachRemaining(e -> byId.put(e.getKey(), e.getValue().asText()));
        FilterLoader.LoadedFilter loaded = loadFilter(filterName);
        IFilter filter = loaded.filter;
        RawDocument raw = new RawDocument(
                input.toUri(), "UTF-8",
                locale(req.path("source").asText("auto")),
                locale(req.path("target").asText("pl")));
        IFilterWriter writer = null;
        int translated = 0;
        try (FilterContext ignored = new FilterContext(loaded)) {
            Path parent = output.toAbsolutePath().getParent();
            if (parent != null) Files.createDirectories(parent);
            filter.open(raw, false);
            writer = filter.createFilterWriter();
            writer.setParameters(filter.getParameters());
            writer.setOptions(locale(req.path("target").asText("pl")), "UTF-8");
            writer.setOutput(output.toString());
            Map<String, Integer> occurrences = new HashMap<>();
            while (filter.hasNext()) {
                Event event = filter.next();
                if (event.isTextUnit()) {
                    TextUnit unit = (TextUnit) event.getTextUnit();
                    String sourceId = unit.getId();
                    int occurrence = occurrences.merge(sourceId, 1, Integer::sum);
                    String targetKey = occurrence == 1 ? sourceId : sourceId + "::" + occurrence;
                    String target = byId.get(targetKey);
                    if (target != null) {
                        LocaleId targetLocale = locale(req.path("target").asText("pl"));
                        if (unit.getSourceSegments().count() > 1) {
                            throw error(
                                "SEGMENTATION_REQUIRED",
                                "Jednostka " + unit.getId() + " zawiera wiele segmentów; merge wymaga segmentowej translacji.",
                                false
                            );
                        }
                        unit.createTarget(targetLocale, true, 4);
                        unit.getTarget(targetLocale).getFirstContent().setCodedText(
                            buildTargetFragment(unit, target).getCodedText()
                        );
                        translated++;
                    }
                }
                writer.handleEvent(event);
            }
            writer.close();
            writer = null;
        } finally {
            if (writer != null) safeCancel(writer);
            safeClose(raw);
            loaded.close();
        }
        ObjectNode result = JSON.createObjectNode();
        result.put("filter", filterName);
        result.put("translated", translated);
        result.put("output", output.toString());
        return result;
    }

    private static ObjectNode hello() {
        ObjectNode result = JSON.createObjectNode();
        result.put("bridge_version", BRIDGE_VERSION);
        ArrayNode ops = result.putArray("operations");
        for (String op : List.of("hello","version","health","capabilities","extract","merge","open","next","apply","close","cancel")) ops.add(op);
        return result;
    }

    private static ObjectNode version() throws Exception {
        ObjectNode result = JSON.createObjectNode();
        result.put("bridge_version", BRIDGE_VERSION);
        result.put("protocol_version", PROTOCOL_VERSION);
        result.put("filter_count", availableFilters().size());
        return result;
    }

    private static ObjectNode health() {
        ObjectNode result = JSON.createObjectNode();
        result.put("healthy", true);
        result.put("sessions", SESSIONS.size());
        return result;
    }

    private static ObjectNode capabilities(String requested) throws Exception {
        ObjectNode result = JSON.createObjectNode();
        ArrayNode filters = result.putArray("filters");
        if (!requested.isEmpty()) filters.add(filterCapabilities(requested));
        else for (String name : availableFilters()) filters.add(filterCapabilities(name));
        return result;
    }

    private static List<String> availableFilters() throws Exception {
        if (!Files.isDirectory(FILTER_STORE)) return List.of();
        try (var stream = Files.list(FILTER_STORE)) {
            return stream.filter(Files::isDirectory)
                    .map(path -> path.getFileName().toString())
                    .sorted()
                    .toList();
        }
    }

    private static ObjectNode filterCapabilities(String name) throws Exception {
        FilterLoader.LoadedFilter loaded = loadFilter(name);
        try (FilterContext ignored = new FilterContext(loaded)) {
            IFilter filter = loaded.filter;
            ObjectNode item = JSON.createObjectNode();
            item.put("name", "okf_" + name);
            item.put("filter", name);
            item.put("display_name", filter.getDisplayName());
            item.put("mime_type", filter.getMimeType());
            item.put("configurations", filter.getConfigurations().size());
            return item;
        } finally { loaded.close(); }
    }

    private static final class FilterContext implements AutoCloseable {
        private final Thread thread = Thread.currentThread();
        private final ClassLoader previous;

        FilterContext(FilterLoader.LoadedFilter loaded) {
            previous = thread.getContextClassLoader();
            thread.setContextClassLoader(loaded.classLoader());
        }

        @Override
        public void close() {
            thread.setContextClassLoader(previous);
        }
    }

    private static FilterLoader.LoadedFilter loadFilter(String name) throws Exception {
        try {
            return FilterLoader.load(FILTER_STORE, name);
        } catch (FilterLoader.FilterLoadException e) {
            throw error(e.code, e.getMessage(), false);
        }
    }

    private static ObjectNode open(ObjectNode req) throws Exception {
        String filterName = req.path("filter").asText("");
        Path input = requiredPath(req, "input"), output = requiredPath(req, "output");
        if (!Files.isRegularFile(input)) throw error("INPUT_NOT_FOUND", "Nie znaleziono pliku wejściowego: " + input, false);
        Path parent = output.toAbsolutePath().getParent();
        if (parent != null) Files.createDirectories(parent);
        LocaleId sourceLocale = locale(req.path("source").asText("auto"));
        LocaleId targetLocale = locale(req.path("target").asText("pl"));
        FilterLoader.LoadedFilter loaded = loadFilter(filterName);
        IFilter filter = loaded.filter;
        RawDocument raw = new RawDocument(input.toUri(), "UTF-8", sourceLocale, targetLocale);
        IFilterWriter writer = null;
        try (FilterContext ignored = new FilterContext(loaded)) {
            filter.open(raw, false);
            writer = filter.createFilterWriter();
            writer.setParameters(filter.getParameters());
            writer.setOptions(targetLocale, "UTF-8");
            writer.setOutput(output.toString());
            String sessionId = req.path("session_id").asText("");
            if (sessionId.isEmpty()) sessionId = UUID.randomUUID().toString();
            if (SESSIONS.containsKey(sessionId)) throw error("INVALID_STATE", "Sesja już istnieje: " + sessionId, false);
            SESSIONS.put(sessionId, new Session(sessionId, filterName, sourceLocale, targetLocale,
                    input, output, raw, loaded, writer));
            ObjectNode result = JSON.createObjectNode();
            result.put("session_id", sessionId);
            result.put("filter", filterName);
            return result;
        } catch (Throwable e) {
            if (writer != null) safeCancel(writer);
            safeClose(raw); loaded.close();
            throw e;
        }
    }

    private static ObjectNode next(ObjectNode req) throws Exception {
        Session s = session(req);
        if (s.pendingEvent != null) throw error("INVALID_STATE", "Poprzednia jednostka TEXT_UNIT wymaga apply", false);
        try (FilterContext ignored = new FilterContext(s.loadedFilter)) {
            while (s.filter.hasNext()) {
            Event event = s.filter.next();
            if (!event.isTextUnit()) { s.writer.handleEvent(event); continue; }
            s.pendingEvent = event;
            s.pendingUnit = (TextUnit) event.getTextUnit();
            s.ordinal++;
            ObjectNode result = JSON.createObjectNode();
            result.put("event", "unit");
            result.set("unit", unitToJson(s.pendingUnit, s.ordinal));
            return result;
        }
        ObjectNode result = JSON.createObjectNode();
            result.put("event", "eof");
            result.put("count", s.ordinal);
            return result;
        }
    }

    private static ObjectNode apply(ObjectNode req) throws Exception {
        Session s = session(req);
        if (s.pendingUnit == null) throw error("INVALID_STATE", "Brak jednostki oczekującej na apply", false);
        String unitId = req.path("unit_id").asText("");
        if (!unitId.equals(s.pendingUnit.getId()))
            throw error("UNIT_NOT_FOUND", "Oczekiwano jednostki " + s.pendingUnit.getId() + ", otrzymano " + unitId, false);
        JsonNode targetNode = req.get("target");
        if (targetNode == null || !targetNode.isTextual())
            throw error("INVALID_REQUEST", "Pole target musi być tekstem w Bridge V1", false);
        try (FilterContext ignored = new FilterContext(s.loadedFilter)) {
            s.pendingUnit.setTargetContent(s.targetLocale, buildTargetFragment(s.pendingUnit, targetNode.asText()));
            s.writer.handleEvent(s.pendingEvent);
            s.pendingEvent = null; s.pendingUnit = null; s.applied++;
            ObjectNode result = JSON.createObjectNode();
            result.put("applied", true); result.put("count", s.applied);
            return result;
        }
    }

    private static TextFragment buildTargetFragment(TextUnit unit, String target) {
        if (!target.contains("\uE101") && !target.contains("\uE102") && !target.contains("\uE103"))
            return new TextFragment(target);
        List<Code> sourceCodes = new ArrayList<>();
        for (TextPart part : unit.getSource()) sourceCodes.addAll(part.getContent().getCodes());
        List<Code> targetCodes = new ArrayList<>();
        StringBuilder coded = new StringBuilder(target.length());
        for (int i = 0; i < target.length(); i++) {
            char marker = target.charAt(i);
            if (!TextFragment.isMarker(marker)) { coded.append(marker); continue; }
            if (++i >= target.length()) throw error("INLINE_CODE_MISMATCH", "Niekompletny marker inline", false);
            int sourceIndex = TextFragment.toIndex(target.charAt(i));
            if (sourceIndex < 0 || sourceIndex >= sourceCodes.size()) throw error("INLINE_CODE_MISMATCH", "Brak kodu inline", false);
            Code source = sourceCodes.get(sourceIndex);
            int index = targetCodes.size();
            targetCodes.add(source.clone());
            coded.append(marker).append(TextFragment.toChar(index));
        }
        return new TextFragment(coded.toString(), targetCodes);
    }

    private static ObjectNode close(ObjectNode req) throws Exception {
        Session s = session(req);
        if (s.pendingEvent != null) throw error("INVALID_STATE", "Nie można zamknąć sesji z niezatwierdzoną jednostką", false);
        try (FilterContext ignored = new FilterContext(s.loadedFilter)) {
            s.writer.close();
        }
        finally { safeClose(s.raw); s.loadedFilter.close(); SESSIONS.remove(s.id); }
        if (!Files.isRegularFile(s.output)) throw error("OUTPUT_ERROR", "Writer nie utworzył output", false);
        ObjectNode result = JSON.createObjectNode();
        result.put("closed", true); result.put("output", s.output.toString()); result.put("count", s.applied);
        return result;
    }

    private static ObjectNode cancel(ObjectNode req) {
        Session s = session(req);
        try (FilterContext ignored = new FilterContext(s.loadedFilter)) {
            safeCancel(s.writer);
            safeClose(s.raw);
        }
        finally { s.loadedFilter.close(); SESSIONS.remove(s.id); try { Files.deleteIfExists(s.output); } catch (Exception ignored) {} }
        ObjectNode result = JSON.createObjectNode();
        result.put("cancelled", true);
        return result;
    }

    private static Session session(ObjectNode req) {
        String id = req.path("session_id").asText("");
        Session s = SESSIONS.get(id);
        if (s == null) throw error("SESSION_NOT_FOUND", "Nie znaleziono sesji: " + id, false);
        return s;
    }

    private static Path requiredPath(ObjectNode req, String field) {
        String value = req.path(field).asText("");
        if (value.isEmpty()) throw error("INVALID_REQUEST", "Brak pola: " + field, false);
        return Paths.get(value);
    }

    private static LocaleId locale(String value) { return LocaleId.fromString(value == null || value.isEmpty() ? "auto" : value); }

    private static ObjectNode unitToJson(TextUnit unit, int ordinal) {
        ObjectNode out = JSON.createObjectNode();
        out.put("id", unit.getId());
        out.put("ordinal", ordinal);
        out.put("source", unit.getSource().getCodedText());
        out.put("plain_source", unit.getSource().getFirstContent().toText());
        ArrayNode parts = out.putArray("parts");
        for (TextPart part : unit.getSource()) {
            ObjectNode item = parts.addObject();
            item.put("id", part.getId());
            item.put("segment", part.isSegment());
            item.put("text", part.getContent().toText());
            item.put("coded_text", part.getContent().getCodedText());
            ArrayNode codes = item.putArray("codes");
            for (Code code : part.getContent().getCodes()) {
                ObjectNode c = codes.addObject();
                c.put("id", code.getId());
                c.put("tag_type", code.getTagType().name());
                c.put("type", code.getType());
                c.put("data", code.getData());
                c.put("outer_data", code.getOuterData());
                if (code.getOriginalId() != null) c.put("original_id", code.getOriginalId());
                if (code.getDisplayText() != null) c.put("display_text", code.getDisplayText());
            }
        }
        return out;
    }

    private static void cleanup(Session s) { safeCancel(s.writer); safeClose(s.raw); s.loadedFilter.close(); }
    private static void safeCancel(IFilterWriter w) { try { w.cancel(); } catch (Throwable ignored) {} safeClose(w); }
    private static void safeClose(AutoCloseable c) { if (c != null) try { c.close(); } catch (Throwable ignored) {} }
}
