package com.sujaytumu.leetcode.workspace;

import com.sujaytumu.leetcode.common.Headers;
import com.sujaytumu.leetcode.workspace.WorkspaceService.DraftView;
import com.sujaytumu.leetcode.workspace.WorkspaceService.NoteView;
import com.sujaytumu.leetcode.workspace.WorkspaceService.Workspace;
import java.util.UUID;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/problems/{slug}/workspace")
public class WorkspaceController {

    public record NoteRequest(String content) {}

    public record DraftRequest(String code) {}

    private final WorkspaceService service;

    public WorkspaceController(WorkspaceService service) {
        this.service = service;
    }

    @GetMapping
    public Workspace get(@PathVariable String slug, @RequestHeader(Headers.CLIENT_ID) UUID clientId) {
        return service.get(clientId, slug);
    }

    @PutMapping("/notes")
    public NoteView saveNote(
            @PathVariable String slug, @RequestHeader(Headers.CLIENT_ID) UUID clientId, @RequestBody NoteRequest body) {
        return service.saveNote(clientId, slug, body.content());
    }

    @PutMapping("/drafts/{language}")
    public DraftView saveDraft(
            @PathVariable String slug,
            @PathVariable String language,
            @RequestHeader(Headers.CLIENT_ID) UUID clientId,
            @RequestBody DraftRequest body) {
        return service.saveDraft(clientId, slug, language, body.code());
    }

    @DeleteMapping("/drafts/{language}")
    public ResponseEntity<Void> deleteDraft(
            @PathVariable String slug, @PathVariable String language, @RequestHeader(Headers.CLIENT_ID) UUID clientId) {
        service.deleteDraft(clientId, slug, language);
        return ResponseEntity.noContent().build();
    }
}
