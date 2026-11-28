package com.sujaytumu.leetcode.config;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

class KeepAwakeTest {

    @Test
    void pingsItsOwnPublicUrlOnlyWhenConfigured() throws IOException {
        List<String> paths = new ArrayList<>();
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        server.createContext("/", exchange -> {
            paths.add(exchange.getRequestURI().getPath());
            exchange.sendResponseHeaders(200, -1);
            exchange.close();
        });
        server.start();
        String url = "http://127.0.0.1:" + server.getAddress().getPort() + "/";
        try {
            new KeepAwake(true, url).ping();
            new KeepAwake(false, url).ping();
            new KeepAwake(true, "").ping();
        } finally {
            server.stop(0);
        }
        assertEquals(List.of("/api/meta"), paths);
        assertDoesNotThrow(() -> new KeepAwake(true, url).ping()); // server gone: logged, not thrown
    }
}
