package org.example.dashboard;

import org.junit.jupiter.api.Test;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

import static org.junit.jupiter.api.Assertions.assertEquals;

class StatsEndpointTest {
    private static final String EMPTY_STATS = "{\"totalRuns\":0,\"inProgress\":0,\"passed\":0,\"failed\":0}";

    private final HttpClient client = HttpClient.newHttpClient();

    @Test
    void emptyStatsOnFreshServer() throws Exception {
        try (ExecutionService execution = new ExecutionService(Duration.ofMillis(20));
             DashboardServer server = new DashboardServer(0, execution)) {
            server.start();

            HttpResponse<String> response = getStats(server);

            assertEquals(200, response.statusCode());
            assertEquals(EMPTY_STATS, response.body());
            assertJsonHeaders(response);
        }
    }

    @Test
    void statsReflectInProgress() throws Exception {
        try (ExecutionService execution = new ExecutionService(Duration.ofMillis(400));
             DashboardServer server = new DashboardServer(0, execution)) {
            server.start();

            assertEquals(202, startRun(server, "TC-1", "In progress case", "pass").statusCode());
            HttpResponse<String> response = getStats(server);

            assertEquals(200, response.statusCode());
            assertEquals("{\"totalRuns\":1,\"inProgress\":1,\"passed\":0,\"failed\":0}", response.body());
            assertJsonHeaders(response);
        }
    }

    @Test
    void statsReflectPassAndFail() throws Exception {
        try (ExecutionService execution = new ExecutionService(Duration.ofMillis(60));
             DashboardServer server = new DashboardServer(0, execution)) {
            server.start();

            assertEquals(202, startRun(server, "TC-2", "Passing case", "pass").statusCode());
            assertEquals(202, startRun(server, "TC-3", "Failing case", "fail").statusCode());

            String expected = "{\"totalRuns\":2,\"inProgress\":0,\"passed\":1,\"failed\":1}";
            HttpResponse<String> response = getStats(server);
            long deadline = System.nanoTime() + Duration.ofSeconds(5).toNanos();
            while (!expected.equals(response.body()) && System.nanoTime() < deadline) {
                Thread.sleep(20);
                response = getStats(server);
            }

            assertEquals(200, response.statusCode());
            assertEquals(expected, response.body());
            assertJsonHeaders(response);
        }
    }

    @Test
    void methodNotAllowedReturns405() throws Exception {
        try (ExecutionService execution = new ExecutionService(Duration.ofMillis(20));
             DashboardServer server = new DashboardServer(0, execution)) {
            server.start();
            URI uri = URI.create("http://localhost:" + server.port() + "/api/stats");

            HttpResponse<String> post = client.send(
                    HttpRequest.newBuilder(uri)
                            .POST(HttpRequest.BodyPublishers.noBody())
                            .build(),
                    HttpResponse.BodyHandlers.ofString());
            assertEquals(405, post.statusCode());
            assertEquals("GET", post.headers().firstValue("Allow").orElse(""));
            assertEquals("{\"error\":\"Use the GET method for this endpoint.\"}", post.body());

            HttpResponse<String> head = client.send(
                    HttpRequest.newBuilder(uri)
                            .method("HEAD", HttpRequest.BodyPublishers.noBody())
                            .build(),
                    HttpResponse.BodyHandlers.ofString());
            assertEquals(405, head.statusCode());
            assertEquals("GET", head.headers().firstValue("Allow").orElse(""));
        }
    }

    private static void assertJsonHeaders(HttpResponse<String> response) {
        assertEquals("application/json; charset=utf-8",
                response.headers().firstValue("Content-Type").orElse(""));
        assertEquals("no-store", response.headers().firstValue("Cache-Control").orElse(""));
        assertEquals("nosniff", response.headers().firstValue("X-Content-Type-Options").orElse(""));
    }

    private HttpResponse<String> getStats(DashboardServer server) throws Exception {
        HttpRequest request = HttpRequest.newBuilder(
                URI.create("http://localhost:" + server.port() + "/api/stats")).GET().build();
        return client.send(request, HttpResponse.BodyHandlers.ofString());
    }

    private HttpResponse<String> startRun(DashboardServer server, String caseId, String title, String outcome)
            throws Exception {
        String form = "caseId=" + caseId + "&title=" + title.replace(' ', '+') + "&outcome=" + outcome;
        return client.send(
                HttpRequest.newBuilder(URI.create("http://localhost:" + server.port() + "/api/runs"))
                        .header("Content-Type", "application/x-www-form-urlencoded")
                        .POST(HttpRequest.BodyPublishers.ofString(form))
                        .build(),
                HttpResponse.BodyHandlers.ofString());
    }
}
