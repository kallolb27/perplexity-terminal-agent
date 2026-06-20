# Research Desk Rules

## Citations
- Include source URLs inline: [title](url)
- For papers: cite as [title](https://arxiv.org/abs/{arxiv_id})
- Prefer primary sources (papers, official docs) over blog posts

## Papers (required tools)
- Use `paper_search` for ML research and literature questions
- Use `read_paper` with the arxiv_id from search results — do not guess IDs
- If `read_paper` returns 404, fall back to `web_fetch` on arxiv.org/abs/...
- Do not use web_search when paper_search is the right tool

## Research notes
- Save new content with `write_file` to `notes/`
- Update existing notes with `read_file` then `edit_file` — do not rewrite whole files unnecessarily
- Use `edit_file` operations: `append` for new sections, `replace` to revise, `delete` to remove stale parts
- Keep edits inside `notes/` unless the user explicitly asks otherwise
- Use lowercase hyphenated filenames: `notes/topic-name.md`

## Reading Large Files
- When you use `read_file`, always check the `has_more` flag in the result.
- If `has_more` is `true`, DO NOT answer the user or edit the file yet. You must autonomously call `read_file` again with the next `start_line` to continue reading the document.
- Only stop calling `read_file` when `has_more` is `false` or you have found the specific information you need.

## Web search
- Use `web_search` before `web_fetch` for non-paper questions
- Do not fetch more than 3 pages per question unless the user asks for depth

## Tone
- Be concise in chat; put detail in the note files