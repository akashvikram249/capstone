package org.example.dashboard;

import org.junit.jupiter.api.Test;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class DashboardServerStatsTest {
    private static final Pattern STATS_PATTERN = Pattern.compile(
            "\\{\"totalRuns\":(\\d+),\"inProgress\":(\\d+),\"passed\":(\\d+),\"failed\":(\\d+)}");
    private static final long POLL_TIMEOUT_MS = 5000;

    private final HttpClient client = HttpClient.newHttpClient();

    @Test
    void emptyStateReturnsZeroCountsWithSecurityHeaders() throws Exception {
        try (ExecutionService execution = new ExecutionService(Duration.ofMillis(200));
             DashboardServer server = new DashboardServer(0, execution)) {
            server.start();

            HttpResponse<String> response = get(server, "/api/stats");

            assertEquals(200, response.statusCode());
            assertEquals("{\"totalRuns\":0,\"inProgress\":0,\"passed\":0,\"failed\":0}", response.body());
            assertEquals("no-store", response.headers().firstValue("Cache-Control").orElse(""));
            assertEquals("nosniff", response.headers().firstValue("X-Content-Type-Options").orElse(""));
        }
    }

    @Test
    void reportsInProgressRunImmediatelyAfterStart() throws Exception {
        try (ExecutionService execution = new ExecutionService(Duration.ofMillis(2000));
             DashboardServer server = new DashboardServer(0, execution)) {
            server.start();

            assertEquals(202, startRun(server, "pass").statusCode());
            HttpResponse<String> response = get(server, "/api/stats");

            assertEquals(200, response.statusCode());
            assertEquals("{\"totalRuns\":1,\"inProgress\":1,\"passed\":0,\"failed\":0}", response.body());
        }
    }

    @Test
    void countsPassedRunAfterCompletion() throws Exception {
        try (ExecutionService execution = new ExecutionService(Duration.ofMillis(200));
             DashboardServer server = new DashboardServer(0, execution)) {
            server.start();

            assertEquals(202, startRun(server, "pass").statusCode());
            HttpResponse<String> response = awaitNoneInProgress(server);

            assertEquals("{\"totalRuns\":1,\"inProgress\":0,\"passed\":1,\"failed\":0}", response.body());
        }
    }

    @Test
    void countsFailedRunAfterCompletion() throws Exception {
        try (ExecutionService execution = new ExecutionService(Duration.ofMillis(200));
             DashboardServer server = new DashboardServer(0, execution)) {
            server.start();

            assertEquals(202, startRun(server, "fail").statusCode());
            HttpResponse<String> response = awaitNoneInProgress(server);

            assertEquals("{\"totalRuns\":1,\"inProgress\":0,\"passed\":0,\"failed\":1}", response.body());
        }
    }

    @Test
    void countsMixedRunsAndTotalEqualsSumOfParts() throws Exception {
        try (ExecutionService execution = new ExecutionService(Duration.ofMillis(200));
             DashboardServer server = new DashboardServer(0, execution)) {
            server.start();

            assertEquals(202, startRun(server, "pass").statusCode());
            assertEquals(202, startRun(server, "pass").statusCode());
            assertEquals(202, startRun(server, "fail").statusCode());
            HttpResponse<String> response = awaitNoneInProgress(server);

            assertEquals("{\"totalRuns\":3,\"inProgress\":0,\"passed\":2,\"failed\":1}", response.body());
            long[] values = parse(response.body());
            assertEquals(values[1] + values[2] + values[3], values[0]);
        }
    }

    @Test
    void nonGetMethodsReturnMethodNotAllowed() throws Exception {
        try (ExecutionService execution = new ExecutionService(Duration.ofMillis(200));
             DashboardServer server = new DashboardServer(0, execution)) {
            server.start();
            URI uri = URI.create("http://localhost:" + server.port() + "/api/stats");

            for (String method : new String[] {"POST", "PUT", "DELETE"}) {
                HttpRequest.BodyPublisher body = method.equals("DELETE")
                        ? HttpRequest.BodyPublishers.noBody()
                        : HttpRequest.BodyPublishers.ofString("x=1");
                HttpResponse<String> response = client.send(
                        HttpRequest.newBuilder(uri).method(method, body).build(),
                        HttpResponse.BodyHandlers.ofString());

                assertEquals(405, response.statusCode(), method);
                assertEquals("GET", response.headers().firstValue("Allow").orElse(""), method);
                assertEquals("{\"error\":\"Use the GET method for this endpoint.\"}", response.body(), method);
            }
        }
    }

    @Test
    void trailingSlashPathReturnsNotFound() throws Exception {
        try (ExecutionService execution = new ExecutionService(Duration.ZERO);
             DashboardServer server = new DashboardServer(0, execution)) {
            server.start();

            HttpResponse<String> response = get(server, "/api/stats/");

            assertEquals(404, response.statusCode());
            assertTrue(response.body().contains("Not found"));
        }
    }

    private HttpResponse<String> awaitNoneInProgress(DashboardServer server) throws Exception {
        long deadline = System.nanoTime() + Duration.ofMillis(POLL_TIMEOUT_MS).toNanos();
        HttpResponse<String> response = get(server, "/api/stats");
        while (parse(response.body())[1] != 0 && System.nanoTime() < deadline) {
            Thread.sleep(25);
            response = get(server, "/api/stats");
        }
        assertEquals(200, response.statusCode());
        assertEquals(0, parse(response.body())[1], "runs did not complete within " + POLL_TIMEOUT_MS + " ms");
        return response;
    }

    private static long[] parse(String body) {
        Matcher matcher = STATS_PATTERN.matcher(body);
        assertTrue(matcher.matches(), "Unexpected stats body: " + body);
        return new long[] {
                Long.parseLong(matcher.group(1)),
                Long.parseLong(matcher.group(2)),
                Long.parseLong(matcher.group(3)),
                Long.parseLong(matcher.group(4))};
    }

    private HttpResponse<String> startRun(DashboardServer server, String outcome) throws Exception {
        return client.send(
                HttpRequest.newBuilder(URI.create("http://localhost:" + server.port() + "/api/runs"))
                        .header("Content-Type", "application/x-www-form-urlencoded")
                        .POST(HttpRequest.BodyPublishers.ofString(
                                "caseId=TC-9&title=Saved+case&outcome=" + outcome))
                        .build(),
                HttpResponse.BodyHandlers.ofString());
    }

    private HttpResponse<String> get(DashboardServer server, String path) throws Exception {
        HttpRequest request = HttpRequest.newBuilder(
                URI.create("http://localhost:" + server.port() + path)).GET().build();
        return client.send(request, HttpResponse.BodyHandlers.ofString());
    }
}
