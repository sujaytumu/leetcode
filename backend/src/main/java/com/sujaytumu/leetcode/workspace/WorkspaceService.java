package com.sujaytumu.leetcode.workspace;

import com.sujaytumu.leetcode.common.ApiExceptions.NotFoundException;
import com.sujaytumu.leetcode.judge.Language;
import com.sujaytumu.leetcode.problem.Problem;
import com.sujaytumu.leetcode.problem.ProblemRepository;
import java.time.Instant;
import java.util.Comparator;
import java.util.List;
import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/** Server-side copy of a client's notes and code drafts, so they follow the device sync code. */
@Service
public class WorkspaceService {

    static final int MAX_NOTE_CHARS = 20_000;
    static final int MAX_CODE_CHARS = 60_000;

    /** {@code updatedAt} is epoch milliseconds; 0 when nothing is stored. */
    public record NoteView(String content, long updatedAt) {}

    public record DraftView(String language, String code, long updatedAt) {}

    public record Workspace(NoteView notes, List<DraftView> drafts) {}

    private final ProblemRepository problems;
    private final ProblemNoteRepository notes;
    private final CodeDraftRepository drafts;

    public WorkspaceService(ProblemRepository problems, ProblemNoteRepository notes, CodeDraftRepository drafts) {
        this.problems = problems;
        this.notes = notes;
        this.drafts = drafts;
    }

    @Transactional(readOnly = true)
    public Workspace get(UUID clientId, String slug) {
        Long problemId = requireProblem(slug).getId();
        NoteView note = notes.findByClientIdAndProblemId(clientId, problemId)
                .map(n -> new NoteView(n.getContent(), millis(n.getUpdatedAt())))
                .orElse(new NoteView("", 0));
        List<DraftView> saved = drafts.findByClientIdAndProblemId(clientId, problemId).stream()
                .sorted(Comparator.comparing(CodeDraft::getLanguage))
                .map(WorkspaceService::view)
                .toList();
        return new Workspace(note, saved);
    }

    /** Saves the note; an empty note removes it. */
    @Transactional
    public NoteView saveNote(UUID clientId, String slug, String content) {
        String text = content == null ? "" : content;
        if (text.length() > MAX_NOTE_CHARS) {
            throw new IllegalArgumentException("Notes are limited to " + MAX_NOTE_CHARS + " characters");
        }
        Long problemId = requireProblem(slug).getId();
        ProblemNote existing = notes.findByClientIdAndProblemId(clientId, problemId).orElse(null);
        if (text.isEmpty()) {
            if (existing != null) {
                notes.delete(existing);
            }
            return new NoteView("", 0);
        }
        ProblemNote note = existing != null ? existing : new ProblemNote(clientId, problemId, text);
        note.setContent(text);
        note = notes.saveAndFlush(note);
        return new NoteView(note.getContent(), millis(note.getUpdatedAt()));
    }

    @Transactional
    public DraftView saveDraft(UUID clientId, String slug, String language, String code) {
        String key = Language.fromKey(language).key();
        String text = code == null ? "" : code;
        if (text.length() > MAX_CODE_CHARS) {
            throw new IllegalArgumentException("Code is limited to " + MAX_CODE_CHARS + " characters");
        }
        Long problemId = requireProblem(slug).getId();
        CodeDraft draft = drafts.findByClientIdAndProblemIdAndLanguage(clientId, problemId, key)
                .orElseGet(() -> new CodeDraft(clientId, problemId, key, text));
        draft.setCode(text);
        return view(drafts.saveAndFlush(draft));
    }

    @Transactional
    public void deleteDraft(UUID clientId, String slug, String language) {
        String key = Language.fromKey(language).key();
        Long problemId = requireProblem(slug).getId();
        drafts.findByClientIdAndProblemIdAndLanguage(clientId, problemId, key).ifPresent(draft -> drafts.delete(draft));
    }

    private static DraftView view(CodeDraft draft) {
        return new DraftView(draft.getLanguage(), draft.getCode(), millis(draft.getUpdatedAt()));
    }

    private static long millis(Instant instant) {
        return instant.toEpochMilli();
    }

    private Problem requireProblem(String slug) {
        return problems.findBySlug(slug).orElseThrow(() -> new NotFoundException("Problem not found: " + slug));
    }
}
