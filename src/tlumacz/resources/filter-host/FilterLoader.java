package pl.tlumacz.filterhost;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import net.sf.okapi.common.filters.IFilter;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

final class FilterLoader {
    private static final ObjectMapper JSON = new ObjectMapper();
    private static final String DESCRIPTOR = "filter.json";
    private static final String PLUGIN_MANIFEST = "plugin.json";
    private static final String ENTRY_CLASS = "entry_class";

    private FilterLoader() {}

    static LoadedFilter load(Path store, String name) throws Exception {
        if (store == null) throw new IllegalArgumentException("Brak magazynu filtrów");
        Path root = store.toAbsolutePath().normalize();
        Path packageDir = root.resolve(name).normalize();
        if (!packageDir.startsWith(root)) throw new IllegalArgumentException("Nieprawidłowa nazwa filtra: " + name);
        if (!Files.isDirectory(packageDir)) throw new FilterLoadException("FILTER_NOT_FOUND", "Brak pakietu filtra: " + name);

        boolean tplugin = Files.isRegularFile(packageDir.resolve(PLUGIN_MANIFEST));
        Path descriptor = packageDir.resolve(DESCRIPTOR);
        if (!Files.isRegularFile(descriptor))
            throw new FilterLoadException("FILTER_DESCRIPTOR_MISSING", "Brak filter.json dla filtra: " + name);

        JsonNode metadata = JSON.readTree(descriptor.toFile());
        String declaredName = metadata.path("name").asText("");
        if (!tplugin && !name.equals(declaredName))
            throw new FilterLoadException("FILTER_DESCRIPTOR_INVALID", "Nazwa filtra w descriptorze nie zgadza się z katalogiem: " + name);

        String entryClass = metadata.path(ENTRY_CLASS).asText("");
        if (entryClass.isEmpty())
            throw new FilterLoadException("FILTER_DESCRIPTOR_INVALID", "Brak entry_class dla filtra: " + name);

        List<URL> urls = new ArrayList<>();
        addJars(urls, tplugin ? packageDir.resolve("lib") : packageDir);
        if (tplugin) {
            JsonNode manifest = JSON.readTree(packageDir.resolve(PLUGIN_MANIFEST).toFile());
            addSharedJars(urls, manifest);
        }
        if (urls.isEmpty())
            throw new FilterLoadException("FILTER_ARTIFACT_MISSING", "Pakiet filtra nie zawiera JAR: " + name);

        ClassLoader parent = FilterLoader.class.getClassLoader();
        URLClassLoader loader = new ChildFirstClassLoader(urls.toArray(URL[]::new), parent, entryClass);
        ClassLoader previousContext = Thread.currentThread().getContextClassLoader();
        Thread.currentThread().setContextClassLoader(loader);
        try {
            Class<?> type = Class.forName(entryClass, true, loader);
            if (!IFilter.class.isAssignableFrom(type))
                throw new FilterLoadException("FILTER_CLASS_INVALID", "Klasa nie implementuje IFilter: " + entryClass);
            IFilter filter = (IFilter) type.getDeclaredConstructor().newInstance();
            return new LoadedFilter(filter, loader);
        } catch (Throwable error) {
            try { loader.close(); } catch (IOException ignored) {}
            throw error;
        } finally {
            Thread.currentThread().setContextClassLoader(previousContext);
        }
    }

    private static void addJars(List<URL> urls, Path directory) throws IOException {
        if (!Files.isDirectory(directory)) return;
        try (var stream = Files.walk(directory)) {
            stream.filter(path -> Files.isRegularFile(path) && path.getFileName().toString().endsWith(".jar"))
                    .sorted(Comparator.comparing(Path::toString))
                    .forEach(path -> {
                        try { urls.add(path.toUri().toURL()); }
                        catch (IOException e) { throw new UncheckedIOException(e); }
                    });
        } catch (UncheckedIOException e) {
            throw e.getCause();
        }
    }

    private static void addSharedJars(List<URL> urls, JsonNode manifest) throws IOException, FilterLoadException {
        Path sharedRoot = Path.of(System.getenv().getOrDefault(
            "TLUMACZ_FILTER_SHARED_LIBS",
            Path.of(System.getProperty("user.dir"), "src", "tlumacz", "resources", "okapi-runtime", "lib").toString()
        )).toAbsolutePath().normalize();
        JsonNode dependencies = manifest.path("dependencies").path("shared");
        if (!dependencies.isArray()) return;
        for (JsonNode dependency : dependencies) {
            String id = dependency.path("id").asText("").trim();
            String version = dependency.path("version").asText("").trim();
            if (id.isEmpty()) throw new FilterLoadException("FILTER_DEPENDENCY_INVALID", "Brak id shared library");
            String declaredFile = dependency.path("file").asText("").trim();
            String basename = declaredFile.isEmpty() ? "" : Path.of(declaredFile).getFileName().toString();
            String safeId = id.replace("/", "_").replace(":", "_");
            String safeVersion = version.isEmpty() ? "unknown" : version.replace("/", "_").replace(":", "_");
            Path jar = basename.isEmpty()
                ? sharedRoot.resolve(safeId + "--" + safeVersion + ".jar")
                : sharedRoot.resolve(basename);
            jar = jar.normalize();
            if (!jar.startsWith(sharedRoot) || !Files.isRegularFile(jar)) {
                jar = sharedRoot.resolve(safeId + "--" + safeVersion + ".jar").normalize();
            }
            if (!jar.startsWith(sharedRoot) || !Files.isRegularFile(jar)) {
                throw new FilterLoadException("FILTER_DEPENDENCY_MISSING", "Brak shared library: " + id + ":" + version);
            }
            urls.add(jar.toUri().toURL());
        }
    }

    private static final class ChildFirstClassLoader extends URLClassLoader {
        private final String entryPackage;

        ChildFirstClassLoader(URL[] urls, ClassLoader parent, String entryClass) {
            super(urls, parent);
            int separator = entryClass.lastIndexOf('.');
            this.entryPackage = separator < 0 ? entryClass : entryClass.substring(0, separator + 1);
        }

        @Override
        protected Class<?> loadClass(String name, boolean resolve) throws ClassNotFoundException {
            if (name.startsWith(entryPackage)) {
                synchronized (getClassLoadingLock(name)) {
                    Class<?> loaded = findLoadedClass(name);
                    if (loaded == null) loaded = findClass(name);
                    if (resolve) resolveClass(loaded);
                    return loaded;
                }
            }
            return super.loadClass(name, resolve);
        }
    }

    static final class LoadedFilter implements AutoCloseable {
        final IFilter filter;
        private final URLClassLoader loader;

        LoadedFilter(IFilter filter, URLClassLoader loader) {
            this.filter = filter;
            this.loader = loader;
        }

        ClassLoader classLoader() {
            return loader;
        }

        @Override
        public void close() {
            try { filter.close(); } catch (Throwable ignored) {}
            try { loader.close(); } catch (IOException ignored) {}
        }
    }

    static final class FilterLoadException extends Exception {
        final String code;
        FilterLoadException(String code, String message) {
            super(message);
            this.code = code;
        }
    }
}
