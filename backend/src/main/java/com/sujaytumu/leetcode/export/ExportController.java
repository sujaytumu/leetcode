package com.sujaytumu.leetcode.export;

import com.sujaytumu.leetcode.common.Headers;
import java.io.IOException;
import java.util.UUID;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/export")
public class ExportController {

    private final ExportService service;

    public ExportController(ExportService service) {
        this.service = service;
    }

    /** Zip of the caller's accepted solutions (one folder per problem) with README indexes. */
    @GetMapping("/solutions.zip")
    public ResponseEntity<byte[]> solutions(@RequestHeader(Headers.CLIENT_ID) UUID clientId) throws IOException {
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"leetcode-solutions.zip\"")
                .contentType(MediaType.parseMediaType("application/zip"))
                .body(service.solutionsZip(clientId));
    }
}
